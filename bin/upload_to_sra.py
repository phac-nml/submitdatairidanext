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

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_submission_xml(submission_xml_path: Path) -> list[dict]:
    """
    Parse a submission XML file and return.

    :param submission_xml_path: Path to the submission XML file
    :type submission_xml_path: Path
    :return: List of libraries with their metadata extracted from the submission XML
    :rtype: list[dict]
    """
    tree = None
    libraries = []
    try:
        tree = ET.parse(submission_xml_path)
    except ET.ParseError as e:
        logger.error(f"Error parsing {submission_xml_path}: {e}")
        sys.exit(-1)
    except FileNotFoundError as e:
        logger.error(f"File not found: {submission_xml_path}")
        sys.exit(-1)
    except Exception as e:
        logger.error(f"An error occurred while parsing {submission_xml_path}: {e}")
        sys.exit(-1)

    if tree is None:
        logger.error(f"Could not parse {submission_xml_path}")
        sys.exit(-1)

    root = tree.getroot()
    action_elem = root.find("Action")
    for child in action_elem:
        if child.tag == "BioProject":
            parsed_submission_xml['bioproject_accession'] = child.find("PrimaryId").text
        elif child.tag == "BioSample":
            parsed_submission_xml['biosample_accession'] = child.find("PrimaryId").text
        elif child.tag == "AddFiles":
            library = {}
            for file_element in child.findall("File"):
                fastq_files = library.setdefault("fastq_files", [])
                fastq_files.append({"filename": file_element.get("file_path")})
            for attribute in child.findall("Attribute"):
                attribute_name = attribute.get("name")
                if attribute_name != "fastq_files":
                    library[attribute_name] = attribute.text
            libraries.append(library)

    return libraries

def connect_and_login(username: str, password: str, server: str, remote_path: Path) -> ftplib.FTP:
    """
    Connects to an FTP server and logs in

    :param username: FTP username
    :param password: FTP password
    :param server: FTP server
    :param remote_path: Remote path on the server
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

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    upload_dir = f"{timestamp}-submission"
    ftp.cwd(str(remote_path))
    logger.info(f"Changed directory to {remote_path}")
    try:
        ftp.mkd(upload_dir)
    except ftplib.error_perm as e:
        logger.error(f"Could not create directory {upload_dir}")
        exit(1)
    try:
        ftp.cwd(upload_dir)
    except ftplib.error_perm as e:
        logger.error(f"Could not change to directory {upload_dir}")
        exit(1)
    except IOError as e:
        logger.error(f"An error occurred: {e}")
        exit(1)
    logger.info(f"Changed directory to {remote_path}/{upload_dir}")
    logger.info(f"Current working directory: {ftp.pwd()}")

    return ftp

def upload_file(ftp: ftplib.FTP, file_to_upload: Path, ):
    """
    Uploads a file to an FTP server

    :param ftp: FTP connection
    :param file_to_upload: Path to the file to upload
    :param username: FTP username
    :param password: FTP password
    :param server: FTP server
    :param remote_path: Remote path on the server
    :return: None
    """
    with open(file_to_upload, 'rb') as f:
        ftp.storbinary(f"STOR {os.path.basename(file_to_upload)}", f)
        logger.info(f"Uploaded {file_to_upload}")


def main(args):

    ftp_conn = connect_and_login(args.ftp_user, args.ftp_password, args.ftp_server, args.remote_path)

    parsed_submission_xml = parse_submission_xml(args.submission_xml)

    files_to_upload = [args.submission_xml] + args.reads
    if not all(file.exists() for file in files_to_upload):
        logger.error("One or more files do not exist. Please check the paths.")
        exit(1)

    timestamp_upload_start = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    upload_metadata_by_library_name = {}
    for library in parsed_submission_xml:
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
        upload_file(ftp_conn, file_path)

    # Create an empty 'submission.ready' file in the remote directory
    with open('submission.ready', 'w') as f:
        pass


    upload_file(ftp_conn, 'submission.ready')
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
    parser.add_argument('--submission-xml', type=Path, help='Path to submission XML file')
    parser.add_argument('--reads', type=Path, nargs='+', help='Path to reads file')
    parser.add_argument('--upload-metadata', type=Path, default="upload_metadata.csv", help='Path to file to write upload metadata')
    args = parser.parse_args()
    main(args)
