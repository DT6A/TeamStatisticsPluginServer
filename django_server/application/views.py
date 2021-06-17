import json
from datetime import datetime, timedelta

import pandas as pd
from django.apps import apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.db import models
from django.db.models import Sum
from django.db.models.functions import Cast
from django.forms import formset_factory
from django.http import HttpResponseNotFound, Http404
from django.shortcuts import redirect, render, HttpResponse
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, DetailView
from plotly.graph_objs import Scatter
from plotly.offline import plot

from .forms import *

# Getting models
Profile = apps.get_model('users', 'Profile')
Team = apps.get_model('users', 'Team')
UserStat = apps.get_model('users', 'UserStat')
Metric = apps.get_model('users', 'Metric')
Achievement = apps.get_model('users', 'Achievement')
FeedMessage = apps.get_model('users', 'FeedMessage')

# Mapping time interval to text representation
PERIODS_DICT = {
    'all': 'All time',
    "365": 'Year',
    "30": 'Month',
    "7": 'Week',
    "1": 'Day',
}


def extract_metric(filtered, metric):
    """
    Returns the sum of metric values.

            Parameters:
                    filtered: Filtered statistic notes
                    metric: Target metric

            Returns:
                    Sum of metric values
    """
    return filtered.annotate(metric_value=Cast(KeyTextTransform(metric, 'metrics'), models.IntegerField())).aggregate(
        Sum('metric_value'))['metric_value__sum']


def aggregate_metric_all_time(user, metric):
    """
    Returns the sum of metric values collected over the all time for the given user.

            Parameters:
                    user: Target user
                    metric: Target metric

            Returns:
                    Sum of metric values of the given user
    """
    s = extract_metric(UserStat.objects.filter(user=user), metric)
    return s if s else 0


def aggregate_metric_within_delta(user, metric, delta):
    """
    Returns the sum of metric values collected from given time point to the current time for the given user.

            Parameters:
                    user: Target user
                    metric: Target metric
                    delta: Time delta

            Returns:
                    Sum of metric values of the given user within required time interval
    """
    s = extract_metric(UserStat.objects.filter(user=user, time_from__gte=datetime.now() - delta), metric)
    return s if s else 0


def aggregate_metric_within_interval(user, metric, left, right):
    """
    Returns the sum of metric values collected within given time time for the given user.

            Parameters:
                    user: Target user
                    metric: Target metric
                    left: Left bound
                    right: Right bound

            Returns:
                    Sum of metric values of the given user within required time interval
    """
    s = extract_metric(UserStat.objects.filter(user=user, time_from__gte=left, time_from__lte=right), metric)
    return s if s else 0


def get_team_metrics(team):
    """
    Returns all metrics tracked in the team.

            Parameters:
                    team: Target team

            Returns:
                Dictionary of tracked metrics, key -- metric name, value -- metric string representation for the
            interface
    """
    return dict({'lines': 'Lines of code'}, **{
        name: str(team.tracked_metrics.get(name=name)) for name in
        team.tracked_metrics.all().values_list('name', flat=True)
    })


def get_user_metrics(user):
    """
    Returns all metrics tracked of user.

            Parameters:
                    user: Target user

            Returns:
                List of metrics name
    """
    teams = user.team_user.all() | user.team_admin.all()
    all_metrics = []
    for team in teams:
        team_metrics_names = get_team_metrics(team).keys()
        all_metrics += team_metrics_names
    return list(set(all_metrics))


def get_user_incomplete_achievements(user):
    """
        Returns incomplete achievements tracked by user.

                Parameters:
                        user: Target user

                Returns:
                    List of incomplete achievements name
    """
    return user.unfinished_achievements.all()


class ProfileListView(ListView):
    """
    A view for list of users

    Attributes:
    ----------
    model :
        Target model
    context_object_name :
        Name of user profile object used within template
    template_name :
        Path to the template
    """
    model = User
    context_object_name = 'users'
    template_name = 'application/profile_list.html'

    def get_queryset(self):
        """
        Form the query set for request

                Returns:
                     Query set with users sorted by number of lines of code the have written
        """
        return sorted(User.objects.all(), key=lambda x: -x.profile.stats_for_all_time)


