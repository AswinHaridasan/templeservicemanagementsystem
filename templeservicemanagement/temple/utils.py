from django.core.mail import send_mail
from django.conf import settings

def send_email_notification(subject, message, recipient_email):
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,  # Sender email
        [recipient_email],  # Recipient email
        fail_silently=False,
    )


def generate_certificate_pdf(certificate):
    """Generates a marriage certificate PDF and returns its file path."""
    from fpdf import FPDF
    import os
    from django.conf import settings

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)

    pdf.cell(200, 10, "Marriage Certificate", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Bride: {certificate.bride_name}", ln=True)
    pdf.cell(200, 10, f"Groom: {certificate.groom_name}", ln=True)
    pdf.cell(200, 10, f"Date: {certificate.marriage_date}", ln=True)

    pdf_output_path = os.path.join(settings.MEDIA_ROOT, "certificates", f"certificate_{certificate.id}.pdf")
    os.makedirs(os.path.dirname(pdf_output_path), exist_ok=True)

    pdf.output(pdf_output_path)
    return pdf_output_path  # ✅ Return the file path
