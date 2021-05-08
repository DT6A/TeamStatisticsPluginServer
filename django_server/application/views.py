from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User


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


class TrackedListView(ListView):
    model = User
    context_object_name = 'users'
    template_name = 'application/tracked_list.html'

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(profile__employer_key=user.profile.ref_key).order_by('username')