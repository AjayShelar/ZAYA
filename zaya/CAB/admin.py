from django.contrib import admin
from .models import *
from django.contrib.contenttypes.admin import GenericTabularInline
from django.forms import TextInput, Textarea
from django.utils.safestring import mark_safe
from django.db import models
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.contrib.auth.models import Group
from xml.dom import ValidationErr
from django import forms
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext, ugettext_lazy as _

# Register your models here.

# class ProfileInline(nested_admin.NestedStackedInline):
#     model = UserProfile
#     fk_name = 'user'


class PlainUserForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = ('username', 'password')


class CustomUserAdmin(UserAdmin):
    model = User
    search_fields = ['phone_number', 'first_name', 'last_name']
    # inlines = [ProfileInline]

    add_fieldsets = ((None, {
        'classes': ('wide', ),
        'fields': ('phone_number', 'first_name', 'last_name'),
    }), )
    fieldsets = ((None, {
        'fields': ('username', 'password')
    }), (_('Personal info'), {
        'fields': ('first_name', 'last_name', 'phone_number')
    }), (_('Permissions'), {
        'fields': ('is_active', 'is_staff')
    }), ('Others', {
        'fields': ('type', 'created_by', 'edited_by', 'groups')
    }))
    add_form = PlainUserForm


class CabAdmin(admin.ModelAdmin):
    model = Cab


class RideAdmin(admin.ModelAdmin):
    model = Ride


class RouteAdmin(admin.ModelAdmin):
    model = Route


class LocationAdmin(admin.ModelAdmin):
    model = Location


admin.site.register(Cab, CabAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Route, RouteAdmin)
admin.site.register(Ride, RideAdmin)
admin.site.register(Location, LocationAdmin)
