from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('post/', views.receive_data, name='post'),
    path('profile/', views.profile, name='profile'),
    path('plugin_login/', views.plugin_login, name='plugin_login'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
]