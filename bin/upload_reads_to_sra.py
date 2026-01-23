#!/usr/bin/env python

"""
Uploads files to the SRA using SFTP.
"""

import argparse
import csv
import datetime
import logging
import os
import socket
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import paramiko
from paramiko.ssh_exception import AuthenticationException, NoValidConnectionsError, SSHException

VERSION = "0.1.0"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')


def parse_addfiles_xml(addfiles_xml_path: Path) -> dict:
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

def connect_and_login(username: str, password: str, server: str, remote_path: Path, upload_dir_name: str):
    """
    Connects to an SFTP server and logs in

    :param username: FTP username
    :param password: FTP password
    :param server: SFTP server
    :param remote_path: Remote path on the server
    :param upload_dir_name: Name of the directory to upload files to
    """
    ssh = None
    ftp = None
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            server,
            port=22,
            username=username,
            password=password,
            allow_agent=False,      # Don't try SSH agent
            look_for_keys=False,    # Don't look for key files
            gss_auth=False,         # Don't try GSSAPI
            gss_kex=False           # Don't try GSSAPI key exchange
        )
        ftp = ssh.open_sftp()
        upload_dir = remote_path / upload_dir_name
        ftp.chdir(str(upload_dir))

    except AuthenticationException as e:
        logger.error(f"Authentication failed: {e}")
        raise

    except NoValidConnectionsError as e:
        logger.error(f"Could not connect to {server}:22 - check network/firewall: {e}")
        raise

    except socket.timeout as e:
        logger.error(f"Connection timed out: {e}")
        raise

    except SSHException as e:
        logger.error(f"SSH error: {e}")
        raise

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

    return (ssh, ftp)

def upload_file(sftp: paramiko.SFTPClient, file_to_upload: Path):
    """
    Uploads a file to an SFTP server

    :param ftp: FTP connection
    :param file_to_upload: Path to the file to upload
    :return: None
    """
    def progress_callback(transferred, total):
        pct = (transferred / total) * 100 if total > 0 else 0
        logger.debug(f"Transferred {transferred}/{total} bytes ({pct:.1f}%)")

    localpath = file_to_upload
    remotepath = os.path.basename(file_to_upload)
    try:
        sftp.put(localpath, remotepath, callback=progress_callback)
        logger.info(f"Upload complete: {remotepath}")

        # Verify file exists
        remote_stat = sftp.stat(remotepath)
        logger.info(f"Remote file size: {remote_stat.st_size} bytes")

    except socket.timeout as e:
        logger.error(f"Connection timed out: {e}")
        raise

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


def main(args):

    upload_dir_name = None
    with open(args.upload_dir_name, 'r') as f:
        upload_dir_name = f.read().strip()
        logger.info(f"Upload directory name: {upload_dir_name}")

    if not upload_dir_name:
        logger.error("Upload directory name is empty. Please check the file.")
        exit(1)

    library = parse_addfiles_xml(args.addfiles_xml)

    # Temporarily inducing failure on one test input to test error handling
    if library['library_name'].startswith('FAILME'):
        logger.error(f"Failed to upload files for library: {library['library_name']}")
        exit(1)

    ssh_conn = None
    ftp_conn = None
    try:
        ssh_conn, ftp_conn = connect_and_login(args.ftp_user, args.ftp_password, args.ftp_server, args.remote_path, upload_dir_name)
    except Exception as e:
        logger.error(f"Connection failed: {e}")
        exit(1)

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
        "irida_id": args.irida_id,
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
        "irida_id",
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
    parser.add_argument('--ftp-server', type=str, default="sftp-private.ncbi.nlm.nih.gov", help='FTP server')
    parser.add_argument('--ftp-user', type=str, default="anonymous", help='FTP user')
    parser.add_argument('--ftp-password', type=str, default="anonymous", help='FTP password')
    parser.add_argument('--remote-path', type=Path, help='Remote path on server')
    parser.add_argument('--addfiles-xml', type=Path, help='Path to addfiles XML file')
    parser.add_argument('--reads', type=Path, nargs='+', help='Path to reads file')
    parser.add_argument('--upload-dir-name', type=Path, default="sra_upload_directory_name.txt", help='File containing upload directory name')
    parser.add_argument('--upload-metadata', type=Path, default="upload_metadata.csv", help='Path to file to write upload metadata')
    parser.add_argument('--irida-id', type=str, help='IRIDA ID for the library')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {VERSION}', help='Show the version of the script')
    args = parser.parse_args()
    main(args)
