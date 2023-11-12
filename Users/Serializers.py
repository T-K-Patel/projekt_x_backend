from datetime import datetime
from django.utils.translation import gettext_lazy as GTL
import random

from .models import User, Query
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from Users.tasks import send_reset_email


def validate_image_size(image):
    max_size = 1024 * 1024 * 5  # 5 MB

    if image.size > max_size:
        raise serializers.ValidationError(
            GTL('The image file size should not exceed 5 MB.'),
            code='invalid_image_size'
        )
    return image


def getTime(time):
    input_format = "%Y-%m-%d"
    datetime_obj = datetime.strptime(time, input_format)
    output_format = "%d/%m/%Y"
    formatted_date = datetime_obj.strftime(output_format)
    return formatted_date


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["username", "dob", "name", "email",
                  "mobile", "state", "profile_photo"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data.get("dob"):
            data["dob"] = getTime(data.get("dob"))
        else:
            data["dob"] = None
        return data


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=11)
    password = serializers.CharField(max_length=100, write_only=True)

    class Meta:
        fields = ("username", "password")

    def validate(self, data):
        username = data.get("username").upper()
        password = data.get("password")

        if username is None:
            raise serializers.ValidationError(
                {"detail": "An username is required to log in."})

        if password is None:
            raise serializers.ValidationError(
                {"detail": "A password is required to log in."})

        user = User.objects.filter(username=username).first()

        if user is None or not user.is_active or not user.is_verified:
            raise serializers.ValidationError(
                {"detail": "A user with this username or password is not found."})

        if not user.check_password(password):
            raise serializers.ValidationError(
                {"detail": "A user with this username or password is not found."})

        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("username", "password", "name",
                  "email", "mobile", "dob", "state")
        model = User
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        data['otp'] = "".join([str(random.randint(0, 9)) for _ in range(6)])
        return data


class ProfilePhotoSerializer(serializers.Serializer):
    profile_photo = serializers.ImageField()

    class Meta:
        fields = ("profile_photo")

    def validate(self, data):
        validate_image_size(data.get("profile_photo"))
        return data


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField()

    class Meta:
        feilds = ["password"]

    def validate(self, attrs):
        data = super().validate(attrs)
        if not data.get("password"):
            raise serializers.ValidationError(
                {"password": "This field is required"})
        if len(data.get("password")) < 8 or len(data.get("password")) > 16:
            raise serializers.ValidationError(
                {"password": "password must be 8 to 16 characters long"})
        return data


class ForgotPasswordVerifySerializer(serializers.Serializer):
    token = serializers.CharField()
    username = serializers.CharField()
    otp = serializers.CharField()

    class Meta:
        feilds = ["username", "token", "otp"]

    def validate(self, data):
        user = get_object_or_404(User, username=data.get("username"))
        if PasswordResetTokenGenerator().check_token(user, data.get("token")):
            if user.otp == data.get("otp"):
                user.otp = ""
                user.is_verified = True
                user.save()
                refresh = RefreshToken.for_user(user)
                data = {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token)
                }
                return data
            raise serializers.ValidationError({"detail": "Invalid otp"},code=400)
        raise serializers.ValidationError({"detail": "Invalid token"},code=400)


class QuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Query
        fields = ["user", "subject", "message", "isSolved"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["user"] = instance.user.username
        return data
