import sqlite3
import json
from typing import List, Dict, Optional
from lead import Lead
from log import log 

# Define the path to your database file
DB_FILE = './leads.db' 

def create_connection():
    """Create and return a database connection object."""
    log(f"Attempting to connect to database file: {DB_FILE}")
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        log("Successfully established database connection.")
        return conn
    except sqlite3.Error as e:
        log(f"Error connecting to database: {e}")
        return None

def initialize_database():
    """
    Creates the 'leads' table if it doesn't already exist, 
    with a UNIQUE constraint on the 'name' column.
    """
    conn = create_connection()
    if conn is None:
        log("Initialization failed: Could not establish connection.")
        return

    try:
        cursor = conn.cursor()
        
        # SQL command to create the 'leads' table
        # 🎯 CHANGE 1: Added UNIQUE constraint to the 'name' column
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,  
            phone TEXT,
            address TEXT,
            city TEXT,
            images TEXT,         
            status INTEGER NOT NULL 
        );
        """
        cursor.execute(create_table_sql)
        conn.commit()
        log(f"Database initialized and 'leads' table ready in {DB_FILE}. (Name is UNIQUE)")
        
    except sqlite3.Error as e:
        log(f"Error creating table: {e}")
    finally:
        if conn:
            conn.close()
            log("Database connection closed after initialization.")


def lead_exists(lead_id: Optional[int] = None, name: Optional[str] = None) -> Optional[int]:
    """
    Checks if a lead already exists in the database.
    Returns the lead's status code if it exists.
    Returns None if no matching lead is found.
    """

    if lead_id is None and name is None:
        log("lead_exists called with no parameters. Returning None.")
        return None

    conn = create_connection()
    if conn is None:
        return None

    try:
        cursor = conn.cursor()

        sql = "SELECT status FROM leads WHERE 1=1"
        params = []

        if lead_id is not None:
            sql += " AND id = ?"
            params.append(lead_id)

        if name is not None:
            sql += " AND name = ?"
            params.append(name)

        log(f"Checking if lead exists: {sql} with params {params}")
        cursor.execute(sql, params)

        row = cursor.fetchone()

        if row is None:
            log("Lead not found.")
            return None

        status = row["status"]
        log(f"Lead exists. Status = {status}")
        return status

    except sqlite3.Error as e:
        log(f"❌ Error checking if lead exists: {e}")
        return None

    finally:
        conn.close()

def get_last_lead_id() -> int:
    """
    Returns the highest lead ID in the database.
    Returns 0 if no leads exist or in case of an error.
    """
    conn = create_connection()
    if conn is None:
        log("Could not connect to DB to get last lead ID.")
        return 0

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(id) AS last_id FROM leads")
        row = cursor.fetchone()
        last_id = row["last_id"] if row and row["last_id"] is not None else 0
        log(f"Last lead ID in database: {last_id}")
        return last_id
    except sqlite3.Error as e:
        log(f"❌ Error fetching last lead ID: {e}")
        return 0
    finally:
        conn.close()


def insert_lead(lead: Lead):
    """Inserts a single lead record into the database."""
    log(f"Attempting to insert new lead: ID {lead.id}, Name: {lead.name}")
    conn = create_connection()
    if conn is None: 
        log(f"Insertion failed for Lead ID {lead.id}: No connection.")
        return

    lead_data = lead.to_dict()
    images_json = json.dumps(lead_data.get('images', []))
    
    try:
        sql = """
        INSERT INTO leads (id, name, phone, address, city, images, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cursor = conn.cursor()
        
        cursor.execute(sql, (
            lead_data['id'],
            lead_data['name'],
            lead_data['phone'],
            lead_data['address'],
            lead_data['city'],
            images_json,
            lead_data.get('status', 0)
        ))
        
        conn.commit()
        inserted_id = cursor.lastrowid
        log(f"✅ Lead successfully inserted. New Row ID: {inserted_id} (Lead ID: {lead.id})")
        return inserted_id
    
    except sqlite3.IntegrityError as e:
        # 🎯 CHANGE 2: Gracefully handle the IntegrityError for duplicate names
        if 'UNIQUE constraint failed: leads.name' in str(e):
            log(f"🛑 Lead insertion skipped: Name '{lead.name}' already exists in the database.")
            return None # Return None to indicate no insertion happened
        else:
            log(f"❌ Error inserting lead ID {lead.id}: Integrity constraint violation. {e}")
    except sqlite3.Error as e:
        log(f"❌ General SQLite Error inserting lead ID {lead.id}: {e}")
    finally:
        if conn:
            conn.close()
            log("Database connection closed after insertion attempt.")


def get_status_label(status_code: int) -> str:
    """Converts the integer status code into a readable label."""
    labels = {
        0: "NEW",
        1: "SCRAPED (Images)",
        2: "WEBSITE DONE",
        3: "DOCS DONE",
        # Default for any unexpected status
        -1: "ERROR/UNKNOWN" 
    }
    return labels.get(status_code, labels[-1])


def display_leads_table(limit: int = 10, min_status: int = 0):
    """
    Queries the database and prints the content of the 'leads' table in a formatted way.
    
    :param limit: Maximum number of rows to display.
    :param min_status: Only display leads with this status code or higher.
    """
    log(f"Fetching up to {limit} leads with status >= {min_status} for display.")
    conn = create_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()
        
        # SQL to select key columns, filtering by status and limiting results
        sql = f"""
        SELECT id, name, city, images, status 
        FROM leads 
        WHERE status >= ?
        ORDER BY id DESC
        LIMIT ?
        """
        cursor.execute(sql, (min_status, limit))
        rows = cursor.fetchall()
        
        if not rows:
            print("\n--- 🚫 Database is Empty or no leads match filter. ---")
            log("No leads found matching display criteria.")
            return

        print("\n" + "="*80)
        print(f"| {'ID':<4} | {'STATUS':<20} | {'NAME':<30} | {'CITY':<10} | {'IMGS':<4} |")
        print("="*80)

        for row in rows:
            # Since conn.row_factory is set, we can access by column name
            lead_id = row['id']
            name = row['name']
            city = row['city']
            status = row['status']
            images_json = row['images']
            
            # Count the number of images (requires parsing JSON)
            try:
                img_count = len(json.loads(images_json))
            except (json.JSONDecodeError, TypeError):
                img_count = 0
            
            status_label = get_status_label(status)

            print(
                f"| {lead_id:<4} | {status_label:<20} | {name[:30]:<30} | {city:<10} | {img_count:<4} |"
            )

        print("="*80 + "\n")
        log(f"Successfully displayed {len(rows)} leads.")
        
    except sqlite3.Error as e:
        log(f"❌ Error displaying database content: {e}")
    finally:
        if conn:
            conn.close()
            
def lead_from_db_row(row: sqlite3.Row) -> Lead:
    """
    Converts a single sqlite3.Row object back into a Lead instance.
    (This is a crucial helper for any retrieval function)
    """
    # 1. Deserialize the 'images' JSON string back into a Python list
    try:
        images_list = json.loads(row['images'])
    except (json.JSONDecodeError, TypeError):
        images_list = []
        
    # 2. Instantiate the Lead class
    return Lead(
        id=row['id'],
        name=row['name'],
        phone=row['phone'],
        address=row['address'],
        city=row['city'],
        images=images_list,
        status=row['status']
    )


def get_leads(lead_id: Optional[int] = None, name: Optional[str] = None, 
             city: Optional[str] = None, status: Optional[int] = None) -> List[Lead]:
    """
    Retrieves a list of Lead objects from the database based on various filters.
    
    Returns: A list of Lead instances.
    """
    conn = create_connection()
    if conn is None:
        return []
    
    # 1. Build the dynamic SQL query and parameters
    sql = "SELECT * FROM leads WHERE 1=1"
    params = []
    
    if lead_id is not None:
        sql += " AND id = ?"
        params.append(lead_id)
        
    if name is not None:
        sql += " AND name LIKE ?" # Use LIKE for partial or case-insensitive search
        params.append(f"%{name}%") 
        
    if city is not None:
        sql += " AND city = ?"
        params.append(city)
        
    if status is not None:
        sql += " AND status = ?"
        params.append(status)
    
    log(f"Executing query: {sql} with parameters: {params}")

    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        # 2. Convert database rows into Lead objects
        leads_list = [lead_from_db_row(row) for row in rows]
        
        log(f"Successfully retrieved {len(leads_list)} lead(s).")
        return leads_list
        
    except sqlite3.Error as e:
        log(f"❌ Error fetching leads: {e}")
        return []
    finally:
        if conn:
            conn.close()

def update_lead_status(lead_id: int, new_status: int) -> bool:
    """
    Updates the status of a lead identified by lead_id.
    Returns True if updated, False otherwise.
    """
    log(f"Attempting to update status for Lead ID {lead_id} → {new_status}")
    conn = create_connection()
    if conn is None:
        log("Status update failed: No DB connection.")
        return False

    try:
        cursor = conn.cursor()
        sql = "UPDATE leads SET status = ? WHERE id = ?"
        cursor.execute(sql, (new_status, lead_id))
        conn.commit()

        if cursor.rowcount == 0:
            log(f"⚠️ No lead found with ID {lead_id}. No update performed.")
            return False

        log(f"✅ Status updated successfully for Lead ID {lead_id}.")
        return True

    except sqlite3.Error as e:
        log(f"❌ Error updating status for Lead ID {lead_id}: {e}")
        return False

    finally:
        conn.close()
        
        
def add_image_to_lead(lead_id: int, image_url: str) -> bool:
    """
    Appends a new image URL to a lead's image list.
    Returns True if successful.
    """
    log(f"Attempting to add image to Lead ID {lead_id}: {image_url}")
    conn = create_connection()
    if conn is None:
        log("Image update failed: No DB connection.")
        return False

    try:
        cursor = conn.cursor()

        # Step 1: Get existing images
        cursor.execute("SELECT images FROM leads WHERE id = ?", (lead_id,))
        row = cursor.fetchone()

        if not row:
            log(f"⚠️ No lead found with ID {lead_id}. Cannot add image.")
            return False

        try:
            current_images = json.loads(row['images']) if row['images'] else []
        except json.JSONDecodeError:
            current_images = []

        # Avoid duplicates
        if image_url in current_images:
            log(f"⚠️ Image already exists in lead ID {lead_id}. Skipping.")
            return False

        # Step 2: Modify image list
        current_images.append(image_url)
        images_json = json.dumps(current_images)

        # Step 3: Write updated list back to DB
        cursor.execute(
            "UPDATE leads SET images = ? WHERE id = ?",
            (images_json, lead_id)
        )
        conn.commit()

        log(f"✅ Image added to Lead ID {lead_id}. Total images: {len(current_images)}")
        return True

    except sqlite3.Error as e:
        log(f"❌ Error adding image to Lead ID {lead_id}: {e}")
        return False

    finally:
        conn.close()
            

if __name__ == "__main__":
    log("--- Starting Database Module Initialization ---")
    initialize_database()
    log("--- Database Module Initialization Complete ---")
    display_leads_table(limit=10, min_status=0)