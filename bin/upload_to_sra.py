#!/usr/bin/env python

"""
Uploads files to an FTP server
"""

import argparse
import logging
import os

from pathlib import Path
from ftplib import FTP

logger = logging.getLogger(__name__)

def upload_file(file_to_upload: Path, username: str, password: str, server: str, remote_path: str):
    """
    Uploads a file to an FTP server
    :param file_to_upload: Path to the file to upload
    :param username: FTP username
    :param password: FTP password
    :param server: FTP server
    :param remote_path: Remote path on the server
    :return: None
    """
    with FTP(server) as ftp:
        ftp.login(username, password)
        logger.info(f"Connected to {server} as {username}")
        ftp.cwd(remote_path)
        logger.info(f"Changed directory to {remote_path}")
        with open(file_path, 'rb') as f:
            ftp.storbinary(f"STOR {os.path.basename(file_path)}", f)
            logger.info(f"Uploaded {file_path} to {remote_path}")


def main(args):
    for file_path in args.files_to_upload:
        upload_file(file_path, args.ftp_user, args.ftp_password, args.ftp_server, args.remote_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Upload files to FTP server')
    parser.add_argument('--ftp-server', type=str, default="ftp-private.ncbi.nlm.nih.gov", help='FTP server')
    parser.add_argument('--ftp-user', type=str, default="anonymous", help='FTP user')
    parser.add_argument('--ftp-password', type=str, default="anonymous", help='FTP password')
    parser.add_argument('--remote-path', type=str, help='Remote path on server')
    parser.add_argument('files_to_upload', type=str, nargs='+', help='Files to upload')
    args = parser.parse_args()
    main(args)