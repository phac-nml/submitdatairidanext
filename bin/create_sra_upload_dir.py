#!/usr/bin/env python

"""
Creates a directory to upload reads and XML files to the SRA.
"""

import argparse
import datetime
import logging
from pathlib import Path

import sftp

VERSION = "0.1.0"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')


def main(args):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    upload_dir_name = f"{timestamp}-submission"

    # Test basic network connectivity before attempting to create upload dir
    if not sftp.test_connectivity(args.ftp_server, 22):
        exit(1)

    ssh_conn, sftp_conn = sftp.connect(args.ftp_user, args.ftp_password, args.ftp_server, args.remote_path)
    sftp_conn.mkdir(upload_dir_name)

    sftp_conn.close()
    ssh_conn.close()

    with open(args.upload_dir_name, 'w') as f:
        f.write(upload_dir_name)
        f.write('\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Upload files to FTP server')
    parser.add_argument('--ftp-server', type=str, default="sftp-private.ncbi.nlm.nih.gov", help='SFTP server')
    parser.add_argument('--ftp-user', type=str, default="anonymous", help='FTP user')
    parser.add_argument('--ftp-password', type=str, default="anonymous", help='FTP password')
    parser.add_argument('--remote-path', type=Path, help='Remote path on server')
    parser.add_argument('--upload-dir-name', type=Path, default="upload_directory_name.txt", help='File containing upload directory name')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {VERSION}', help='Show the version of the script')
    args = parser.parse_args()
    main(args)
