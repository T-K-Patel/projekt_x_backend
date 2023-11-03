from django.http import HttpResponse
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


def page_not_found(request, exception):
    return HttpResponse("<!DOCTYPE html>"
                        "<html lang='en'>"

                        "<head>"
                        "<meta charset='UTF-8' />"
                        "<meta name='viewport' content='width=device-width, initial-scale=1.0' />"
                        "<title>Error 404</title>"
                        "</head>"
                        "<body>"
                        "<center>"
                        "<h1>Error 404 (Page not found)</h1>"
                        "<p>The requested resource was not found on this server.</p>"
                        "<a href='/'><button style='padding:5px; background-color:lightgrey;'>Go to Home</button></a>"
                        "</center>"
                        "</body>"
                        "</html>")
