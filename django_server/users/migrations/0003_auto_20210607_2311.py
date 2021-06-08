# Generated by Django 3.1.7 on 2021-06-07 20:11

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20210607_2310'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userstat',
            name='time_from',
            field=models.DateTimeField(default=datetime.datetime(2021, 6, 7, 20, 11, 0, 164189, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='userstat',
            name='time_to',
            field=models.DateTimeField(default=datetime.datetime(2021, 6, 7, 20, 11, 0, 164212, tzinfo=utc)),
        ),
    ]