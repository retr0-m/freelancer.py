"""Script that gives images description for generating the website with more context

Returns:
    JSON list: List of images paths with description
"""

import base64
from pathlib import Path
import requests
from lead import Lead
from log import log, log_fatal_error

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llava:7b"
MAX_RETRIES = 5 # for connection error


def image_to_base64(image_path: str) -> str:
    image_bytes = Path(image_path).read_bytes()
    return base64.b64encode(image_bytes).decode("utf-8")

def ask_llava(prompt: str, image_path: str):
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }

    if image_path:
        payload["images"] = [image_to_base64(image_path)]

    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()

    return response.json()["response"]

def get_dict(lead: Lead) -> dict:

    images: list[str] = lead.images
    descriptions: dict = {}

    for image in images:
        log(f"Giving image description... ({image})")
        for try_number in range(MAX_RETRIES):
            try:
                answer = ask_llava(
                    prompt="you're a web developer, shortly describe the following image that may be used to build a website in 20 words ",
                    image_path=image
                )
                descriptions[image]=str(answer)
                log("Description successfully received!")
                break
            except requests.exceptions.HTTPError as e:
                if(try_number<=1) : log(f"CONNECTION ERROR WHILE PROMPTING LLAVA:7B MODEL, RETRYING WITH A MAX OF {MAX_RETRIES}, ERROR IS THE FOLLOWING: {e}")
                else: log(f"Retrying connection with llava:7b... (try number: {try_number})")
            except Exception as e:
                log_fatal_error(str(e))
    return descriptions



if __name__ == "__main__":
    log("="*50)
    log("\t\tTESTING SCRIPT")
    log("="*50)


    #TEST 1
    log('TEST-1 with following sandbox data:      Lead(150, "Al-74", "21312432", "Via Trevano 74, 6900 Lugano, Switzerland", "Lugano", [], 0)')
    l=Lead(150, "Al-74", "21312432", "Via Trevano 74, 6900 Lugano, Switzerland", "Lugano", "aaa@aaaa.aa", ["./leads/1/images/1.jpg","./leads/1/images/2.jpg"], 0)
    descr=get_dict(l)
    log(str(descr))

    log("="*50)


    # image = "./images/1.jpg"

    # answer = ask_llava(
    #     prompt="you're a web developer, shortly describe the following image that may be used to build a website in 20 words ",
    #     image_path=image
    # )

    # log("\nLLaVA response:\n")
    # log(answer)