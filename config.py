"""
Docstring for config

* CONFIG FILE IS ONLY FOR RUNNING SERVER VERSION, EVERY STRING WILL BE IGNORED ON CURRENT MAIN BRANCH.
"""

VERSION="SERVER 1.8.2"


# * create_website.py
GEMINI_MODEL = "gemini-2.5-flash"
PROMPT_FILE = "../generate_website_prompt.json"


TEMP_PATH="__temp__" # * Used by many scripts in SERVER version

# * server.py
CUSTOMERS_TYPE = [
    # Food & hospitality
    "restaurant",
    "ristorante",
    "restaurant",
    "bar",
    "cafe",
    "caffè",
    "café",
    "bakery",
    "panetteria",
    "bäckerei",
    "boulangerie",
    "pizzeria",
    "hotel",
    "hôtel",

    # Beauty & wellness
    "hair salon",
    "parrucchiere",
    "friseursalon",
    "salon de coiffure",
    "barber",
    "barbiere",
    "barbier",
    "beauty salon",
    "centro estetico",
    "kosmetikstudio",
    "institut de beauté",

    # Medical
    "dentist",
    "dentista",
    "zahnarzt",
    "dentiste",
    "doctor",
    "medico",
    "arzt",
    "médecin",

    # Professional services
    "lawyer",
    "avvocato",
    "anwalt",
    "avocat",
    "accountant",
    "commercialista",
    "buchhalter",
    "expert-comptable",

    # Real estate & fitness
    "real estate agency",
    "agenzia immobiliare",
    "immobilienagentur",
    "agence immobilière",
    "gym",
    "palestra",
    "fitnessstudio",
    "salle de sport",

    # Automotive & trades
    "car repair",
    "officina",
    "autowerkstatt",
    "garage automobile",
    "plumber",
    "idraulico",
    "klempner",
    "plombier",
    "electrician",
    "elettricista",
    "elektriker",
    "électricien",

    # Creative & retail
    "photographer",
    "fotografo",
    "fotograf",
    "photographe",
    "marketing agency",
    "agenzia di marketing",
    "marketingagentur",
    "agence marketing",
    "retail store",
    "negozio",
    "einzelhandelsgeschäft",
    "magasin"
]

CUSTOMERS_CITY = [
    "Zürich",
    "Zurich",
    "Bern",
    "Basel",
    "Luzern",
    "St. Gallen",
    "Genf",
    "Geneva",
    "Lausanne",
    "Neuchâtel",
    "Lugano",
    "Bellinzona",
    "Locarno",
]

MAX_LEADS_TO_DISPLAY = 2 # * This means, when there are no leads generated how many should the program generate? and if there are some that have already been generated, how many should be added?



# * imgs_description.py
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llava:7b"
MAX_RETRIES = 5
