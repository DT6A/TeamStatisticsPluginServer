from datetime import datetime, timedelta

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils import timezone

from PIL import Image


class UserStat(models.Model):
    lines_written = models.IntegerField(default=0)
    time_from = models.DateTimeField(default=timezone.now())
    time_to = models.DateTimeField(default=timezone.now())
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'


    @property
    def stats_for_all_time(self):
        s = UserStat.objects.filter(user=self.user).aggregate(Sum('lines_written'))['lines_written__sum']
        return s if s else 0

    def lines_written_within_delta(self, delta):
        s = UserStat.objects.filter(user=self.user, time_from__gte=datetime.now() - delta) \
            .aggregate(Sum('lines_written'))['lines_written__sum']
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