def get_all_metrics_dict():
    """
    Returns all available metrics

            Returns:
                    Dictionary of all metrics, key -- metric name, value -- metric string representation for the
            interface
    """
    return dict({'lines': 'Lines of code'}, **{
        name: str(Metric.objects.get(name=name)) for name in Metric.objects.all().values_list('name', flat=True)
    })


def update_achievements(user):
    """
    Update completed achievements for user
    """

    incomplete_achievements = get_user_incomplete_achievements(user)
    for achieve in incomplete_achievements:
        completed = True
        for name, goal in achieve.metric_to_goal.items():
            current = aggregate_metric_all_time(user, name)
            if current < goal:
                completed = False
        if completed:
            achieve.assigned_users.remove(user)
            achieve.completed_users.add(user)
            achieve.save()


class UserDetailView(DetailView):
    """
    A view for showing detailed information about the user

    Attributes:
    ----------
    model :
        Target model
    context_object_name :
        Name of user object used within template
    template_name :
        Path to the template
    """
    model = User
    context_object_name = 'object'
    template_name = 'application/profile_detail.html'

    @staticmethod
    def add_finished_achievements(user, context):
        context['finished_achievements'] = user.finished_achievements.all()
        return context

    def get_context_data(self, **kwargs):
        """
        Fills request context

                Returns:
                        Filled context
        """
        context = super().get_context_data(**kwargs)
        context = self.add_metrics_options(self.object, context)
        context['metric_text'] = 'Lines of code'
        context['metric_value'] = aggregate_metric_within_delta(self.object, 'lines', timedelta(days=int(30)))
        context['default_period'] = '30'
        context['default_metric'] = 'lines'
        context['default_metric_text'] = 'Lines of code' if context['default_metric'] == 'lines' else str(
            Metric.objects.get(name=context['default_metric']))
        context['achievement_l'] = Achievement.objects.all().filter(
            id__in=self.request.user.unfinished_achievements.all())
        context = self.add_finished_achievements(self.request.user, context)
        return context

    @staticmethod
    def add_metrics_options(user, context):
        """
        Modifies context with available metrics and time periods

                Returns:
                        Modified context
        """
        context['metrics'] = user.profile.get_metrics()
        context['metrics_l'] = dict(context['metrics'])
        del context['metrics_l']['lines']
        untracked_qs = Metric.objects.exclude(name__in=list(context['metrics_l'].keys()))
        context['untracked'] = {
            name: str(untracked_qs.get(name=name)) for name in untracked_qs.values_list('name', flat=True)
        }
        context['periods'] = PERIODS_DICT
        return context

    def post(self, request, *args, **kwargs):
        """
        Process post request

                Parameters:
                    request: Request to process

                Returns:
                        Rendered view
        """
        metric = request.POST.get('metrics', 'lines')
        if request.POST.get('query', None) == "update_achievements":
            user = request.user
            update_achievements(user)
        interval = request.POST.get('time', 'all')
        user = request.POST.get('user_id', None)
        context = {'object': User.objects.get(pk=user)}

        if interval == 'all':
            context['metric_value'] = aggregate_metric_all_time(user, metric)
        else:
            context['metric_value'] = aggregate_metric_within_delta(user, metric, timedelta(days=int(interval)))

        query = request.POST.get('query', None)
        if query == 'add_metric' and request.POST.get('metrics_add', None):
            context['object'].profile.add_metric(request.POST['metrics_add'])
        elif query == 'rm_metric' and request.POST.get('metrics_rm', None):
            context['object'].profile.remove_metric(request.POST['metrics_rm'])
        elif query == 'rm_achievement' and request.POST.get('achievement_rm', None):
            achievement = Achievement.objects.get(name=request.POST.get('achievement_rm', None))
            achievement.assigned_users.remove(user)

        context = self.add_metrics_options(context['object'], context)
        context['metric_text'] = 'Lines of code' if metric == 'lines' else str(Metric.objects.get(name=metric))

        context['default_period'] = request.POST.get('time', '30')
        context['default_metric'] = request.POST.get('metrics', 'lines')
        context['achievement_l'] = Achievement.objects.all().filter(id__in=request.user.unfinished_achievements.all())
        context['default_metric_text'] = 'Lines of code' if context['default_metric'] == 'lines' else str(
            Metric.objects.get(name=context['default_metric']))
        context = self.add_finished_achievements(self.request.user, context)
        return render(request, 'application/profile_detail.html', context)


