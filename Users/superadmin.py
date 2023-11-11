from django.urls import path
from .superadmin_views import *

urlpatterns = [
    path("create/", ValidateMe, name="sa_verify_me"),
    path("register/<str:token>", SuperadminCreationView.as_view(), name="sa_create_superadmin"),
    path("getusers/", GetAllUsers.as_view(), name="sa_get_users"),
]
