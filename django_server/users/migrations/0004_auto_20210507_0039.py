# Generated by Django 3.1.7 on 2021-05-06 21:39

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20210507_0037'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userstat',
            name='time_from',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 6, 21, 39, 20, 688568, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='userstat',
            name='time_to',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 6, 21, 39, 20, 688568, tzinfo=utc)),
        ),
    ]