class TeamListView(ListView):
    """
    A view for showing list of teams the user belongs to

    Attributes:
    ----------
    model :
        Target model
    context_object_name :
        Name of teams list object used within template
    template_name :
        Path to the template
    """
    model = User
    context_object_name = 'teams'
    template_name = 'application/teams_list.html'

    def get_queryset(self):
        """
        Form a query set

                Returns:
                        Query set with commands the user belongs to
        """
        user = self.request.user
        return (user.team_admin.all() | user.team_user.all()).distinct()


class TeamDetailView(DetailView):
    """
    A view for showing detailed information about the team

    Attributes:
    ----------
    model :
        Target model
    context_object_name :
        Name of team object used within template
    template_name :
        Path to the template
    """
    model = Team
    context_object_name = 'object'
    template_name = 'application/team_detail.html'

    @staticmethod
    def add_metrics_options(team, context):
        """
        Modifies context with metrics tracked by the team and time periods

                Parameters:
                        team: Target team
                        context: Context to modify
                Returns:
                        Modified context
        """
        context['metrics'] = team.get_team_metrics()
        context['periods'] = PERIODS_DICT
        return context

    def add_is_admin(self, team, context):
        """
        Adds to context information whether the user is administrator

                Parameters:
                        team: Target team
                        context: Context to modify
                Returns:
                        Modified context
        """
        user = self.request.user
        if team.admins.all().filter(pk=user.id).exists():
            context['is_admin'] = True
        else:
            context['is_admin'] = False
        return context

    @staticmethod
    def add_users_sats(team, metric_getter, context):
        """
        Modifies context with data about team members metrics

                Parameters:
                        team: Target team
                        metric_getter: Method to gain metric
                        context: Context to modify
                Returns:
                        Modified context
        """
        users = team.admins.all() | team.users.all()
        context['dict'] = {}
        for user in users:
            context['dict'][user.username] = metric_getter(user)
        return context

    @staticmethod
    def add_plot(metric, interval, context):
        """
        Modifies context with team members metrics plot

                Parameters:
                        metric: Target metric
                        interval: Time interval to obtain data within
                        context: Context to modify
                Returns:
                        Modified context
        """
        plots = []
        team = context['object']

        for user in team.admins.all() | team.users.all():
            if interval != 1:
                date_data = [(datetime.now() - timedelta(days=int(i))).date() for i in range(interval)]
                date_y = [aggregate_metric_within_interval(user,
                                                           metric,
                                                           datetime.now() - timedelta(days=i),
                                                           datetime.now() - timedelta(days=i - 1))
                          for i in range(1, interval + 1)]
            else:
                date_data = [(datetime.now() - timedelta(hours=int(i))) for i in range(24)]
                date_y = [aggregate_metric_within_interval(user,
                                                           metric,
                                                           datetime.now() - timedelta(hours=i),
                                                           datetime.now() - timedelta(hours=i - 1))
                          for i in range(1, 25)]

            name = user.first_name + " " + user.last_name if user.first_name or user.last_name else user.username
            fig = Scatter(x=date_data, y=date_y,
                          mode='lines', name=name,
                          opacity=0.5,
                          )
            plots.append(fig)

        if interval != 1:
            date_data = [(datetime.now() - timedelta(days=int(i))).date() for i in range(interval)]
            date_y = [context['threshold'] for _ in range(1, interval + 1)]
        else:
            date_data = [(datetime.now() - timedelta(hours=int(i))) for i in range(24)]
            date_y = [context['threshold'] for _ in range(1, 25)]

        fig = Scatter(x=date_data, y=date_y,
                      mode='lines', name="THRESHOLD",
                      opacity=1, marker_color='red'
                      )
        plots.append(fig)

        plot_div = plot({
            'data': plots,
            'layout': {'title': 'Stats', 'xaxis': {'title': 'Time'}, 'yaxis': {'title': context['metrics'][metric]}}
        },
            output_type='div', include_plotlyjs=False, show_link=False, link_text="")
        context['plot_div'] = plot_div
        return context

    def get_context_data(self, **kwargs):
        """
        Fills request context

                Returns:
                        Filled context
        """
        if self.request.user not in self.object.admins.all() | self.object.users.all():
            raise Http404

        context = super().get_context_data(**kwargs)
        context = self.add_metrics_options(self.object, context)
        context = self.add_is_admin(self.object, context)
        context = self.add_users_sats(self.object,
                                      lambda u: aggregate_metric_within_delta(u, 'lines', timedelta(days=int(30))),
                                      context)
        context['object'] = self.object
        context['default_period'] = '30'
        context['default_metric'] = 'lines'
        context['default_metric_text'] = get_all_metrics_dict()['lines']
        context['threshold'] = 400
        context = self.add_plot('lines', 30, context)

        return context

    def post(self, request, *args, **kwargs):
        """
        Process post request

                Parameters:
                    request: Request to process

                Returns:
                        Rendered view
        """
        team = Team.objects.get(pk=request.POST['target_team_id'])
        if request.user not in team.admins.all() | team.users.all():
            raise Http404
        metric = request.POST.get('metrics', 'lines')
        interval = request.POST.get('time', '30')

        context = {}
        context = self.add_metrics_options(team, context)
        context = self.add_is_admin(team, context)

        if interval == 'all':
            extracter = lambda u: aggregate_metric_all_time(u, metric)
        else:
            extracter = lambda u: aggregate_metric_within_delta(u, metric, timedelta(days=int(interval)))
        context = self.add_users_sats(team, extracter, context)

        context['object'] = team
        context['default_period'] = request.POST.get('time', 'all')
        context['default_metric'] = request.POST.get('metrics', 'lines')
        context['default_metric_text'] = team.get_team_metrics()[context['default_metric']]
        context['threshold'] = int(request.POST.get('threshold', 400))

        if interval == 'all':
            context = self.add_plot(metric, 365, context)
        else:
            context = self.add_plot(metric, int(interval), context)
        return render(request, 'application/team_detail.html', context)

    @staticmethod
    @login_required
    def administrate_team(request, pk):
        """
        View function for team administration

                Parameters:
                        request: Request to process
                        pk: Target team id

                Returns:
                        Rendered view
        """
        team = Team.objects.get(pk=pk)
        user = request.user
        if not team.admins.all().filter(pk=user.id).exists():
            return HttpResponseNotFound("You are not an administrator of the team")

        context = {'object': team}

        if request.method == 'POST':
            query = request.POST.get('query', None)

            if query == 'admin':
                user = User.objects.get(pk=request.POST['target_user_id'])
                FeedMessage(sender=team.name, receiver=user,
                            msg_content=f"You are now admin of \"{team.name}\" team", created_at=timezone.now()).save()
                for admin in team.admins.all():
                    FeedMessage(sender=team.name, receiver=admin,
                                msg_content=f"{user.username} is now an admin of \"{team.name}\" team",
                                created_at=timezone.now()).save()
                team.users.remove(user)
                team.admins.add(user)
            elif query == 'remove':
                user = User.objects.get(pk=request.POST['target_user_id'])
                team.users.remove(user)
                FeedMessage(sender=team.name, receiver=user,
                            msg_content=f"You have been removed from \"{team.name}\" team",
                            created_at=timezone.now()).save()
                for admin in team.admins.all():
                    FeedMessage(sender=team.name, receiver=admin,
                                msg_content=f"{user.username} was removed from \"{team.name}\" team",
                                created_at=timezone.now()).save()
            elif query == 'add_metric' and request.POST.get('metrics_add', None):
                metric = Metric.objects.get(name=request.POST['metrics_add'])
                team.tracked_metrics.add(metric)
                team.save()
                for u in team.users.all() | team.admins.all():
                    FeedMessage(sender=team.name, receiver=u,
                                msg_content=f"{str(metric)} is now tracked in \"{team.name}\" team",
                                created_at=timezone.now()).save()
                    u.profile.add_metric(request.POST['metrics_add'])
            elif query == 'rm_metric' and request.POST.get('metrics_rm', None):
                metric = Metric.objects.get(name=request.POST['metrics_rm'])
                team.tracked_metrics.remove(metric)
                team.save()
                for u in team.users.all() | team.admins.all():
                    FeedMessage(sender=team.name, receiver=u,
                                msg_content=f"{str(metric)} is not tracked anymore in \"{team.name}\" team",
                                created_at=timezone.now()).save()

        context = TeamDetailView.add_metrics_options(team, context)
        del context['metrics']['lines']
        untracked_qs = Metric.objects.exclude(name__in=list(context['metrics'].keys()))
        context['untracked'] = {
            name: str(untracked_qs.get(name=name)) for name in untracked_qs.values_list('name', flat=True)
        }

        return render(request, 'application/team_administration.html', context)


