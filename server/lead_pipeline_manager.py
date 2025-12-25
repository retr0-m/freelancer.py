"""
    This script manages:
        when its appropriate to call the lead pipeline
        how should it be called (arg lead_number)
"""
import sys
sys.path.insert(1, '../')


from config import CUSTOMERS_TYPE, CUSTOMERS_CITY, MAX_LEADS_TO_DISPLAY, TEMP_PATH
from log import log, log_empty_row, logo


import find_customers
import temp_leads
import scrape_images
import create_website
import database
import imgs_descriptions
from pathlib import Path


def how_many_leads_in_temp() -> int:
    """
    Returns the number of lead folders in TEMP_PATH.
    """
    temp_dir = Path(TEMP_PATH)

    if not temp_dir.exists() or not temp_dir.is_dir():
        return 0

    return sum(
        1 for p in temp_dir.iterdir()
        if p.is_dir()
    )

current_type_number:int = 0
type_max_number:int = len(CUSTOMERS_TYPE) - 1
current_city_number:int = 0
city_max_number:int = len(CUSTOMERS_CITY) - 1

# ? This core function (lead pipeline) updates current_type number everytime it doesnt finds any leads, and then if it runs out of types it goes to the next customer city, resetting the types.
def lead_pipeline(lead_number: int):
    global current_city_number, current_type_number
    while True:
        lead_list=find_customers.find_and_initialize_leads(CUSTOMERS_TYPE[current_type_number], CUSTOMERS_CITY[current_city_number], max_leads=lead_number)
        if not lead_list:
            if current_type_number < type_max_number:
                current_type_number+=1
                log(f"Changing customer type because no lead was found:\n\tfrom: {CUSTOMERS_TYPE[current_type_number]} -> to: {CUSTOMERS_TYPE[current_type_number+1]}")

            elif current_type_number == type_max_number and current_city_number < city_max_number:
                current_type_number = 0
                current_type_number+=1
                log(f"Starting off from zero customers type because no lead was found:\n\tfrom: {CUSTOMERS_TYPE[current_type_number]} -> to: {CUSTOMERS_TYPE[current_type_number+1]}\nAnd changed the city\n\tfrom: {CUSTOMERS_CITY[current_city_number]} -> to: {CUSTOMERS_CITY[current_city_number+1]}")

            elif current_type_number == type_max_number and current_city_number == city_max_number:
                log("Could not change neither the city and neither the type of customers, ran out of types and cities.")

        else:
            break


    temp_leads.create(lead_list) # ? Creating the dirs tree for the incoming leads

    for lead in lead_list:

        files=scrape_images.search_lead_server_images(lead)
        if files:
            lead.add_server_images(files)
            lead.change_status(1) # * Status 1 = images scraped
            images_description=imgs_descriptions.get_dict(lead)
            lead.add_images_description(images_description)
            lead.change_status(2) # * Status 2 = images described



    for lead in lead_list:
        create_website.generate_and_save_temp_website(lead)
        lead.change_status(3) # * Status 3 = website done


        database.insert_lead(lead)
        database.display_leads_table(limit=20, min_status=0)


        lead.change_status(4) # * Status 4 = waiting for human approval


    # * FROM NOW ON IF A LEAD WEBSITE IS APPROVED THE CODE WILL FOLLOW IN ./server_human_approval.py -> approved()




def mainloop():
    log("[mainloop] \t STARTING...")
    n : int = 0
    while True:
        n+=1
        log(f"Recalled server.lead_pipeline_manager.mainloop().while-true (:81) -> ({n})")
        leads_waiting_for_approval: int = how_many_leads_in_temp()
        while leads_waiting_for_approval <= MAX_LEADS_TO_DISPLAY:
            lead_number: int = MAX_LEADS_TO_DISPLAY - leads_waiting_for_approval
            try:
                lead_pipeline(lead_number)
            except Exception as e:
                log(f"UNCATCHED EXEPTION DURING THE EXECUTION OF LEAD_PIPELINE, EXITING.... (server.lead_pipeline_manager.mainloop:last-line)\n\tThe exception was the following:\n{e}")
                exit()