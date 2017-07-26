# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-07-26 02:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Credential',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_id', models.CharField(max_length=255)),
                ('client_secret', models.CharField(max_length=255)),
                ('grant_type', models.CharField(max_length=255)),
            ],
        ),
    ]
