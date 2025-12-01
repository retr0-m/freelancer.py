from ftplib import FTP_TLS
from lead import Lead
from dotenv import load_dotenv
import os
from log import log

load_dotenv()
try:
    FTPS_HOST = os.getenv("FTPS_HOST")
    FTPS_USERNAME = os.getenv("FTPS_USERNAME")
    FTPS_PASSWORD = os.getenv("FTPS_PASSWORD")
except:
    log("One or more of the following vars is not stored in .env: FTPS_HOST, FTPS_USERNAME, FTPS_PASSWORD")


def ftps_initialize(host, username, password) -> FTP_TLS:
    log("Trying to connect to FTPS host...")
    ftps = FTP_TLS(host)
    log("Connected to FTPS host, logging in...")
    ftps.login(username, password)
    log("Logged in successfully.")
    ftps.prot_p()  # secure the data channel
    log(f"Secured data channel with PROT P. Connected to {host}")
    return ftps


def ensure_remote_dir(ftps: FTP_TLS, remote_path: str):
    """
    Recursively create remote directories if they don't exist.
    Keeps you in the final directory.
    """
    parts = remote_path.lstrip("/").split("/")
    current = ""
    for part in parts:
        current = part if current == "" else f"{current}/{part}"
        try:
            log(f"Trying to enter remote directory: {current}")
            ftps.cwd(current)
            log(f"Entered remote directory: {current}")
        except Exception as e_cwd:
            log(f"Could not enter directory {current}: {e_cwd}. Attempting to create it.")
            try:
                ftps.mkd(current)
                log(f"Created remote directory: {current}")
            except Exception as e_mkd:
                log(f"Failed to create directoy {current}: {e_mkd}")
            try:
                ftps.cwd(current)
                log(f"Entered remote directory after creation: {current}")
            except Exception as e_mkd:
                log(f"Failed to enter remote directory after creation {current}: {e_mkd}")


def ftps_upload_folder(ftps: FTP_TLS, local_folder: str, remote_folder: str):
    log(f"Preparing to upload folder: {local_folder} → {remote_folder}")

    if not os.path.exists(local_folder):
        log(f"Local folder does not exist: {local_folder}")
        return
    if not os.listdir(local_folder):
        log(f"Local folder is empty: {local_folder}")
        return

    for root, dirs, files in os.walk(local_folder):
        rel_path = os.path.relpath(root, local_folder)
        remote_path = remote_folder if rel_path == "." else f"{remote_folder}/{rel_path}"

        # ensure remote path exists and enter it
        ensure_remote_dir(ftps, remote_path)

        for filename in files:
            local_file_path = os.path.join(root, filename)
            log(f"Attempting to upload file: {local_file_path} to {remote_path}/{filename}")
            try:
                with open(local_file_path, "rb") as f:
                    full_remote = f"{remote_path}/{filename}"
                    log(f"STOR command path = {full_remote}")
                    ftps.storbinary(f"STOR {full_remote}", f)
                    log(f"Uploaded: {local_file_path} → {remote_path}/{filename}")
            except Exception as e:
                log(f"Failed to upload {local_file_path}: {e}")

    log(f"Folder upload complete for {local_folder}")


def upload_to_ftp(leads: list[Lead]) -> int:
    log("Starting FTP upload process for leads.")
    ftps = ftps_initialize(FTPS_HOST, FTPS_USERNAME, FTPS_PASSWORD)
    try:
        for lead in leads:
            local_folder = f"./leads/{lead.id}/"
            remote_folder = f"matteocola.com/preview/f/{lead.id}"
            log(f"Uploading lead ID {lead.id}")
            ftps_upload_folder(ftps, local_folder, remote_folder)
        log("All leads uploaded successfully.")
    finally:
        ftps.quit()
        log("FTPS connection closed.")

    return 0


if __name__ == "__main__":
    log("=" * 50)
    log("TESTING SCRIPT")

    l1 = Lead(1, "TEST", "21312432", "Via Trevano 74, 6900 Lugano, Switzerland", "Lugano", [], 0)
    l2 = Lead(2, "TEST2", "21312333", "Via Trevano 74, 6900 Lugano, Switzerland", "Lugano", [], 0)
    upload_to_ftp([l1, l2])