# forms.py
from typing import Any
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class SuperadminCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username",
            "name",
            "email",
            "mobile",
            "state",
            "dob",
            "password1",
            "password2",
        ]

    def form_valid(self, form):
        # Set is_superuser to True before saving the user object
        form.instance.is_superuser = True
        form.instance.is_active = True
        form.instance.is_staff = True
        form.instance.is_verified = True
        return super().form_valid(form)

    def save(self, commit: bool = ...) -> Any:
        self.instance.is_superuser = True
        self.instance.is_active = True
        self.instance.is_staff = True
        self.instance.is_verified = True
        return super().save(commit)
