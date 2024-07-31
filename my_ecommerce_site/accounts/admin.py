from django.contrib import admin
from .models import *



class ProfileInline(admin.StackedInline):
    model = Profile


class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = ['username', 'email', 'first_name', 'last_name']
    inlines = [ProfileInline]


class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['user']


class BillingAddressAdmin(admin.ModelAdmin):
    list_display = ['user']



admin.site.register(User, UserAdmin)
