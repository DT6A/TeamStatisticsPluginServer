from datetime import datetime, timedelta

from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.core.management.utils import get_random_secret_key
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, Model
from django.db.models.functions import Cast
from django.utils import timezone

from django.db.models.expressions import RawSQL, Func, F

from PIL import Image


class UserStat(models.Model):
    metrics = models.JSONField(default=dict)
    time_from = models.DateTimeField(default=timezone.now())
    time_to = models.DateTimeField(default=timezone.now())
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class UserUniqueToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, default=get_random_secret_key)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'

    @staticmethod
    def aggregate_lines(filtered):
        return filtered.annotate(lines_value=Cast(KeyTextTransform('lines', 'metrics'), models.IntegerField())).aggregate(Sum('lines_value'))['lines_value__sum']

    @property
    def stats_for_all_time(self):
        s = self.aggregate_lines(UserStat.objects.filter(user=self.user))
        return s if s else 0

    def lines_written_within_delta(self, delta):
        s = self.aggregate_lines(UserStat.objects.filter(user=self.user, time_from__gte=datetime.now() - delta))
        return s if s else 0

    @property
    def stats_for_last_year(self):
        return self.lines_written_within_delta(timedelta(days=365))

    @property
    def stats_for_last_month(self):
        return self.lines_written_within_delta(timedelta(days=30))

    @property
    def stats_for_last_week(self):
        return self.lines_written_within_delta(timedelta(days=7))

    @property
    def stats_for_last_day(self):
        return self.lines_written_within_delta(timedelta(days=1))


class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    users = models.ManyToManyField(User, related_name='team_user', blank=True)
    admins = models.ManyToManyField(User, related_name='team_admin')
    invite_key = models.CharField(max_length=100, default=get_random_secret_key)

    def __str__(self):
        return self.name
