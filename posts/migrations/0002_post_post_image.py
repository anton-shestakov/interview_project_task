# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-05 13:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='post_image',
            field=models.ImageField(default='media/images/no-img.png', upload_to='media/images/'),
        ),
    ]
