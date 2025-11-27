Activity diegram:
graph TD
    subgraph Initialization
        A[Start: main.py] --> B{database.py:<br>Initialize SQLite DB};
    end

    subgraph Step 1: Find Customers
        B --> C[find_customers.py];
        C --> D{Input: leads/index.csv};
        D --> E{Output: Populate leads.db<br>Status: 0 (New)};
        E -- Each Lead --> F[Lead Class in DB];
    end

    subgraph Step 2: Scrape Images
        F -- Filter: Status = 0 --> G[scrape_images.py<br>(Concurrent Execution)];
        G -- Uses --> H{Selenium for Google Images};
        H -- Downloads images --> I{Output: leads/{lead_id}/imgs/<br>{lead_id}_{img_id}.png};
        I --> J{Update leads.db<br>Lead.images: list[str]<br>Lead.status: 1 (Images Scraped)};
    end

    subgraph Step 3: Create Websites
        J -- Filter: Status = 1 --> K[create_websites.py<br>(Yield Method)];
        K --> L{Prompt Gemini 3 with<br>Lead Data + Image Paths};
        L --> M{Output: leads/{lead_id}/website/<br>index.html + assets};
        M --> N{Update leads.db<br>Lead.status: 2 (Website Done)};
    end

    subgraph Step 4: [Internal: main.py] Update Status
        N --> P[main.py: Loop through yields,<br>Mark website creation complete];
    end

    subgraph Step 5: Create Documentation
        P -- Filter: Status = 2 --> Q[create_documentation.py];
        Q --> R{Generate QR Code from Website URL};
        Q --> S{Replace QR in Template PDF};
        S --> T{Output: leads/{lead_id}/documents/proposal/<br>proposal.pdf + whats_included.pdf};
        T --> U{Update leads.db<br>Lead.status: 3 (Documentation Done)};
    end

    subgraph Finalization
        U --> V[End: All Leads Processed];
    end

file structure:
project_root/
├── main.py                    # Orchestrates the pipeline
├── find_customers.py          # Step 1 Script
├── scrape_images.py           # Step 2 Script
├── create_websites.py         # Step 3 Script (yields)
├── create_documentation.py    # Step 5 Script
├── database.py                # Database interaction logic (SQLite)
├── logger.py                  # Custom logging utility
├── leads.db                   # ⚡ SQLite Database (stores all Lead objects)
└── leads/
    ├── index.csv              # (Initial input, then imported into DB)
    └── {lead_id}/             # Per-lead directory
        ├── imgs/
        │   └── {lead_id}_{img_id}.png  # (e.g., 23_01.png, 23_02.png)
        ├── website/
        │   └── index.html
        │   └── style.css
        │   └── ...
        └── documents/
            └── proposal/
                └── proposal.pdf
                └── whats_included.pdf