@login_required
def create_team(request):
    """
    View function for team creation

            Parameters:
                    request: Request to process

            Returns:
                    Rendered view
    """
    if request.method == 'POST':
        form = TeamForm(request.POST)

        if form.is_valid():
            team = form.save()

            team.admins.add(request.user)
            team.save()

            messages.success(request, f'Team \"{team.name}\" was created')
            FeedMessage(sender=team.name, receiver=request.user, msg_content=f"You have created \"{team.name}\" team",
                        created_at=timezone.now()) \
                .save()
            return redirect('app-teams')
    else:
        form = TeamForm()

    return render(request, 'application/create_with_form.html', {'form': form, 'target': 'team'})


@login_required
def join_team(request):
    """
    View function for team joining

            Parameters:
                    request: Request to process

            Returns:
                    Rendered view
    """
    if request.method == 'POST':
        form = TeamJoinForm(request.POST)

        if form.is_valid():
            key = form.cleaned_data['invite_key']

            if Team.objects.filter(invite_key=key).exists():
                team = Team.objects.get(invite_key=key)
                if team.admins.all().filter(pk=request.user.id).exists() or team.users.all().filter(
                        pk=request.user.id).exists():
                    form.add_error('invite_key', 'You are already a member of the team')
                    return render(request, 'application/join_team.html', {'form': form})

            else:
                form.add_error('invite_key', 'Invalid key')
                return render(request, 'application/join_team.html', {'form': form})

            team.users.add(request.user)
            FeedMessage(sender=team.name, receiver=request.user, msg_content=f"You have joined \"{team.name}\" team",
                        created_at=timezone.now()) \
                .save()
            for admin in team.admins.all():
                FeedMessage(sender=team.name, receiver=admin,
                            msg_content=f"{request.user.username} joined \"{team.name}\" team",
                            created_at=timezone.now()) \
                    .save()
            messages.success(request, f'You joined to \"{team.name}\" team')

            for tm in team.get_team_metrics():
                if tm != 'lines':
                    request.user.profile.add_metric(tm)

            return redirect('app-teams')
    else:
        form = TeamJoinForm()
        form.fields['invite_key'].initial = ""

    return render(request, 'application/join_team.html', {'form': form})


