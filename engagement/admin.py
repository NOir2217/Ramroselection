from django.contrib import admin
from .models import WishlistItem, RecentlyViewed, Review

@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'session_key', 'product', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('customer__email', 'session_key', 'product__name')

@admin.register(RecentlyViewed)
class RecentlyViewedAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'session_key', 'product', 'viewed_at')
    list_filter = ('viewed_at',)
    search_fields = ('customer__email', 'session_key', 'product__name')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'customer', 'rating', 'title', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'rating', 'created_at')
    search_fields = ('product__name', 'customer__email', 'title')
    actions = ['approve_reviews']

    @admin.action(description='Approve selected reviews')
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
