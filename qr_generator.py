# Importing library
import qrcode
from log import log
from lead import Lead
import os
def generate_qr(lead: Lead):

    # Data to be encoded
    data = f'https://www.matteocola.com/preview/f/{lead.id}/index.html'

    # Encoding data using make() function
    img = qrcode.make(data)

    log("qr generated... saving it...")
    # Saving as an image file
    try:
        img.save(f'./leads/{lead.id}/documents/qr_code.png')
        
    except FileNotFoundError:
        log("documents folder not found, creating one.")
        os.makedirs(f"./leads/{lead.id}/documents/", exist_ok=True)
        img.save(f'./leads/{lead.id}/documents/qr_code.png')
    log("done!")


if __name__ == "__main__":
    log("="*50)
    log("TESTING SCRIPT")
    
    #TEST 1
    log('TEST-1 with following sandbox data:      Lead(150, "Al-74", "21312432", "Via Trevano 74, 6900 Lugano, Switzerland", "Lugano", [], 0)')
    
    
    l=Lead(150, "Al-74", "21312432", "Via Trevano 74, 6900 Lugano, Switzerland", "Lugano", [], 0)
    
    generate_qr(l)