@login_required
def team_to_csv(request, pk):
    """
    View function for downloading csv file with statistics about all users from the team

            Parameters:
                    request: Request to process
                    pk: Team id

            Returns:
                    Rendered view
    """
    team = Team.objects.get(pk=pk)
    users = team.users.all() | team.admins.all()

    data = json.dumps([{'user': o.user.username,
                        'metrics': o.metrics,
                        'time_from': str(o.time_from),
                        'time_to': str(o.time_to)}
                       for o in list(UserStat.objects.filter(user__in=users))])
    df = pd.read_json(data)
    metrics_df = pd.json_normalize(df['metrics'])
    del df['metrics']
    df = pd.concat([df, metrics_df], axis=1)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={team.name}.csv'
    df.to_csv(path_or_buf=response, sep=';', float_format='%.2f', index=False, decimal=",")
    return response


class FeedMessageListView(ListView):
    """
    User feed view

    Attributes
    ----------
    model :
        Target model
    context_object_name :
        Name of user profile object used within template
    template_name :
        Path to the template
    ordering :
        Order to list objects
    """
    model = FeedMessage
    context_object_name = 'feed_messages'
    template_name = 'application/feed.html'
    paginate_by = 15

    def get_queryset(self):
        """
        Form the query set for request

                Returns:
                     Query set with users sorted by number of lines of code the have written
        """
        return FeedMessage.objects.filter(receiver=self.request.user).order_by('-created_at', '-created_at__second')


@login_required
def contribute(request):
    """
    View function for contribution page

            Parameters:
                    request: Request to process

            Returns:
                    Rendered view
    """
    return render(request, 'application/contribution_navigation.html', {})


