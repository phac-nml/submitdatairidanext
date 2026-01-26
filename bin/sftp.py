"""
Shared network functionality
"""

import logging
import os
import socket
from pathlib import Path

import paramiko
from paramiko.ssh_exception import AuthenticationException, NoValidConnectionsError, SSHException

VERSION = "0.1.0"

logger = logging.getLogger(__name__)

def test_connectivity(server: str, port: int = 22, timeout: int = 10) -> bool:
    """
    Test basic network connectivity to host, independent of authentication

    :param server: Server to connect to
    :param port: Port to connect over
    :param timeout: Connection timeout in seconds
    """
    logger.info(f"Testing TCP connectivity to {server}:{port}...")
    try:
        sock = socket.create_connection((server, port), timeout=timeout)
        sock.close()
        logger.info(f"Successfully connected to {server}:{port}")
        return True
    except socket.timeout:
        logger.error(f"Connection to {server}:{port} timed out")
        return False
    except Exception as e:
        logger.error(f"Connection to {server}:{port} failed: {e}")
        return False


def connect(username: str, password: str, server: str, remote_path: Path):
    """
    Connects to an SFTP server, and logs in and changes to a specific remote path

    :param username: FTP username
    :param password: FTP password
    :param server: FTP server
    :param remote_path: Remote path on the server
    :return connections: Tuple of SSH and SFTP connections
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

    return (ssh, sftp)


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
