from django.http import JsonResponse
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Product
from .serializers import ProductSerializer

class ProductDetailAPIView(generics.RetrieveAPIView):
    """
    Returns full product details including nested variants, images, reviews, and size guide.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'slug'
    permission_classes = [AllowAny]

from django.http import JsonResponse
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Product
from .serializers import ProductSerializer
from django.db.models import Q

class ProductDetailAPIView(generics.RetrieveAPIView):
    """
    Returns full product details including nested variants, images, reviews, and size guide.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'slug'
    permission_classes = [AllowAny]

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

def api_products(request):
    """
    API endpoint that retrieves products with filtering.
    """
    products = Product.objects.all()
    
    # Text Search
    q = request.GET.get('q')
    if q:
        products = products.filter(
            Q(name__icontains=q) | 
            Q(brand__icontains=q) | 
            Q(category__name__icontains=q)
        )
        
    # Standard Filters
    category = request.GET.get('category')
    if category:
        products = products.filter(Q(category__slug=category) | Q(category__parent__slug=category))
        
    skin_type = request.GET.get('skin_type')
    if skin_type:
        products = products.filter(skin_type__icontains=skin_type)
        
    finish = request.GET.get('finish')
    if finish:
        products = products.filter(finish__icontains=finish)
        
    is_vegan = request.GET.get('is_vegan')
    if is_vegan == 'true':
        products = products.filter(is_vegan=True)
        
    is_cruelty_free = request.GET.get('is_cruelty_free')
    if is_cruelty_free == 'true':
        products = products.filter(is_cruelty_free=True)
        
    # Variant Filters
    size = request.GET.get('size')
    if size:
        products = products.filter(variants__size__iexact=size, variants__stock_quantity__gt=0).distinct()
        
    color = request.GET.get('color')
    if color:
        products = products.filter(variants__color__iexact=color, variants__stock_quantity__gt=0).distinct()

    data = [_serialize_product(p) for p in products]
    return JsonResponse(data, safe=False)

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

class ProductRecommendationsAPIView(APIView):
    """
    GET /api/products/<slug>/recommendations/
    Returns up to 8 recommended products:
      1. Manually curated related_products (M2M) first.
      2. Falls back to same-category products, excluding self.
    """
    permission_classes = [DRFAllowAny]

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
