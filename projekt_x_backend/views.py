from django.shortcuts import render, redirect
from django.contrib import auth
from Users.models import Profile
from Workshops.models import Workshop
from django.core.files.storage import default_storage

def Home(request):
    if request.user.username:
        profile = Profile.objects.filter(
            user__username=request.user.username).first()
        if profile:
            print(default_storage.url(profile.profile_photo))
    else:
        profile = None
    return render(request, "Home/home.html", {"username": request.user.username, "profile": profile})


def workshop(request):
    workshops = Workshop.objects.all().values()
    print(workshops)
    return render(request, "Workshops/workshops.html", {"workshops": workshops})


def Home2(request):
    if request.user.username:
        profile = Profile.objects.filter(
            user__username=request.user.username).first()
    else:
        profile = None
    return render(request, "Home/home.html", {"username": request.user.username, "profile": profile})


def x_logout(request):
    auth.logout(request)
    return redirect("/")


def x_login(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(
            request=request, username=username, password=password)
        if user is not None and user.is_staff:
            auth.login(request, user)
            return redirect('/')
        else:
            return render(request, 'HTML/login.html', {'error': 'Invalid Credentials'})
    return render(request, 'HTML/login.html')
