# Generated by Django 4.2.11 on 2024-07-16 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_role_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='partnercommunication',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]