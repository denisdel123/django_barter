from users.apps import UsersConfig
from django.urls import path
from .views import register
from django.contrib.auth import views as auth_views

app_name = UsersConfig.name

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
