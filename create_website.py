from google import genai
import os 
from log import log

GEMINI_MODEL="gemini-3-flash"


def generate_prompt(customer_details: list[str]):
    p=""
    p+="\n".join(customer_details)
    return p

def generate_website(client, prompt):
    log("prompting model for website")
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL, contents=prompt
        )
    except Exception as e:
        log("could not generate website for the following reason:\n"+e)


def init_client():
    log("initializing client")
    API_KEY = os.getenv("GEMINI_API_KEY") 
    client = genai.Client(api_key=API_KEY)
    return client



