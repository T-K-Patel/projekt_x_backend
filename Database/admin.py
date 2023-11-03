from django.contrib import admin
from .models import *

# Register your models here.
class ClubAdmin(admin.ModelAdmin):
	list_display = ("name", 'board')
	search_fields = ('id', "name", 'board')


class HostelAdmin(admin.ModelAdmin):
	list_display = ["id","name","residents"]
	search_fields = ('id', "name")

class CollegeAdmin(admin.ModelAdmin):
	list_display = ["id","college_name","college_city","college_state"]
	search_fields = ("id","college_name","college_city","college_state")


admin.site.register(Club, ClubAdmin)
admin.site.register(Hostel, HostelAdmin)
admin.site.register(College, CollegeAdmin)
