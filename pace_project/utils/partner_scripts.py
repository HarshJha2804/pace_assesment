import csv
import logging
import string
import random
from typing import Dict, Optional

from pace_project.paceapp.models import State, Country
from pace_project.users.models import Partner
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress

from pace_project.utils.scripts import fetch_country
from pace_project.utils.utils import get_partner_role_obj
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q

User = get_user_model()
logger = logging.getLogger(__name__)


def generate_random_password(length: int = 10) -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def fetch_country_by_country_code(country_code: str) -> Optional[Country]:
    return Country.objects.filter(
        Q(country_code__icontains=country_code) | Q(country_name__iexact=country_code)
    ).first()


def fetch_state(*, name: str, country: Country) -> Optional[State]:
    return State.objects.filter(name__iexact=name, country=country).first()


def is_partner_exists(company_name: str, legal_name: str, email: str) -> bool:
    return (
        Partner.objects.filter(company_name__iexact=company_name).exists()
        or Partner.objects.filter(legal_name__iexact=legal_name).exists()
        or Partner.objects.filter(email__iexact=email).exists()
        or User.objects.filter(email__iexact=email).exists()
    )


def create_user_allauth_email(user: User) -> EmailAddress:
    return EmailAddress.objects.get_or_create(
        user=user,
        email=user.email,
        defaults={"verified": True, "primary": True}
    )[0]


def create_partner_user(user_data: Dict) -> Optional[User]:
    """Create a user and mark their email as verified."""
    password = generate_random_password()
    user_data['password'] = password
    user = User.objects.create_user(**user_data)
    if user:
        create_user_allauth_email(user=user)
        user.set_password(password)
        user.save()
    return user


def create_partner(*, partner_data: Dict) -> Partner:
    return Partner.objects.create(**partner_data)


def send_partner_credentials_email(user: User, password: str):
    """Send an email to the partner with login credentials."""
    subject = "Welcome to Infinite Group!"
    message = (
        f"Dear {user.name},\n\n"
        f"Welcome to Infinite Group! Your account has been successfully created.\n\n"
        f"Login details:\n"
        f"Email: {user.email}\n"
        f"Password: {password}\n\n"
        f"Please log in and change your password at your earliest convenience.\n\n"
        "Best regards,\n"
        "Infinite Group Team"
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        # bcc=['admin@infinitegroup.org'],
        fail_silently=False,
    )


def load_partners_from_csv():
    """Load and save partners from a CSV file into the database."""
    csv_file_path = "F:\pace\dump\partner-data.csv"
    try:
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            partner_reader = csv.DictReader(file)
            added_count = 0
            existing_count = 0

            for partner_data in partner_reader:
                company_name = partner_data.get("company_name", "").strip()
                email = partner_data.get("email", "").strip()
                legal_name = partner_data.get("legal_name", "").strip()

                if not company_name or not email:
                    continue

                if not is_partner_exists(company_name=company_name, legal_name=legal_name, email=email):
                    country_name = partner_data.get("country", "").strip()
                    mobile_country_code = partner_data.get("mobile_country_code", "").strip()
                    whatsapp_country_code = partner_data.get("whatsapp_country_code", "").strip()
                    user_data = {
                        "email": email,
                        "name": company_name,
                        "role": get_partner_role_obj(),
                    }
                    user_obj = create_partner_user(user_data=user_data)
                    if user_obj:
                        partner_country = fetch_country(name=country_name)
                        p_data = {
                            "company_name": company_name,
                            "user": user_obj,
                            "legal_name": legal_name,
                            "contact_name": partner_data.get("contact_name", "").strip(),
                            "email": email,
                            "designation": partner_data.get("designation", "").strip(),
                            "mobile_country_code": fetch_country_by_country_code(mobile_country_code),
                            "mobile_number": partner_data.get("mobile_number", "").strip(),
                            "whatsapp_country_code": fetch_country_by_country_code(whatsapp_country_code),
                            "whatsapp_number": partner_data.get("whatsapp_number", "").strip(),
                            "company_type": partner_data.get("company_type", "").strip(),
                            "address": partner_data.get("address", "").strip(),
                            "country": partner_country,
                            "state": fetch_state(name=partner_data.get("state", "").strip(), country=partner_country),
                            "city": partner_data.get("city", "").strip(),
                            "pincode": partner_data.get("pincode", "").strip(),
                            "is_active": True,
                            "onboarding_completed": True,
                            "website": partner_data.get("website", "").strip(),
                            "on_boarded_by": User.objects.filter(is_superuser=True).first()
                        }
                        create_partner(partner_data=p_data)
                        # send_partner_credentials_email(user=user_obj, password=user_data['password'])
                        added_count += 1
                        logger.info(f"{added_count}. Added partner: {company_name}")
                    else:
                        logger.warning(f"Failed to create user for: {email}")
                else:
                    existing_count += 1
                    logger.info(f"Partner already exists: {company_name}")

            logger.info(f"Partners added: {added_count}, existing: {existing_count}")

    except Exception as e:
        logger.error(f"Error loading partners from CSV: {e}")
