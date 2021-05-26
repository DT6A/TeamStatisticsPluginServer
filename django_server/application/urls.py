from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('', ProfileListView.as_view(), name='app-home'),
    path('teams/', login_required(TeamListView.as_view()), name='app-teams'),
    path('create_team/', create_team, name='app-create-team'),
    path('profile/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('team/<int:pk>/', login_required(TeamDetailView.as_view()), name='team-detail'),
    path('team/<int:pk>/administrate', TeamDetailView.administrate_team, name='team-administrate'),
    path('join_team', join_team, name='team-join'),
    path('team/<int:pk>/csv', team_to_csv, name='team-csv'),
]