import base64
import os

from django.conf import settings
from django.template.loader import render_to_string
import io
from pace_project.users.models import UGStudentAcademic, Student, PGStudentAcademic, Partner
from django.core.mail import EmailMultiAlternatives
from xhtml2pdf import pisa


def add_ug_student_academics(*, student: Student, form_data):
    """
    Save the academic details of an undergraduate student for use in Application.
    """
    # Extract form data into a dictionary
    fields = [
        "country_id", "board_id", "stream_id", "sub_stream_id",
        "year_id", "tenth_marks", "work_experience", "academic_pathway",
        "diploma_overall", "twelfth_overall", "twelfth_math_marks",
        "twelfth_eng_marks", "best_four_marks", "english_test_id",
        "eng_test_overall", "speaking", "writing", "reading", "listening"
    ]
    data = {field: form_data.get(field) for field in fields}

    # Create UGStudentAcademic instance with basic details
    academic_record = UGStudentAcademic.objects.create(
        student=student,
        country_id=data["country_id"],
        board_id=data["board_id"],
        stream_id=data["stream_id"],
        sub_stream_id=data["sub_stream_id"],
        passing_year_id=data["year_id"],
        tenth_marks=data["tenth_marks"],
        work_experience=data["work_experience"],
        academic_pathway=data["academic_pathway"],
    )

    # Set marks based on academic pathway
    if data["academic_pathway"] == 'diploma' and data["diploma_overall"]:
        academic_record.overall_marks = data["diploma_overall"]
    elif data["academic_pathway"] == 'intermediate' and data["twelfth_overall"]:
        academic_record.overall_marks = data["twelfth_overall"]
        academic_record.twelfth_math_marks = data["twelfth_math_marks"]
        academic_record.twelfth_english_marks = data["twelfth_eng_marks"]
        academic_record.twelfth_best_four_marks = data["best_four_marks"]

    # Save the initial instance
    academic_record.save()

    # Set English test details if available
    if data["english_test_id"]:
        academic_record.english_test_type_id = data["english_test_id"]
        academic_record.english_overall = data["eng_test_overall"]
        academic_record.speaking = data["speaking"]
        academic_record.writing = data["writing"]
        academic_record.reading = data["reading"]
        academic_record.listening = data["listening"]
        academic_record.save()


def add_pg_student_academics(*, student: Student, form_data):
    """
        Save the academic details of a postgraduate student for use in later assessment discoveries.
    """
    # Extract form data into a dictionary
    fields = [
        "country_id", "board_id", "stream_id", "sub_stream_id",
        "year_id", "work_experience", "academic_pathway", "twelfth_eng_marks",
        "diploma_overall", "ug_overall", "level_diploma", "english_test_id",
        "eng_test_overall", "speaking", "writing", "reading", "listening"
    ]
    data = {field: form_data.get(field) for field in fields}

    # Create PGStudentAcademic instance with basic details
    academic_record = PGStudentAcademic.objects.create(
        student=student,
        country_id=data["country_id"],
        board_id=data["board_id"],
        stream_id=data["stream_id"],
        sub_stream_id=data["sub_stream_id"],
        passing_year_id=data["year_id"],
        work_experience=data["work_experience"],
        academic_pathway=data["academic_pathway"],
    )

    # Set marks based on academic pathway
    if data["academic_pathway"] == 'intermediate_ug' and data["twelfth_eng_marks"]:
        academic_record.twelfth_english_marks = data["twelfth_eng_marks"]
        academic_record.ug_overall_marks = data["ug_overall"]

    elif data["academic_pathway"] == 'diploma_ug' and data["diploma_overall"]:
        academic_record.diploma_overall_marks = data["diploma_overall"]
        academic_record.ug_overall_marks = data["ug_overall"]

    elif data["academic_pathway"] == 'level_diploma' and data["level_diploma"]:
        academic_record.level_diploma_marks = data["level_diploma"]

    # Save the initial instance
    academic_record.save()

    # Set English test details if available
    if data["english_test_id"]:
        academic_record.english_test_type_id = data["english_test_id"]
        academic_record.english_overall = data["eng_test_overall"]
        academic_record.speaking = data["speaking"]
        academic_record.writing = data["writing"]
        academic_record.reading = data["reading"]
        academic_record.listening = data["listening"]
        academic_record.save()


def generate_partner_agreement_pdf(*, partner: Partner):
    """Generate PDF content from the partnership agreement template."""
    image_path = os.path.join(settings.STATIC_ROOT, "logo/infinitegroup-logo-light.png")
    with open(image_path, 'rb') as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode('utf-8')

    context = {
        'image_base64': encoded_string,
        "partner": partner
    }

    template_name = "partner/agreements/dubai_office_agreement.html"
    from pace_project.core.enums import CountryEnum
    if partner.country.country_name == CountryEnum.INDIA.value:
        template_name = "partner/agreements/india_office_agreement.html"

    html_content = render_to_string(template_name, context)
    pdf_buffer = io.BytesIO()  # In-memory buffer for PDF

    # Create PDF from HTML
    pdf = pisa.pisaDocument(io.StringIO(html_content), pdf_buffer)

    if pdf.err:
        return None  # Indicate PDF generation failure

    pdf_buffer.seek(0)  # Move to the beginning of the buffer
    return pdf_buffer


def send_partner_agreement_email(*, partner: Partner):
    """Send an email with the partnership agreement PDF attached."""
    pdf_file = generate_partner_agreement_pdf(partner=partner)
    if not pdf_file:
        return False  # PDF generation failed
    context = {
        'partner': partner,
        "email": partner.email,
        "country_code": partner.country.country_code,
        "mobile": partner.mobile_number,
        "contact_person": partner.contact_name,
        "address": partner.get_full_address,
    }
    subject = "Welcome to Infinite Group | Partnership Contract"
    recipient_list = [partner.email]
    pdf_filename = f'partnership_agreement_{partner.company_name}.pdf'
    email_message = render_to_string("emailtemplates/partner_agreement_email.html", context)

    email = EmailMultiAlternatives(
        subject=subject,
        body=email_message,  # Plain text version (optional)
        to=recipient_list,
    )
    email.attach_alternative(email_message, 'text/html')
    email.attach(pdf_filename, pdf_file.getvalue(), 'application/pdf')
    return email.send(fail_silently=False)
