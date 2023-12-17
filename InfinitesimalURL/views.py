import datetime,random,string
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework.views import Response,APIView
from . models import ShortURL
from .serializers import *
# Create your views here.

def generateShort(length=10):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


def GetShort(request,url):
    url = get_object_or_404(ShortURL,short=url)
    url.save()
    return redirect(url.url)

class ShortenURL(APIView):
    
    def get(self,request):
        s = ShortURL.objects.all()
        ser = ShortURLSerializer(s,many=True)
        return Response(ser.data)
    
    def post(self,request):
        data = request.data
        shorts = ShortURL.objects.all().values_list("short")
        print(shorts)
        if data.get("abbr"):
            short = data.get("abbr")
            if (short,) in shorts:
                return HttpResponse("Abbr Invalid",status=400)
        else:
            short = generateShort()
            while (short,) in shorts:
                short = generateShort()
        data["short"] = short
        print(data)
        url = data.get("url")
        name = data.get("name")
        serializer = ShortURLSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return HttpResponse(f"http://127.0.0.1:8000/infinitesimal/{short}")
        else:
            return Response(serializer.errors,status=400)