import os.path
import sys
import argparse
import logging
import datetime
import subprocess
import tarfile
import ftplib

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-5.5s]  %(message)s",
    handlers=[
        logging.FileHandler(
            "logs/" + f"{datetime.now().strftime('%d-%b-%Y %H_%M_%S')}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

def main() -> None:

    parser = argparse.ArgumentParser(usage="%(prog)s [options]", description="This is a tool to \
                                     build and upload website")
    
    parser.add_argument(
        "public_dir", metavar='/path/to/your.dir', type=str,
        help="input path public folder"
    )

    args = parser.parse_args()
    public_dir = args.dest_dir
    

    remove_public_dir(public_dir)
    gohugo_run()
    tar_public()
    rm_on_server()
    ftp_to_server()
    untar_on_server()


def remove_public_dir(public_dir) -> None:

    def deltree(target):
        for d in os.listdir(target):
            try:
                deltree(target + '/' + d)
            except OSError:
                os.remove(target + '/' + d)
        os.rmdir(target)
    
    deltree(public_dir)


def gohugo_run() -> None:
    cmd = "c:\\gohugo"
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, creationflags=0x08000000)
    process.wait()

def tar_public(public_dir) -> None:
        with tarfile.open(public_dir + "\public.tar.gz", "w:gz") as tar:
            tar.add(public_dir, arcname=".")
    
def rm_on_server() -> None:
    

def ftp_to_server() -> None:


def untar_on_server() -> None: