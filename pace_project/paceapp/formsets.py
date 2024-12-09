from django.forms import inlineformset_factory

from pace_project.paceapp.forms import EntryCriteriaForm
from pace_project.paceapp.models import EntryCriteria, Course

EntryCriteriaFormSet = inlineformset_factory(
    parent_model=Course,  # Assuming Course is the parent model
    model=EntryCriteria,
    form=EntryCriteriaForm,
    extra=1,  # Number of extra forms
    can_delete=True  # Allow deletion of forms
)
