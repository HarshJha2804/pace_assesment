# Generated by Django 4.2.11 on 2024-08-03 11:30

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('paceapp', '0036_university_logo'),
        ('core', '0015_applicationstatuslog_created_by'),
    ]

    operations = [
        migrations.CreateModel(
            name='CountrySpecificDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('is_active', models.BooleanField(default=True)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='paceapp.country')),
                ('document_name', models.ManyToManyField(related_name='country_specific_documents', to='core.documenttemplate')),
            ],
            options={
                'indexes': [models.Index(fields=['country'], name='core_countr_country_658aae_idx')],
            },
        ),
    ]