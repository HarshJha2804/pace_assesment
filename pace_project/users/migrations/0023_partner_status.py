# Generated by Django 4.2.11 on 2024-07-26 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0022_student_assessment_status_student_english_test_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='status',
            field=models.CharField(choices=[('new', 'New'), ('follow-up', 'Follow-up'), ('not-interested', 'Not Interested'), ('interested', 'Interested')], default='new', max_length=30),
        ),
    ]