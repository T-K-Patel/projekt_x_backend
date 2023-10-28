import json
import time

from django.forms import model_to_dict
from projekt_x_backend import settings
from rest_framework.permissions import *
from rest_framework.response import Response
from rest_framework.views import APIView
from Users.permissions import *
from .Serializers import *


def getTime(time):
    input_format = "%Y-%m-%dT%H:%M:%S%z"
    datetime_obj = datetime.strptime(time, input_format)
    output_format = "%d/%m/%Y %H:%M %p"
    formatted_date = datetime_obj.strftime(output_format)
    return formatted_date

    # permission_classes = [IsAuthenticated]


class WorkshopsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = get_object_or_404(Profile, user=request.user)
        wksp = Workshop.objects.filter(
            hostel__name=user.hostel.name).prefetch_related("club")
        data = {}
        for w in wksp:
            if w.club.name not in data:
                data[w.club.name] = []
            data[w.club.name].append(WorkshopSerializer(
                w, context={'host_url': request.build_absolute_uri('/')}).data)
        res = dict(sorted(data.items()))
        print(res)
        return Response(res)


class WorkshopByIdView(APIView):
    def get(self, request, id):
        workshop = get_object_or_404(Workshop, id=id)
        workshop = WorkshopSerializer(
            workshop, context={'host_url': request.build_absolute_uri('/')}).data
        return Response(workshop)


class WorkshopByClubView(APIView):
    def get(self, request, club):
        workshop = Workshop.objects.filter(club__name=club)
        workshop = WorkshopSerializer(workshop, many=True, context={
                                      'host_url': request.build_absolute_uri('/')}).data
        return Response(workshop)


class AddWorkshop(APIView):
    permission_classes = [IsAuthenticated, IsRep | IsSecy]

    def post(self, request):
        creator = request.user
        data = request.data.copy()
        data["added_by"] = creator.pk

        hostels = json.loads(data.get('hostel'))
        if type(hostels) != list:
            print(hostels)
            return Response({"hostel": "Hostels must be in list"}, status=400)

        if len(hostels) == 0:
            return Response({"hostel": "This field may not be blank."}, status=400)

        temp = []
        for hostel in hostels:
            hstl = Hostel.objects.filter(name=hostel).first()
            if not hstl:
                return Response({"hostel": "Enter valid hostel names."}, status=400)
            temp.append(hstl.pk)

        serializer = AddWorkshopSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        w = serializer.save()
        w.hostel.set(temp)
        return Response({"detail": "Workshop added successfully"})


class UpdateWorkshop(APIView):
    permission_classes = [IsAuthenticated, IsStaff | IsAdminUser]

    def post(self, request):
        user = request.user
        data = request.data
        data['user'] = user.username

        if not data.get("id"):
            return Response({"id": "This field is required."}, status=400)
        if data.get("time") is None and data.get("venue") is None:
            return Response({"detail": "Update data is required."}, status=400)

        w_id = get_object_or_404(Workshop, id=data.get("id"))

        if w_id.added_by.user != request.user:
            return Response({"detail": "You can't update this workshop."}, status=403)

        data["time"] = data.get("time") or w_id.time
        data["venue"] = data.get("venue") or w_id.venue

        serializer = UpdateWorkshopSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        w_id.time = data.get("time")
        w_id.venue = data.get("venue")
        w_id.save()

        return Response({'detail': "Workshop updated successfully."})


class RewardPonts(APIView):
    permission_classes = [IsAuthenticated, IsRep | IsSecy]

    def post(self, request):
        attendees = request.data.get("attendees")
        cant_add = []
        reward = request.data.get("reward")
        if not attendees:
            return Response({"attendees": "This field is required."}, status=400)
        if type(attendees) != list:
            return Response({"detail": "Attendees must be in list"}, status=400)
        for attendee in attendees:
            try:
                user = Profile.objects.get(user__username=attendee)
                user.points = user.points + int(reward)
                user.save()
            except (Exception):
                cant_add.append(attendee)
        if cant_add:
            return Response({"cant_add": cant_add}, status=404)
        return Response({"detail": "Rewards given successfully"})
