#!/usr/bin/env python

"""
Uploads files to the SRA using FTP.
"""

import argparse
import csv
import datetime
import ftplib
import json
import logging
import os
import sys

import xml.etree.ElementTree as ET

from pathlib import Path

VERSION = "0.1.0"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def parse_addfiles_xml(addfiles_xml_path: Path) -> list[dict]:
    """
    Parse an addfiles XML file and return.

    :param addfiles_xml_path: Path to the addfiles XML file
    :type addfiles_xml_path: Path
    :return: Dict of metadata extracted from the addfiles XML file
    :rtype: dict
    """
    tree = None
    try:
        tree = ET.parse(addfiles_xml_path)
    except ET.ParseError as e:
        logger.error(f"Error parsing addfiles_xml_path: {e}")
        sys.exit(-1)
    except FileNotFoundError as e:
        logger.error(f"File not found: {addfiles_xml_path}")
        sys.exit(-1)
    except Exception as e:
        logger.error(f"An error occurred while parsing {addfiles_xml_path}: {e}")
        sys.exit(-1)

    if tree is None:
        logger.error(f"Could not parse {addfiles_xml_path}")
        sys.exit(-1)

    library = {}
    root = tree.getroot()
    if root.tag == "AddFiles":
        library = {}
        for file_element in root.findall("File"):
            fastq_files = library.setdefault("fastq_files", [])
            fastq_files.append({"filename": file_element.get("file_path")})
        for attribute in root.findall("Attribute"):
            attribute_name = attribute.get("name")
            if attribute_name != "fastq_files":
                library[attribute_name] = attribute.text

    return library

def connect_and_login(username: str, password: str, server: str, remote_path: Path, upload_dir_name: str) -> ftplib.FTP:
    """
    Connects to an FTP server and logs in

    :param username: FTP username
    :param password: FTP password
    :param server: FTP server
    :param remote_path: Remote path on the server
    :param upload_dir_name: Name of the directory to upload files to
    :return ftp: FTP connection
    """
    ftp = None
    try:
        ftp = ftplib.FTP(server, user=username, passwd=password)
    except ConnectionRefusedError as e:
        logger.error(f"Could not connect to {server} as {username}")
        exit(1)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        exit(1)
    if not ftp:
        logger.error("Could not connect to FTP server")
        exit(1)

    logger.info(f"Connected to {server} as {username}")
    cwd = ftp.pwd()
    logger.info(f"Current working directory: {cwd}")

    upload_dir = os.path.join(remote_path, upload_dir_name)

    try:
        ftp.cwd(upload_dir)
    except ftplib.error_perm as e:
        logger.error(f"Could not change to directory {upload_dir}")
        exit(1)
    except IOError as e:
        logger.error(f"An error occurred: {e}")
        exit(1)
    logger.info(f"Changed directory to {upload_dir}")
    logger.info(f"Current working directory: {ftp.pwd()}")

    return ftp

def upload_file(ftp: ftplib.FTP, file_to_upload: Path, ):
    """
    Uploads a file to an FTP server

    :param ftp: FTP connection
    :param file_to_upload: Path to the file to upload
    :return: None
    """
    # Temporarily forcing failure on one test input to test error handling
    if file_to_upload.name.startswith('sample2'):
        raise Exception("Simulated upload failure for testing purposes.")
    with open(file_to_upload, 'rb') as f:
        ftp.storbinary(f"STOR {os.path.basename(file_to_upload)}", f)
        logger.info(f"Uploaded {file_to_upload}")


def main(args):

    upload_dir_name = None
    with open(args.upload_dir_name, 'r') as f:
        upload_dir_name = f.read().strip()
        logger.info(f"Upload directory name: {upload_dir_name}")

    if not upload_dir_name:
        logger.error("Upload directory name is empty. Please check the file.")
        exit(1)

    library = parse_addfiles_xml(args.addfiles_xml)

    ftp_conn = connect_and_login(args.ftp_user, args.ftp_password, args.ftp_server, args.remote_path, upload_dir_name)

    files_to_upload =  args.reads
    if not all(file.exists() for file in files_to_upload):
        logger.error("One or more files do not exist. Please check the paths.")
        exit(1)

    timestamp_upload_start = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    upload_metadata_by_library_name = {}

    library_name = library.get("library_name", None)
    if not library_name:
        logger.error("Library name is missing in the submission XML.")
        exit(-1)
    library_metadata = {
        "library_name": library.get("library_name", None),
        "sra_upload_status": "PENDING",
        "timestamp_sra_upload_start": timestamp_upload_start,
        "timestamp_sra_upload_complete": None,
    }
    upload_metadata_by_library_name[library_name] = library_metadata

    for file_path in files_to_upload:
        try:
            upload_file(ftp_conn, file_path)
        except Exception as e:
            logger.error(f"Failed to upload {file_path}: {e}")
            library_metadata["sra_upload_status"] = "FAILED"
            library_metadata["timestamp_sra_upload_complete"] = None
            exit(-1)

    timestamp_upload_complete = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for library_name, metadata in upload_metadata_by_library_name.items():
        metadata["sra_upload_status"] = "COMPLETED"
        metadata["timestamp_sra_upload_complete"] = timestamp_upload_complete

    # Write upload metadata to a CSV file
    upload_metadata_path = args.upload_metadata
    upload_metadata_fieldnames = [
        "library_name",
        "sra_upload_status",
        "timestamp_sra_upload_start",
        "timestamp_sra_upload_complete",
    ]
    with open(upload_metadata_path, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=upload_metadata_fieldnames)
        writer.writeheader()
        for library_name, metadata in upload_metadata_by_library_name.items():
            writer.writerow(metadata)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Upload files to FTP server')
    parser.add_argument('--ftp-server', type=str, default="ftp-private.ncbi.nlm.nih.gov", help='FTP server')
    parser.add_argument('--ftp-user', type=str, default="anonymous", help='FTP user')
    parser.add_argument('--ftp-password', type=str, default="anonymous", help='FTP password')
    parser.add_argument('--remote-path', type=Path, help='Remote path on server')
    parser.add_argument('--addfiles-xml', type=Path, help='Path to addfiles XML file')
    parser.add_argument('--reads', type=Path, nargs='+', help='Path to reads file')
    parser.add_argument('--upload-dir-name', type=Path, default="sra_upload_directory_name.txt", help='File containing upload directory name')
    parser.add_argument('--upload-metadata', type=Path, default="upload_metadata.csv", help='Path to file to write upload metadata')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {VERSION}', help='Show the version of the script')
    args = parser.parse_args()
    main(args)
