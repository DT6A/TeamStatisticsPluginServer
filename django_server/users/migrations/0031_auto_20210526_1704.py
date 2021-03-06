# Generated by Django 3.1.7 on 2021-05-26 14:04

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0030_auto_20210525_1257'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='tracked_metrics',
            field=models.ManyToManyField(blank=True, related_name='metrics', to='users.Metric'),
        ),
        migrations.AlterField(
            model_name='userstat',
            name='time_from',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 26, 14, 4, 36, 378818, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='userstat',
            name='time_to',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 26, 14, 4, 36, 378818, tzinfo=utc)),
        ),
    ]
