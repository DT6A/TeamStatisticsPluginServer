# Generated by Django 3.1.7 on 2021-05-25 09:55

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0028_auto_20210523_2309'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userstat',
            name='time_from',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 25, 9, 55, 8, 161376, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='userstat',
            name='time_to',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 25, 9, 55, 8, 161376, tzinfo=utc)),
        ),
    ]
