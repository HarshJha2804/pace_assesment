# Generated by Django 4.2.11 on 2024-07-31 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0025_employee_assigned_regions'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='emergency_contact_relation',
            field=models.CharField(blank=True, choices=[('father', 'Father'), ('mother', 'Mother'), ('brother', 'Brother'), ('sister', 'Sister'), ('wife', 'Wife'), ('husband', 'Husband')], max_length=30, null=True),
        ),
    ]