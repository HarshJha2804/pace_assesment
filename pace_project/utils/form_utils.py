
def update_form_field_attributes(*, fields, attributes):
    """
        Update multiple fields with given attributes.

        :param fields: A list of tuples (field_name, placeholder)
        :param attributes: Dictionary of attributes to update
        """
    for field_name, placeholder in fields:
        field = fields.get(field_name)
        if field:
            field.widget.attrs.update({'placeholder': placeholder, **attributes})


# form_utils.py
def update_field_attributes(form, fields_attributes):
    """
    Update multiple fields with given attributes.

    :param form: The form instance
    :param fields_attributes: A dictionary where keys are field names and values are dictionaries of attributes
    """
    for field_name, attrs in fields_attributes.items():
        if field_name in form.fields:
            form.fields[field_name].widget.attrs.update(attrs)


def set_placeholder(form, fields_placeholders):
    """
    Set placeholder text for multiple fields.

    :param form: The form instance
    :param fields_placeholders: A dictionary where keys are field names and values are placeholder texts
    """
    for field_name, placeholder in fields_placeholders.items():
        if field_name in form.fields:
            form.fields[field_name].widget.attrs['placeholder'] = placeholder


def set_empty_label(form, fields_empty_labels):
    """
    Set empty label for multiple fields.

    :param form: The form instance
    :param fields_empty_labels: A dictionary where keys are field names and values are empty labels
    """
    for field_name, empty_label in fields_empty_labels.items():
        if field_name in form.fields and hasattr(form.fields[field_name], 'empty_label'):
            form.fields[field_name].empty_label = empty_label
