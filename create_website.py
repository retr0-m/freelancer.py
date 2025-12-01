from google import genai
import os 
from log import log
from lead import Lead
from dotenv import load_dotenv
import re

load_dotenv()

GEMINI_MODEL = "gemini-2.5-flash"
PROMPT_BASE = "You're a web designer and developer\ncreate an amazing, modern and professional themed website, make it responsive and use placeholders instead of images, so i can add them later, for the following restaurant with italian content:"
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


def is_html(content: str) -> bool:
    log("Checking if content is HTML")

    if not isinstance(content, str):
        return False

    # Trim leading whitespace
    text = content.strip().lower()

    # 1. Must contain at least one HTML tag pattern
    tag_pattern = re.compile(r"<([a-z]+)(\s+[^>]*)?>", re.IGNORECASE)
    if not tag_pattern.search(text):
        return False

    # 2. Check for forbidden patterns (like escaped HTML)
    # Example: "&lt;html&gt;" is not real HTML
    if "&lt;" in text and "&gt;" in text:
        return False

    # 3. Check for common structural tags
    structural_tags = ["<html", "<body", "<head", "<div", "<p", "<span"]
    if not any(tag in text for tag in structural_tags):
        return False

    # 4. Ensure there's at least one closing tag
    if "</" not in text:
        return False

    # 5. Basic check: tags must appear in pairs
    open_tags = re.findall(r"<([a-z0-9]+)[^>]*>", text)
    close_tags = re.findall(r"</([a-z0-9]+)>", text)

    # Normalize lists
    open_tags = [t for t in open_tags if t not in ("br", "img", "hr", "meta", "link", "input")]
    close_tags = close_tags

    if len(close_tags) == 0:
        return False

    # Not perfect, but helps prevent random noise from passing
    if len(close_tags) > len(open_tags):
        return True  # Closing more means it's definitely HTML

    # Matching tag names roughly
    if any(tag in close_tags for tag in open_tags):
        return True

    return False
        

def run_prompt(client, prompt):
    log("prompting model for website...")
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
        log("Could not generate website for the following reason: "+str(e))


def init_client():
    log("Initializing client")
    try:
        client = genai.Client(api_key=API_KEY)
        log("CLient initialized")
        return client
    except Exception as e:
        log("Failed client initialization: "+str(e))
        
        

def strip_leads_folder(path: str) -> str:
    """
    Convert './leads/150/images/1.jpg' → './images/1.jpg'
    by removing the first two path segments after '.'.
    """
    parts = path.split('/')
    
    # Example parts: ['.', 'leads', '150', 'images', '1.jpg']
    # We want: ['.', 'images', '1.jpg']
    if len(parts) >= 5 and parts[0] == '.' and parts[1] == 'leads':
        return './' + '/'.join(parts[3:])
    
    # fallback: return original
    return path 

def save_website_to_file(lead: Lead,website_content):
    log(f"Saving website content to ./leads/{lead.id}/index.html")
    with open(f"./leads/{lead.id}/index.html", "a") as f:
        chars=f.write(str(website_content))
    log(f"Done writing {chars} characters into the index file")


def generate_and_save_website(lead: Lead): #main function
    """
    Main function that should be called when using this file as a imported library
    """
    client = init_client()
    prompt = generate_prompt(lead)
    website_content=run_prompt(client, prompt)
    save_website_to_file(lead, website_content)
    


if __name__ == "__main__":
    log("="*50)
    log("TESTING SCRIPT")
    
    #TEST 1
    log('TEST-1 with following sandbox data:      Lead(150, "Al-74", "21312432", "Via Trevano 74, 6900 Lugano, Switzerland", "Lugano", [], 0)')
    l=Lead(150, "Al-74", "21312432", "Via Trevano 74, 6900 Lugano, Switzerland", "Lugano", ["./leads/150/images/1.jpg","./leads/150/images/2.png"], 0)
    generate_and_save_website(l)
    
    