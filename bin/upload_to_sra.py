#!/usr/bin/env python

"""
Uploads files to an FTP server
"""

import argparse
import datetime
import ftplib
import logging
import os

from pathlib import Path

logger = logging.getLogger(__name__)


def connect_and_login(username: str, password: str, server: str, remote_path: str) -> ftplib.FTP:
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
        ftp = ftplib.FTP(server, user=username, passwd=password, source_address=('0.0.0.0', 0))
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
    ftp.cwd(remote_path)
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
    logging_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=logging_format)

    ftp_conn = connect_and_login(args.ftp_user, args.ftp_password, args.ftp_server, args.remote_path)

    for file_path in args.files_to_upload:
        upload_file(ftp_conn, file_path)

    # Create an empty 'submission.ready' file in the remote directory
    with open('submission.ready', 'w') as f:
        pass
    upload_file(ftp_conn, 'submission.ready')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Upload files to FTP server')
    parser.add_argument('--ftp-server', type=str, default="ftp-private.ncbi.nlm.nih.gov", help='FTP server')
    parser.add_argument('--ftp-user', type=str, default="anonymous", help='FTP user')
    parser.add_argument('--ftp-password', type=str, default="anonymous", help='FTP password')
    parser.add_argument('--remote-path', type=str, help='Remote path on server')
    parser.add_argument('files_to_upload', type=str, nargs='+', help='Files to upload')
    args = parser.parse_args()
    main(args)
