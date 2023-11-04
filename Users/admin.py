from Users.models import *
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.utils.translation import gettext_lazy as _


# Register your models here.


SA_FIELDS_SETS = (
    (None, {'fields': ('username', 'password')}),
    ('Personal info', {
        'fields': ('name', 'email', 'mobile', 'dob', 'state', 'profile_photo', 'otp')}),
    ('Permissions', {
        'fields': ('is_verified', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
    }),
    ('Important dates', {'fields': ('last_login', 'date_joined')})
)
ST_FIELDS_SETS = (
    (None, {'fields': ('username',)}),
    ('Personal Info', {'fields': ('name', 'mobile',
     'email', 'dob', 'state', 'profile_photo')}),
    ('Permissions', {'fields': ('is_active', 'is_staff',
                                'is_superuser', 'groups', 'user_permissions')}),
    ('Important dates', {'fields': ('date_joined',)}),
)


class MyUserAdmin(UserAdmin):
    list_display = ['id', 'username', 'name', 'email',
                    'mobile', 'is_staff', 'is_verified']
    search_fields = ['id', 'username', 'name',
                     'email', 'mobile', 'state', 'is_staff', 'is_verified']

    list_filter = ["state", "is_verified",
                   "is_staff", "is_active", "is_superuser"]
    readonly_fields = ['username', 'last_login', 'date_joined', 'profile_photo', "is_verified",
                       "is_superuser", 'is_staff', 'groups', "otp", 'user_permissions']
    filter_horizontal = ['groups', 'user_permissions']
    ordering = ("-id",)

    add_fieldsets = (
        (None, {'fields': ('username',)}),
        ('Personal info', {
         'fields': ('name', 'email', 'mobile', 'dob', 'state')}),
        ('Password', {"fields": ('password1', "password2")})
    )

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ["date_joined"]
        if obj:
            if obj.is_superuser:
                return ['username', 'name', 'email', 'mobile']
            if obj.is_verified:
                return self.readonly_fields + ['email']
        return self.readonly_fields

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return self.add_fieldsets

        if (request.user.is_superuser):
            return SA_FIELDS_SETS

        if obj.is_superuser:
            return (
                (None, {'fields': ('username',)}),
                ('Personal info', {
                 'fields': ('name', 'email', 'mobile', 'profile_photo')}),
            )
        return ST_FIELDS_SETS


class QueryAdmin(admin.ModelAdmin):
    list_display = ('user', "subject", "message", "date_created")
    search_fields = ('user__username', "subject", "message")
    ordering = ("-id",)


admin.site.register(User, MyUserAdmin)
admin.site.register(Query, QueryAdmin)
