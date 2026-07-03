from django.urls import path
from .views import (
    CartAPIView, CartItemAPIView, CartItemDetailAPIView, CheckoutAPIView,
    OrderListAPIView, OrderRetrieveAPIView, OrderReturnAPIView,
    AdminDashboardStatsView, AdminOrderListAPIView, AdminOrderStatusUpdateAPIView,
    AdminLowStockAPIView, AdminExpiringProductsAPIView,
    AdminDiscountListAPIView, AdminDiscountDetailAPIView,
    AdminAbandonedCartsAPIView, AdminAnalyticsAPIView,
)

urlpatterns = [
    path('cart/', CartAPIView.as_view(), name='cart-detail'),
    path('cart/items/', CartItemAPIView.as_view(), name='cart-item-list'),
    path('cart/items/<int:pk>/', CartItemDetailAPIView.as_view(), name='cart-item-detail'),
    path('checkout/', CheckoutAPIView.as_view(), name='checkout'),

    path('orders/', OrderListAPIView.as_view(), name='order-list'),
    path('orders/<str:order_number>/', OrderRetrieveAPIView.as_view(), name='order-detail'),
    path('orders/items/<int:item_id>/return/', OrderReturnAPIView.as_view(), name='order-return'),

    # Admin endpoints
    path('admin/dashboard/', AdminDashboardStatsView.as_view(), name='admin-dashboard-stats'),
    path('admin/orders/', AdminOrderListAPIView.as_view(), name='admin-order-list'),
    path('admin/orders/<int:pk>/status/', AdminOrderStatusUpdateAPIView.as_view(), name='admin-order-status'),
    path('admin/inventory/low-stock/', AdminLowStockAPIView.as_view(), name='admin-low-stock'),
    path('admin/inventory/expiring/', AdminExpiringProductsAPIView.as_view(), name='admin-expiring'),

    # Phase 8.2 — Discount rules
    path('admin/discounts/', AdminDiscountListAPIView.as_view(), name='admin-discount-list'),
    path('admin/discounts/<int:pk>/', AdminDiscountDetailAPIView.as_view(), name='admin-discount-detail'),

    # Phase 8.3 — Abandoned carts
    path('admin/abandoned-carts/', AdminAbandonedCartsAPIView.as_view(), name='admin-abandoned-carts'),

    # Phase 9 — Analytics
    path('admin/analytics/', AdminAnalyticsAPIView.as_view(), name='admin-analytics'),
]
