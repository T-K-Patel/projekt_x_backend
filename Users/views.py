from django.views.generic.edit import CreateView
import json
import random
import time
import datetime
import uuid
import jwt
import pyshorteners

from django.urls import reverse_lazy


from django.contrib.auth.password_validation import validate_password
from django.db.models import Q
from django.forms import ValidationError
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.views import TokenRefreshView as TRV

from .Serializers import *
from .permissions import IsCaptchaVerified
from .tasks import upload_profile
from .encryptions import decrypt, encrypt
from .models import User
from .forms import SuperadminCreationForm
from .tasks import send_reset_email, send_reg_email

from projekt_x_backend import settings

# Create your views here.


def RandomPass(n=16):
    chars = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM78945612307894561230"
    password = "".join([random.choice(chars) for _ in range(n)])
    return password


def getTime(time):
    input_format = "%Y-%m-%dT%H:%M:%S%z"
    datetime_obj = datetime.strptime(time, input_format)

    # Format the datetime object into "dd/mm/yyyy" format
    output_format = "%d/%m/%Y %H:%M %p"
    formatted_date = datetime_obj.strftime(output_format)
    return formatted_date


class ValidateToken(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.is_active and user.is_verified:
            return Response("Valid Token")
        return Response("Invalid Token", status=401)


class TokenRefreshView(TRV):
    def post(self, request):
        resp = super().post(request=request)
        access_token = resp.data["access"]
        payload = jwt.decode(
            access_token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload["user_id"]
        user = User.objects.filter(id=user_id).first()
        if user and user.is_active:
            if not user.is_verified:
                return Response({"detail": "User not found."}, status=404)
            return resp
        return Response(
            {"detail": "Your account has been deleted or is inactive."}, status=404
        )


class RegisterView(APIView):
    permission_classes = [IsCaptchaVerified]

    def post(self, request):
        data = request.data
        username = data.get("username")
        email = data.get("email")

        if username:
            username = username.upper()
            data["username"] = username

        data["email"] = email.lower()
        password = data.get("password")

        if not password:
            return Response({"detail": "Password is required"}, status=400)
        if len(password) < 8:
            return Response(
                {"detail": "Password must be atleast 8 characters long."}, status=400
            )
        if len(password) > 16:
            return Response(
                {"detail": "Password must not be more than 16 characters long."},
                status=400,
            )

        user = User.objects.filter(
            Q(username=username) | Q(email=email) | Q(
                mobile=request.data.get("mobile"))
        ).first()

        if user:
            if not user.is_verified:
                if (timezone.now() - user.date_joined).total_seconds() < 600:
                    return Response(
                        {"detail": "Wait for 10 minutes before retrying."}, status=400
                    )
                user.delete()
            else:
                return Response(
                    {
                        "detail": "User with given username, email or mobile already exists."
                    },
                    status=400,
                )

        serializer = RegisterSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(password)
            user.save()
            token = PasswordResetTokenGenerator().make_token(user)
            send_reg_email(
                {"otp": serializer.validated_data["otp"],
                    "username": username, "name": user.name},
                data["email"],
            )
            return Response({"username": username, "token": token})
        else:
            return Response({"detail": serializer.errors}, status=400)


class RegisterVerifyView(APIView):
    def post(self, request):
        data = request.data
        print(data)
        if not (data.get("username") and data.get("token")):
            return Response({"detail": "Invalid data"}, status=400)
        serializer = ForgotPasswordVerifySerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response("Profile verification successful")


class LoginView(APIView):
    permission_classes = [IsCaptchaVerified]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = get_object_or_404(User, username=request.user.username)
        if not user.is_verified:
            return Response({"detail": "Profile is not verified."}, status=403)
        serializer = ProfileSerializer(user)
        data = serializer.data

        return Response(data)


class UpdateProfilePhoto(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        user = get_object_or_404(User, username=request.user.username)
        try:
            image_file = f"Users/profile_photo/{user.username.lower()}/{str(uuid.uuid4())}.{request.data.get('profile_photo').name.split('.')[-1]}"
        except:
            image_file = f"Users/profile_photo/{user.username.lower()}/{str(uuid.uuid4())}.jpg"

        serializer = ProfilePhotoSerializer(data=request.data)

        if serializer.is_valid():
            profile_photo = serializer.validated_data["profile_photo"]
            try:
                url = upload_profile(profile_photo, image_file)
                user.profile_photo = url
                user.save()
            except:
                return Response({"detail": "Error uploading profile photo"}, status=400)

            return Response("Profile photo updated successfully.")
        else:
            return Response(serializer.errors, status=400)


class ForgotPasswordSendView(APIView):
    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        user = User.objects.filter(
            Q(username=username) | Q(email=email)).first()
        if not (username or email):
            return Response(
                {"detail": "Username or Email Required to reset password"}, status=400
            )
        if not user:
            return Response(
                {"detail": "User with given username or email not found"}, status=404
            )

        otp = "".join([str(random.randint(0, 9)) for _ in range(6)])

        data = {
            "user": user.username or 1,
            "exp_time": int(time.time() + 600),
            "otp": otp,
        }

        enc_data = encrypt(json.dumps(data))
        user.otp = otp
        user.save()

        s = pyshorteners.Shortener()
        original_url = (
            f"{request.build_absolute_uri('/')}users/reset_password/{enc_data}"
        )
        short_url = s.tinyurl.short(original_url)

        context = {"username": user.name, "url": short_url}

        if user.email:
            success = send_reset_email(context, user.email)
        else:
            success = send_reset_email(context)
        if success:
            return Response("Email Sent to registered email.")
        return Response(
            {"detail": "Error sending mail. try again afteer some time"}, status=400
        )


def reset_password_page(request, enc_data):
    try:
        details = decrypt(enc_data)
        details_dict = json.loads(details)
        exp_time = details_dict["exp_time"]
        username = details_dict["user"]
        otp = details_dict["otp"]
    except:
        return HttpResponse(
            "<h1 style='text-align:center; margin-top: 20px;'>Invalid Link.</h1>"
        )

    user = None
    if username:
        user = User.objects.filter(username=username).first()

    if exp_time <= time.time() or (user is None) or (not user.otp) or (user.otp != otp):
        return HttpResponse(
            "<h1 style='text-align:center; margin-top: 20px;'>Link has Expired.</h1>"
        )

    if request.method == "POST":
        p1 = request.POST.get("password")
        p2 = request.POST.get("password2")
        if p1 != p2:
            return render(
                request,
                "reset_password.html",
                {
                    "user": user,
                    "error": "Password does not match.",
                    "passwords": {"first": p1, "second": p2},
                },
                status=400,
            )
        try:
            validate_password(p1)
        except ValidationError as error:
            return render(
                request,
                "reset_password.html",
                {
                    "user": user,
                    "error": error,
                    "passwords": {"first": p1, "second": p2},
                },
                status=400,
            )

        user.set_password(p1)
        user.otp = ""
        user.save()
        return HttpResponse(
            "<h1 style='text-align:center; margin-top: 20px;'>Password Reset Successful.</h1>"
        )

    return render(request, "reset_password.html", {"user": user.username})


class QueryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        querries = Query.objects.filter(user=request.user)
        serializer = QuerySerializer(querries, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data
        data["user"] = request.user.pk
        data["isSolved"] = False
        serializer = QuerySerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Query added successfully"})


def csrf_failure_view(
    request, reason="CSRF Failure", template_name="Errors/custom_csrf_failure.html"
):
    return render(request, template_name, {"reason": reason})
