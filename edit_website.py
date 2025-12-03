from google import genai
import os 
from log import log
from lead import Lead
from dotenv import load_dotenv
from create_website import run_prompt, init_client, is_html

load_dotenv()

GEMINI_MODEL = "gemini-2.5-flash"
PROMPT_BASE = "You're a web designer and developer\napply the following edits:"
try:
    API_KEY = os.getenv("GEMINI_API_KEY")   
except Exception as e:
    log("Could'nt load API_KEY for gemini: "+str(e))


def generate_prompt(lead: Lead):
    log("Generating prompt...")
    p=PROMPT_BASE
    p+="\n- Name: "+str(lead.name)
    p+="\n- Phone number: "+str(lead.phone)
    p+="\n- Address: "+str(lead.address)
    
    p+="\nAnd using the following images"
    
    for i in lead.images:
        p+="\n"+str(strip_leads_folder(i))
    p+="Give just the code, no words, no '''. single file that will be named index.html, and dont use placeholders for images, just use the images provided."
    log("Done!")
    return p


def apply_edits(edits: list[Edit]):
    pass