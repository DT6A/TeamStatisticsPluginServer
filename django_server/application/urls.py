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
    path('join_team', join_team, name='team-join'),
    #path('user/<str:username>', UserPostListView.as_view(), name='user-posts'),
    #path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    #path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    #path('post/new/', PostCreateView.as_view(), name='post-create'),
    #path('about/', views.about, name='blog-about'),
]