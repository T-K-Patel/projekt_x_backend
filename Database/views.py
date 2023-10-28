from collections import OrderedDict
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import College
from Database.serializers import HostelSerializer, ClubSerializer, CollegeSerializer

class AddHostelView(APIView):
    def post(self, request):
        data = request.data
        err = []
        hostels = data.get("hostels")
        if hostels:
            for hostel in hostels:
                serializer = HostelSerializer(
                    data=OrderedDict({"name": hostel}))
                if serializer.is_valid():
                    serializer.save()
                else:
                    err.append({"hostel": hostel, "error": serializer.errors})

            return Response({"detail": err})
        return Response({"detail": "Provide hostels to be added"})


class AddClubView(APIView):
    def post(self, request):
        data = request.data
        err = []
        hostels = data.get("clubs")
        if hostels:
            for hostel in hostels:
                serializer = ClubSerializer(data=OrderedDict({"name": hostel}))
                if serializer.is_valid():
                    serializer.save()
                else:
                    err.append({"club": hostel, "error": serializer.errors})

            return Response({"detail": err})
        return Response({"detail": "Provide hostels to be added"})


class AddCollegeView(APIView):
    def post(self, request):
        data = request.data
        err = []
        for college in data:
            serializer = CollegeSerializer(data=college)
            if serializer.is_valid():
                serializer.save()
            else:
                college["error"] = serializer.errors
                err.append(college)
        return Response({"message": "Added Succesfuly", "error": err})


class FetchCollegeView(APIView):
    def get(self, request):
        state = request.GET.get("state")
        city = request.GET.get("city")
        if state:
            if city:
                colleges = College.objects.filter(
                    college_state=state, college_city=city)
                serializer = CollegeSerializer(colleges, many=True)
                return Response(sorted(serializer.data, key=lambda x: x["college_name"]))
            else:
                colleges = College.objects.filter(
                    college_state=state).values('college_city').distinct()
                college_list = [college['college_city']
                                for college in colleges]
                college_list.sort()
                return Response(college_list)
        colleges = College.objects.values('college_state').distinct()

        return Response(sorted([col["college_state"] for col in colleges]))


class AllCollegesView(APIView):
    def get(self, request):
        colleges = College.objects.all()
        serializer = CollegeSerializer(colleges, many=True)
        return Response(serializer.data)