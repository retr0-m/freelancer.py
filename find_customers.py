from lead import Lead
import googlemaps
from log import log
import pandas as pd
import time
from typing import List, Dict
import os
from dotenv import load_dotenv
import database



# Setup

load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=API_KEY)


def find_and_initialize_leads(keyword: str, location: str, radius: int = 5000, max_leads: int=0) -> List[Lead]: # if max == 0 searches all the leads it can, else it will stop at {max} leads
    """
    Finds leads via Google Maps API and initializes them as Lead objects.
    
    Returns: A list of Lead objects that pass the filtering criteria (no website).
    """
    leads_list: List[Lead] = []
    # 1. Geocoding della città
    try:
        geocode_result = gmaps.geocode(location)
    except googlemaps.exceptions.TransportError:
        log("FATAL ERROR: GoogleMaps Transport error, connect to the internet to run this script.")
        print("Aborting...")
        exit()
    if not geocode_result:
        log(f"Città non trovata: {location}")
        return []

    lat_lng = geocode_result[0]['geometry']['location']
    
    # 2. Ricerca luoghi (Places Nearby)
    places_result = gmaps.places_nearby(
        location=lat_lng,
        radius=radius,
        keyword=keyword
    )
    
    last_lead_id_in_db = database.get_last_lead_id()
    lead_id_counter = last_lead_id_in_db + 1
    while True:
        for place in places_result.get('results', []):
            if max_leads != 0:
                if lead_id_counter - last_lead_id_in_db > max_leads:
                    return leads_list
            try:
                place_details = gmaps.place(
                    place_id=place['place_id'], 
                    fields=['name', 'website', 'formatted_phone_number', 'formatted_address']
                )
            except Exception as e:
                log(f"Error while receiving Place Details for ID {place['place_id']}: {e}")
                continue
            result = place_details.get('result', {})
            website = result.get('website')
            name = result.get('name')

            is_social_site = website and ("facebook.com" in website or "instagram.com" in website)
            
            if not website or is_social_site:
                
                # Assign the current sequential ID
                current_id = lead_id_counter
                
                # Create the Lead object
                lead_obj = Lead.from_map_data(
                    lead_id=current_id,
                    result=result,
                    city=location,
                    website_status=website if website else "Nessun Sito"
                )
                
                exists=database.lead_exists(name=lead_obj.name)
                if not exists:
                    leads_list.append(lead_obj)
                    log(f"🎯 LEAD found and initialized: ID {current_id}, {lead_obj.name}")
                    lead_id_counter += 1
                else:
                    log(f"Lead ({lead_obj.name}) skipped because it was already existing in db")
        
        if 'next_page_token' in places_result:
            time.sleep(2) 
            log("Fetching next page of results...")
            places_result = gmaps.places_nearby(
                location=lat_lng,
                radius=radius,
                keyword=keyword,
                page_token=places_result['next_page_token']
            )
        else:
            break

    return leads_list


def save_leads_to_csv(leads_list: List[Lead]):
    """
    Accepts a list of Lead objects and saves their data to the index.csv file.
    """
    # 1. Convert list of Lead objects to a list of dictionaries
    # We use the to_dict() method (if implemented, or manually map fields)
    
    # Assuming the Lead class has a .to_dict() method:
    # data = [lead.to_dict() for lead in leads_list]
    
    # Manual mapping for safety here:
    data = [{
        'id': lead.id,
        'name': lead.name,
        'phone': lead.phone,
        'address': lead.address,
        'city': lead.city,
        'proposed': "Yes" if lead.status else "",
    } for lead in leads_list]
    
    # 2. Create DataFrame and save
    df = pd.DataFrame(data)
    df.to_csv("./leads/index.csv", index=False)
    log(f"Saved {len(leads_list)} leads to ./leads/index.csv")
    return df

# --- Execution Example ---

if __name__ == "__main__":
    
    log("="*50)
    log("TESTING SCRIPT")
    
    #TEST 1
    log('TEST-1 with following sandbox data:      "Ristorante", "Lugano"')
    database.initialize_database()
    found_leads = find_and_initialize_leads("Ristorante", "Lugano", max_leads=0)
    save_leads_to_csv(found_leads)
    
    
        