# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-13 12:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('upload', '0009_sdesign'),
    ]

    operations = [
        migrations.AddField(
            model_name='stud',
            name='rollno',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
    ]
