# Generated by Django 4.2.11 on 2024-11-15 09:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('paceapp', '0043_course_link_course_scholarship_course_tuition_fees'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0049_updatenews'),
    ]

    operations = [
        migrations.CreateModel(
            name='Webinar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('agenda', models.CharField(blank=True, max_length=255, null=True, verbose_name='Agenda ')),
                ('webinar_for', models.CharField(choices=[('Internal Team', 'Internal Team'), ('Partner', 'Partner')], default='Internal Team', max_length=100)),
                ('medium', models.CharField(choices=[('zoom', 'Zoom'), ('microsoft teams', 'Microsoft Teams')], default='zoom', max_length=100)),
                ('schedule', models.DateTimeField()),
                ('meeting_link', models.TextField(blank=True, null=True)),
                ('remark', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_webinar', to=settings.AUTH_USER_MODEL)),
                ('university', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='webinar', to='paceapp.university')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]