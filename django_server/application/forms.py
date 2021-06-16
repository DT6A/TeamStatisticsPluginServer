from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from django.apps import apps

Team = apps.get_model('users', 'Team')
Metric = apps.get_model('users', 'Metric')
CharCountingMetric = apps.get_model('users', 'CharCountingMetric')
SubstringCountingMetric = apps.get_model('users', 'SubstringCountingMetric')
WordCountingMetric = apps.get_model('users', 'WordCountingMetric')
Achievement = apps.get_model('users', 'Achievement')
SpecificLengthPasteCounterMetric = apps.get_model('users', 'SpecificLengthPasteCounterMetric')
SpecificLengthCopyCounterMetric = apps.get_model('users', 'SpecificLengthPasteCounterMetric')
SpecificBranchCommitCounterMetric = apps.get_model('users', 'SpecificBranchCommitCounterMetric')


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


class WordCountingMetricForm(ModelForm):
    class Meta:
        model = WordCountingMetric
        fields = ['word']


class SpecificLengthCopyCounterMetricForm(ModelForm):
    class Meta:
        model = SpecificLengthCopyCounterMetric
        fields = ['substring_length']


class SpecificLengthPasteCounterMetricForm(ModelForm):
    class Meta:
        model = SpecificLengthPasteCounterMetric
        fields = ['substring_length']


class SpecificBranchCommitCounterMetricForm(ModelForm):
    class Meta:
        model = SpecificBranchCommitCounterMetric
        fields = ['branch_name']


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
