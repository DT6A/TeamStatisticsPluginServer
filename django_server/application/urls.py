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
    path('contribute/create_word_metric/', create_word_metric, name='app-create-word-metric'),
    path('contribute/create_paste_metric/', create_paste_metric, name='app-create-paste-metric'),
    path('contribute/create_copy_metric/', create_copy_metric, name='app-create-copy-metric'),
    path('contribute/branch/', create_branch_metric, name='app-create-branch-metric'),
    path('contribute/create_achievement/', login_required(CreateAchievementView.as_view()), name='app-create-achievement'),
    path('profile/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('team/<int:pk>/', login_required(TeamDetailView.as_view()), name='team-detail'),
    path('team/<int:pk>/administrate', TeamDetailView.administrate_team, name='team-administrate'),
    path('join_team', join_team, name='team-join'),
    path('team/<int:pk>/csv', team_to_csv, name='team-csv'),
    path('feed', login_required(FeedMessageListView.as_view()), name='app-feed'),
    path('achievement/<int:pk>/', login_required(AchievementDetailView.as_view()), name='achievement-detail'),
    path('achievements/', login_required(AchievementListView.as_view()), name='achievement-list'),
]