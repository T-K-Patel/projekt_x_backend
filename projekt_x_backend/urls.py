"""
URL configuration for projekt_x_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
from projekt_x_backend import views

urlpatterns = [
    path('', views.Home,name="Home"),
    path('2', views.Home2,name="Home2"),
    path('workshop/', views.workshop),
    path('login/', views.x_login,name="Login"),
    path('logout/', views.x_logout,name="Logout"),
    path('admin/', admin.site.urls),
    path('users/', include("Users.urls")),
    path('workshops/', include("Workshops.urls")),
    path('database/', include("Database.urls")),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)