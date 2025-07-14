#!/usr/bin/env python

"""
Creates a directory to upload reads and XML files to the SRA.
"""

import argparse
import datetime
import ftplib
import logging
import os

from pathlib import Path

VERSION = "0.1.0"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

    upload_dir_name = None
    with open(args.upload_dir_name, 'r') as f:
        upload_dir_name = f.read().strip()
        logger.info(f"Upload directory name: {upload_dir_name}")

    if not upload_dir_name:
        logger.error("Upload directory name is empty. Please check the file.")
        exit(1)

    ftp_conn = connect_and_login(args.ftp_user, args.ftp_password, args.ftp_server, args.remote_path, upload_dir_name)

    upload_file(ftp_conn, args.submission_xml)
    logger.info(f"Uploaded submission XML file: {args.submission_xml}")

    with open('submission.ready', 'w') as f:
        pass
    logger.info("Created submission.ready file.")
    upload_file(ftp_conn, 'submission.ready')
    logger.info("Uploaded submission.ready file.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Complete an SRA FTP upload')
    parser.add_argument('--ftp-server', type=str, default="ftp-private.ncbi.nlm.nih.gov", help='FTP server')
    parser.add_argument('--ftp-user', type=str, default="anonymous", help='FTP user')
    parser.add_argument('--ftp-password', type=str, default="anonymous", help='FTP password')
    parser.add_argument('--submission-xml', type=Path, help='Path to submission XML file')
    parser.add_argument('--remote-path', type=Path, help='Remote path on server')
    parser.add_argument('--upload-dir-name', type=Path, default="upload_directory_name.txt", help='File containing upload directory name')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {VERSION}', help='Show the version of the script')
    args = parser.parse_args()
    main(args)
