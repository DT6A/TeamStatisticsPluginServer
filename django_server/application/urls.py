from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('', ProfileListView.as_view(), name='app-home'),
    path('tracked/', login_required(TrackedListView.as_view()), name='app-tracked'),
    path('profile/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    #path('user/<str:username>', UserPostListView.as_view(), name='user-posts'),
    #path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    #path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    #path('post/new/', PostCreateView.as_view(), name='post-create'),
    #path('about/', views.about, name='blog-about'),
]