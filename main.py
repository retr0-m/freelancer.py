import find_customers
import database
import scrape_images
import create_website
import create_documentation
import qr_generator
import os
from log import log, log_empty_row
import ftp_manager

CUSTOMERS_TYPE="Ristorante"
CUSTOMERS_CITY="Lugano"


def main():
    log_empty_row()
    log("="*17+" FREELANCER.PY "+"="*18)
    log("="*50)
    
    #init db
    database.initialize_database()
    
    lead_list=find_customers.find_and_initialize_leads(CUSTOMERS_TYPE, CUSTOMERS_CITY, max_leads=2)
    if lead_list:
        find_customers.save_leads_to_csv(lead_list)
    else:
        log("Aborting because no lead was found.")
        exit()
        
    for lead in lead_list:
        
        files=scrape_images.search_lead_images(lead)
        
        if files:
            lead.add_images(files)
            lead.change_status(1) # Status 1 = images scraped
        
        create_website.generate_and_save_website(lead)
        lead.change_status(2) # Status 2 = website done
        
        # create documentation in ./leads/id/documents/* - qr_generator creates the documents dir if it doesnt finds it
        qr_generator.generate_qr(lead)
        create_documentation.create_preview_document(lead)
        
        database.insert_lead(lead)
        database.display_leads_table(limit=20, min_status=0)

        #last step: uploading to ftp matteocola.com/preview/lead.id/index.html
    
    ftp_manager.upload_to_ftp(lead_list)
    
    log("Done! ran all the scripts with no fatal errors. exiting...")
    exit(0)
    
    

if __name__ == "__main__":
    main()