from django.urls import path
from .views import ProductDetailAPIView, api_products, api_search_products, ProductRecommendationsAPIView

urlpatterns = [
    path('', api_products, name='api-products-list'),
    path('search/', api_search_products, name='api-products-search'),
    path('<slug:slug>/recommendations/', ProductRecommendationsAPIView.as_view(), name='api-product-recommendations'),
    path('<slug:slug>/', ProductDetailAPIView.as_view(), name='api-product-detail'),
]
