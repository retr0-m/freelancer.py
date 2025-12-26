"""
Docstring for server
this file manages to fully run the whole program multiple times to find unlimited leads and wait every 10/20 leads for human approval to generate other ones
This acts as a main.py that will:
    send Instagram DMS messages to acquire leads customers.
    And in future take customers requests and apply them.

Pipline:
    Find lead
    Download images
    Describe images
    Generate website
    -> set on db as "Waiting for human approval" (status: 5)
    Then user goes to a webpage on the server running this script and approves/edits the website.


Lead status index for server version:
    0 = lead found
    1 = images Scraped
    2 = images described
    3 = website Done
    4 = waiting for human approval on web server
        -> -1 = not approved (delete it)
        -> 5 = approved
    6 = Documentation Done
    7 = uploaded to ftps
    8 = proposal sent. (instagram)
    9 = customer acquired
    10 = online with customer preferences

The server creates website until config.MAX_WEBSITES_UNTIL_APPROVAL
"""



from sys import argv
import sys
from subprocess import run
import lead_pipeline_manager
import server_human_approval

# caution: path[0] is reserved for script path (or '' in REPL)


sys.path.insert(1, '../')
import database
from log import log, log_empty_row, logo
import temp_leads
from config import CUSTOMERS_TYPE, CUSTOMERS_CITY


def print_help():
    log(
        "Usage:\n"
        "  python server.py <use_graphical_editor> [customers_type] [customers_city] [leads_to_generate]\n\n"
        "Arguments:\n"
        "  customers_type       : e.g. Barber, Restaurant, Dentist\n"
        "  customers_city       : e.g. Zurich, Berlin, Paris\n"
        "  leads_to_generate    : integer\n\n"
        "Example:\n"
        "  python script.py false Barber Zurich 10"
    )


def get_argv():
    global CUSTOMERS_TYPE, CUSTOMERS_CITY, LEADS_TO_GENERATE

    args = argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print_help()
        return


    # CUSTOMERS_TYPE
    if len(args) >= 1:
        CUSTOMERS_TYPE = args[0]
        log(f"Using '{CUSTOMERS_TYPE}' as CUSTOMERS_TYPE (from argv)")
    else:
        log(f"No argv for CUSTOMERS_TYPE found, using default '{CUSTOMERS_TYPE}'")

    # CUSTOMERS_CITY
    if len(args) >= 2:
        CUSTOMERS_CITY = args[1]
        log(f"Using '{CUSTOMERS_CITY}' as CUSTOMERS_CITY (from argv)")
    else:
        log(f"No argv for CUSTOMERS_CITY found, using default '{CUSTOMERS_CITY}'")

    # LEADS_TO_GENERATE
    if len(args) >= 3:
        try:
            LEADS_TO_GENERATE = int(args[3])
            log(f"Using {LEADS_TO_GENERATE} as LEADS_TO_GENERATE (from argv)")
        except ValueError:
            log(
                f"Invalid argv for LEADS_TO_GENERATE ('{args[3]}'), "
                f"using default {LEADS_TO_GENERATE}"
            )
    else:
        log("No argv for LEADS_TO_GENERATE found, using default.")


# ! KILLING server_human_approval.srv when program exites
from server_human_approval import stop_server
import atexit

@atexit.register
def shutdown():
    stop_server()



def main():
    print("Running scripts... (See log.txt for details)")
    log_empty_row()
    logo()
    get_argv()
    #init db
    database.initialize_database()

    log("Running human approval server...")
    server_human_approval.run_server_in_different_thread()

    lead_pipeline_manager.mainloop()

    #TODO: SEND PROPOSAL

    # wipe_sandbox_data() only for devs purposes, this will wipe all the data you collected about the leads...


    log("Done! ran all the scripts with no fatal errors.")


def test_1():
    from lead_pipeline_manager import how_many_leads_in_temp
    print(how_many_leads_in_temp())



def wipe_sandbox_data():
    # ! Used for developing purposes, REMOVE IN CASE OF RUNNING IN A REAL ENVIRONMENT.
    def reset_db():
        run("rm ./leads.db",shell=True)
        run("touch ./leads.db",shell=True)
    temp_leads.wipe_all()
    reset_db()



if __name__ == "__main__":
    main()

