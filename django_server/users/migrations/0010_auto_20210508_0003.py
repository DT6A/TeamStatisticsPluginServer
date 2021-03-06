# Generated by Django 3.1.7 on 2021-05-07 21:03

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_auto_20210507_1255'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userstat',
            name='lines_written',
        ),
        migrations.AddField(
            model_name='userstat',
            name='metrics',
            field=models.JSONField(default={}),
        ),
        migrations.AlterField(
            model_name='userstat',
            name='time_from',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 7, 21, 3, 49, 867296, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='userstat',
            name='time_to',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 7, 21, 3, 49, 867296, tzinfo=utc)),
        ),
    ]
