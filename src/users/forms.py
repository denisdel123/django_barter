from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from core import mixins


class RegisterForm(mixins.StyleFormMixin, UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
