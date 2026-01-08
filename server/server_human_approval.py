"""
Docstring for server.server_human_approval
hosts a page with the leads index.html file in a temp folder (server.temp.lead_id)
and if the user accepts it will be uploaded to FTPS
"""

import shutil
from pathlib import Path
import sys

from instagram.social_media_manager import InstagramManager

sys.path.insert(1, '../')
import screenshot_website
import qr_generator
import create_documentation
from lead import Lead
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from log import log
import ftp_manager

import database
from config import TEMP_PATH

from fastapi.responses import FileResponse
import threading


app = FastAPI()
srv=None

TEMP_DIR = Path(TEMP_PATH)
log(f"[INIT] TEMP_DIR set to: {TEMP_DIR.resolve()}")



from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount TEMP_DIR/*/images as static so HTML <img> links work without changing HTML
# For each lead folder, mount its images folder dynamically


@app.get("/preview/{lead_id}/images/{image_name:path}")
def serve_image(lead_id: int, image_name: str):
    image_path = TEMP_DIR / str(lead_id) / "images" / image_name
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image_path.resolve())


# ------------------------
# Models
# ------------------------

class ReviewRequest(BaseModel):
    approved: bool


# ------------------------
# Routes
# ------------------------

@app.get("/preview/{lead_id}", response_class=HTMLResponse)
def preview_website(lead_id: int):
    index_path = TEMP_DIR / str(lead_id) / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Website not found")

    html_content = index_path.read_text(encoding="utf-8")
    # Inject <base> right after <head>
    html_content = html_content.replace("<head>", f"<head><base href='/preview/{lead_id}/'>")
    return HTMLResponse(html_content)



@app.post("/review/{lead_id}")
def review_website(lead_id: int, review: ReviewRequest):
    """
    Accept or reject a website.
    """
    log(f"[REVIEW] Review received for lead_id={lead_id} | approved={review.approved}")

    lead_path = TEMP_DIR / str(lead_id)

    if not lead_path.exists():
        log(f"[REVIEW][ERROR] Lead directory not found: {lead_path}")
        raise HTTPException(status_code=404, detail="Lead not found")
    lead_id = int(lead_id)

    if review.approved:
        log(f"[REVIEW] Lead {lead_id} approved")
        database.update_lead_status(lead_id, 5)  # approved

        approved(database.get_leads(lead_id=lead_id)[0])
        return {"status": "approved"}

    else:
        log(f"[REVIEW] Lead {lead_id} rejected")
        database.update_lead_status(lead_id, -1)  # rejected
        shutil.rmtree(TEMP_DIR / str(lead_id), ignore_errors=True)
        return {"status": "rejected"}


def approved(lead: Lead) -> None:
    """Gets called each time a lead was human-approved in the /review route.

    Args:
        lead (Lead): Lead that was approved
    """
    link = ftp_manager.ftps_upload_lead_from_server(lead)
    # lead.record_preview()

    path: str = TEMP_PATH+"/"+str(lead.id)+"/index.html"
    video_paths=[]
    video_paths.append(
        screenshot_website.html_file_to_scrolling_video(
            html_path=path,
            output_dir=f"./{TEMP_PATH}/{lead.id}/videos/",
            width=390,
            height=844,
            scroll_step=20,
            scroll_delay=0.03
            )
        )
    video_paths.append(
        screenshot_website.html_file_to_scrolling_video(
            html_path=path,
            output_dir=f"./{TEMP_PATH}/{lead.id}/videos/",
            width=1440,
            height=900,
            scroll_step=20,
            scroll_delay=0.03
            )
        )

    bot = InstagramManager()
    uname=str(lead.instagram)

    # ? double checking instagram username.
    if lead.instagram:
        bot.send_proposal_to_user_by_username(lead.instagram, video_paths, link)
    else:
        if lead.fetch_instagram() is not None:
            bot.send_proposal_to_user_by_username(uname, video_paths, link)
        else:
            log("Lead initialized and approved but couldnt find the instagram. Double check function in lead_pipeline_manager to check for instagram before initializing ")

    log(f"DONE APPLYING APPROVE PIPELINE FOR LEAD: {str(lead)}")
    delete_preview(lead.id)






@app.delete("/preview/{lead_id}")
def delete_preview(lead_id: int):
    """
    Manual delete (optional).
    """
    log(f"[DELETE] Manual delete requested for lead_id={lead_id}")

    lead_path = TEMP_DIR / str(lead_id)

    if not lead_path.exists():
        log(f"[DELETE][ERROR] Lead directory not found: {lead_path}")
        raise HTTPException(status_code=404, detail="Lead not found")

    shutil.rmtree(lead_path)
    log(f"[DELETE] Successfully deleted {lead_path}")
    return {"status": "deleted"}


@app.get("/api/leads")
def list_leads():
    log("[API] Listing pending leads")

    leads = []
    try:
        for lead_dir in TEMP_DIR.iterdir():
            index_file = lead_dir / "index.html"
            if index_file.exists():
                leads.append({
                    "id": lead_dir.name,
                    "preview_url": f"/preview/{lead_dir.name}"
                })

        log(f"[API] Found {len(leads)} pending lead(s)")
        return JSONResponse(leads)

    except Exception as e:
        log(f"[API][ERROR] Failed to list leads: {e}")
        raise


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    log("[DASHBOARD] Dashboard loaded")
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request}
    )


# ------------------------
# Server startup
# ------------------------

def run_server():
    global srv

    config = uvicorn.Config(
        "server_human_approval:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )

    srv = uvicorn.Server(config)
    srv.run()

def run_server_in_different_thread():
    server_thread = threading.Thread(
        target=run_server,
        daemon=True
    )
    server_thread.start()


def stop_server():
    global srv
    if srv:
        srv.should_exit = True
    srv=None
    log("Succesfully killed web server interface thread (probably @onexit -> server_human_approval.stop_server())")


if __name__ == "__main__":
    log("[SERVER] Launched via __main__")
    run_server()
