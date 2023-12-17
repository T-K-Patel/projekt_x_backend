from django.contrib import admin
from .models import *
# Register your models here.
class ShortURLAdmin(admin.ModelAdmin):
    list_display = ['short', 'name', 'url', 'modified', 'created']
    list_search= ['short', 'name', 'url', 'modified', 'created']
    

admin.site.register(ShortURL,ShortURLAdmin)