from django.contrib import admin

from Users.models import *

# Register your models here.

class UserAdmin(admin.ModelAdmin):
	list_display = ('user', 'name', 'hostel', 'mobile', 'isRep', "isSecy", "club",
	                "registered_by", "registered_on")
	search_fields = ("user__username", 'name', 'hostel__name', 'mobile', 'isRep', "isSecy", "club__name")
	filter_horizontal = ('attended_events',)


class QueryAdmin(admin.ModelAdmin):
	list_display = ('user', "subject", "message", "date_created")
	search_fields = ('user__username', "subject", "message")


admin.site.register(Profile, UserAdmin)
admin.site.register(Query, QueryAdmin)