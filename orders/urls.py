from django.urls import path
from .views import (
    CartAPIView, CartItemAPIView, CartItemDetailAPIView, CheckoutAPIView,
    OrderListAPIView, OrderRetrieveAPIView, OrderReturnAPIView
)

urlpatterns = [
    path('cart/', CartAPIView.as_view(), name='cart-detail'),
    path('cart/items/', CartItemAPIView.as_view(), name='cart-item-list'),
    path('cart/items/<int:pk>/', CartItemDetailAPIView.as_view(), name='cart-item-detail'),
    path('checkout/', CheckoutAPIView.as_view(), name='checkout'),
    
    path('orders/', OrderListAPIView.as_view(), name='order-list'),
    path('orders/<str:order_number>/', OrderRetrieveAPIView.as_view(), name='order-detail'),
    path('orders/items/<int:item_id>/return/', OrderReturnAPIView.as_view(), name='order-return'),
]
