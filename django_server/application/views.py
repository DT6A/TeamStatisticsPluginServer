from datetime import datetime, timedelta

from django.apps import apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.db import models
from django.db.models import Sum
from django.db.models.functions import Cast
from django.shortcuts import redirect, render
from django.views.generic import ListView, DetailView

from .forms import TeamForm, TeamJoinForm

Profile = apps.get_model('users', 'Profile')
Team = apps.get_model('users', 'Team')
UserStat = apps.get_model('users', 'UserStat')


class ProfileListView(ListView):
    model = User
    context_object_name = 'users'
    template_name = 'application/profile_list.html'

    def get_queryset(self):
        return sorted(User.objects.all(), key=lambda x: -x.profile.stats_for_all_time)


class UserDetailView(DetailView):
    model = User
    context_object_name = 'object'
    template_name = 'application/profile_detail.html'


class TeamListView(ListView):
    model = User
    context_object_name = 'teams'
    template_name = 'application/teams_list.html'

    def get_queryset(self):
        user = self.request.user
        return user.team_admin.all() | user.team_user.all()


def extract_metric(filtered, metric):
    return filtered.annotate(metric_value=Cast(KeyTextTransform(metric, 'metrics'), models.IntegerField())).aggregate(
        Sum('metric_value'))['metric_value__sum']


def aggregate_metric_all_time(user, metric):
    s = extract_metric(UserStat.objects.filter(user=user), metric)
    return s if s else 0


def aggregate_metric_within_delta(user, metric, delta):
    s = extract_metric(UserStat.objects.filter(user=user, time_from__gte=datetime.now() - delta), metric)
    return s if s else 0


class TeamDetailView(DetailView):
    model = Team
    context_object_name = 'object'
    template_name = 'application/team_detail.html'

    METRICS_DICT = {
            'lines': 'Lines of code',
            'SUBSTRING_COUNTING__coq': 'coq substrings',
        }

    PERIODS_DICT = {
            'all': 'All time',
            "365": 'Year',
            "30": 'Month',
            "7": 'Week',
            "1": 'Day',
        }

    def add_metrics_options(self, context):
        context['metrics'] = self.METRICS_DICT
        context['periods'] = self.PERIODS_DICT
        return context

    def add_is_admin(self, team, context):
        user = self.request.user
        if team.admins.all().filter(pk=user.id).exists():
            context['is_admin'] = True
        else:
            context['is_admin'] = False
        return context

    @staticmethod
    def add_users_sats(team, metric_getter, context):
        users = team.admins.all() | team.users.all()
        context['dict'] = {}
        for user in users:
            context['dict'][user.username] = metric_getter(user)
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_metrics_options(context)
        context = self.add_is_admin(self.object, context)
        context = self.add_users_sats(self.object, lambda u: u.profile.stats_for_all_time, context)
        context['default_period'] = 'all'
        context['default_metric'] = 'lines'
        context['default_metric_text'] = self.METRICS_DICT['lines']

        return context

    def post(self, request, *args, **kwargs):
        team = Team.objects.get(pk=request.POST['target_team_id'])
        metric = request.POST.get('metrics', 'lines')
        interval = request.POST.get('time', 'all')

        context = {}
        context = self.add_metrics_options(context)
        context = self.add_is_admin(team, context)

        if interval == 'all':
            extracter = lambda u: aggregate_metric_all_time(u, metric)
        else:
            extracter = lambda u: aggregate_metric_within_delta(u, metric, timedelta(days=int(interval)))
        context = self.add_users_sats(team, extracter, context)

        context['object'] = team
        context['default_period'] = request.POST.get('time', 'all')
        context['default_metric'] = request.POST.get('metrics', 'lines')
        context['default_metric_text'] = self.METRICS_DICT[context['default_metric']]
        if request.POST['query'] == 'admin':
            user = User.objects.get(pk=request.POST['target_user_id'])
            team.users.remove(user)
            team.admins.add(user)
        return render(request, 'application/team_detail.html', context)


@login_required
def create_team(request):
    if request.method == 'POST':
        form = TeamForm(request.POST)

        if form.is_valid():
            team = form.save()

            team.admins.add(request.user)
            team.save()

            messages.success(request, f'Team \"{team.name}\" was created')
            return redirect('app-teams')
    else:
        form = TeamForm()

    return render(request, 'application/create_team.html', {'form': form})


@login_required
def join_team(request):
    if request.method == 'POST':
        form = TeamJoinForm(request.POST)

        if form.is_valid():
            key = form.cleaned_data['invite_key']

            if Team.objects.filter(invite_key=key).exists():
                team = Team.objects.get(invite_key=key)
                if team.admins.all().filter(pk=request.user.id).exists() or team.users.all().filter(pk=request.user.id).exists():
                    form.add_error('invite_key', 'You are already a member of the team')
                    return render(request, 'application/join_team.html', {'form': form})

            else:
                form.add_error('invite_key', 'Invalid key')
                return render(request, 'application/join_team.html', {'form': form})

            team.users.add(request.user)
            messages.success(request, f'You joined to \"{team.name}\" team')
            return redirect('app-teams')
    else:
        form = TeamJoinForm()
        form.fields['invite_key'].initial = ""

    return render(request, 'application/join_team.html', {'form': form})
