# Generated by Django 4.2.11 on 2024-07-24 10:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('meetcom', '0002_communicationtype'),
    ]

    operations = [
        migrations.CreateModel(
            name='Communication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('subject', models.CharField(max_length=200)),
                ('body', models.TextField(blank=True, null=True)),
                ('communication_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='meetcom.communicationtype')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='communications', to=settings.AUTH_USER_MODEL)),
                ('related_meeting', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='communications', to='meetcom.meeting')),
            ],
            options={
                'verbose_name': 'Communication',
                'verbose_name_plural': 'Communications',
            },
        ),
    ]