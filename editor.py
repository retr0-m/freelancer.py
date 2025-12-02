from log import log
from lead import Lead
from google import genai
import os 
from dotenv import load_dotenv
from create_website import is_html, init_client, format_html


load_dotenv()

GEMINI_MODEL = "gemini-2.5-flash"
PROMPT_BASE = "You're a web designer and developer\napply the following edits:"
try:
    API_KEY = os.getenv("GEMINI_API_KEY")   
except Exception as e:
    log("Could'nt load API_KEY for gemini: "+str(e))
    


class Edit:
    def __init__(self, string: str, lead: Lead):
        self.string=string
        self.lead=lead
        self.prompt=""
    def __str__(self):
        return f"{self.string}"

    def add_prompt(self, p:str):
        self.prompt = p
    

def yes_or_no_input(text: str): #deprecated
    while True:
        s=input(text+"  [Y/n]")
        if "y" in s.lower():
            return True
        elif "n" in s.lower():
            return False
        else:
            "Answer with y or n"
        

def prompt_user_edits(lead_list: list[Lead]) -> list[Edit]:
    # will be { lead.id : "Make the title bolder..."}
    log("Waiting for user to type edits for the websites.")
    edits=[]
    for lead in lead_list:
        s=input(f"Anything wrong with website with id {lead.id} - {lead.name}?     (ENTER to skip)\n\t-> ")
        if(s.strip()!=""):
            edits.append(Edit(s, lead))
            log("User entered the following edit: "+s)
    return edits

def generate_prompt(edit: Edit):
    log("Generating prompt...")
    p=PROMPT_BASE
    p+=str(edit)
    p+="\nto the following HTML:\n\n"
    with open(f"./leads/{edit.lead.id}/index.html", "r", encoding="utf-8") as f:
        html=f.read()
    for line in html:
        p+=line
    p+="\n\n"
    p+="\nGive just the code, no words, no '''. single file that will be named index.html, and dont use placeholders for images, just use the images provided."
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

def replace_website_content(lead: Lead,website_content):
    log(f"Replacing website content on ./leads/{lead.id}/index.html")
    website_content=format_html(website_content)
    with open(f"./leads/{lead.id}/index.html", "w", encoding="utf-8") as f:
        chars = f.write(str(website_content))
    log(f"Done writing {chars} characters into the index file")
    

def apply_user_edits(edits_list: list[Edit]):
    # prompt_gemini...
    for e in edits_list:
        e.add_prompt(
            generate_prompt(e)
        )
    client=init_client()
    for e in edits_list:
        content=run_prompt(client, e.prompt)
        replace_website_content(e.lead, content)



if __name__ == "__main__":
    log("="*50)
    log("TESTING SCRIPT")
    lead_list=[
        Lead(1,"Al-74", "0797556550", "Via caccolemontate 15", "Lugano", [], 4),
        Lead(2,"Al-74", "0797556550", "Via caccolemontate 15", "Lugano", [], 4),
    ]
    edits=prompt_user_edits(lead_list)
    for e in edits:
        e.add_prompt(
            generate_prompt(e)
        )
    client=init_client()
    for e in edits:
        content=run_prompt(client, e.prompt)
        replace_website_content(e.lead, content)
    
    
