from lead import Lead
from log import log
import webbrowser
import os
import shutil
import subprocess

def open_website_preview(lead:Lead):

    local_html = f"./leads/{lead.id}/index.html"
    full_path = os.path.abspath(local_html)
    webbrowser.open(f"file://{full_path}")

def open_website_on_vscode(lead: Lead):
    subprocess.run(("code ./graphical_editor/temp/{lead.id}/"), shell=True)


def open_graphical_editor(lead: Lead):
    log("opening editor")
    open_website_on_vscode(lead)
    # Paths
    original_html = f"./leads/{lead.id}/index.html"
    original_images_dir = f"./leads/{lead.id}/images"

    temp_dir = f"./graphical_editor/temp/{lead.id}"
    temp_images_dir = os.path.join(temp_dir, "images")

    # Create temp dirs
    os.makedirs(temp_dir, exist_ok=True)

    # Copy images if they exist
    if os.path.exists(original_images_dir):
        if os.path.exists(temp_images_dir):
            shutil.rmtree(temp_images_dir)
        shutil.copytree(original_images_dir, temp_images_dir)
        log(f"Copied images to {temp_images_dir}")
    else:
        log(f"No images found in {original_images_dir}")

    log(f"Made temp file in: {temp_dir}/index.html")
    temp_file = os.path.join(temp_dir, "index.html")

    # Read original HTML
    with open(original_html, "r", encoding="utf-8") as f:
        html = f.read()

    # Inject script at the bottom of <body>
    script_tag = '<script src="../../editor.js"></script>'
    if "</body>" in html:
        html = html.replace("</body>", f"{script_tag}</body>")
    else:
        html += script_tag

    # Write temporary file
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(html)

    # Open in browser
    full_path = os.path.abspath(temp_file)
    webbrowser.open(f"file://{full_path}")

if __name__ == "__main__":
    log("="*50)
    log("TESTING SCRIPT")

    #TEST 1
    log('TEST-1 with following sandbox data:      Lead(150, "Al-74", "21312432", "Via Trevano 74, 6900 Lugano, Switzerland", "Lugano", [], 0)')
    l=Lead(1, "Al-74", "21312432", "Via Trevano 74, 6900 Lugano, Switzerland", "Lugano", ["./leads/150/images/1.jpg","./leads/150/images/2.png"], 0)
    open_graphical_editor(l)

