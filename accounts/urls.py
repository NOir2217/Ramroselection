from django.urls import path
from .views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    LogoutView,
    RegisterView,
    ProfilePreferencesView,
    AddressListCreateAPIView,
    AddressDetailAPIView
)
from django_ratelimit.decorators import ratelimit

urlpatterns = [
    # Rate limit auth endpoints: 5 per minute per IP
    path('token/', ratelimit(key='ip', rate='5/m', block=True)(CustomTokenObtainPairView.as_view()), name='token_obtain_pair'),
    path('token/refresh/', ratelimit(key='ip', rate='5/m', block=True)(CustomTokenRefreshView.as_view()), name='token_refresh'),
    path('token/logout/', ratelimit(key='ip', rate='5/m', block=True)(LogoutView.as_view()), name='token_logout'),
    path('register/', ratelimit(key='ip', rate='5/m', block=True)(RegisterView.as_view()), name='register'),
    path('preferences/', ProfilePreferencesView.as_view(), name='profile_preferences'),
    path('addresses/', AddressListCreateAPIView.as_view(), name='address_list_create'),
    path('addresses/<int:pk>/', AddressDetailAPIView.as_view(), name='address_detail'),
]
