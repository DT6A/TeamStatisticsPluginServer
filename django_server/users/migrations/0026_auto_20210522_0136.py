# Generated by Django 3.1.7 on 2021-05-21 22:36

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0025_auto_20210521_2127'),
    ]

    operations = [
        migrations.CreateModel(
            name='Metric',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.AlterField(
            model_name='userstat',
            name='time_from',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 21, 22, 36, 6, 541577, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='userstat',
            name='time_to',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 21, 22, 36, 6, 541577, tzinfo=utc)),
        ),
        migrations.CreateModel(
            name='CharCountingMetric',
            fields=[
                ('metric_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='users.metric')),
                ('char', models.CharField(max_length=1, unique=True)),
            ],
            bases=('users.metric',),
        ),
        migrations.CreateModel(
            name='SubstringCountingMetric',
            fields=[
                ('metric_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='users.metric')),
                ('substring', models.CharField(max_length=100, unique=True)),
            ],
            bases=('users.metric',),
        ),
    ]
