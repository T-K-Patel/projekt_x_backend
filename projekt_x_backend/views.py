from django.shortcuts import render, redirect
from django.contrib import auth


def Home(request):
    profile = None
    if request.user.is_authenticated:
        profile = request.user
    return render(request, "Home/home.html", {"username": request.user.username, "profile": profile})


# def workshop(request):
#     workshops = Workshop.objects.all().values()
#     print(workshops)
#     return render(request, "Workshops/workshops.html", {"workshops": workshops})


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
