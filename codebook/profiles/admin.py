from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import MyUser, Profile
from .forms import MyUserCreationForm, MyUserChangeForm, ProfileForm


class MyUserAdmin(UserAdmin):
    form = MyUserChangeForm
    add_form = MyUserCreationForm

    list_display = ('email', 'first_name', 'last_name', 'date_joined', 'last_login', 'is_staff')
    add_fieldsets = (
        ('User info', {'classes': ('wide',),
                       'fields': ('email', 'password1', 'password2')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
    )
    search_fields = ('email', 'first_name', 'last_name')
    filter_horizontal = ()


class ProfileAdmin(admin.ModelAdmin):
    form = ProfileForm
    list_display = ('user', 'reputation')
    list_filter = ('user__date_joined',)
    fieldsets = (
        (None, {'fields': ('user', )}),
        ('Profile Information', {'fields': ('reputation', 'follows')}),
    )
    filter_horizontal = ('follows',)


admin.site.register(MyUser, MyUserAdmin)
admin.site.register(Profile, ProfileAdmin)