@login_required
def create_char_metric(request):
    """
    View function for character metric creation

            Parameters:
                    request: Request to process

            Returns:
                    Rendered view
    """
    if request.method == 'POST':
        form = CharCountingMetricForm(request.POST)

        if form.is_valid():
            metric = form.save()

            metric.name = 'CharCounter(' + metric.char + ')'
            metric.save()

            messages.success(request, f'Metric was created')
            FeedMessage(sender=metric.name, receiver=request.user,
                        msg_content=f"You have created \"{metric.char}\" tracking metric",
                        created_at=timezone.now()) \
                .save()
            return redirect('app-contribute')
    else:
        form = CharCountingMetricForm()

    return render(request, 'application/create_with_form.html', {'form': form, 'target': 'char counting metric'})


@login_required
def create_substring_metric(request):
    """
    View function for substring metric creation

            Parameters:
                    request: Request to process

            Returns:
                    Rendered view
    """
    if request.method == 'POST':
        form = SubstringCountingMetricForm(request.POST)

        if form.is_valid():
            metric = form.save()

            metric.name = 'WordCounter(' + metric.substring + ')'
            metric.save()

            messages.success(request, f'Metric was created')
            FeedMessage(sender=metric.name, receiver=request.user,
                        msg_content=f"You have created \"{metric.substring}\" tracking metric",
                        created_at=timezone.now()) \
                .save()
            return redirect('app-contribute')
    else:
        form = SubstringCountingMetricForm()

    return render(request, 'application/create_with_form.html', {'form': form, 'target': 'substring counting metric'})


@login_required
def create_paste_metric(request):
    """
    View function for paste metric creation

            Parameters:
                    request: Request to process

            Returns:
                    Rendered view
    """
    if request.method == 'POST':
        form = SpecificLengthPasteCounterMetricForm(request.POST)

        if form.is_valid():
            if form.cleaned_data['substring_length'] <= 0:
                messages.warning(request, f'Length must be positive')
                return render(request, 'application/create_with_form.html',
                              {'form': form, 'target': 'paste metric'})
            metric = form.save()

            metric.name = 'SpecificLengthPasteCounter(' + str(metric.substring_length) + ')'
            # metric.string_representation = "SpecificLengthPasteCounter"
            metric.save()

            messages.success(request, f'Metric was created')
            FeedMessage(sender=metric.name, receiver=request.user,
                        msg_content=f"You have created metric which tracks pastes of length {metric.substring_length}",
                        created_at=timezone.now()) \
                .save()
            return redirect('app-contribute')
    else:
        form = SpecificLengthPasteCounterMetricForm()

    return render(request, 'application/create_with_form.html', {'form': form, 'target': 'paste metric'})


@login_required
def create_copy_metric(request):
    """
    View function for copy metric creation

            Parameters:
                    request: Request to process

            Returns:
                    Rendered view
    """
    if request.method == 'POST':
        form = SpecificLengthCopyCounterMetricForm(request.POST)

        if form.is_valid():
            if form.cleaned_data['substring_length'] <= 0:
                messages.warning(request, f'Length must be positive')
                return render(request, 'application/create_with_form.html',
                              {'form': form, 'target': 'copy metric'})
            print("Before saving")
            metric = form.save()
            print("After saving")

            metric.name = 'SpecificLengthCopyCounter(' + str(metric.substring_length) + ')'
            # metric.string_representation = f"SpecificLengthCopyCounter  {metric.substring_length}"
            metric.save()

            messages.success(request, f'Metric was created')
            FeedMessage(sender=metric.name, receiver=request.user,
                        msg_content=f"You have created metric which tracks copies of length {metric.substring_length}",
                        created_at=timezone.now()) \
                .save()
            return redirect('app-contribute')
    else:
        form = SpecificLengthCopyCounterMetricForm()

    return render(request, 'application/create_with_form.html', {'form': form, 'target': 'copy metric'})


@login_required
def create_branch_metric(request):
    """
    View function for branch tracking metric creation

            Parameters:
                    request: Request to process

            Returns:
                    Rendered view
    """
    if request.method == 'POST':
        form = SpecificBranchCommitCounterMetricForm(request.POST)

        if form.is_valid():
            metric = form.save()

            metric.name = '_'.join(metric.branch_name.split()) + '_BRANCH_METRIC'
            metric.save()

            messages.success(request, f'Metric was created')
            FeedMessage(sender=metric.name, receiver=request.user,
                        msg_content=f"You have created metric which tracks \"{metric.branch_name}\" branch",
                        created_at=timezone.now()) \
                .save()
            return redirect('app-contribute')
    else:
        form = SpecificBranchCommitCounterMetricForm()

    return render(request, 'application/create_with_form.html', {'form': form, 'target': 'branch commits counter metric'})


