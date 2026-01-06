"""
This script should only used by developers to recreate the proposal
documentation for all leads in the database.
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PyPDF2 import PdfReader, PdfWriter
import io
from lead import Lead
from log import log
import qr_generator
import database
import subprocess
import sys
import os
import zipfile
from datetime import datetime

def choose_printer_and_print(files: list[str]):
    """
    Displays available printers, lets the user choose one,
    then prints the provided list of files.
    """

    # 1. Get available printers
    result = subprocess.run(
        ["lpstat", "-p"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0 or not result.stdout.strip():
        print("❌ No printers found.")
        return

    printers = [
        line.split()[1]
        for line in result.stdout.splitlines()
        if line.startswith("printer")
    ]

    if not printers:
        print("❌ No usable printers detected.")
        return

    # 2. Display printers
    print("\nAvailable printers:")
    for i, printer in enumerate(printers, start=1):
        print(f"  {i}. {printer}")

    # 3. User selection
    try:
        choice = int(input("\nSelect printer number: ").strip())
        printer_name = printers[choice - 1]
    except (ValueError, IndexError):
        print("❌ Invalid selection.")
        return

    print(f"\n🖨️ Using printer: {printer_name}")

    # 4. Print files
    for file in files:
        print(f"Printing: {file}")
        subprocess.run([
            "lp",
            "-d", printer_name,
            file
        ])

    print("\n✅ Printing completed.")

def create_preview_document_tantum(lead: Lead):
    INPUT_PDF = "./document_templates/proposal.pdf"
    OUTPUT_PDF = f"./leads/{lead.id}/documents/proposal_tantum.pdf"
    QR_IMAGE = f"./leads/{lead.id}/documents/qr_code.png"
    TITLE_TEXT = lead.name

    TITLE_X, TITLE_Y = 50, 780

    QR_X, QR_Y = 40, 550
    QR_WIDTH, QR_HEIGHT = 200, 200

    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=A4)

    c.setFont("Helvetica-Bold", 28)
    c.drawString(TITLE_X, TITLE_Y, TITLE_TEXT)

    c.drawImage(QR_IMAGE, QR_X, QR_Y, width=QR_WIDTH, height=QR_HEIGHT, mask='auto')

    c.save()
    packet.seek(0)

    overlay_pdf = PdfReader(packet)
    original_pdf = PdfReader(INPUT_PDF)
    writer = PdfWriter()

    page = original_pdf.pages[0]
    page.merge_page(overlay_pdf.pages[0])
    writer.add_page(page)

    for i in range(1, len(original_pdf.pages)):
        writer.add_page(original_pdf.pages[i])

    with open(OUTPUT_PDF, "wb") as f:
        writer.write(f)

    log("Done! Created:", OUTPUT_PDF)


def create_zip_with_files(files_path, destination_path):
    """
    Creates a ZIP archive containing the given files.

    :param files_path: list[str] | str
        - List of file paths OR a directory path
    :param destination_path: str
        - Path to the resulting .zip file
    """

    # Normalize input: directory → list of files
    if isinstance(files_path, str):
        if not os.path.isdir(files_path):
            raise ValueError(f"Path does not exist or is not a directory: {files_path}")

        files = [
            os.path.join(files_path, f)
            for f in os.listdir(files_path)
            if os.path.isfile(os.path.join(files_path, f))
        ]
    else:
        files = files_path
    if not files:
        raise ValueError("No files to zip.")

    # Ensure destination folder exists
    os.makedirs(os.path.dirname(destination_path) or ".", exist_ok=True)

    with zipfile.ZipFile(destination_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in files:
            print(".", end="")
            if not os.path.isfile(file):
                continue
            lead_id = file.split("/")[2]  # ./leads/{id}/documents/...
            arcname = f"proposal_{lead_id}.pdf"
            zipf.write(file, arcname)

    return destination_path

if __name__ == "__main__":

    # some sort of shell
    print("Documentation shell ('help' for explanation)")
    while True:
        try:
            cmd=input(">> ")
            cmd=cmd.strip()
        except KeyboardInterrupt:
            exit()
        if cmd == "help":
            print("\nhelp -> shows this message\ntest -> runs test protocol for this script\ngenerate -> generates doc for all leads in ./leads/.\nprint -> prints the documents.\nzip -> saves a zip with the documents\n\tzip download -> to download folder\n\tzip current -> to current folder")
        elif cmd == "test":
            log("="*50)
            log("TESTING SCRIPT")

            #TEST 1
            log('TEST-1 with following sandbox data:      Lead(150, "Al-74", "21312432", "Via Trevano 74, 6900 Lugano, Switzerland", "Lugano", [], 0)')
            l=Lead(
                    150,
                    "Al-74",
                    "21312432",
                    "Via Trevano 74, 6900 Lugano, Switzerland",
                    "Lugano",
                    [],
                    0
                )

            qr_generator.generate_qr(l)
            create_preview_document_tantum(l)
        elif cmd == "generate":
            leads=database.get_leads()
            for l in leads:
                print("\r",end="")
                print("#"*l.id, end="")
                qr_generator.generate_qr(l)
                create_preview_document_tantum(l)

        elif cmd == "zip download":
            last_id=database.get_last_lead_id()
            files=[]
            for i in range(0,last_id):
                files.append(f"./leads/{i}/documents/proposal_tantum.pdf")
            create_zip_with_files(
                files,
                destination_path=f"/Users/kali/Downloads/documents_{datetime.now()}.zip"
                )

        elif cmd == "zip current":
            last_id=database.get_last_lead_id()
            files=[]
            for i in range(0,last_id):
                files.append(f"./leads/{i}/documents/proposal_tantum.pdf")
            create_zip_with_files(files,destination_path=f"./documents_{datetime.now()}.zip")

        elif cmd == "print":
            last_id=database.get_last_lead_id()
            files=[]
            for i in range(0,last_id):
                files.append(f"./leads/{i}/documents/proposal_tantum.pdf")
            choose_printer_and_print(files)

        elif cmd == "exit":
            exit()

        else:
            print("command not found, type 'help' to get help")
