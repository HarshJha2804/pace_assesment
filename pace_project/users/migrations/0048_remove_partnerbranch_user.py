# Generated by Django 4.2.11 on 2024-11-25 07:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0047_partnerbranch_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='partnerbranch',
            name='user',
        ),
    ]