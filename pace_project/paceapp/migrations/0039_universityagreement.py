# Generated by Django 5.0.7 on 2024-08-14 12:03

import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paceapp', '0038_country_is_active_for_student_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UniversityAgreement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('agreement_start_date', models.DateField(blank=True, null=True)),
                ('agreement_end_date', models.DateField(blank=True, null=True)),
                ('upload_agreement', models.FileField(blank=True, null=True, upload_to='university/agreements/')),
                ('is_active', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_agreements', to=settings.AUTH_USER_MODEL)),
                ('university', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='paceapp.university')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]