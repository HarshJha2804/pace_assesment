from enum import Enum


class StatusTemplate(Enum):
    ACTIVE = '<span class="status status-green">Active</span>'
    INACTIVE = '<span class="status">Inactive</span>'
