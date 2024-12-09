from django.contrib import admin

from pace_project.partner.models import PartnerCommission, PartnerCommissionSetup


@admin.register(PartnerCommission)
class PartnerCommissionAdmin(admin.ModelAdmin):
    list_display = ['university', 'partner', 'date', 'commission_type', 'commission', 'created_by']


@admin.register(PartnerCommissionSetup)
class PartnerCommissionSetupAdmin(admin.ModelAdmin):
    list_display = ['country', 'university', 'commission_type', 'created_by']
