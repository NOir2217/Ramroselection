from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem, ReturnRequest, DiscountRule

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'created_at', 'updated_at')
    search_fields = ('id', 'customer__email', 'customer__user__username')
    inlines = [CartItemInline]

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'guest_email', 'status', 'total', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'guest_email', 'customer__email', 'customer__user__username')
    inlines = [OrderItemInline]

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'variant', 'quantity')
    search_fields = ('cart__id', 'variant__product__name')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'variant', 'quantity', 'unit_price')
    search_fields = ('order__order_number', 'variant__product__name')

@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_item', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_item__order__order_number', 'reason')

@admin.register(DiscountRule)
class DiscountRuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'rule_type', 'is_active', 'active_from', 'active_to')
    list_filter = ('rule_type', 'is_active')
    search_fields = ('code',)
