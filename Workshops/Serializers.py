from datetime import datetime

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers

from Database.models import Club, Hostel
from Users.models import Profile
from Workshops.models import Workshop

HOSTELS = ["Aravali", "Girnar", "Jwalamukhi", "Karakoram", "Kumaon", "Nilgiri", "Shivalik", "Satpura",
           "Udaigiri", "Vindhyachal", "Zanskar", "Dronagiri", "Saptagiri", "Kailash", "Himadri", "Sahyadri", "Nalanda"]


def getTime(time):
    input_format = "%Y-%m-%dT%H:%M:%S%z"
    datetime_obj = datetime.strptime(time, input_format)
    output_format = "%d/%m/%Y %I:%M %p"
    formatted_date = datetime_obj.strftime(output_format)
    return formatted_date


class ClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = ["name"]


class HostelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hostel
        fields = ["name"]


class WorkshopSerializer(serializers.ModelSerializer):
    hostel = HostelSerializer(many=True)

    class Meta:
        model = Workshop
        exclude = ['added_by', "date_added"]

    def to_representation(self, instance):
        data = super(WorkshopSerializer, self).to_representation(instance)
    # Manipulate the data dictionary here
        data["club"] = instance.club.name
        data['time'] = getTime(data.get("time"))
        data["hostel"] = [hostel.name for hostel in instance.hostel.all()]
        if self.context["host_url"]:
            data['poster'] = self.context["host_url"] + data.get("poster")[1:]
        return data


class AddWorkshopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workshop
        fields = ('title', 'poster', 'venue',
                  'description', 'contact_person', 'time', 'duration', "added_by")

    def validate(self, data):
        if (timezone.now() - data.get('time')).total_seconds() > 900:
            raise serializers.ValidationError(
                {"time": "Can't add event after 15 minutes from start of event"})
        profile = Profile.objects.get(user=data.get("added_by"))
        data["club"] = profile.club
        return data


class UpdateWorkshopSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    time = serializers.DateTimeField()
    venue = serializers.CharField()

    class Meta:
        fields = ('id', 'time', "venue")

    def validate(self, data):
        event = get_object_or_404(Workshop, id=data.get("id"))
        if (timezone.now() - data.get('time')).total_seconds() > 900:
            raise serializers.ValidationError(
                {"detail": "Can't update event after 15 minutes from start of event"})
        if (data.get('time') - event.time).total_seconds() < 0:
            raise serializers.ValidationError(
                {"detail": "Can't prepone event"})
        return data
