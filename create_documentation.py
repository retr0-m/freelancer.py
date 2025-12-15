from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PyPDF2 import PdfReader, PdfWriter
import io
from lead import Lead
from log import log
import qr_generator


def create_preview_document(lead: Lead):
    INPUT_PDF = "./document_templates/proposal.pdf"
    OUTPUT_PDF = f"./leads/{lead.id}/documents/proposal.pdf"
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


if __name__ == "__main__":
    log("="*50)
    log("TESTING SCRIPT")

    #TEST 1
    log('TEST-1 with following sandbox data:      Lead(150, "Al-74", "21312432", "Via Trevano 74, 6900 Lugano, Switzerland", "Lugano", [], 0)')
    l=Lead(150, "Al-74", "21312432", "Via Trevano 74, 6900 Lugano, Switzerland", "Lugano", [], 0)

    qr_generator.generate_qr(l)
    create_preview_document(l)

