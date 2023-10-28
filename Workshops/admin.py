from django.contrib import admin

from Workshops.models import *


# Register your models here.
class WorkshopAdmin(admin.ModelAdmin):
	list_display = ('title', 'club', 'time','added_by',"date_added")
	search_fields = ('title','club__name', 'time', 'venue', "description")
	filter_horizontal = ['hostel']


admin.site.register(Workshop, WorkshopAdmin)
