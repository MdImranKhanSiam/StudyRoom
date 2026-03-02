from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Room


class RoomForm(ModelForm):
    class Meta:
        model = Room
        # fields = '__all__'
        fields = ("name", "topic", "description")

class RegisterForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class" : "input-field"
            }
        )
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
            "placeholder": "Password",
            "class": "input-field"
            }
        )
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "Confirm Password",
            "class": "input-field"
        })
    )

    class Meta:
        model = User
        fields = ("username", "password1", "password2")