#!/usr/bin/env python

"""
Uploads files to an FTP server
"""

import argparse
import csv
import datetime
import ftplib
import json
import logging
import os
import subprocess
import sys

from pathlib import Path

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def parse_multi_upload_manifest(manifest_path: Path) -> dict:
    """
    Parse a multi-upload manifest JSON file and return the parsed data.

    :param manifest_path: Path to the multi-upload manifest JSON file
    :type manifest_path: Path
    :return: Parsed manifest data
    :rtype: dict
    """
    if not manifest_path.is_file():
        logger.error(f"Manifest file not found: {manifest_path}")
        sys.exit(-1)

    manifest_data = {}
    try:
        with open(manifest_path, 'r') as f:
            manifest_data = json.load(f)
            logger.info(f"Parsed multi-upload manifest: {manifest_path}")

    except json.JSONDecodeError as e:
        logger.error(f"Error parsing {manifest_path}: {e}")
        sys.exit(-1)

    return manifest_data



def main(args):
    upload_manifest_by_library_name = parse_multi_upload_manifest(args.multi_upload_manifest)

    if not upload_manifest_by_library_name:
        logger.error("No valid upload manifest data found.")
        sys.exit(-1)

    for library_name, upload_manifest in upload_manifest_by_library_name.items():
        logger.info(f"Processing library: {library_name}")
        upload_dir_name = f"{library_name}_upload"
        os.makedirs(upload_dir_name)
        os.chdir(upload_dir_name)
        logger.info(f"Changed working directory to {upload_dir_name}")
        for fastq_file in upload_manifest.get("fastq", []):
            fastq_file_path = Path('..', fastq_file['value'])
            if not fastq_file_path.is_file():
                logger.error(f"Fastq file not found: {fastq_file_path}")
                sys.exit(-1)
            try:
                # symlink the fastq file to the upload directory
                os.symlink(fastq_file_path, fastq_file_path.name)
            except FileExistsError:
                logger.warning(f"File already exists in upload directory: {fastq_file_path.name}, skipping symlink creation.")
            except OSError as e:
                logger.error(f"Error creating symlink for {fastq_file_path}: {e}")
                sys.exit(-1)

        upload_manifest_path = Path("upload_manifest.json")
        with open(upload_manifest_path, 'w') as f:
            try:
                json.dump(upload_manifest, f, indent=4)
                f.write('\n')
                logger.info(f"Written upload manifest for library {library_name} to {upload_manifest_path}")
            except IOError as e:
                logger.error(f"Error writing upload manifest for library {library_name}: {e}")
                sys.exit(-1)

        # Temporarily only performing validation here
        # So we can test/develop without performing any actual uploads.
        upload_command = [
            "ena-webin-cli",
            "-context", "reads",
            "-userName", args.upload_username,
            "-password", args.upload_password,
            "-manifest", str(upload_manifest_path),
            "-inputDir", '.',
            "-validate",
            "-test" if args.test_upload else ""
        ]

        # Execute the upload command
        try:
            subprocess.run(upload_command, check=True)
            logger.info(f"Successfully uploaded files for library: {library_name}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to upload files for library {library_name}: {e}")
            sys.exit(-1)

        os.chdir('..')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Upload files to ENA using webin-cli')
    parser.add_argument('--upload-username', type=str, help='Upload user')
    parser.add_argument('--upload-password', type=str, help='Upload password')
    parser.add_argument('--multi-upload-manifest', type=Path, help='Path multi upload manifest JSON file')
    parser.add_argument('--input-dir', type=Path, help='Path to location of files to upload')
    parser.add_argument('--test-upload', action='store_true', help='Submit a test upload')
    parser.add_argument('--upload-metadata', type=Path, default="upload_metadata.csv", help='Path to file to write upload metadata')
    args = parser.parse_args()
    main(args)
