#!/usr/bin/env python

"""
Creates a directory to upload reads and XML files to the SRA.
"""

import argparse
import datetime
import logging
import socket

from pathlib import Path

import paramiko
from paramiko.ssh_exception import AuthenticationException, NoValidConnectionsError, SSHException

VERSION = "0.1.0"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')


def connect_and_create_upload_dir(username: str, password: str, server: str, remote_path: Path, upload_dir_name: str):
    """
    Connects to an SFTP server and logs in

    :param username: FTP username
    :param password: FTP password
    :param server: FTP server
    :param remote_path: Remote path on the server
    :param upload_dir_name: Name of the directory to upload files to
    :return ftp: FTP connection
    """
    ssh = None
    sftp = None
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
        sftp = ssh.open_sftp()
        logger.info(f"Connected to {server} as {username}")

        cwd = sftp.getcwd()
        logger.info(f"Current working directory: {cwd}")

        sftp.chdir(str(remote_path))
        logger.info(f"Changed directory to {remote_path}")

        sftp.mkdir(upload_dir_name)

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

    return None


def main(args):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    upload_dir_name = f"{timestamp}-submission"

    connect_and_create_upload_dir(args.ftp_user, args.ftp_password, args.ftp_server, args.remote_path, upload_dir_name)
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
