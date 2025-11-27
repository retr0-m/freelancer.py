import find_customers
import database

CUSTOMERS_TYPE="Ristorante"
CUSTOMERS_CITY="Lugano"


def main():
    #init db
    lead_list=find_customers.find_and_initialize_leads(CUSTOMERS_TYPE, CUSTOMERS_CITY)
    if lead_list:
        find_customers.save_leads_to_csv(lead_list)
        
    for lead in lead_list:
        database.insert_lead(lead)
    
    
    
    database.display_leads_table(limit=10, min_status=0)
    

if __name__ == "__main__":
    main()