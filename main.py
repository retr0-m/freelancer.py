
import database
from time import sleep
import scrape_images
import create_website
import create_documentation
import find_customers
import qr_generator
from log import log, log_empty_row
import ftp_manager
import preview
import graphical_editor
CUSTOMERS_TYPE = "Barber"
CUSTOMERS_CITY = "Zurich"
LEADS_TO_GENERATE = 1

def main():
    log_empty_row()
    log("="*17+" FREELANCER.PY "+"="*18)
    log("="*50)

    #init db
    database.initialize_database()

    lead_list=find_customers.find_and_initialize_leads(CUSTOMERS_TYPE, CUSTOMERS_CITY, max_leads=LEADS_TO_GENERATE)
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
        preview.open_graphical_editor(lead) #one at a time

        graphical_editor.current_lead=lead
        graphical_editor.start_server()
        try:
            sleep(2)
            input("\nEdit website on browser\nPress ENTER to upload files to FTPS once you're done editing\nCTRL+C to cancel edits.\n")
        except KeyboardInterrupt:
            graphical_editor.stop_server(save=False)
            exit()

        graphical_editor.stop_server(save=True)


        # uploading to FTPS
        ftp_manager.ftps_upload_lead(lead)         ##TODO: save temp preview to actual ./leads/leadid


        # preview.open_website_preview(lead)

    #OLD METHOD TO APPLY EDITS BY TERMINAL (until commit "Graphical editor on browser - just demo, not implemented yet")
    ## TODO: add argv to set  editor graphical or by terminal.
    # while True:
    #     # human check
    #     edits=editor.prompt_user_edits(lead_list) ##TODO need to take back Edit() maybe user a super for praphical
    #     if len(edits) == 0:
    #         break
    #     editor.apply_user_edits(edits)



    log("Done! ran all the scripts with no fatal errors. exiting...")
    exit(0)



if __name__ == "__main__":
    main()