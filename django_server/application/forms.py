from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from django.apps import apps

Team = apps.get_model('users', 'Team')
Metric = apps.get_model('users', 'Metric')
CharCountingMetric = apps.get_model('users', 'CharCountingMetric')
SubstringCountingMetric = apps.get_model('users', 'SubstringCountingMetric')
Achievement = apps.get_model('users', 'Achievement')


class TeamForm(ModelForm):
    class Meta:
        model = Team
        fields = ['name']


class CharCountingMetricForm(ModelForm):
    class Meta:
        model = CharCountingMetric
        fields = ['char']


class SubstringCountingMetricForm(ModelForm):
    class Meta:
        model = SubstringCountingMetric
        fields = ['substring']


class AchievementForm(ModelForm):
    class Meta:
        model = Achievement
        fields = ['name']


class AchievementMetricForm(forms.Form):
    metric = forms.ModelChoiceField(queryset=Metric.objects.all(), required=True)
    goal = forms.IntegerField()


class TeamJoinForm(ModelForm):
    class Meta:
        model = Team
        fields = ['invite_key']
