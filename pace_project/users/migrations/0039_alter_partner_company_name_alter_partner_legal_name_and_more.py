# Generated by Django 4.2.11 on 2024-10-01 09:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0038_employee_users_emplo_mobile__c39bfa_idx_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partner',
            name='company_name',
            field=models.CharField(help_text='Company Name', max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='partner',
            name='legal_name',
            field=models.CharField(help_text='Registered Company Name', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='partner',
            name='on_boarded_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='onboarding', to=settings.AUTH_USER_MODEL),
        ),
    ]