# Generated by Django 5.1.6 on 2025-02-19 10:46

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_id', models.CharField(max_length=100)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('city', models.CharField(max_length=100)),
                ('street_name', models.CharField(max_length=100)),
                ('street_no', models.CharField(max_length=10)),
                ('local', models.CharField(blank=True, max_length=100, null=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20)),
            ],
        ),
        migrations.DeleteModel(
            name='ActiveClient',
        ),
        migrations.DeleteModel(
            name='OfficialAddress',
        ),
    ]
