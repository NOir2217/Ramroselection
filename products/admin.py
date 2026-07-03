from django.contrib import admin
from .models import Category, Product, ProductVariant, ProductImage, SizeGuide, Collection

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('variant_type', 'size', 'color', 'color_hex', 'shade', 'shade_hex', 'volume', 'stock_quantity', 'low_stock_threshold', 'extra_price', 'sku_suffix')

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('variant', 'image_url', 'image_type', 'display_order')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'parent')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'category', 'product_type', 'rating', 'sku', 'is_new', 'is_sale')
    list_filter = ('category', 'product_type', 'is_new', 'is_sale')
    search_fields = ('name', 'sku', 'brand')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductVariantInline, ProductImageInline]

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'variant_type', 'size', 'color', 'shade', 'volume', 'stock_quantity')
    list_filter = ('variant_type',)
    search_fields = ('product__name', 'sku_suffix')

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'variant', 'image_type', 'display_order')
    list_filter = ('image_type',)

@admin.register(SizeGuide)
class SizeGuideAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'brand')
    search_fields = ('category__name', 'brand')

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'is_active', 'display_order')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('products',)
