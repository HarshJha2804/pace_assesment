from enum import Enum


class StatusTypeEnum(Enum):
    APPLICATION_PENDING_FROM_IOA = "Pending From IG"
    ASSESSMENT_SENT = "Assessment Sent"
    ASSESSMENT_REJECTED = "Assessment Rejected"
    APPLICATION_SUBMITTED = "Application Submitted"
    APPLICATION_PENDING_FROM_AGENT = "Pending From Partner"
    APPLICATION_REJECTED_BY_IOA = "Rejected By IG"
    CONDITIONAL_OFFER_LETTER = "Conditional Offer Received"
    UNCONDITIONAL_OFFER_LETTER = "UnConditional Offer Received"
    CAS_RECEIVED = "CAS Received"
    PRESCREENING_APPROVED = "Prescreening Approved"
    PRESCREENING_PENDING = "Prescreening Pending"
    PRESCREENING_REJECTED = 'Prescreening Rejected'
    FEE_PAID = "Fee Paid"
    COE_APPLIED = "COE Applied"
    COE_RECEIVED = "COE Received"
    VISA_LODGED = "VISA Lodged"
    VISA_GRANT = "VISA Grant"
    VISA_REFUSED = "VISA Refused"
    REVISED_OFFER_PENDING = 'Revised Offer Pending'
    CAS_APPLIED = "CAS Applied"


class ApplicationAttributeEnum(Enum):
    PRE_CAS_INTERVIEW = "pre_cas_interview"
    CAS_SHIELD_LOGIN = "cas_shield_login"
    CAS_SHIELD_PASSWORD = "cas_shield_password"
    MEDICAL = "medical"


class CountryEnum(Enum):
    INDIA = "India"
