# Generated by Django 4.2.11 on 2024-06-14 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_partner'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]