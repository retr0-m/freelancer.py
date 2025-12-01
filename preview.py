from lead import Lead
from log import log
import webbrowser
import os

def open_website_preview(lead:Lead):
    
    local_html = f"./leads/{lead.id}/index.html"
    full_path = os.path.abspath(local_html)
    webbrowser.open(f"file://{full_path}")