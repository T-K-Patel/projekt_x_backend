from django.urls import path
from .views import *

urlpatterns = [
	path('view/', WorkshopsView.as_view(), name="View Workshop"),
	path('workshop_by_id/<int:id>', WorkshopByIdView.as_view(), name="workshop_by_id"),
	path('workshop_by_club/<str:club>', WorkshopByClubView.as_view(), name="workshop_by_club"),
	path('add/', AddWorkshop.as_view(), name="Add Workshop"),
	path('reward/', RewardPonts.as_view(), name="Give Rewards"),
	path('update/', UpdateWorkshop.as_view(), name="Update Workshop"),
]