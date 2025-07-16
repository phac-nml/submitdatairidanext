#!/usr/bin/env python

"""
Appends errors to upload metadata.
"""

import argparse
import csv
import json
import logging
import os

from pathlib import Path

VERSION = "0.1.0"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_upload_metadata(upload_metadata_paths: list[Path]) -> dict:
    """
    Parse the upload metadata CSV file and return the data as a dictionary.

    :param upload_metadata_paths: Path to the upload metadata CSV file
    :type metadata_path: Path
    :return: Parsed metadata
    :rtype: dict
    """
    metadata = {}
    for metadata_path in upload_metadata_paths:
        if not metadata_path.is_file():
            logger.error(f"Metadata file not found: {metadata_path}")
            continue
        logger.info(f"Parsing upload metadata: {metadata_path}")
        try:
            with open(metadata_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    irida_id = row.get('irida_id')
                    if irida_id:
                        metadata[irida_id] = row
                    else:
                        logger.warning(f"Row in {metadata_path} does not contain 'irida_id': {row}")
            logger.info(f"Parsed upload metadata: {metadata_path}")

        except csv.Error as e:
            logger.error(f"Error parsing {metadata_path}: {e}")
            continue

    return metadata


def parse_errors(errors_path: Path) -> list[dict]:
    """
    Parse the errors CSV file and return the data as a list of dictionaries.

    :param errors_path: Path to the errors CSV file
    :type errors_path: Path
    :return: Parsed errors
    :rtype: list[dict]
    """
    if not errors_path.is_file():
        logger.error(f"Errors file not found: {errors_path}")
        return []

    logger.info(f"Parsing errors: {errors_path}")
    errors = []
    try:
        with open(errors_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                errors.append(row)
        logger.info(f"Parsed errors: {errors_path}")

    except csv.Error as e:
        logger.error(f"Error parsing {errors_path}: {e}")

    return errors


def append_errors_to_metadata(upload_metadata: dict, errors: list[dict], destination: str) -> dict:
    """
    Append errors to the upload metadata.

    :param upload_metadata: Parsed upload metadata
    :type upload_metadata: dict
    :param errors: Parsed errors
    :type errors: list[dict]
    :param destination: Destination for the upload (e.g., "SRA" or "ENA")
    :type destination: str
    :return: Updated upload metadata with errors appended
    :rtype: dict
    """
    for error in errors:
        irida_id = error.get('sample')
        library_name = error.get('sample_name')
        if not all([irida_id, library_name]):
            logger.warning(f"Error row missing 'sample' or 'sample_name': {error}")
            continue
        if irida_id in upload_metadata:
            logger.warning(f"Found error for sample with upload metadata: {irida_id}")
        else:
            upload_metadata[irida_id] = {
                'irida_id': irida_id,
                'library_name': library_name,
                f'{destination.lower()}_upload_status': 'FAILED',
            }

    return upload_metadata


def main(args):
    metadata = parse_upload_metadata(args.upload_metadata)
    if not metadata:
        logger.error("No valid upload metadata found.")
        exit(1)

    errors = parse_errors(args.errors)

    metadata = append_errors_to_metadata(metadata, errors, args.destination)

    print(json.dumps(metadata, indent=4))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Complete an SRA FTP upload')
    parser.add_argument('--upload-metadata', type=Path, nargs='+', help='Path to the upload metadata CSV file(s)')
    parser.add_argument('--errors', type=Path, help='Path to the errors CSV file')
    parser.add_argument('--destination', type=str, default='SRA', help='Destination for the upload ("SRA" or "ENA", (default: "SRA"))')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {VERSION}', help='Show the version of the script')
    args = parser.parse_args()
    main(args)
