# Generated by Django 4.2.11 on 2024-11-22 07:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paceapp', '0043_course_link_course_scholarship_course_tuition_fees'),
    ]

    operations = [
        migrations.AddField(
            model_name='university',
            name='commission_frequency',
            field=models.CharField(blank=True, choices=[('intakewise', 'Intakewise'), ('annually', 'Annually'), ('partially', 'Partially')], default='intakewise', max_length=100, null=True),
        ),
    ]