# Generated by Django 4.2.11 on 2024-10-03 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0040_partner_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='agreement',
            field=models.FileField(blank=True, null=True, upload_to='partner/agreement'),
        ),
        migrations.AddField(
            model_name='partner',
            name='is_agreement_sent',
            field=models.BooleanField(default=False),
        ),
    ]