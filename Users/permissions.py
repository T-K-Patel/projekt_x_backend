import requests
from rest_framework.permissions import BasePermission
from .models import *
import os
from functools import wraps
from django.core.exceptions import PermissionDenied


CAPTCHA_KEY = os.environ["CAPTCHA_KEY"]

# users/middleware.py


def superuser_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to access this resource.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff


class IsSuperuser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser


class IsCaptchaVerified(BasePermission):
    def has_permission(self, request, view):
        captcha_response = request.META.get("HTTP_CAPTCHA_RESPONSE")
        response = requests.get(
            f"https://www.google.com/recaptcha/api/siteverify?secret={CAPTCHA_KEY}&response={captcha_response}"
        )
        if response.status_code == 200:
            response = response.json()
            if response["success"]:
                return True
        return False
