from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from django.apps import apps

Team = apps.get_model('users', 'Team')


class TeamForm(ModelForm):
    class Meta:
        model = Team
        fields = ['name']


class TeamJoinForm(ModelForm):
    class Meta:
        model = Team
        fields = ['invite_key']
