from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView
from django.apps import apps

Profile = apps.get_model('users', 'Profile')


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.profile.employer_key:
            context['overseer'] = Profile.objects.get(ref_key=self.object.profile.employer_key).user
        return context


class TrackedListView(ListView):
    model = User
    context_object_name = 'users'
    template_name = 'application/tracked_list.html'

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(profile__employer_key=user.profile.ref_key).order_by('username')

