# Generated by Django 4.2.11 on 2024-10-24 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0040_partneronboardingrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='partneronboardingrequest',
            name='is_any_branch',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='partneronboardingrequest',
            name='number_of_branch',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='partneronboardingrequest',
            name='target_for_next_intake',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]