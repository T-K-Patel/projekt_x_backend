from rest_framework import serializers

from Database.models import Hostel, Club, College


class HostelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hostel
        fields = ["name"]

    def validate(self, data):
        return data


class ClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = ["name", "board"]

    def validate(self, data):
        return data


class CollegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = College
        fields = '__all__'

    def validate(self, attrs):
        return attrs
