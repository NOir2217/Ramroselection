from rest_framework import serializers
from .models import Cart, CartItem
from products.serializers import ProductVariantSerializer

class CartItemSerializer(serializers.ModelSerializer):
    variant = ProductVariantSerializer(read_only=True)
    variant_id = serializers.IntegerField(write_only=True)
    line_total = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CartItem
        fields = ('id', 'variant', 'variant_id', 'quantity', 'line_total')

    def get_line_total(self, obj):
        return obj.quantity * (obj.variant.product.price + obj.variant.extra_price)

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Cart
        fields = ('id', 'items', 'subtotal', 'created_at', 'updated_at')

    def get_subtotal(self, obj):
        # Use .all() which hits the prefetch cache when available
        return sum(
            item.quantity * (item.variant.product.price + item.variant.extra_price)
            for item in obj.items.all()
        )

from .models import Order, OrderItem, ReturnRequest, DiscountRule

class DiscountRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountRule
        fields = '__all__'

class ReturnRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnRequest
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    variant = ProductVariantSerializer(read_only=True)
    return_requests = ReturnRequestSerializer(many=True, read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'variant', 'quantity', 'unit_price', 'return_requests')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'order_number', 'customer', 'guest_email', 'status', 'shipping_address', 'subtotal', 'discount_total', 'shipping_fee', 'total', 'applied_discount_code', 'created_at', 'updated_at', 'tracking_history', 'items')
