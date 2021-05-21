# Generated by Django 3.1.7 on 2021-05-21 18:27

import datetime
from django.conf import settings
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0024_auto_20210521_2109'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='admins',
            field=models.ManyToManyField(related_name='team_admin', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='team',
            name='users',
            field=models.ManyToManyField(blank=True, related_name='team_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='userstat',
            name='time_from',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 21, 18, 27, 23, 427592, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='userstat',
            name='time_to',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 21, 18, 27, 23, 427592, tzinfo=utc)),
        ),
    ]
