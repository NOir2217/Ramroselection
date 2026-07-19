from django.urls import path
from django_ratelimit.decorators import ratelimit
from .views import WishlistAPIView, WishlistItemAPIView, RecentlyViewedAPIView

urlpatterns = [
    path('wishlist/', ratelimit(key='ip', rate='20/m', block=True)(WishlistAPIView.as_view()), name='wishlist-list'),
    path('wishlist/items/<int:pk>/', WishlistItemAPIView.as_view(), name='wishlist-detail'),
    path('recently-viewed/', ratelimit(key='ip', rate='60/m', block=True)(RecentlyViewedAPIView.as_view()), name='recently-viewed'),
]
