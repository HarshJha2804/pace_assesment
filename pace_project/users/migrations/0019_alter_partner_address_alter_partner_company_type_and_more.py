# Generated by Django 4.2.11 on 2024-07-22 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_employee_mobile_country_code_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partner',
            name='address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='partner',
            name='company_type',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='partner',
            name='office_type',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddIndex(
            model_name='partner',
            index=models.Index(fields=['company_name', 'email', 'mobile_number'], name='users_partn_company_cc4218_idx'),
        ),
    ]