from enum import Enum


class MeetingStatusEnum(Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"


class CommunicationTypeEnum(Enum):
    EMAIL = "email"
