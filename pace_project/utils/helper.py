from pace_project.core.models.generic_models import GenericRemark


def create_generic_remark(*, content_object, remark, created_by):
    GenericRemark.objects.create(
        content_object=content_object,
        remark=remark,
        created_by=created_by
    )
