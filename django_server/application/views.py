from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User


class ProfileListView(ListView):
    model = User
    context_object_name = 'users'
    template_name = 'application/profile_list.html'
