from multiprocessing import Process, Queue
from log import log
from editor import Edit, is_html
from create_website import format_html
from lead import Lead
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import os
from google import genai
import threading
import asyncio
from time import sleep
import subprocess
import shutil
from glob import glob


load_dotenv()

GEMINI_MODEL = "gemini-2.5-flash"
PROMPT_BASE = "You're a web designer and developer\napply the following edits:\n"
try:
    API_KEY = os.getenv("GEMINI_API_KEY")   
except Exception as e:
    log("Could'nt load API_KEY for gemini: "+str(e))


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

current_lead = None
last_website_content = "" # for saving


server_thread = None
server_instance = None

def start_server():
    global server_thread, server_instance

    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server_instance = uvicorn.Server(config)

    def run():
        asyncio.run(server_instance.serve())

    server_thread = threading.Thread(target=run, daemon=True)
    server_thread.start()

def stop_server(save:bool = False):
    if save: replace_website_content(current_lead, last_website_content)
    global server_instance, server_thread
    if server_instance is not None:
        # Ask the server to exit
        server_instance.should_exit = True
    if server_thread is not None:
        server_thread.join()



@app.post("/receive")
async def receive(request: Request):
    if current_lead is None:
        return JSONResponse({"status": "error", "message": "Lead not set"}, status_code=400)

    data = await request.json()

    # Separate generic and specific
    generic = data.get("generic", "")
    specific = {k: v for k, v in data.items() if k != "generic"}

    # Create Edit object with the external Lead
    edit = Edit(generic, current_lead, specific)

    # Example: print to check
    log("Initialized Edit class based on data received: "+str(edit))
    
    apply_user_edit(edit)

    return JSONResponse({"status": "ok"})

def init_client():
    log("Initializing client")
    try:
        client = genai.Client(api_key=API_KEY)
        log("CLient initialized")
        return client
    except Exception as e:
        log("Failed client initialization: "+str(e))

def generate_prompt(edit: Edit):
    log("Generating prompt...")
    p=PROMPT_BASE
    if edit.generic:  
        p+=str(edit.generic)
    if edit.generic and edit.specific:
        p+="\nAnd the following edits to specific elements:"
    if edit.specific:
        p+="\nSpecific selector to element to edit    :    Edits to apply"
        for k in edit.specific:
            p += "\n" + k + " : " + edit.specific[k]
        
    
    p+="\nto the following HTML:\n\n"
    with open(f"./graphical_editor/temp/{edit.lead.id}/index.html", "r", encoding="utf-8") as f:
        html=f.read()
    for line in html:
        p+=line
    p+="\n\n"
    p+="\nGive just the code, no words, no '''html. single file that will be named index.html, and dont use placeholders for images, just use the images provided except for menu items, for that use placeholders."
    edit.add_prompt(p)
    log("Done!")
    return p


def run_prompt(client, prompt):
    log("prompting model to apply edits...")
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL, contents=prompt
        )
        
        if is_html(response.text):
            log("Succesfully received a response with HTML code.")
        else:
            log("Gemini gave an output that wasnt recognized as a website: "+response.text)
            exit()
        return response.text
    except Exception as e:
        log("Couldn't apply edits to specified website for the following reason: "+str(e))



def replace_temp_website_content(lead: Lead, website_content: str):
    log(f"Replacing website content on ./graphical_editor/temp/{lead.id}/index.html")

    website_content = format_html(website_content)
    temp_folder = f"./graphical_editor/temp/{lead.id}"
    temp_index = os.path.join(temp_folder, "index.html")

    with open(temp_index, "w", encoding="utf-8") as f:
        chars = f.write(str(website_content))

    log(f"Done writing {chars} characters into the index file")

    # Copy images into the leads folder
    src_images = os.path.join(temp_folder, "images")
    dest_images = f"./leads/{lead.id}/images"

    log(f"Putting images from path {src_images}/* to {dest_images}/*")

    # Create destination directory if needed
    os.makedirs(dest_images, exist_ok=True)

    copied = 0
    for file in glob(os.path.join(src_images, "*")):
        if os.path.isfile(file):
            try:
                shutil.copy(file, dest_images)
                copied += 1
            except Exception as e:
                log(f"⚠️ Failed to copy {file}: {e}")

    log(f"📸 {copied} image(s) successfully copied for Lead ID {lead.id}")
def replace_website_content(
    lead: Lead, 
    website_content: str
    ):
    log(f"Replacing website content on ./leads/{lead.id}/index.html")
    website_content=format_html(website_content)
    path=f"./graphical_editor/temp/{lead.id}/index.html"
    with open(path, "w", encoding="utf-8") as f:
        chars = f.write(str(website_content))
    log(f"Done writing {chars} characters into the index file")



def apply_user_edit(edit: Edit):
    global last_website_content
    generate_prompt(edit)
    client = init_client()
    content = format_html(
        run_prompt(client, edit.prompt)
    )
    last_website_content=content
    replace_temp_website_content(edit.lead, content)
    replace_website_content(edit.lead, content)


if __name__ == "__main__":
    log("="*50)
    log("TESTING SCRIPT")
    # Set a temporary lead for testing
    current_lead = Lead(6, "Al-74", "0797556550", "Via caccolemontate 15", "Lugano", [], 4)
    edit=Edit(
        generic="",
        lead=current_lead,
        specific={}
    )
    generate_prompt(edit)
    print(edit.prompt)
    # start_server()
    # sleep(300)
    # stop_server()
    
    
