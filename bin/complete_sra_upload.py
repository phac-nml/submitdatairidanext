#!/usr/bin/env python

"""
Creates a directory to upload reads and XML files to the SRA.
"""

import argparse
import logging
from pathlib import Path

import sftp

VERSION = "0.1.0"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')


def main(args):

    upload_dir_name = None
    with open(args.upload_dir_name) as f:
        upload_dir_name = f.read().strip()
        logger.info(f"Upload directory name: {upload_dir_name}")

    if not upload_dir_name:
        logger.error("Upload directory name is empty. Please check the file.")
        exit(1)

    # Test basic network connectivity before attempting to complete upload
    if not sftp.test_connectivity(args.ftp_server, 22):
        exit(1)

    ssh_conn = None
    sftp_conn = None
    upload_dir = args.remote_path / upload_dir_name
    ssh_conn, sftp_conn = sftp.connect(args.ftp_user, args.ftp_password, args.ftp_server, upload_dir)

    try:
        sftp.upload_file(sftp_conn, args.submission_xml)
    except Exception as e:
        logger.error(f"Failed to upload {args.submission_xml}: {e}")
        exit(1)

    logger.info(f"Uploaded submission XML file: {args.submission_xml}")

    with open('submit.ready', 'w') as f:
        pass
    logger.info("Created submit.ready file.")
    sftp.upload_file(sftp_conn, 'submit.ready')
    logger.info("Uploaded submit.ready file.")

    sftp_conn.close()
    ssh_conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Complete an SRA FTP upload')
    parser.add_argument('--ftp-server', type=str, default="sftp-private.ncbi.nlm.nih.gov", help='SFTP server')
    parser.add_argument('--ftp-user', type=str, default="anonymous", help='FTP user')
    parser.add_argument('--ftp-password', type=str, default="anonymous", help='FTP password')
    parser.add_argument('--submission-xml', type=Path, help='Path to submission XML file')
    parser.add_argument('--remote-path', type=Path, help='Remote path on server')
    parser.add_argument('--upload-dir-name', type=Path, default="upload_directory_name.txt", help='File containing upload directory name')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {VERSION}', help='Show the version of the script')
    args = parser.parse_args()
    main(args)
