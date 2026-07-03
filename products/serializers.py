from rest_framework import serializers
from .models import Product, ProductVariant, ProductImage, SizeGuide, Category
from engagement.models import Review

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = '__all__'

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'

class SizeGuideSerializer(serializers.ModelSerializer):
    categoryName = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = SizeGuide
        fields = ('id', 'categoryName', 'brand', 'chart_data')

class ReviewSerializer(serializers.ModelSerializer):
    customerName = serializers.CharField(source='customer.user.username', read_only=True, default='Guest')
    
    class Meta:
        model = Review
        fields = ('id', 'customerName', 'rating', 'title', 'body', 'photo_urls', 'created_at')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(source='product_images', many=True, read_only=True)
    reviews = serializers.SerializerMethodField()
    sizeGuide = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_reviews(self, obj):
        # Only return approved reviews for the public API
        approved_reviews = obj.reviews.filter(is_approved=True).order_by('-created_at')
        return ReviewSerializer(approved_reviews, many=True).data

    def get_sizeGuide(self, obj):
        if obj.product_type == 'clothing' and obj.category:
            guide = obj.category.size_guides.filter(brand=obj.brand).first()
            if not guide:
                # Fallback to category default size guide
                guide = obj.category.size_guides.filter(brand__isnull=True).first()
            if guide:
                return SizeGuideSerializer(guide).data
        return None
