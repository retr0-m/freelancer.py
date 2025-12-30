# proposal_sender.py
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path
from lead import Lead
from log import log
import os
from dotenv import load_dotenv
load_dotenv()



# ---------------- CONFIG ----------------
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
# ----------------------------------------

def send_email(lead: Lead) -> bool:
    """
    Sends a proposal email with attached PDF to the given Lead.
    Returns True if email was sent successfully, False otherwise.
    """

    # Check for email
    if not lead.email:
        log(f" Lead {lead.name} has no email. Skipping proposal.")
        return False

    # Proposal PDF path
    proposal_path = Path(f"./leads/{lead.id}/documents/proposal.pdf")
    if not proposal_path.exists():
        log(f" Proposal PDF not found for Lead ID {lead.id} at {proposal_path}")
        return False

    # Email content
    subject = f"{lead.name} — Il tuo nuovo sito web è pronto 🎉"
    preview_url = f"https://matteocola.com/preview/f/{lead.id}/index.html"
    body = f"""
Buongiorno {lead.name},

Vi ho creato un sito web.
Sono uno sviluppatore di siti web e ho notato che non ne avete uno, quindi ho creato questa "anteprima" così che voi possiate prendere in maggior considerazione di adottarne uno.

Potete trovare l'anteprima al seguente indirizzo: {preview_url}

Solitamente mi presento di persona consegnando un foglio che trovate in allegato.
Tutto il contenuto è naturalmente una bozza e tutto il design e contenuto può essere cambiato su richeista.

Cordiali saluti,
Matteo
Web Designer — matteocola.com
"""

    # Create the email
    msg = EmailMessage()
    msg["From"] = SENDER_EMAIL
    msg["To"] = lead.email
    msg["Subject"] = subject
    msg.set_content(body)

    # Attach PDF
    try:
        with open(proposal_path, "rb") as f:
            pdf_data = f.read()
            msg.add_attachment(
                pdf_data,
                maintype="application",
                subtype="pdf",
                filename="proposta.pdf"
            )
    except Exception as e:
        log(f" Failed to attach PDF for Lead {lead.id}: {e}")
        return False

    # Send email via SMTP SSL
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            log(f"📩 Proposal email sent successfully to {lead.email} (Lead ID {lead.id})")

            # Update lead status in DB
            lead.change_status(3)
            return True

    except Exception as e:
        log(f" Failed to send email to {lead.email} (Lead ID {lead.id}): {e}")
        return False


def send_instagram():
    pass    #TODO IMPLEMENT THIS FUNC


# ---------------- TESTING ----------------
if __name__ == "__main__":
    from lead import Lead

    # Dummy lead for testing
    test_lead = Lead(
        id=5,
        name="Ristorante Test",
        phone="+4123456789",
        email="matteo.cola@hotmail.com",
        address="Via Roma 1",
        city="Lugano",
        images=[],
        status=0
    )

    send_proposal(test_lead)
