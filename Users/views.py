import jwt
# import requests
from rest_framework.permissions import IsAuthenticated, IsAdminUser
# from django.forms.models import model_to_dict
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
# from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView as TRV
# from rest_framework_simplejwt.exceptions import TokenError
from Workshops.models import Workshop
from .Serializers import *
from .permissions import *
# from django.urls import reverse
# from django.middleware.csrf import get_token
from projekt_x_backend import settings


# Create your views here.


def send_email(entry, password, email="johnny.x.mia@gmail.com"):
    subject = 'Registration Successful.'
    message = 'Dear User, Your registration on Projekt-X was successful.\n\nHere are the profile credentials.\n\nEntry Number: ' + \
              entry + "\nPassword: " + password + \
        "\n\nVisit site to verify your profile.\n\nNote: This is temporary password.\nYou must change your Password."
    sender_email = 'tk.web.mail.madana@gmail.com'
    recipient_list = [email]
    email = EmailMessage(subject, message, sender_email, recipient_list)
    email.send()


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
        if user.is_active:
            return Response("Valid Token")
        return Response("Invalid Token", status=401)


class TokenRefreshView(TRV):
    def post(self, request):
        resp = super().post(request=request)
        access_token = resp.data["access"]
        payload = jwt.decode(
            access_token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        user = User.objects.filter(id=user_id).first()
        if user and user.is_active:
            profile = Profile.objects.filter(user=user).first()
            if profile:
                return resp
            else:
                return Response({"detail": "User Profile not found."}, status=404)
        return Response({"detail": "Your account has been deleted or is inactive."}, status=404)


class RegisterView(APIView):
    permission_classes = [IsAuthenticated, IsSuperuser | IsAdminUser]

    def post(self, request):
        data = request.data
        entry = data.get("entry")
        email = data.get("email")

        if not validate_entry(entry):
            return Response({"entry": ["Enter a valid entry number."]}, status=400)

        if not email:
            email = (entry[4:7]+entry[2:4]+entry[7:]+"@iitd.ac.in")

        if entry:
            entry = entry.upper()
            data["entry"] = entry

        data["email"] = email.lower()
        data["registered_by"] = Profile.objects.get(user=request.user).pk
        hostel = Hostel.objects.filter(name=data.get("hostel")).first()
        if hostel:
            data["hostel"] = hostel.pk
        elif data.get("hostel"):
            return Response({"hostel": ["Enter a valid hostel name."]}, status=400)

        staff = False
        if data.get('isSecy') or data.get('isRep'):
            staff = True
        if not data.get("password"):
            return Response({"detail": "Password is required"})
        if len(data.get("password")) < 8:
            return Response({"detail": "Password must be atleast 8 characters long."})
        if len(data.get("password")) > 16:
            return Response({"detail": "Password must not be more than 16 characters long."})

        password = data.get("password")

        if User.objects.filter(username=entry).exists():
            return Response({"detail": "User alresdy Registered"})

        user = User.objects.create_user(
            entry, email, password, is_staff=staff)

        data['user'] = user.pk
        serializer = RegisterSerializer(data=data)
        print(data)
        if serializer.is_valid():
            serializer.save()
        else:
            user.delete()
            return Response(serializer.errors, status=400)
        token = PasswordResetTokenGenerator().make_token(user)
        send_email(entry, password)
        return Response({"entry": entry, "token": token})


class LoginView(APIView):
    permission_classes = [IsCaptchaVerified]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


class Reset(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        new_password = request.data.get('password')

        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password changed successfully'})


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = get_object_or_404(Profile, user=request.user)
        if not user.isVerified:
            return Response({"detail": "Profile is not verified."}, status=403)
        serializer = ProfileSerializer(
            user, context={'host_url': request.build_absolute_uri('/')})
        data = serializer.data
        # for i in range(len(data["attended_events"])):
        #     data["attended_events"][i]["time"] = getTime(
        #         data["attended_events"][i]["time"])

        return Response(data)


class UpdateProfilePhoto(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        user = get_object_or_404(Profile, user=request.user)

        serializer = ProfilePhotoSerializer(data=request.data)

        if serializer.is_valid():
            profile_photo = serializer.validated_data['profile_photo']
            user.profile_photo = profile_photo
            user.save()

            return Response('Profile photo updated successfully')
        else:
            return Response(serializer.errors, status=400)


class LeaderboardView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        data = Profile.objects.all().order_by("-points")
        serializer = LeaderboardSerializer(data, many=True)
        data = serializer.data
        r = min(len(data), 20)
        data = data[:r]
        for i in range(r):
            data[i]["rank"] = i+1
        return Response(data)


def fetch_Attended_Events(entry):
    profile = get_object_or_404(Profile, user__username=entry)
    events = profile.attended_events
    if events:
        events = events.split("|")
        events = list(map(int, events))
        print(events)
        events.sort()
    return events


class AddAttendedEvents(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        entry = request.user.username
        ids = fetch_Attended_Events(entry)
        events = []
        if ids:
            for i in ids:
                title = Workshop.objects.get(id=i).title
                events.append({"id": i, "title": title})
        return Response({"attended_events": events})

    def post(self, request):
        entry = request.user.username
        event = request.data.get("add_event")
        if event:
            temp = Workshop.objects.filter(id=event).first()
            if not temp:
                return Response({"detail": "Event Not found."}, status=404)
            events = fetch_Attended_Events(entry)
            if int(event) in events:
                return Response({"detail": "Event already exist"}, status=400)
            events.append(int(event))
            events = list(set(events))
            events.sort()
            events = map(str, events)
            profile = get_object_or_404(Profile, entry=entry)
            profile.attended_events = "|".join(events)
            profile.save()
            return Response({"detail": "Event added successfully"})
        else:
            return Response({"add_event": "This field is required"}, status=400)


class MassRegisterUsers(APIView):
    permission_classes = [IsAuthenticated, IsBSWRep]

    def post(self, request):
        data = request.data
        creator = get_object_or_404(Profile, user=request.user)
        print(request)
        if type(data.get("users")) == list:
            cant_reg = []
            for entry in data.get("users"):
                entry["hostel"] = creator.hostel.pk
                entry["isVerified"] = True
                entry["registered_by"] = creator
                serializer = MassRegisterSerializer(data=entry)
                if serializer.is_valid():
                    username = serializer.validated_data.get("entry")
                    email = serializer.validated_data.get("email")
                    password = RandomPass()
                    user = User.objects.create_user(
                        username, email, password)
                    if user:
                        send_email(entry=username, password=password)
                        serializer.save()
                    else:
                        cant_reg.append({"entry": entry.get('entry'), "error": {
                            "detail": "User is Superuser"}})
                else:
                    cant_reg.append(
                        {"entry": entry.get('entry'), "error": serializer.errors})
            if cant_reg:
                return Response(
                    {"detail": f"Can't register {len(cant_reg)} of {len(data.get('users'))} users",
                     "users": cant_reg},
                    status=400)
            return Response({"detail": "Registered Successfully"})
        return Response({"detail": "Users should be in list"}, status=400)


class ResetPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(username = request.user.username)
        print(serializer.validated_data.get("password"))
        user.set_password(serializer.validated_data.get("password"))
        user.save()
        return Response({"detail": "Password Reset Successful."})


class ForgotPasswordSendView(APIView):
    def post(self, request):
        data = request.data
        serializer = ForgotPasswordSendSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


class ForgotPasswordVerifyView(APIView):
    def post(self, request):
        data = request.data
        serializer = ForgotPasswordVerifySerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


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
