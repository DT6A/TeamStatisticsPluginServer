# Generated by Django 3.1.7 on 2021-06-08 15:20

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0032_auto_20210608_0940'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userstat',
            name='time_from',
            field=models.DateTimeField(default=datetime.datetime(2021, 6, 8, 15, 20, 50, 412079, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='userstat',
            name='time_to',
            field=models.DateTimeField(default=datetime.datetime(2021, 6, 8, 15, 20, 50, 412210, tzinfo=utc)),
        ),
    ]
