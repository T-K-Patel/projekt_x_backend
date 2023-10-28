from django.urls import path

from .views import *

urlpatterns = [
	path('addhostel/', AddHostelView.as_view(), name="addhostel"),
	path('addclub/', AddClubView.as_view(), name="addclub"),
	path('add_college/', AddCollegeView.as_view(), name="addclg"),
	path('fetch_college/', FetchCollegeView.as_view(), name="getclg"),
	path('all_college/', AllCollegesView.as_view(), name="allCLG"),
]
