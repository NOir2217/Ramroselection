from rest_framework import serializers
from .models import Product, ProductVariant, ProductImage, SizeGuide, Category, Collection
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
                guide = obj.category.size_guides.filter(brand__isnull=True).first()
            if guide:
                return SizeGuideSerializer(guide).data
        return None


class CollectionSerializer(serializers.ModelSerializer):
    productCount = serializers.SerializerMethodField()
    products = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    bannerImageUrl = serializers.CharField(source='banner_image_url', required=False, allow_blank=True, allow_null=True)
    isActive = serializers.BooleanField(source='is_active', required=False)
    displayOrder = serializers.IntegerField(source='display_order', required=False)

    class Meta:
        model = Collection
        fields = ('id', 'name', 'slug', 'description', 'bannerImageUrl', 'isActive', 'displayOrder', 'productCount', 'products')

    def get_productCount(self, obj):
        return obj.products.count()

    def create(self, validated_data):
        product_ids = validated_data.pop('products', [])
        collection = Collection.objects.create(**validated_data)
        collection.products.set(product_ids)
        return collection

    def update(self, instance, validated_data):
        product_ids = validated_data.pop('products', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if product_ids is not None:
            instance.products.set(product_ids)
        return instance
