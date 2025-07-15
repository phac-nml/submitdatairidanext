#!/usr/bin/env python

"""
Uploads files to the ENA using the ena-webin-cli tool.
"""

import argparse
import csv
import datetime
import json
import logging
import os
import subprocess
import sys

from pathlib import Path

VERSION = "0.1.0"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def parse_upload_manifest(manifest_path: Path) -> dict:
    """
    Parse an upload manifest JSON file and return the parsed data.

    :param manifest_path: Path to the multi-upload manifest JSON file
    :type manifest_path: Path
    :return: Parsed manifest data
    :rtype: dict
    """
    if not manifest_path.is_file():
        logger.error(f"Manifest file not found: {manifest_path}")
        sys.exit(1)

    manifest_data = {}
    try:
        with open(manifest_path, 'r') as f:
            manifest_data = json.load(f)
            logger.info(f"Parsed upload manifest: {manifest_path}")

    except json.JSONDecodeError as e:
        logger.error(f"Error parsing {manifest_path}: {e}")
        sys.exit(1)

    return manifest_data


def main(args):
    upload_manifest = parse_upload_manifest(args.upload_manifest)

    if not upload_manifest:
        logger.error("No valid upload manifest data found.")
        exit(1)

    library_name = upload_manifest.get("library_name", None)

    # Temporarily inducing failure on one test input to test error handling
    if library_name.startswith('FAILME'):
        logger.error(f"Failed to upload files for library: {library_name}")
        exit(1)

    if not library_name:
        logger.error("Library name not found in upload manifest.")
        exit(1)

    upload_metadata = {
        "library_name": library_name,
        "ena_upload_status": "PENDING",
        "timestamp_ena_upload_start": None,
        "timestamp_ena_upload_end": None,
    }

    # Temporarily only performing validation here
    # So we can test/develop without performing any actual uploads.
    upload_command = [
        "ena-webin-cli",
        "-context", "reads",
        "-userName", args.upload_username,
        "-password", args.upload_password,
        "-manifest", str(args.upload_manifest),
        "-inputDir", '.',
        "-validate",
        "-test" if args.test_upload else ""
    ]

    # Execute the upload command
    timestamp_upload_start = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    upload_metadata["timestamp_ena_upload_start"] = timestamp_upload_start
    try:
        subprocess.run(upload_command, check=True)
        logger.info(f"Successfully uploaded files for library: {library_name}")
        timestamp_upload_end = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        upload_metadata["timestamp_ena_upload_end"] = timestamp_upload_end
        upload_metadata["ena_upload_status"] = "COMPLETED"
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to upload files for library {library_name}: {e}")
        upload_metadata["ena_upload_status"] = "FAILED"
    except Exception as e:
        logger.error(f"An unexpected error occurred while uploading files for library {library_name}: {e}")
        upload_metadata["ena_upload_status"] = "FAILED"

    upload_metadata_path = Path(args.upload_metadata)
    with open(upload_metadata_path, 'w', newline='') as csvfile:
        fieldnames = ["library_name", "ena_upload_status", "timestamp_ena_upload_start", "timestamp_ena_upload_end"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(upload_metadata)
    logger.info(f"Upload metadata written to {upload_metadata_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Upload files to ENA using webin-cli')
    parser.add_argument('--upload-username', type=str, help='Upload user')
    parser.add_argument('--upload-password', type=str, help='Upload password')
    parser.add_argument('--upload-manifest', type=Path, help='Path upload manifest JSON file')
    parser.add_argument('--input-dir', type=Path, help='Path to location of files to upload')
    parser.add_argument('--test-upload', action='store_true', help='Submit a test upload')
    parser.add_argument('--upload-metadata', type=Path, default="upload_metadata.csv", help='Path to file to write upload metadata')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {VERSION}', help='Show the version of the script')
    args = parser.parse_args()
    main(args)