class CreateAchievementView(View):
    """
        Achievement creation view

        Attributes
        ----------
        goals_factory :
            Factory for creating multiple metrics goals
        template_name :
            Path to the template
    """
    goals_factory = formset_factory(AchievementMetricForm, min_num=1, validate_min=True)
    template_name = 'application/create_achievement.html'

    def get(self, request, *args, **kwargs):
        form = AchievementForm()
        return render(request, self.template_name, {'form': form, 'goal_forms': self.goals_factory()})

    def post(self, request, *args, **kwargs):
        form = AchievementForm(request.POST)
        goals = self.goals_factory(request.POST)

        if goals.is_valid() and form.is_valid():
            d = {}
            is_ok = True
            for goal in goals:
                metric = goal.cleaned_data['metric']
                number_goal = goal.cleaned_data['goal']
                if metric.name in d:
                    is_ok = False
                    messages.warning(request, f'Metric \"{metric}\" is repeated')
                if number_goal <= 0:
                    is_ok = False
                    messages.warning(request, f'Metric \"{metric}\" goal value must be positive')
                d[metric.name] = number_goal
            if is_ok:
                for goal in goals:
                    metric = goal.cleaned_data['metric']
                    if metric not in request.user.profile.tracked_metrics.all():
                        request.user.profile.tracked_metrics.add(metric)

                achieve = form.save()
                achieve.assigned_users.add(request.user)
                achieve.metric_to_goal = d
                achieve.save()

                messages.success(request, f'Achievement was created')
                FeedMessage(sender=achieve.name, receiver=request.user,
                            msg_content=f"You have created \"{achieve.name}\" achievement",
                            created_at=timezone.now()) \
                    .save()

                return redirect('app-contribute')

        context = {'form': form, 'goal_forms': goals}

        return render(request, self.template_name, context)


class AchievementDetailView(DetailView):
    """
    A view for showing detailed information about the achievement

    Attributes:
    ----------
    model :
        Target model
    context_object_name :
        Name of user object used within template
    template_name :
        Path to the template
    """
    model = Achievement
    context_object_name = 'object'
    template_name = 'application/achievement_detail.html'

    @staticmethod
    def add_achievement_goals_to_context(achievement, context):
        context['metric_to_goal'] = {
            'Lines of code written' if name == 'lines' else str(Metric.objects.get(name=name)):
                achievement.metric_to_goal[name] for name in
            achievement.metric_to_goal
        }
        return context

    @staticmethod
    def add_tracking_to_context(achievement, user, context):
        context['is_obtained'] = achievement in user.finished_achievements.all()
        context['is_tracked'] = (achievement in user.unfinished_achievements.all()) or context['is_obtained']
        return context

    def fill_context(self, achievement, user, context):
        context = self.add_achievement_goals_to_context(achievement, context)
        context = self.add_tracking_to_context(achievement, user, context)
        return context

    def get_context_data(self, **kwargs):
        """
        Fills request context

                Returns:
                        Filled context
        """
        context = super().get_context_data(**kwargs)
        context = self.fill_context(self.object, self.request.user, context)
        print(context)
        return context

    def post(self, request, *args, **kwargs):
        """
        Process post request

                Parameters:
                    request: Request to process

                Returns:
                        Rendered view
        """
        achievement = Achievement.objects.get(pk=request.POST.get('target_achievement_id', None))
        achievement.assigned_users.add(request.user)
        achievement.save()
        for metric_name in achievement.metric_to_goal:
            metric = Metric.objects.get(name=metric_name)
            if metric not in request.user.profile.tracked_metrics.all():
                request.user.profile.tracked_metrics.add(metric)
        context = {'object': achievement}
        context = self.fill_context(achievement, request.user, context)
        return render(request, self.template_name, context)


class AchievementListView(ListView):
    """
    A view for list of achivements

    Attributes:
    ----------
    model :
        Target model
    context_object_name :
        Name of user profile object used within template
    template_name :
        Path to the template
    """
    model = Achievement
    context_object_name = 'achievements'
    template_name = 'application/achievement_list.html'
    ordering = ['-id']
