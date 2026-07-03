from django.contrib import admin
from .models import CustomerProfile, Address

class AddressInline(admin.TabularInline):
    model = Address
    extra = 1
    fields = ('full_name', 'phone', 'street', 'city', 'postal_code', 'country', 'is_default')

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'email', 'is_vip', 'phone')
    list_filter = ('is_vip',)
    search_fields = ('email', 'user__username', 'phone')
    inlines = [AddressInline]

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', 'full_name', 'city', 'country', 'is_default')
    list_filter = ('city', 'country', 'is_default')
    search_fields = ('full_name', 'street', 'city')
