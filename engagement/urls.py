from django.urls import path
from .views import WishlistAPIView, WishlistItemAPIView, RecentlyViewedAPIView

urlpatterns = [
    path('wishlist/', WishlistAPIView.as_view(), name='wishlist-list'),
    path('wishlist/items/<int:pk>/', WishlistItemAPIView.as_view(), name='wishlist-detail'),
    path('recently-viewed/', RecentlyViewedAPIView.as_view(), name='recently-viewed'),
]
