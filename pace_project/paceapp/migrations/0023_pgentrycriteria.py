# Generated by Django 4.2.11 on 2024-05-27 05:38

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('paceapp', '0022_entrycriteria_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='PGEntryCriteria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('twelfth_english_marks', models.IntegerField(blank=True, null=True)),
                ('diploma_overall_marks', models.IntegerField(blank=True, null=True)),
                ('ug_overall_marks', models.IntegerField(blank=True, null=True)),
                ('level_diploma_marks', models.IntegerField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('board', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='paceapp.board')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='paceapp.country')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='paceapp.course')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]