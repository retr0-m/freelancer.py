"""
Docstring for find_lead_instagram
This script is responsable of finding the right instagram account for a certain lead.
"""

from typing import Optional, Dict
import re

import os
import requests

from log import log
from dotenv import load_dotenv



load_dotenv()

API_KEY = os.getenv("GOOGLE_INSTAGRAM_SEARCH_API_KEY")
CSE_ID = os.getenv("GOOGLE_INSTAGRAM_SEARCH_CX")

GOOGLE_CSE_URL = "https://www.googleapis.com/customsearch/v1"


def search_instagram_via_google_cse(query: str):
    log(f"[INSTAGRAM SEARCH] Google CSE query: {query}")
    if not API_KEY or not CSE_ID:
        raise RuntimeError("Google CSE API key or CX missing")

    params = {
        "key": API_KEY,
        "cx": CSE_ID,
        "q": query,
        "num": 5,
    }

    resp = requests.get(GOOGLE_CSE_URL, params=params, timeout=10)
    log(f"[INSTAGRAM SEARCH] Google CSE HTTP {resp.status_code}")
    resp.raise_for_status()
    data = resp.json()

    for item in data.get("items", []):
        log(f"[INSTAGRAM SEARCH] Inspecting result item: {item.get('title', 'no-title')}")
        link = item.get("link", "")
        match = re.search(r"instagram\.com/([^/?#]+)", link)
        if match:
            handle = match.group(1)
            log(f"[INSTAGRAM SEARCH] Found Instagram handle: {handle}")
            return {
                "handle": handle,
                "url": f"https://instagram.com/{handle}",
                "confidence": 0.85,
                "source": "google_cse"
            }

    return None

def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def from_lead(lead) -> Optional[Dict]:
    """
    Try to infer the Instagram account for a lead.
    Returns structured result or None.

    Args:
        lead (Lead): the lead in need of the instagram

    Returns:
        Dict:
            {
                "handle": "businessname",
                "url": "https://instagram.com/businessname",
                "confidence": 0.82,
                "method": "name+city"
            }
    """
    log(f"[FROM_LEAD] Starting Instagram search for lead ID={lead.id}, name='{lead.name}'")

    queries = []

    # Strategy 1: business name + city
    if lead.name and lead.city:
        queries.append(f"{lead.name} {lead.city} instagram")

    # Strategy 2: business name only
    if lead.name:
        queries.append(f"{lead.name} instagram")

    # Strategy 3: phone number (rare but powerful)
    if lead.phone and lead.phone != "N/A":
        queries.append(f"{lead.phone} instagram")

    # Strategy 4: website/email domain (if available)
    if lead.email:
        domain = lead.email.split("@")[-1]
        queries.append(f"{domain} instagram")

    log(f"[FROM_LEAD] Generated search queries: {queries}")

    # ---- placeholder search logic ----
    # You plug Google, SerpAPI, Bing, DuckDuckGo, etc. here
    for q in queries:
        log(f"[FROM_LEAD] Trying query: {q}")
        try:
            result = search_instagram_via_google_cse(q)
        except Exception as e:
            log(f"[FROM_LEAD][ERROR] Google CSE failed for query '{q}': {e}")
            result = None

        if result:
            log(f"[FROM_LEAD] Instagram match found for lead ID={lead.id} using query '{q}'")
            return {
                "handle": result["handle"],
                "url": f"https://instagram.com/{result['handle']}",
                "confidence": result["confidence"],
                "method": q
            }

    log(f"[FROM_LEAD] No Instagram account found for lead ID={lead.id}")
    return None

# ! JUST A TEST FUNCTION, DO NOT USE THIS IN REAL DEPLOYMENT
def fake_search_instagram(query: str) -> Optional[dict]:
    """
    Mock search function.
    Replace with real search later.
    """
    if "instagram" in query.lower():
        return {
            "handle": "example_business",
            "confidence": 0.75
        }
    return None
