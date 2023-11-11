import json
import random
import time
import datetime
import uuid
import os
import pyshorteners

from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q
from django.forms import ValidationError
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.views import TokenRefreshView as TRV

from .Serializers import *
from .permissions import IsCaptchaVerified, superuser_required
from .tasks import upload_profile
from .encryptions import decrypt, encrypt
from .models import User
from .forms import SuperadminCreationForm
from .tasks import send_reset_email, send_reg_email

from projekt_x_backend import settings
from django.views.generic.edit import CreateView


def decode(text):
    try:
        text = json.loads(decrypt(text))

        return text["exp"] > int(time.time())
    except:
        return False


def ValidateMe(request):
    error = None
    status = 200
    if request.method == "POST":
        if request.POST.get("creation_key") == os.environ["SECRET_KEY"]:
            return redirect(
                "/__superadmin__/register/"
                + encrypt(json.dumps({"exp": int(time.time()) + 180}))
            )
        error = "Invalid Creation Key"
        status = 203
    return render(request, "HTML/verify_superuser.html", {"creation_key_errors": error}, status=status)


class SuperadminCreationView(CreateView):
    template_name = "HTML/create_superadmin.html"

    def get(self, request, token):
        form = SuperadminCreationForm()
        if not decode(token):
            return HttpResponse("<center><h1>Invalid Url</h1></center>")
        return render(
            request,
            self.template_name,
            {
                "form": form,
            },
        )

    def post(self, request, token):
        print("Got Validated")
        form = SuperadminCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/login/")
        else:
            return render(
                request,
                self.template_name,
                {"form": form},
                status=400,
            )


class SaProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


@method_decorator(superuser_required, name="dispatch")
class GetAllUsers(APIView):
    def get(self, request, *args, **kwargs):
        # Your superuser API logic using self.request
        users = User.objects.all()
        serializer = SaProfileSerializer(users, many=True)
        data = serializer.data
        return Response(data)
