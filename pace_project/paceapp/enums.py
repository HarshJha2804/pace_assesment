from django.db import models
from enum import Enum


class LevelEnum(Enum):
    POSTGRADUATE = "Postgraduate"
    UNDERGRADUATE = "Undergraduate"


class UGAcademicPathWayEnum(Enum):
    DIPLOMA = "diploma"
    INTERMEDIATE = "intermediate"


class PGAcademicPathWayEnum(Enum):
    INTERMEDIATE_UG = "intermediate_ug"
    DIPLOMA_UG = "diploma_ug"
    LEVEL_DIPLOMA = "level_diploma"


class RoleEnum(Enum):
    SUPERADMIN = "Superadmin"
    ADMIN = "Admin"
    CHIEF_EXECUTIVE_OFFICER = "Chief executive officer"
    CHIEF_OPERATING_OFFICER = "Chief operating officer"
    CHIEF_FINANCIAL_OFFICER = "Chief financial officer"
    PARTNER_ONBOARDING_OFFICER = "Partner Onboarding Officer"
    PARTNER = "Partner"
    STUDENT = "Student"
    ASSESSMENT_OFFICER = "Assessment officer"
    APPLICATION_MANAGER = "Application manager"
    STUDENT_ACCOUNT_MANAGER = "Student account manager"
    COMPLIANCE_MANAGER = "Compliance manager"
    COMPLIANCE_OFFICER = "Compliance officer"
    VISA_OFFICER = "Visa officer"
    COUNTRY_HEAD = "Country head"
    REGIONAL_MARKETING_HEAD = "Regional marketing head"
    RELATIONSHIP_MANAGER = "Relationship manager"
    INTERVIEW_OFFICER = "Interview officer"
    DATA_MANAGEMENT_OFFICER = "Data management officer"
    VICE_PRESIDENT = "Vice President"
    PARTNER_ACCOUNT_MANAGER = "Partner Account Manager"


class ActivityStreamVerb(Enum):
    TOTAL_ASSESSMENT = "Total Assessment"
    SENT_ASSESSMENT = "Assessment Sent"
    REJECTED_ASSESSMENT = "Assessment Reject"
    TOTAL_APPLICATION = "Total Application"
    APPLICATION_PENDING_FROM_IOA = "Pending From IG"
    APPLICATION_PENDING_FROM_AGENT = "Pending From Partner"
    APPLICATION_SUBMITTED = "Application Submitted"
    APPLICATION_REJECTED_BY_IOA = "Rejected By IG"
    CONDITIONAL_OFFER_LETTER = "Conditional Offer Received"
    UNCONDITIONAL_OFFER_LETTER = "UnConditional Offer Received"
    FEE_PAID = "Fee Paid"
    COE_APPLIED = "COE Applied"
    COE_RECEIVED = "COE Received"
    VISA_LODGED = "VISA Lodged"
    VISA_GRANT = "VISA Grant"
    VISA_REFUSED = "VISA Refused"
    PRESCREENING_PENDING = "Prescreening Pending"


class UploadFileType(Enum):
    PDF = 'pdf'
    JPG = 'jpg'
    PNG = 'png'
    Doc = 'doc'
