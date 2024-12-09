from pace_project.utils.templates import StatusTemplate


def get_status_template(*, is_active):
    """
    Returns the HTML status template based on the is_active parameter.

    Args:
        is_active (bool): The active status of the object.

    Returns:
        str: The HTML status template.
    """
    return StatusTemplate.ACTIVE.value if is_active else StatusTemplate.INACTIVE.value
