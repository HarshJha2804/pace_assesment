# Generated by Django 4.2.11 on 2024-09-09 06:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0033_alter_student_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='owner_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='partner',
            name='owner_mobile_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='partner',
            name='owner_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]