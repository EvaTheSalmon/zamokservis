import os.path
import sys
import argparse
import logging
import datetime
import subprocess
import tarfile
import paramiko

from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-5.5s]  %(message)s",
    handlers=[
        logging.FileHandler(
            "logs/" + f"{datetime.now().strftime('%d-%b-%Y %H_%M_%S')}.log"
        ),
        logging.StreamHandler(sys.stdout),
    ],
)


def main() -> None:

    load_dotenv(".env")

    host = os.getenv("SFTP_HOST")
    port = int(os.getenv("SFTP_PORT", 22))
    username = os.getenv("SFTP_USERNAME")
    password = os.getenv("SFTP_PASSWORD")

    local_public_dir = os.getenv("LOCAL_PUBLIC_DIR")
    local_backup_dir = os.getenv("LOCAL_BACKUP_DIR")
    remote_webroot_dir = os.getenv("REMOTE_WEBROOT_DIR")

    parser = argparse.ArgumentParser(
        usage="%(prog)s [options]",
        description="This is a tool to \
                                     build and upload website",
    )

    args = parser.parse_args()

    remove_public_dir(local_public_dir)
    gohugo_run()
    tar_public()
    rm_on_server(host, port, username, password, local_backup_dir, remote_webroot_dir)
    sftp_to_server(host, port, username, password, local_backup_dir, remote_webroot_dir)


def remove_public_dir(public_dir) -> None:

    def deltree(target):
        for d in os.listdir(target):
            try:
                deltree(target + "/" + d)
            except OSError:
                os.remove(target + "/" + d)
        os.rmdir(target)

    deltree(public_dir)


def gohugo_run() -> None:
    cmd = "c:\\gohugo"
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, creationflags=0x08000000)
    process.wait()


def tar_public(public_dir) -> None:
    with tarfile.open(public_dir + "\public.tar.gz", "w:gz") as tar:
        tar.add(public_dir, arcname=".")


def rm_on_server(host: str, port: int, username: str, password: str, local_backup_dir: str, remote_webroot_dir: str) -> None:

    try:
        transport = paramiko.Transport((host, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        ssh_client = transport.open_channel("session")

        # Create current state backup
        backup_filename = f"{remote_webroot_dir.rstrip('/').split('/')[-1]}_backup.tar.gz"

        backup_filepath = f"/tmp/{backup_filename}"

        archive_command = f"tar -czf {backup_filepath} -C {remote_webroot_dir} ."

        ssh_client.exec_command(archive_command)

        ssh_client.recv_exit_status()

        # Download backup
        local_backup_path = os.path.join(local_backup_dir, backup_filename)
        
        sftp.get(backup_filepath, local_backup_path)
        
        print(f"Backup downloaded {backup_filename} to {local_backup_path}")

        # Removing main dir content
        remove_command = f"rm -rf {remote_webroot_dir}/*"
        
        ssh_client.exec_command(remove_command)
        
        ssh_client.recv_exit_status()
        
        print(f"Main dir {remote_webroot_dir} cleared ")

    except Exception as e:
        print(f"Error occured: {e}")

    finally:
        sftp.close()
        ssh_client.close()
        transport.close()


def sftp_to_server(host: str, port: int, username: str, password: str, local_backup_dir: str, remote_webroot_dir: str) -> None:

    transport = paramiko.Transport((host, port))

    try:
        transport.connect(username=username, password=password)

        sftp = paramiko.SFTPClient.from_transport(transport)

        sftp.put(local_backup_dir, remote_webroot_dir)

        ssh_client = transport.open_channel("session")

        print(f"File succesfully uploaded {remote_webroot_dir}")

        untar_command = f"tar -xvzf {remote_webroot_dir}"

        ssh_client.exec_command(untar_command)

        ssh_client.recv_exit_status()


    except Exception as e:
        print(f"Error occured: {e}")

    finally:
        sftp.close()
        ssh_client.close()
        transport.close()