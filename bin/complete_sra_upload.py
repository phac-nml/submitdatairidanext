#!/usr/bin/env python

"""
Creates a directory to upload reads and XML files to the SRA.
"""

import argparse
import datetime
import ftplib
import logging
import os
import socket

from pathlib import Path

import paramiko
from paramiko.ssh_exception import AuthenticationException, NoValidConnectionsError, SSHException


VERSION = "0.1.0"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

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

    ssh_conn = None
    ftp_conn = None
    ssh_conn, ftp_conn = connect_and_login(args.ftp_user, args.ftp_password, args.ftp_server, args.remote_path, upload_dir_name)

    try:
        upload_file(ftp_conn, args.submission_xml)
    except Exception as e:
        logger.error(f"Failed to upload {args.submission_xml}: {e}")
        exit(1)

    logger.info(f"Uploaded submission XML file: {args.submission_xml}")

    with open('submission.ready', 'w') as f:
        pass
    logger.info("Created submission.ready file.")
    upload_file(ftp_conn, 'submission.ready')
    logger.info("Uploaded submission.ready file.")

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
