import find_customers
import database
import scrape_images
from log import log

CUSTOMERS_TYPE="Ristorante"
CUSTOMERS_CITY="Lugano"


def main():
    log("="*50)
    log("="*20+" FREELANCER.PY "+"="*20)
    #init db
    lead_list=find_customers.find_and_initialize_leads(CUSTOMERS_TYPE, CUSTOMERS_CITY)
    if lead_list:
        find_customers.save_leads_to_csv(lead_list)
        
    for lead in lead_list:
        files=scrape_images.search_lead_images(lead)
        lead.add_images(files)
        database.insert_lead(lead)
    print(repr(lead))
    
    
    
    database.display_leads_table(limit=10, min_status=0)
    

if __name__ == "__main__":
    main()