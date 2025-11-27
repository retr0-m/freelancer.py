import os
import requests
from dotenv import load_dotenv
from lead import Lead
from log import log
# Load environment variables from .env
load_dotenv()

API_KEY = os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY")
CSE_ID = os.getenv("GOOGLE_CUSTOM_SEARCH_CX")

if not API_KEY or not CSE_ID:
    raise ValueError("Missing API key or Search Engine ID in .env file")

def google_image_search(query, num_images=10, output_dir="images"):
    os.makedirs(output_dir, exist_ok=True)

    downloaded = 0
    start = 1

    log(f"Searching images for: {query}")

    while downloaded < num_images:
        # Google API returns max 10 images per request
        n = min(10, num_images - downloaded)

        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": API_KEY,
            "cx": CSE_ID,
            "q": query,
            "searchType": "image",
            "num": n,
            "start": start,
            "imgSize": "xlarge",
        }

        response = requests.get(url, params=params).json()
    
        items = response.get("items", [])

        if not items:
            log("No more images found.")
            break
        img_index=0
        for item in items:
            img_index+=1
            img_url = item.get("link")
            if not img_url:
                continue

            try:
                img_data = requests.get(img_url, timeout=10).content
                if len(img_data) < 10_000:  # 10 KB threshold
                    print(f"Skipped small image ({len(img_data)} bytes): {img_url}")
                    continue
                ext = img_url.split(".")[-1].split("?")[0]
                if len(ext) > 4:
                    ext = "jpg"  # fallback if weird extension

                filename = f"{img_index}.{ext}"
                filepath = os.path.join(output_dir, filename)

                with open(filepath, "wb") as f:
                    f.write(img_data)

                log(f"Downloaded: {filepath}")
                downloaded += 1

                if downloaded >= num_images:
                    break

            except Exception as e:
                log(f"Failed to download {img_url}: {e}")

        start += n

    log("images scraping done")

def search_lead_images(lead:Lead):
    query=f"*{lead.name} {lead.city}*"
    
    img_path=f"./leads/{lead.id}/images"
    google_image_search(query, num_images=5, output_dir=img_path)



if __name__ == "__main__":
    l=Lead(1, "", "21312432", "Via pizzaculo2", "Lugano", [], 0)
    search_lead_images(l)