# Generated by Django 5.0.7 on 2024-09-09 09:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0035_pgstudentacademic_work_experience_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='on_boarded_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]