from google import genai
import os
from log import log
from lead import Lead
from dotenv import load_dotenv
import json
import re

load_dotenv()

GEMINI_MODEL = "gemini-2.5-flash"
PROMPT_FILE = "./generate_website_prompt.json"

try:
    API_KEY = os.getenv("GEMINI_API_KEY")
except Exception as e:
    log("Couldn't load API_KEY for gemini: " + str(e))


def generate_prompt(lead: Lead) -> str:
    log("Generating JSON prompt...")

    # Load base prompt
    try:
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            prompt_base = json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load prompt base: {e}")

    # Build final prompt payload
    prompt = {
        "system": prompt_base,
        "business": {
            "name": lead.name,
            "phone_number": lead.phone,
            "address": lead.address
        },
        "images": {
            strip_leads_folder(img): lead.images_description[img] for img in lead.images_description
        }
    }

    log("Done!")

    # Return as JSON string for the model
    return json.dumps(prompt, ensure_ascii=False, indent=2)


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


def format_html(content):
    c=str(content).replace("```html", "")
    return c.replace("```", "")

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
    website_content=format_html(website_content)
    with open(f"./leads/{lead.id}/index.html", "a") as f:
        chars=f.write(str(website_content))
    log(f"Done writing {chars} characters into the index file")


def generate_and_save_website(lead: Lead): #main function
    """
    Main function that should be called when using this file as a imported library
    """
    client = init_client()
    prompt = generate_prompt(lead)
    log(f"Running prompt with following data: \n{prompt}")
    website_content=run_prompt(client, prompt)
    save_website_to_file(lead, website_content)



if __name__ == "__main__":
    log("="*50)
    log("TESTING SCRIPT")
    log("="*50)

    #TEST 1
    log('TEST-1 with following sandbox data:      Lead(150, "Al-74", "21312432", "Via Trevano 74, 6900 Lugano, Switzerland", "Lugano", [], 0)')
    l=Lead(150, "Al-74", "21312432", "Via Trevano 74, 6900 Lugano, Switzerland", "Lugano", "aaa@aaaa.aa", ["./leads/150/images/1.jpg","./leads/150/images/2.png"], 0)
    images_descriptions={'./leads/1/images/1.jpg': ' The image shows an urban scene with historical architecture. There is a large church prominently featured in the center with a tall clock tower and a statue at its peak. The church has a distinctive facade, possibly made of stone or concrete, with a classical design. A bell tower with clocks on each side adds to the grandeur of the structure. In front of the church, there is a town square with a few people visible and benches placed for public use. Surrounding buildings have balconies and windows that suggest they might be residential or commercial in nature. The sky is overcast, indicating it could be a cool day or the photo may have been taken during a time of year when the weather is not ideal. The road is relatively clear with no significant traffic, except for one motorcycle visible on the right side of the frame. There are trees and plants around the area, adding to the aesthetic appeal of the location. ', './leads/1/images/2.jpg': ' The image depicts an elegant indoor dining area with modern decor, featuring a wall of plants and stylish lighting. It has a sophisticated ambiance, with a large table set for dinner surrounded by chairs, and a view through the window to another room. '}
    l.add_images_description(images_descriptions)
    prompt=generate_prompt(l)
    print(prompt)

    log("="*50)


    # #TEST 1
    # log('TEST-2 with following sandbox data:      Lead(150, "Al-74", "21312432", "Via Trevano 74, 6900 Lugano, Switzerland", "Lugano", [], 0)')
    # l=Lead(150, "Al-74", "21312432", "Via Trevano 74, 6900 Lugano, Switzerland", "Lugano", "aaa@aaa.aaa", ["./leads/150/images/1.jpg","./leads/150/images/2.png"], 0)
    # generate_and_save_website(l)

