from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Product, Collection
from .serializers import ProductSerializer
from django.db.models import Q, Count
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer
    lookup_field = 'slug'
    permission_classes = [AllowAny]

from rest_framework.pagination import PageNumberPagination

class ProductPagination(PageNumberPagination):
    page_size = 40
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProductListAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    pagination_class = ProductPagination

    def get_queryset(self):
        qs = Product.objects.select_related('category').all()
        params = self.request.GET

        q = params.get('q')
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(brand__icontains=q) | Q(category__name__icontains=q))

        category = params.get('category')
        if category:
            qs = qs.filter(Q(category__slug=category) | Q(category__parent__slug=category))

        skin_type = params.get('skin_type')
        if skin_type:
            qs = qs.filter(skin_type__icontains=skin_type)

        finish = params.get('finish')
        if finish:
            qs = qs.filter(finish__icontains=finish)

        is_vegan = params.get('is_vegan')
        if is_vegan == 'true':
            qs = qs.filter(is_vegan=True)

        is_cruelty_free = params.get('is_cruelty_free')
        if is_cruelty_free == 'true':
            qs = qs.filter(is_cruelty_free=True)

        size = params.get('size')
        if size:
            qs = qs.filter(variants__size__iexact=size, variants__stock_quantity__gt=0).distinct()

        color = params.get('color')
        if color:
            qs = qs.filter(variants__color__iexact=color, variants__stock_quantity__gt=0).distinct()

        return qs

def _serialize_product(p):
    item = {
        'id': str(p.id),
        'name': p.name,
        'price': float(p.price),
        'rating': float(p.rating),
        'reviewCount': p.review_count,
        'image': p.image,
        'category': p.category.name if p.category else '',
        'slug': p.slug,
    }
    if p.original_price is not None:
        item['originalPrice'] = float(p.original_price)
    if p.is_new:
        item['isNew'] = True
    if p.is_sale:
        item['isSale'] = True
    if p.sale_percentage is not None:
        item['salePercentage'] = p.sale_percentage
    return item

def api_search_products(request):
    q = request.GET.get('q', '')
    if len(q) < 2:
        return JsonResponse([], safe=False)
        
    products = Product.objects.filter(
        Q(name__icontains=q) | 
        Q(brand__icontains=q) | 
        Q(category__name__icontains=q)
    )[:8]
    
    data = [_serialize_product(p) for p in products]
    return JsonResponse(data, safe=False)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny as DRFAllowAny
from rest_framework import status

class ProductRecommendationsAPIView(APIView):
    permission_classes = [DRFAllowAny]

    @method_decorator(cache_page(60 * 15))  # 15 min cache
    def get(self, request, slug):
        from django.shortcuts import get_object_or_404

        product = get_object_or_404(Product, slug=slug)
        recs = []

        # 1. Curated related products
        related = product.related_products.all()[:8]
        recs.extend(related)

        # 2. Fill remaining slots with same-category products
        if len(recs) < 8 and product.category:
            exclude_ids = [product.id] + [r.id for r in recs]
            same_cat = (
                Product.objects
                .filter(category=product.category)
                .exclude(id__in=exclude_ids)
                .order_by('-rating')[:8 - len(recs)]
            )
            recs.extend(same_cat)

        data = [_serialize_product(p) for p in recs]
        return Response(data)


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 7 — Admin Product Views
# ─────────────────────────────────────────────────────────────────────────────

from rest_framework.permissions import BasePermission
from .serializers import ProductVariantSerializer, ProductImageSerializer, CollectionSerializer


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff


class AdminProductListAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '')
        products = Product.objects.select_related('category').annotate(
            variant_count=Count('variants'),
            image_count=Count('product_images'),
        ).order_by('name')

        if search:
            products = products.filter(
                Q(name__icontains=search) |
                Q(sku__icontains=search) |
                Q(brand__icontains=search)
            )

        data = []
        for p in products:
            low_stock = p.variants.filter(stock_quantity__lte=5).count()
            data.append({
                'id': p.id,
                'name': p.name,
                'sku': p.sku,
                'slug': p.slug,
                'price': float(p.price),
                'image': p.image,
                'productType': p.product_type,
                'category': p.category.name if p.category else '',
                'variantCount': p.variant_count,
                'imageCount': p.image_count,
                'lowStockVariants': low_stock,
            })

        return Response(data)


class AdminVariantAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        variants = product.variants.all()
        serializer = ProductVariantSerializer(variants, many=True)
        return Response(serializer.data)

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        data = request.data.copy()
        data['product'] = product.id

        serializer = ProductVariantSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, product_id):
        variant = get_object_or_404(ProductVariant, id=request.data.get('id'), product_id=product_id)
        serializer = ProductVariantSerializer(variant, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, product_id):
        variant = get_object_or_404(ProductVariant, id=request.data.get('id'), product_id=product_id)
        variant.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminBulkVariantCreateAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        variants_data = request.data.get('variants', [])

        created = []
        errors = []
        for v_data in variants_data:
            v_data['product'] = product.id
            v_data['variant_type'] = product.variants.first().variant_type if product.variants.exists() else 'size_color'
            serializer = ProductVariantSerializer(data=v_data)
            if serializer.is_valid():
                serializer.save()
                created.append(serializer.data)
            else:
                errors.append(serializer.errors)

        return Response({
            'created': created,
            'errors': errors,
            'createdCount': len(created),
        }, status=status.HTTP_201_CREATED if created else status.HTTP_400_BAD_REQUEST)


class AdminBulkImageUploadAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        images_data = request.data.get('images', [])

        created = []
        for img_data in images_data:
            img_data['product'] = product.id
            serializer = ProductImageSerializer(data=img_data)
            if serializer.is_valid():
                serializer.save()
                created.append(serializer.data)

        return Response({
            'created': created,
            'createdCount': len(created),
        }, status=status.HTTP_201_CREATED)

    def patch(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        orders = request.data.get('imageOrders', [])

        for item in orders:
            ProductImage.objects.filter(id=item['id'], product=product).update(display_order=item['displayOrder'])

        return Response({'status': 'reordered'})


class AdminReviewModerationAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk=None):
        from engagement.models import Review
        pending = Review.objects.filter(is_approved=False).select_related('product', 'customer').order_by('-created_at')

        data = []
        for r in pending:
            data.append({
                'id': r.id,
                'productName': r.product.name,
                'customerName': r.customer.user.username if r.customer else 'Guest',
                'rating': r.rating,
                'title': r.title,
                'body': r.body,
                'photoUrls': r.photo_urls,
                'createdAt': r.created_at.isoformat(),
            })
        return Response(data)

    def patch(self, request, pk):
        from engagement.models import Review
        review = get_object_or_404(Review, id=pk)
        review.is_approved = request.data.get('isApproved', True)
        review.save()
        return Response({'id': review.id, 'isApproved': review.is_approved})


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 8.1 — Admin Collection Views
# ─────────────────────────────────────────────────────────────────────────────

class AdminCollectionListAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        search = request.GET.get('search', '')
        collections = Collection.objects.all().order_by('display_order', 'name')

        if search:
            collections = collections.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(products__name__icontains=search)
            ).distinct()

        data = []
        for c in collections:
            data.append({
                'id': c.id,
                'name': c.name,
                'slug': c.slug,
                'description': c.description,
                'bannerImageUrl': c.banner_image_url,
                'isActive': c.is_active,
                'displayOrder': c.display_order,
                'productCount': c.products.count(),
            })
        return Response(data)

    def post(self, request):
        serializer = CollectionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminCollectionDetailAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        collection = get_object_or_404(Collection, id=pk)
        serializer = CollectionSerializer(collection)
        return Response(serializer.data)

    def patch(self, request, pk):
        collection = get_object_or_404(Collection, id=pk)
        serializer = CollectionSerializer(collection, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        collection = get_object_or_404(Collection, id=pk)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
