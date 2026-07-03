from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories')

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        if self.parent:
            return f"{self.parent} -> {self.name}"
        return self.name

class Product(models.Model):
    PRODUCT_TYPE_CHOICES = [
        ('clothing', 'Clothing'),
        ('cosmetics', 'Cosmetics'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0, db_index=True)
    review_count = models.IntegerField(default=0)
    image = models.URLField(max_length=500)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products', db_index=True)
    is_new = models.BooleanField(default=False, db_index=True)
    is_sale = models.BooleanField(default=False, db_index=True)
    sale_percentage = models.IntegerField(null=True, blank=True)

    # Rich metadata
    description = models.TextField()
    brand = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES, default='other')
    material_or_ingredients = models.TextField(help_text="Fabric list or ingredient list")
    is_vegan = models.BooleanField(null=True, blank=True, db_index=True) # cosmetics only
    is_cruelty_free = models.BooleanField(null=True, blank=True, db_index=True) # cosmetics only
    is_hypoallergenic = models.BooleanField(null=True, blank=True)
    season = models.CharField(max_length=50, null=True, blank=True) # clothing only
    fit = models.CharField(max_length=50, null=True, blank=True) # e.g. slim/oversized/regular
    skin_type = models.CharField(max_length=50, null=True, blank=True, db_index=True) # oily/dry/sensitive/combination
    finish = models.CharField(max_length=50, null=True, blank=True, db_index=True) # matte/dewy/glossy
    sku = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    related_products = models.ManyToManyField('self', blank=True, symmetrical=True)

    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    VARIANT_TYPE_CHOICES = [
        ('size_color', 'Size & Color'),
        ('shade_finish_volume', 'Shade, Finish & Volume'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    variant_type = models.CharField(max_length=50, choices=VARIANT_TYPE_CHOICES)
    size = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    color = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    color_hex = models.CharField(max_length=7, null=True, blank=True) # for swatch
    shade = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    shade_hex = models.CharField(max_length=7, null=True, blank=True) # for swatch
    volume = models.CharField(max_length=50, null=True, blank=True)
    stock_quantity = models.IntegerField(default=0, db_index=True)
    low_stock_threshold = models.IntegerField(default=5)
    batch_number = models.CharField(max_length=100, null=True, blank=True) # cosmetics
    expiration_date = models.DateField(null=True, blank=True, db_index=True) # cosmetics
    extra_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    sku_suffix = models.CharField(max_length=100)

    def __str__(self):
        details = []
        if self.size: details.append(f"Size: {self.size}")
        if self.color: details.append(f"Color: {self.color}")
        if self.shade: details.append(f"Shade: {self.shade}")
        if self.volume: details.append(f"Volume: {self.volume}")
        return f"{self.product.name} Variant ({', '.join(details)})"

class ProductImage(models.Model):
    IMAGE_TYPE_CHOICES = [
        ('primary', 'Primary'),
        ('angle', 'Angle'),
        ('swatch', 'Swatch'),
        ('on_model', 'On Model'),
        ('user_upload', 'User Upload'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_images')
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True, related_name='images')
    image_url = models.URLField(max_length=500)
    image_type = models.CharField(max_length=20, choices=IMAGE_TYPE_CHOICES, default='angle')
    display_order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} Image ({self.image_type})"

class SizeGuide(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='size_guides')
    brand = models.CharField(max_length=255, null=True, blank=True)
    chart_data = models.JSONField(help_text="JSON list of size, chest_in, chest_cm, waist_in, etc.")

    def __str__(self):
        brand_str = f" - {self.brand}" if self.brand else ""
        return f"Size Guide: {self.category.name}{brand_str}"

class Collection(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    banner_image_url = models.URLField(max_length=500, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    products = models.ManyToManyField(Product, blank=True, related_name='collections')

    def __str__(self):
        return self.name
