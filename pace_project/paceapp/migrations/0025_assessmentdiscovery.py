# Generated by Django 4.2.11 on 2024-06-21 08:00

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_student_passport_number'),
        ('paceapp', '0024_board_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssessmentDiscovery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('is_processed', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('courses', models.ManyToManyField(to='paceapp.course')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.student')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]