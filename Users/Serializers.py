import random

from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from Database.serializers import ClubSerializer, HostelSerializer
from Workshops.Serializers import WorkshopSerializer
from .models import Profile, Query


def send_email(otp):
    subject = 'OTP to reset PPassword'
    message = 'OTP to reset your password is:\n' + otp
    sender_email = 'tk.web.mail.madana@gmail.com'
    recipient_list = ['johnny.x.mia@gmail.com']
    email = EmailMessage(subject, message, sender_email, recipient_list)
    email.send()


def validate_entry(entry):
    return entry != None and len(entry) == 11 and entry[4:6].isalpha() & entry[:4].isdigit() & entry[6:].isdigit()


class ProfileSerializer(serializers.ModelSerializer):
    attended_events = WorkshopSerializer(many=True)

    class Meta:
        model = Profile
        fields = ["entry", "hostel", "attended_events", "name", "email",
                  "mobile", "room", "state", "profile_photo", "isRep", "isSecy", "points"]
        # exclude = ["otp", "registered_by", "isVerified", "registered_on"]
        # include = ["entry"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data["isRep"] or data["isSecy"]:
            data["club"] = instance.club.name
        data["hostel"] = instance.hostel.name
        data["profile_photo"] = "https://storage.googleapis.com/projekt-x-402611.appspot.com/" + \
            data.get("profile_photo")
        return data


class LeaderboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["entry", 'name', "points"]


class LoginSerializer(serializers.Serializer):
    entry = serializers.CharField(max_length=11)
    password = serializers.CharField(max_length=100, write_only=True)

    class Meta:
        fields = ("entry", "password")

    def validate(self, data):
        entry = data.get("entry").upper()
        password = data.get("password")

        if entry is None:
            raise serializers.ValidationError(
                {"detail": "An username is required to log in."})

        if password is None:
            raise serializers.ValidationError(
                {"detail": "A password is required to log in."})

        user = User.objects.filter(username=entry).first()
        profile = Profile.objects.filter(user__username=entry).first()

        if user is None or profile is None or not user.is_active or not profile.isVerified:
            raise serializers.ValidationError(
                {"detail": "A user with this username or password is not found."})

        if not user.check_password(password):
            raise serializers.ValidationError(
                {"detail": "A user with this username or password is not found."})

        refresh = RefreshToken.for_user(user)
        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "isRep": profile.isRep,
            "isSecy": profile.isSecy
        }
        return data


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("user", "name", "email", "mobile", "hostel", "room", "state", "isRep", "isSecy", "club",
                  "registered_by")
        model = Profile

    def validate(self, data):

        if data.get('isRep') and data.get("registered_by").isRep:
            raise serializers.ValidationError(
                {"isRep": "You can't register Rep"}, code=403)

        if data.get('isSecy') and (data.get("registered_by").isRep or data.get("registered_by").isSecy):
            raise serializers.ValidationError(
                {"isSecy": "You can't register Secy"}, code=403)

        data['otp'] = "".join([random.choice('0123456789') for _ in range(6)])

        return data


class ProfilePhotoSerializer(serializers.Serializer):
    profile_photo = serializers.ImageField()

    class Meta:
        fields = ("profile_photo")

    def validate(self, attrs):
        return attrs


class MassRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("entry", "name", "email", "mobile", "isVerified",
                  "hostel", "room", "state", "registered_by")
        model = Profile

    def validate(self, data):
        entry = data.get("entry")
        email = data.get("email")
        mobile = data.get("mobile")

        if Profile.objects.filter(Q(entry=entry) | Q(mobile=mobile) | Q(email=email)).exists():
            raise serializers.ValidationError(
                {"detail": "User already registered!"})

        if User.objects.filter(Q(username=entry) | Q(email=email)).exists():
            raise serializers.ValidationError(
                {"detail": "User already registered!"})

        return data


class ForgotPasswordSendSerializer(serializers.Serializer):
    entry = serializers.CharField()

    class Meta:
        feilds = ["entry"]

    def validate(self, data):
        user = get_object_or_404(User, username=data.get("entry"))
        profile = get_object_or_404(Profile, user=user)
        if not profile.isVerified:
            raise serializers.ValidationError(
                {"detail": "A user with this username is not found."})
        otp = "".join([str(random.randint(0, 9)) for _ in range(6)])
        profile.otp = otp
        profile.save()
        send_email(otp)
        token = PasswordResetTokenGenerator().make_token(user)
        return {"token": token}


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField()

    class Meta:
        feilds = ["password"]

    def validate(self, attrs):
        data = super().validate(attrs)
        if not data.get("password"):
            raise serializers.ValidationError(
                {"password": "This field is required"})
        if len(data.get("password")) < 6 or len(data.get("password")) > 16:
            raise serializers.ValidationError(
                {"password": "password must be 6 to 16 characters long"})
        return data


class ForgotPasswordVerifySerializer(serializers.Serializer):
    token = serializers.CharField()
    entry = serializers.CharField()
    otp = serializers.CharField()

    class Meta:
        feilds = ["entry", "token", "otp"]

    def validate(self, data):
        print(data)
        user = get_object_or_404(User, username=data.get("entry"))
        profile = get_object_or_404(Profile, user=user)
        if PasswordResetTokenGenerator().check_token(user, data.get("token")):
            if profile.otp == data.get("otp"):
                profile.otp = ""
                profile.isVerified = True
                profile.save()
                refresh = RefreshToken.for_user(user)
                data = {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "isStaff": user.is_staff,
                    "isRep": profile.isRep,
                    "isSecy": profile.isSecy
                }
                return data
            raise serializers.ValidationError({"detail": "Invalid otp"})
        raise serializers.ValidationError({"detail": "Invalid token"})


class QuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Query
        fields = ["user", "subject", "message", "isSolved"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["user"] = instance.user.username
        return data
