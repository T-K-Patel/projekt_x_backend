import requests
from rest_framework.permissions import BasePermission
from .models import *
import os

CAPTCHA_KEY = os.environ["CAPTCHA_KEY"]


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff


class IsSuperuser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser


class IsCaptchaVerified(BasePermission):
    def has_permission(self, request, view):
        captcha_response = request.META.get('HTTP_CAPTCHA_RESPONSE')
        response = requests.get(
            f"https://www.google.com/recaptcha/api/siteverify?secret={CAPTCHA_KEY}&response={captcha_response}")
        if response.status_code == 200:
            response = response.json()
            if response['success']:
                return True
        return False
