from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.generic import ListView, DetailView
from django.apps import apps
from django.contrib import messages

from .forms import TeamForm, TeamJoinForm

Profile = apps.get_model('users', 'Profile')
Team = apps.get_model('users', 'Team')


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


class TeamDetailView(DetailView):
    model = Team
    context_object_name = 'object'
    template_name = 'application/team_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if self.object.admins.all().filter(pk=user.id).exists():
            context['is_admin'] = True
        else:
            context['is_admin'] = False
        return context

    def post(self, request, *args, **kwargs):
        user = User.objects.get(pk=request.POST['target_user_id'])
        team = Team.objects.get(pk=request.POST['target_team_id'])
        team.users.remove(user)
        team.admins.add(user)

        return HttpResponseRedirect(self.request.path_info)


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