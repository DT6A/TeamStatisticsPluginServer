# Generated by Django 3.1.7 on 2021-06-17 14:01

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0040_auto_20210615_0155'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpecificLengthCopyCounterMetric',
            fields=[
                ('metric_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='users.metric')),
                ('substring_length', models.IntegerField(unique=True)),
            ],
            bases=('users.metric',),
        ),
        migrations.CreateModel(
            name='SpecificLengthPasteCounterMetric',
            fields=[
                ('metric_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='users.metric')),
                ('substring_length', models.IntegerField(unique=True)),
            ],
            bases=('users.metric',),
        ),
        migrations.AlterField(
            model_name='feedmessage',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2021, 6, 17, 14, 1, 48, 64937, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='userstat',
            name='time_from',
            field=models.DateTimeField(default=datetime.datetime(2021, 6, 17, 14, 1, 48, 45012, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='userstat',
            name='time_to',
            field=models.DateTimeField(default=datetime.datetime(2021, 6, 17, 14, 1, 48, 45012, tzinfo=utc)),
        ),
        migrations.DeleteModel(
            name='SpecificLengthCopyPasteCounter',
        ),
    ]
