#!/usr/bin/env python

"""Combine multiple Upload Manifest JSON Files."""

import argparse
import json
import logging
import sys

from pathlib import Path

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main(args):
    combined_manifest_by_library_name = {}

    for manifest_file in args.upload_manifests:
        if not manifest_file.is_file():
            logger.error(f"File not found: {manifest_file}")
            sys.exit(-1)
        manifest_data = {}
        with open(manifest_file, 'r') as f:
            try:
                manifest_data = json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing {manifest_file}: {e}")
                sys.exit(-1)

        library_name = manifest_data.get("library_name")
        if not library_name:
            logger.error(f"Library name not found in {manifest_file}.")
            sys.exit(-1)
        if library_name in combined_manifest_by_library_name:
            logger.error(f"Duplicate library name found: {library_name} in {manifest_file}.")
            sys.exit(-1)
        combined_manifest_by_library_name[library_name] = manifest_data

    with open(args.output, 'w') as output_file:
        try:
            json.dump(combined_manifest_by_library_name, output_file, indent=4)
            logger.info(f"Combined manifest written to {args.output}")
        except IOError as e:
            logger.error(f"Error writing to output file {args.output}: {e}")
            sys.exit(-1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a combined Upload Manifest JSON file from multiple manifest files')
    parser.add_argument('upload_manifests', type=Path, nargs='+', help='Upload Manifest JSON files')
    parser.add_argument('--output', type=str, help='Output file')
    args = parser.parse_args()
    main(args)
