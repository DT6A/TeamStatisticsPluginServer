from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('', ProfileListView.as_view(), name='app-home'),
    path('teams/', login_required(TeamListView.as_view()), name='app-teams'),
    path('create_team/', create_team, name='app-create-team'),
    path('contribute/', contribute, name='app-contribute'),
    path('contribute/create_char_metric/', create_char_metric, name='app-create-char-metric'),
    path('contribute/create_substring_metric/', create_substring_metric, name='app-create-substring-metric'),
    path('contribute/create_achievement/', login_required(CreateAchievementView.as_view()), name='app-create-achievement'),
    path('profile/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('team/<int:pk>/', login_required(TeamDetailView.as_view()), name='team-detail'),
    path('team/<int:pk>/administrate', TeamDetailView.administrate_team, name='team-administrate'),
    path('join_team', join_team, name='team-join'),
    path('team/<int:pk>/csv', team_to_csv, name='team-csv'),
    path('feed', login_required(FeedMessageListView.as_view()), name='app-feed'),
]