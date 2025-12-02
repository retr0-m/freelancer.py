from ftplib import FTP_TLS
import os
from dotenv import load_dotenv
from log import log
from lead import Lead

def connect_ftps(host: str, username: str, password: str) -> FTP_TLS:
    """
    Connect to a Windows FTPS server (explicit FTPS, IIS compatible).
    """
    log("Attempting to connect to FTPS...")
    try:
        ftps = FTP_TLS()
        ftps.connect(host, 21, timeout=10)
        ftps.auth()
        ftps.login(username, password)
        ftps.prot_p()          # required for encrypted STOR
        log("Succesfully connected!")
    except Exception as E:
        log(f"Could not connect to ftps for the following reason: {E}")
    return ftps


# -------------------------------------------------
#   FIX: Windows IIS causes socket.timeout on STOR
#   We use a custom STOR that avoids `.unwrap()`
# -------------------------------------------------
def storbinary_no_tear(ftps: FTP_TLS, cmd: str, fp, blocksize=8192):
    """
    IIS-compatible STOR command — avoids TLS shutdown timeout.
    """
    conn = ftps.transfercmd(cmd)
    while True:
        block = fp.read(blocksize)
        if not block:
            break
        conn.sendall(block)

    try:
        conn.close()      # Do NOT call unwrap()
    except:
        pass

    ftps.voidresp()


# -------------------------------------------------
#   REMOTE FOLDER CREATION (Windows-safe)
# -------------------------------------------------
def ftps_create_folder(ftps: FTP_TLS, remote_path: str):
    """
    Creates a folder recursively on a Windows FTPS server.
    Example: ftps_create_folder(ftps, "/preview/f/123")
    """

    # Normalize path
    parts = remote_path.strip('/').split('/')

    ftps.cwd('/')  # Always start from root on Windows FTPS

    for part in parts:
        if not part:
            continue
        try:
            ftps.cwd(part)
        except:
            # Try to create folder
            try:
                ftps.mkd(part)
            except:
                pass   # It might already exist
            ftps.cwd(part)




# -------------------------------------------------
#   SEND A FILE (local → remote)
# -------------------------------------------------
def ftps_send_file(ftps: FTP_TLS, local_path: str, remote_path: str):
    """
    Upload a single file from local_path → remote_path.
    Automatically creates the remote directory tree.
    """
    # Extract directory part
    remote_dir = os.path.dirname(remote_path)

    # Ensure folder exists
    ftps_create_folder(ftps, remote_dir)

    # Confirm root for upload
    ftps.cwd('/')

    # Upload file using IIS-safe STOR
    with open(local_path, "rb") as f:
        log(f"Uploading {local_path} → {remote_path}")
        storbinary_no_tear(ftps, f"STOR {remote_path}", f)

def ftps_upload_dir(ftps: FTP_TLS, local_dir: str, remote_dir: str):
    """
    Uploads all files inside a directory (non-recursive) to a remote FTPS folder.
    Perfect for folders that contain only images or static files.
    """
    if not os.path.isdir(local_dir):
        raise ValueError(f"Local path is not a directory: {local_dir}")

    # Ensure remote directory exists
    ftps_create_folder(ftps, remote_dir)

    # Loop through files
    for filename in os.listdir(local_dir):
        local_path = os.path.join(local_dir, filename)

        # skip subfolders
        if os.path.isdir(local_path):
            continue

        remote_path = f"{remote_dir}/{filename}"

        log(f"Uploading {local_path} → {remote_path}")
        try:
            with open(local_path, "rb") as f:
                storbinary_no_tear(ftps, f"STOR {remote_path}", f)
        except Exception as e:
            log(f"ERROR WHILE UPLOADING FILE {local_path} ----- {e}")

def init_vars():
    load_dotenv()

    FTPS_HOST = os.getenv("FTPS_HOST")
    FTPS_USER = os.getenv("FTPS_USERNAME")
    FTPS_PASS = os.getenv("FTPS_PASSWORD")
    
    return FTPS_HOST, FTPS_PASS, FTPS_USER
    


def ftps_upload_lead(lead:Lead):
   
    FTPS_HOST, FTPS_PASS, FTPS_USER = init_vars()

    ftps = connect_ftps(FTPS_HOST, FTPS_USER, FTPS_PASS)

    
    ftps_create_folder(ftps, f"/matteocola.com/preview/f/{lead.id}")

    ftps_send_file(
        ftps,
        local_path=f"./leads/{lead.id}/index.html",
        remote_path=f"/matteocola.com/preview/f/{lead.id}/index.html"
    )
    ftps_create_folder(ftps, f"/matteocola.com/preview/f/{lead.id}/images")
    
    ftps_upload_dir(ftps, f"./leads/{lead.id}/images", f"/matteocola.com/preview/f/{lead.id}/images")

    log("Done!")
    
    ftps.quit()
    
    
    
def ftps_upload_lead_list(lead_list: list[Lead]):
    for lead in lead_list:
        ftps_upload_lead(lead)

if __name__ == "__main__":
    
    log("="*50)
    log("TESTING SCRIPT")
    
    #TEST 1
    log('TEST-1 with following sandbox data:      Lead(1, "Al-74", "21312432", "Via Trevano 74, 6900 Lugano, Switzerland", "Lugano", ["./leads/150/images/1.jpg","./leads/150/images/2.png"], 0)')
    l=Lead(1, "Al-74", "21312432", "Via Trevano 74, 6900 Lugano, Switzerland", "Lugano", ["./leads/150/images/1.jpg","./leads/150/images/2.png"], 0)
    ftps_upload_lead(l)
    
    