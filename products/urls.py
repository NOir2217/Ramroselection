from django.urls import path
from .views import (
    ProductDetailAPIView, ProductListAPIView, api_search_products, ProductRecommendationsAPIView,
    AdminProductListAPIView, AdminVariantAPIView, AdminBulkVariantCreateAPIView,
    AdminBulkImageUploadAPIView, AdminReviewModerationAPIView,
    AdminCollectionListAPIView, AdminCollectionDetailAPIView,
)

urlpatterns = [
    path('', ProductListAPIView.as_view(), name='api-products-list'),
    path('search/', api_search_products, name='api-products-search'),
    path('<slug:slug>/recommendations/', ProductRecommendationsAPIView.as_view(), name='api-product-recommendations'),
    path('<slug:slug>/', ProductDetailAPIView.as_view(), name='api-product-detail'),

    # Admin endpoints
    path('admin/list/', AdminProductListAPIView.as_view(), name='admin-product-list'),
    path('admin/<int:product_id>/variants/', AdminVariantAPIView.as_view(), name='admin-variant-manage'),
    path('admin/<int:product_id>/variants/bulk/', AdminBulkVariantCreateAPIView.as_view(), name='admin-variant-bulk'),
    path('admin/<int:product_id>/images/', AdminBulkImageUploadAPIView.as_view(), name='admin-bulk-images'),
    path('admin/reviews/', AdminReviewModerationAPIView.as_view(), name='admin-review-list'),
    path('admin/reviews/<int:pk>/', AdminReviewModerationAPIView.as_view(), name='admin-review-moderate'),

    # Phase 8.1 — Collection endpoints
    path('admin/collections/', AdminCollectionListAPIView.as_view(), name='admin-collection-list'),
    path('admin/collections/<int:pk>/', AdminCollectionDetailAPIView.as_view(), name='admin-collection-detail'),
]
