from django.core.exceptions import PermissionDenied
from django.utils.functional import cached_property
from django.views.generic import View

from pace_project.users.models import Partner
from pace_project.utils.utils import get_partner_role_obj


class PartnerRequiredMixin(View):

    @cached_property
    def partner(self):
        return self.get_partner_profile()

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        if not request.user.is_staff:
            user_role = getattr(request.user, 'role', None)
            partner_role = get_partner_role_obj()
            if user_role == partner_role and self.partner:
                return super().dispatch(request, *args, **kwargs)
            else:
                raise PermissionDenied("Warning: Your account does not have an associated Partner profile.")
        else:
            raise PermissionDenied("You do not have partner permissions.")

    def get_partner_profile(self):
        try:
            return self.request.user.partner
        except Partner.DoesNotExist:
            return None
