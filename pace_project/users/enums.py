from enum import Enum


class PartnerCommunicationEnum(Enum):
    MOBILE = "mobile"
    EMAIL = "email"
    WHATSAPP = "whatsapp"


class PartnerStatusEnum(Enum):
    NEW = "new"
    FOLLOW_UP = "follow-up"
    NOT_INTERESTED = "not-interested"
    INTERESTED = "interested"
