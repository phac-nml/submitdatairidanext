#!/usr/bin/env python

"""
Creates a directory to upload reads and XML files to the SRA.
"""

import argparse
import datetime
import ftplib
import logging

from pathlib import Path

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def connect_and_create_upload_dir(username: str, password: str, server: str, remote_path: Path, upload_dir_name: str) -> ftplib.FTP:
    """
    Connects to an FTP server, logs in, and creates a directory for uploads.

    :param username: FTP username
    :param password: FTP password
    :param server: FTP server
    :param remote_path: Remote path on the server
    :param upload_dir_name: Name of the directory to create for uploads
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

    ftp.cwd(str(remote_path))
    logger.info(f"Changed directory to {remote_path}")
    try:
        ftp.mkd(upload_dir_name)
    except ftplib.error_perm as e:
        logger.error(f"Could not create directory {upload_dir_name}")
        exit(1)

    return ftp


def main(args):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    upload_dir_name = f"{timestamp}-submission"
    ftp_conn = connect_and_create_upload_dir(args.ftp_user, args.ftp_password, args.ftp_server, args.remote_path, upload_dir_name)
    with open(args.upload_dir_name, 'w') as f:
        f.write(upload_dir_name)
        f.write('\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Upload files to FTP server')
    parser.add_argument('--ftp-server', type=str, default="ftp-private.ncbi.nlm.nih.gov", help='FTP server')
    parser.add_argument('--ftp-user', type=str, default="anonymous", help='FTP user')
    parser.add_argument('--ftp-password', type=str, default="anonymous", help='FTP password')
    parser.add_argument('--remote-path', type=Path, help='Remote path on server')
    parser.add_argument('--upload-dir-name', type=Path, default="upload_directory_name.txt", help='File containing upload directory name')
    args = parser.parse_args()
    main(args)