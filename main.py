from time import sleep
from sys import argv
import database
import scrape_images
import create_website
import create_documentation
import find_customers
import qr_generator
from log import log, log_empty_row, logo
import ftp_manager
import preview
import graphical_editor
import proposal_sender

CUSTOMERS_TYPE = "Barber"
CUSTOMERS_CITY = "Zurich"
LEADS_TO_GENERATE = 1

def get_argv():
    global CUSTOMERS_TYPE, CUSTOMERS_CITY, LEADS_TO_GENERATE

    # argv[0] is the script name
    args = argv[1:]

    if len(args) >= 1:
        CUSTOMERS_TYPE = args[0]
        log(f"Using '{CUSTOMERS_TYPE}' as CUSTOMERS_TYPE (from argv)")
    else:
        log(f"No argv for CUSTOMERS_TYPE found, using default '{CUSTOMERS_TYPE}'")

    if len(args) >= 2:
        CUSTOMERS_CITY = args[1]
        log(f"Using '{CUSTOMERS_CITY}' as CUSTOMERS_CITY (from argv)")
    else:
        log(f"No argv for CUSTOMERS_CITY found, using default '{CUSTOMERS_CITY}'")

    if len(args) >= 3:
        try:
            LEADS_TO_GENERATE = int(args[2])
            log(f"Using {LEADS_TO_GENERATE} as LEADS_TO_GENERATE (from argv)")
        except ValueError:
            log(
                f"Invalid argv for LEADS_TO_GENERATE ('{args[2]}'), "
                f"using default {LEADS_TO_GENERATE}"
            )
    else:
        log(f"No argv for LEADS_TO_GENERATE found, using default {LEADS_TO_GENERATE}")

def main():
    log_empty_row()
    logo()


    get_argv()

    #init db
    database.initialize_database()

    lead_list=find_customers.find_and_initialize_leads(CUSTOMERS_TYPE, CUSTOMERS_CITY, max_leads=LEADS_TO_GENERATE)
    if lead_list:
        find_customers.save_leads_to_csv(lead_list)
    else:
        log("Aborting because no lead was found.")
        exit()
    for lead in lead_list:
        uploaded_ftp=False

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
            graphical_editor.stop_server(save=True)
            # uploading to FTPS
            ftp_manager.ftps_upload_lead(lead)
            uploaded_ftp=True
        except KeyboardInterrupt:
            graphical_editor.stop_server(save=False)


        if uploaded_ftp:
            try:
                sleep(2)
                input("\nPress ENTER to send e-mail proposal\nCTRL+C to cancel.\n")

                if not lead.email:
                    log("Could not find lead email")
                else:
                    proposal_sender.send_proposal(lead)

                    lead.change_status(3)
            except KeyboardInterrupt:
                exit()

            database.update_lead_status(lead.id, 3)

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