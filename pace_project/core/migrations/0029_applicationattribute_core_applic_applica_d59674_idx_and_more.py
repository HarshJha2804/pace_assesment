# Generated by Django 4.2.11 on 2024-09-10 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_rmuniversityintake'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='applicationattribute',
            index=models.Index(fields=['application', 'key'], name='core_applic_applica_d59674_idx'),
        ),
        migrations.AddConstraint(
            model_name='applicationattribute',
            constraint=models.UniqueConstraint(fields=('application', 'key'), name='unique_application_key'),
        ),
    ]