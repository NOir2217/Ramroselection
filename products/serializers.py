from rest_framework import serializers
from .models import Product, ProductVariant, ProductImage, SizeGuide, Category, Collection
from engagement.models import Review

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = '__all__'
        read_only_fields = ('product',)

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'
        read_only_fields = ('product',)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if instance.image_url:
            val = str(instance.image_url)
            if not (val.startswith('http://') or val.startswith('https://')):
                request = self.context.get('request')
                if request:
                    rep['image_url'] = request.build_absolute_uri(instance.image_url.url)
                else:
                    rep['image_url'] = instance.image_url.url
        return rep

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

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if instance.image:
            val = str(instance.image)
            if not (val.startswith('http://') or val.startswith('https://')):
                request = self.context.get('request')
                if request:
                    rep['image'] = request.build_absolute_uri(instance.image.url)
                else:
                    rep['image'] = instance.image.url
        return rep


    def get_reviews(self, obj):
        # Use prefetched approved_reviews if available (from list views),
        # otherwise fall back to a DB query (detail views).
        if hasattr(obj, 'approved_reviews'):
            approved_reviews = obj.approved_reviews
        else:
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
