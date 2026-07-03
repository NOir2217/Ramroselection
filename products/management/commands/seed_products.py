from django.core.management.base import BaseCommand
from django.utils.text import slugify
from products.models import Category, Product, ProductVariant, ProductImage, SizeGuide, Collection
from orders.models import DiscountRule
from engagement.models import Review
import random


REVIEW_TITLES = [
    "Absolutely love it!", "Great quality", "Worth every penny",
    "Exceeded my expectations", "Highly recommend", "Good but not perfect",
    "Decent product", "Not bad for the price", "Amazing!", "Would buy again"
]
REVIEW_BODIES = [
    "This is exactly what I was looking for. The quality is outstanding.",
    "Very happy with this purchase. Fast delivery and great packaging.",
    "The product looks exactly like the photos. Really satisfied.",
    "Good value for money. I've been using it for a week now and it works great.",
    "Slightly different from what I expected but still a solid product overall.",
    "Not entirely happy but it does the job. May try a different brand next time.",
    "Excellent! Will definitely order again.",
    "The texture and finish are perfect. Totally recommend to everyone.",
    "It's okay. Nothing extraordinary but gets the job done.",
    "My skin loves this. Been using for 2 weeks and already see results.",
]


class Command(BaseCommand):
    help = 'Seeds the database with realistic dummy data for products, variants, images, reviews, size guides, discounts, and collections'

    def handle(self, *args, **kwargs):
        self.stdout.write('Flushing existing data...')
        Collection.objects.all().delete()
        DiscountRule.objects.all().delete()
        Review.objects.all().delete()
        ProductImage.objects.all().delete()
        ProductVariant.objects.all().delete()
        SizeGuide.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Flush complete.'))

        # ─── CATEGORIES ────────────────────────────────────────────────────────
        clothing = Category.objects.create(name='Clothing', slug='clothing')
        cosmetics = Category.objects.create(name='Cosmetics', slug='cosmetics')

        tops = Category.objects.create(name='Tops', slug='tops', parent=clothing)
        dresses = Category.objects.create(name='Dresses', slug='dresses', parent=clothing)
        bags = Category.objects.create(name='Bags', slug='bags', parent=clothing)

        makeup = Category.objects.create(name='Makeup', slug='makeup', parent=cosmetics)
        hair = Category.objects.create(name='Hair', slug='hair', parent=cosmetics)
        nails = Category.objects.create(name='Nails', slug='nails', parent=cosmetics)
        cream = Category.objects.create(name='Cream', slug='cream', parent=cosmetics)

        self.stdout.write('Categories created.')

        # ─── SIZE GUIDES ────────────────────────────────────────────────────────
        SizeGuide.objects.create(
            category=tops,
            brand=None,
            chart_data=[
                {"size": "XS", "chest_in": 32, "chest_cm": 81, "waist_in": 25, "waist_cm": 64},
                {"size": "S",  "chest_in": 34, "chest_cm": 86, "waist_in": 27, "waist_cm": 69},
                {"size": "M",  "chest_in": 36, "chest_cm": 91, "waist_in": 29, "waist_cm": 74},
                {"size": "L",  "chest_in": 38, "chest_cm": 97, "waist_in": 31, "waist_cm": 79},
                {"size": "XL", "chest_in": 41, "chest_cm": 104, "waist_in": 34, "waist_cm": 86},
            ]
        )
        SizeGuide.objects.create(
            category=dresses,
            brand=None,
            chart_data=[
                {"size": "XS", "chest_in": 33, "chest_cm": 84, "waist_in": 26, "waist_cm": 66, "hip_in": 36, "hip_cm": 91},
                {"size": "S",  "chest_in": 35, "chest_cm": 89, "waist_in": 28, "waist_cm": 71, "hip_in": 38, "hip_cm": 97},
                {"size": "M",  "chest_in": 37, "chest_cm": 94, "waist_in": 30, "waist_cm": 76, "hip_in": 40, "hip_cm": 102},
                {"size": "L",  "chest_in": 39, "chest_cm": 99, "waist_in": 32, "waist_cm": 81, "hip_in": 42, "hip_cm": 107},
                {"size": "XL", "chest_in": 42, "chest_cm": 107, "waist_in": 35, "waist_cm": 89, "hip_in": 45, "hip_cm": 114},
            ]
        )
        self.stdout.write('Size guides created.')

        # ─── DISCOUNT RULES ─────────────────────────────────────────────────────
        DiscountRule.objects.create(
            code='SAVE10',
            rule_type='percent_off',
            config={'percent': 10, 'applies_to': 'cosmetics'},
            is_active=True,
        )
        DiscountRule.objects.create(
            code='BUNDLE2',
            rule_type='buy_x_get_y',
            config={'buy': 2, 'get': 1, 'category_slug': 'makeup'},
            is_active=True,
        )
        DiscountRule.objects.create(
            code=None,
            rule_type='percent_off',
            config={'percent': 5, 'applies_to': 'all'},
            is_active=True,
        )
        self.stdout.write('Discount rules created.')

        # ─── PRODUCTS ───────────────────────────────────────────────────────────
        products_data = [
            # ── TOPS ──
            {
                'name': 'Classic White Linen Shirt',
                'category': tops, 'product_type': 'clothing',
                'price': 2499, 'original_price': 3499,
                'rating': 4.5, 'review_count': 89, 'is_sale': True, 'sale_percentage': 29,
                'brand': 'Zephyr', 'description': 'A breathable white linen shirt perfect for summer.',
                'material_or_ingredients': '100% Linen', 'season': 'Summer', 'fit': 'Regular',
                'images': [
                    {'url': 'https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=600&h=750&fit=crop', 'type': 'primary'},
                    {'url': 'https://images.unsplash.com/photo-1607345366928-199ea26cfe3e?w=600&h=750&fit=crop', 'type': 'angle'},
                    {'url': 'https://images.unsplash.com/photo-1506634572416-48cdfe530110?w=600&h=750&fit=crop', 'type': 'on_model'},
                ],
                'variants': [
                    {'size': 'S', 'color': 'White', 'color_hex': '#FFFFFF', 'stock': 15},
                    {'size': 'M', 'color': 'White', 'color_hex': '#FFFFFF', 'stock': 20},
                    {'size': 'L', 'color': 'White', 'color_hex': '#FFFFFF', 'stock': 10},
                    {'size': 'XL', 'color': 'White', 'color_hex': '#FFFFFF', 'stock': 5},
                ],
                'popular': True,
            },
            {
                'name': 'Floral Crop Top',
                'category': tops, 'product_type': 'clothing',
                'price': 1299, 'rating': 4.2, 'review_count': 54, 'is_new': True,
                'brand': 'Bloom', 'description': 'A vibrant floral crop top for casual outings.',
                'material_or_ingredients': '95% Cotton, 5% Elastane', 'season': 'Summer', 'fit': 'Slim',
                'images': [
                    {'url': 'https://images.unsplash.com/photo-1551163943-3f6a855d1153?w=600&h=750&fit=crop', 'type': 'primary'},
                    {'url': 'https://images.unsplash.com/photo-1562572159-4efd90078d23?w=600&h=750&fit=crop', 'type': 'angle'},
                    {'url': 'https://images.unsplash.com/photo-1539109136881-3be0616acf4b?w=600&h=750&fit=crop', 'type': 'on_model'},
                ],
                'variants': [
                    {'size': 'XS', 'color': 'Pink', 'color_hex': '#FFB6C1', 'stock': 12},
                    {'size': 'S',  'color': 'Pink', 'color_hex': '#FFB6C1', 'stock': 18},
                    {'size': 'M',  'color': 'Pink', 'color_hex': '#FFB6C1', 'stock': 8},
                ],
                'popular': False,
            },
            {
                'name': 'Striped Oversized Tee',
                'category': tops, 'product_type': 'clothing',
                'price': 1599, 'rating': 4.3, 'review_count': 73,
                'brand': 'Stripes & Co.', 'description': 'A relaxed-fit striped tee, great for layering.',
                'material_or_ingredients': '100% Cotton', 'season': 'All Season', 'fit': 'Oversized',
                'images': [
                    {'url': 'https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?w=600&h=750&fit=crop', 'type': 'primary'},
                    {'url': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600&h=750&fit=crop', 'type': 'angle'},
                ],
                'variants': [
                    {'size': 'S',  'color': 'Navy', 'color_hex': '#001F5B', 'stock': 10},
                    {'size': 'M',  'color': 'Navy', 'color_hex': '#001F5B', 'stock': 14},
                    {'size': 'L',  'color': 'Navy', 'color_hex': '#001F5B', 'stock': 9},
                    {'size': 'XL', 'color': 'Grey', 'color_hex': '#808080', 'stock': 6},
                ],
                'popular': True,
            },
            {
                'name': 'Silk Blend Blouse',
                'category': tops, 'product_type': 'clothing',
                'price': 3199, 'original_price': 4199, 'rating': 4.6, 'review_count': 112,
                'is_sale': True, 'sale_percentage': 24,
                'brand': 'Luxe Edit', 'description': 'An elegant silk-blend blouse for office or evening.',
                'material_or_ingredients': '70% Silk, 30% Polyester', 'season': 'All Season', 'fit': 'Regular',
                'images': [
                    {'url': 'https://images.unsplash.com/photo-1568252542512-9fe8fe9c87bb?w=600&h=750&fit=crop', 'type': 'primary'},
                    {'url': 'https://images.unsplash.com/photo-1504703395950-b89145a5425b?w=600&h=750&fit=crop', 'type': 'angle'},
                    {'url': 'https://images.unsplash.com/photo-1529139574466-a303027c1d8b?w=600&h=750&fit=crop', 'type': 'on_model'},
                ],
                'variants': [
                    {'size': 'S',  'color': 'Ivory', 'color_hex': '#FFFFF0', 'stock': 8},
                    {'size': 'M',  'color': 'Ivory', 'color_hex': '#FFFFF0', 'stock': 11},
                    {'size': 'L',  'color': 'Blush', 'color_hex': '#FFB7B2', 'stock': 7},
                ],
                'popular': True,
            },
            # ── DRESSES ──
            {
                'name': 'Boho Maxi Dress',
                'category': dresses, 'product_type': 'clothing',
                'price': 3999, 'rating': 4.7, 'review_count': 145, 'is_new': True,
                'brand': 'Terra', 'description': 'A free-flowing boho maxi dress with floral prints.',
                'material_or_ingredients': '100% Viscose', 'season': 'Summer', 'fit': 'Loose',
                'images': [
                    {'url': 'https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=600&h=750&fit=crop', 'type': 'primary'},
                    {'url': 'https://images.unsplash.com/photo-1485968579580-b6d095142e6e?w=600&h=750&fit=crop', 'type': 'angle'},
                    {'url': 'https://images.unsplash.com/photo-1520975916090-3105956dac38?w=600&h=750&fit=crop', 'type': 'on_model'},
                ],
                'variants': [
                    {'size': 'XS', 'color': 'Terracotta', 'color_hex': '#E2725B', 'stock': 5},
                    {'size': 'S',  'color': 'Terracotta', 'color_hex': '#E2725B', 'stock': 9},
                    {'size': 'M',  'color': 'Terracotta', 'color_hex': '#E2725B', 'stock': 12},
                    {'size': 'L',  'color': 'Sage',       'color_hex': '#B2AC88', 'stock': 7},
                ],
                'popular': True,
            },
            {
                'name': 'Little Black Dress',
                'category': dresses, 'product_type': 'clothing',
                'price': 4499, 'original_price': 5999, 'rating': 4.8, 'review_count': 201,
                'is_sale': True, 'sale_percentage': 25,
                'brand': 'Noir Atelier', 'description': 'A timeless little black dress for every occasion.',
                'material_or_ingredients': '80% Polyester, 20% Spandex', 'season': 'All Season', 'fit': 'Slim',
                'images': [
                    {'url': 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=600&h=750&fit=crop', 'type': 'primary'},
                    {'url': 'https://images.unsplash.com/photo-1566206091558-7f218b696731?w=600&h=750&fit=crop', 'type': 'angle'},
                    {'url': 'https://images.unsplash.com/photo-1518310383802-640c2de311b2?w=600&h=750&fit=crop', 'type': 'on_model'},
                ],
                'variants': [
                    {'size': 'XS', 'color': 'Black', 'color_hex': '#000000', 'stock': 10},
                    {'size': 'S',  'color': 'Black', 'color_hex': '#000000', 'stock': 15},
                    {'size': 'M',  'color': 'Black', 'color_hex': '#000000', 'stock': 13},
                    {'size': 'L',  'color': 'Black', 'color_hex': '#000000', 'stock': 8},
                ],
                'popular': True,
            },
            {
                'name': 'Pastel Wrap Dress',
                'category': dresses, 'product_type': 'clothing',
                'price': 2999, 'rating': 4.4, 'review_count': 66,
                'brand': 'Pastelle', 'description': 'A chic pastel wrap dress for brunch or casual events.',
                'material_or_ingredients': '100% Chiffon', 'season': 'Spring', 'fit': 'Wrap',
                'images': [
                    {'url': 'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=600&h=750&fit=crop', 'type': 'primary'},
                    {'url': 'https://images.unsplash.com/photo-1594938298603-c8148c4b4d74?w=600&h=750&fit=crop', 'type': 'angle'},
                ],
                'variants': [
                    {'size': 'S', 'color': 'Lavender', 'color_hex': '#E6E6FA', 'stock': 8},
                    {'size': 'M', 'color': 'Lavender', 'color_hex': '#E6E6FA', 'stock': 11},
                    {'size': 'L', 'color': 'Mint',     'color_hex': '#98FF98', 'stock': 6},
                ],
                'popular': False,
            },
            # ── BAGS ──
            {
                'name': 'Premium Leather Handbag',
                'category': bags, 'product_type': 'clothing',
                'price': 8999, 'original_price': 12999, 'rating': 4.5, 'review_count': 128,
                'is_sale': True, 'sale_percentage': 31,
                'brand': 'Luxe Leather Co.', 'description': 'A handcrafted full-grain leather handbag.',
                'material_or_ingredients': '100% Full-Grain Leather',
                'images': [
                    {'url': 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=600&h=750&fit=crop', 'type': 'primary'},
                    {'url': 'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=600&h=750&fit=crop', 'type': 'angle'},
                    {'url': 'https://images.unsplash.com/photo-1566150905458-1bf1fc113f0d?w=600&h=750&fit=crop', 'type': 'on_model'},
                ],
                'variants': [
                    {'size': 'One Size', 'color': 'Tan',   'color_hex': '#D2B48C', 'stock': 8},
                    {'size': 'One Size', 'color': 'Black', 'color_hex': '#000000', 'stock': 12},
                ],
                'popular': True,
            },
            {
                'name': 'Designer Crossbody Bag',
                'category': bags, 'product_type': 'clothing',
                'price': 6799, 'rating': 4.4, 'review_count': 156,
                'brand': 'Maison Edit', 'description': 'A structured crossbody bag with gold hardware.',
                'material_or_ingredients': 'Vegan Leather',
                'images': [
                    {'url': 'https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=600&h=750&fit=crop', 'type': 'primary'},
                    {'url': 'https://images.unsplash.com/photo-1601924994987-69e26d50dc26?w=600&h=750&fit=crop', 'type': 'angle'},
                ],
                'variants': [
                    {'size': 'One Size', 'color': 'Camel',  'color_hex': '#C19A6B', 'stock': 7},
                    {'size': 'One Size', 'color': 'Cognac', 'color_hex': '#9A463D', 'stock': 5},
                ],
                'popular': False,
            },
            {
                'name': 'Vintage Canvas Tote Bag',
                'category': bags, 'product_type': 'clothing',
                'price': 2999, 'rating': 4.3, 'review_count': 98, 'is_new': True,
                'brand': 'Canvas Story', 'description': 'A durable canvas tote with vintage print.',
                'material_or_ingredients': '100% Cotton Canvas',
                'images': [
                    {'url': 'https://images.unsplash.com/photo-1582134485381-ba4feb89d357?w=600&h=750&fit=crop', 'type': 'primary'},
                    {'url': 'https://images.unsplash.com/photo-1558171813-eb96e70a9044?w=600&h=750&fit=crop', 'type': 'angle'},
                ],
                'variants': [
                    {'size': 'One Size', 'color': 'Natural', 'color_hex': '#F5F5DC', 'stock': 20},
                    {'size': 'One Size', 'color': 'Black',   'color_hex': '#000000', 'stock': 15},
                ],
                'popular': False,
            },
            # ── MAKEUP ──
            {
                'name': 'Luxury Matte Lipstick',
                'category': makeup, 'product_type': 'cosmetics',
                'price': 1299, 'rating': 4.6, 'review_count': 210, 'is_new': True,
                'brand': 'Velvet Rouge', 'description': 'Long-lasting matte lipstick with vibrant pigment.',
                'material_or_ingredients': 'Castor Oil, Candelilla Wax, Vitamin E',
                'is_vegan': True, 'is_cruelty_free': True, 'finish': 'Matte',
                'images': [
                    {'url': 'https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=600&h=750&fit=crop', 'type': 'primary'},
                    {'url': 'https://images.unsplash.com/photo-1631214524020-7e18db9a8f92?w=600&h=750&fit=crop', 'type': 'angle'},
                ],
                'variants': [
                    {'shade': 'Classic Red',   'shade_hex': '#C0392B', 'volume': '3.5g', 'stock': 25},
                    {'shade': 'Berry Burst',   'shade_hex': '#8E44AD', 'volume': '3.5g', 'stock': 18},
                    {'shade': 'Nude Beige',    'shade_hex': '#D4A574', 'volume': '3.5g', 'stock': 30},
                    {'shade': 'Coral Crush',   'shade_hex': '#FF6B6B', 'volume': '3.5g', 'stock': 12},
                ],
                'popular': True,
            },
            {
                'name': 'Glossy Lip Oil',
                'category': makeup, 'product_type': 'cosmetics',
                'price': 999, 'rating': 4.4, 'review_count': 87,
                'brand': 'GlowLab', 'description': 'Nourishing lip oil for a glossy, plump look.',
                'material_or_ingredients': 'Jojoba Oil, Rose Hip Oil, Vitamin C',
                'is_vegan': True, 'is_cruelty_free': True, 'finish': 'Glossy',
                'images': [
                    {'url': 'https://images.unsplash.com/photo-1625093523002-a0fa2c88e6d5?w=600&h=750&fit=crop', 'type': 'primary'},
                    {'url': 'https://images.unsplash.com/photo-1599305090598-fe179d501227?w=600&h=750&fit=crop', 'type': 'angle'},
                ],
                'variants': [
                    {'shade': 'Crystal Clear', 'shade_hex': '#E8F4F8', 'volume': '6ml', 'stock': 22},
                    {'shade': 'Rose Petal',    'shade_hex': '#FFB7B2', 'volume': '6ml', 'stock': 19},
                    {'shade': 'Cherry Pop',    'shade_hex': '#DC143C', 'volume': '6ml', 'stock': 14},
                ],
                'popular': False,
            },
            {
                'name': 'Professional Makeup Brush Set',
                'category': makeup, 'product_type': 'cosmetics',
                'price': 3999, 'original_price': 5499, 'rating': 4.7, 'review_count': 143,
                'is_sale': True, 'sale_percentage': 27,
                'brand': 'Artistry Pro', 'description': '12-piece professional brush set with synthetic bristles.',
                'material_or_ingredients': 'Synthetic Bristles, Aluminium Ferrule, Wooden Handle',
                'is_cruelty_free': True,
                'images': [
                    {'url': 'https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=600&h=750&fit=crop', 'type': 'primary'},
                    {'url': 'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=600&h=750&fit=crop', 'type': 'angle'},
                ],
                'variants': [
                    {'shade': 'Rose Gold Set', 'shade_hex': '#B76E79', 'volume': '12pcs', 'stock': 15},
                    {'shade': 'Black Set',     'shade_hex': '#1C1C1C', 'volume': '12pcs', 'stock': 20},
                ],
                'popular': True,
            },
            {
                'name': 'Waterproof Mascara',
                'category': makeup, 'product_type': 'cosmetics',
                'price': 1599, 'rating': 4.6, 'review_count': 212,
                'brand': 'LashLux', 'description': 'Volumizing waterproof mascara for bold lashes.',
                'material_or_ingredients': 'Beeswax, Acacia Senegal, Carnauba Wax',
                'is_cruelty_free': True, 'finish': 'Matte',
                'images': [
                    {'url': 'https://images.unsplash.com/photo-1631214524020-7e18db9a8f92?w=600&h=750&fit=crop', 'type': 'primary'},
                    {'url': 'https://images.unsplash.com/photo-1583241800698-e8ab01830a6a?w=600&h=750&fit=crop', 'type': 'angle'},
                ],
                'variants': [
                    {'shade': 'Jet Black',  'shade_hex': '#0A0A0A', 'volume': '10ml', 'stock': 30},
                    {'shade': 'Brown Black','shade_hex': '#3D2B1F', 'volume': '10ml', 'stock': 18},
                ],
                'popular': True,
            },
            {
                'name': 'Dewy Foundation SPF30',
                'category': makeup, 'product_type': 'cosmetics',
                'price': 2799, 'original_price': 3499, 'rating': 4.3, 'review_count': 95,
                'is_sale': True, 'sale_percentage': 20,
                'brand': 'Skincentric', 'description': 'Buildable coverage foundation with SPF30 protection.',
                'material_or_ingredients': 'Water, Glycerin, Niacinamide, Titanium Dioxide',
                'is_vegan': True, 'is_cruelty_free': True, 'finish': 'Dewy', 'skin_type': 'dry',
                'images': [
                    {'url': 'https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=600&h=750&fit=crop', 'type': 'primary'},
                    {'url': 'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=600&h=750&fit=crop', 'type': 'angle'},
                ],
                'variants': [
                    {'shade': 'Porcelain',   'shade_hex': '#F5E6CC', 'volume': '30ml', 'stock': 12},
                    {'shade': 'Ivory',       'shade_hex': '#F2DEB3', 'volume': '30ml', 'stock': 15},
                    {'shade': 'Warm Beige',  'shade_hex': '#D4A55A', 'volume': '30ml', 'stock': 10},
                    {'shade': 'Caramel',     'shade_hex': '#8B5E3C', 'volume': '30ml', 'stock': 8},
                ],
                'popular': True,
            },
            # ── HAIR ──
            {
                'name': 'Nourishing Argan Hair Oil',
                'category': hair, 'product_type': 'cosmetics',
                'price': 1299, 'rating': 4.8, 'review_count': 234,
                'brand': 'Moroccan Glow', 'description': 'Pure argan oil for frizz-free, shiny hair.',
                'material_or_ingredients': '100% Pure Argan Oil, Vitamin E',
                'is_vegan': True, 'is_cruelty_free': True, 'is_hypoallergenic': True,
                'images': [
                    {'url': 'https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=600&h=750&fit=crop', 'type': 'primary'},
                    {'url': 'https://images.unsplash.com/photo-1527799820374-dcf8d9d4a388?w=600&h=750&fit=crop', 'type': 'angle'},
                ],
                'variants': [
                    {'shade': 'Original', 'shade_hex': '#D4A017', 'volume': '100ml', 'stock': 40},
                    {'shade': 'Original', 'shade_hex': '#D4A017', 'volume': '200ml', 'stock': 25},
                ],
                'popular': True,
            },
            {
                'name': 'Keratin Hair Mask',
                'category': hair, 'product_type': 'cosmetics',
                'price': 1799, 'rating': 4.5, 'review_count': 112, 'is_new': True,
                'brand': 'SmoothLab', 'description': 'Deep conditioning keratin mask for damaged hair.',
                'material_or_ingredients': 'Keratin, Panthenol, Shea Butter, Sweet Almond Oil',
                'is_vegan': False, 'is_cruelty_free': True,
                'images': [
                    {'url': 'https://images.unsplash.com/photo-1519415510236-718bdfcd89c8?w=600&h=750&fit=crop', 'type': 'primary'},
                    {'url': 'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=600&h=750&fit=crop', 'type': 'angle'},
                ],
                'variants': [
                    {'shade': 'Honey Repair', 'shade_hex': '#FFC04C', 'volume': '250ml', 'stock': 20},
                    {'shade': 'Honey Repair', 'shade_hex': '#FFC04C', 'volume': '500ml', 'stock': 12},
                ],
                'popular': False,
            },
            {
                'name': 'Hair Straightening Serum',
                'category': hair, 'product_type': 'cosmetics',
                'price': 1899, 'rating': 4.1, 'review_count': 78,
                'brand': 'SilkSmooth', 'description': 'Anti-frizz serum that straightens while you style.',
                'material_or_ingredients': 'Dimethicone, Cyclomethicone, Panthenol',
                'is_cruelty_free': True,
                'images': [
                    {'url': 'https://images.unsplash.com/photo-1614094082869-cd4e4b2905c7?w=600&h=750&fit=crop', 'type': 'primary'},
                ],
                'variants': [
                    {'shade': 'Clear', 'shade_hex': '#F0F8FF', 'volume': '150ml', 'stock': 18},
                ],
                'popular': False,
            },
            # ── NAILS ──
            {
                'name': 'Gel Nail Polish Kit',
                'category': nails, 'product_type': 'cosmetics',
                'price': 3499, 'original_price': 4999, 'rating': 4.3, 'review_count': 67,
                'is_sale': True, 'sale_percentage': 30,
                'brand': 'GelPerfect', 'description': 'Professional gel nail kit for salon results at home.',
                'material_or_ingredients': 'HEMA, Di-HEMA Trimethylhexyl Dicarbamate, Photoinitiator',
                'is_cruelty_free': True,
                'images': [
                    {'url': 'https://images.unsplash.com/photo-1604654894610-df63bc536371?w=600&h=750&fit=crop', 'type': 'primary'},
                    {'url': 'https://images.unsplash.com/photo-1604654894610-df63bc536371?w=600&h=750&fit=crop', 'type': 'angle'},
                ],
                'variants': [
                    {'shade': 'Cherry Red',    'shade_hex': '#C0392B', 'volume': '10ml', 'stock': 20},
                    {'shade': 'Blush Pink',    'shade_hex': '#FFB7B2', 'volume': '10ml', 'stock': 18},
                    {'shade': 'Midnight Blue', 'shade_hex': '#003366', 'volume': '10ml', 'stock': 12},
                ],
                'popular': True,
            },
            {
                'name': 'Nail Art Sticker Set',
                'category': nails, 'product_type': 'cosmetics',
                'price': 899, 'rating': 4.0, 'review_count': 54, 'is_new': True,
                'brand': 'NailArt Co.', 'description': '3D nail art stickers for creative at-home nail art.',
                'material_or_ingredients': 'Vinyl, Acrylic Adhesive',
                'is_vegan': True, 'is_cruelty_free': True,
                'images': [
                    {'url': 'https://images.unsplash.com/photo-1632345031435-8727f6897d53?w=600&h=750&fit=crop', 'type': 'primary'},
                ],
                'variants': [
                    {'shade': 'Floral Mix', 'shade_hex': '#FF9999', 'volume': '1 sheet', 'stock': 35},
                    {'shade': 'Geometric',  'shade_hex': '#888888', 'volume': '1 sheet', 'stock': 30},
                ],
                'popular': False,
            },
            {
                'name': 'Cuticle Repair Oil',
                'category': nails, 'product_type': 'cosmetics',
                'price': 699, 'rating': 4.5, 'review_count': 91,
                'brand': 'NailCare+', 'description': 'Intensive cuticle oil pen for on-the-go nail care.',
                'material_or_ingredients': 'Sweet Almond Oil, Jojoba Oil, Vitamin E, Tea Tree Extract',
                'is_vegan': True, 'is_cruelty_free': True, 'is_hypoallergenic': True,
                'images': [
                    {'url': 'https://images.unsplash.com/photo-1604654894610-df63bc536371?w=600&h=750&fit=crop', 'type': 'primary'},
                ],
                'variants': [
                    {'shade': 'Original', 'shade_hex': '#FFFACD', 'volume': '3.5ml', 'stock': 50},
                ],
                'popular': False,
            },
            # ── CREAM ──
            {
                'name': 'Anti-Aging Night Cream',
                'category': cream, 'product_type': 'cosmetics',
                'price': 4599, 'rating': 4.6, 'review_count': 92, 'is_new': True,
                'brand': 'Ageless Rx', 'description': 'Retinol-powered night cream for visible anti-aging results.',
                'material_or_ingredients': 'Retinol 0.3%, Hyaluronic Acid, Peptide Complex, Niacinamide',
                'is_vegan': False, 'is_cruelty_free': True, 'skin_type': 'all', 'finish': 'Matte',
                'images': [
                    {'url': 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=600&h=750&fit=crop', 'type': 'primary'},
                    {'url': 'https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600&h=750&fit=crop', 'type': 'angle'},
                ],
                'variants': [
                    {'shade': 'Original', 'shade_hex': '#FFF5E6', 'volume': '50ml', 'stock': 15},
                    {'shade': 'Rich',     'shade_hex': '#FFE4B5', 'volume': '100ml', 'stock': 10},
                ],
                'popular': True,
            },
            {
                'name': 'Hydrating Face Cream SPF20',
                'category': cream, 'product_type': 'cosmetics',
                'price': 3299, 'original_price': 4299, 'rating': 4.5, 'review_count': 189,
                'is_sale': True, 'sale_percentage': 23,
                'brand': 'Hydraboost', 'description': 'Lightweight daily moisturiser with SPF20 protection.',
                'material_or_ingredients': 'Water, Glycerin, Cetearyl Alcohol, SPF20 Filters',
                'is_vegan': True, 'is_cruelty_free': True, 'skin_type': 'combination', 'finish': 'Dewy',
                'images': [
                    {'url': 'https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600&h=750&fit=crop', 'type': 'primary'},
                    {'url': 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=600&h=750&fit=crop', 'type': 'angle'},
                ],
                'variants': [
                    {'shade': 'Original', 'shade_hex': '#FAEBD7', 'volume': '50ml', 'stock': 22},
                    {'shade': 'Light',    'shade_hex': '#FFF8F0', 'volume': '75ml', 'stock': 17},
                ],
                'popular': True,
            },
            {
                'name': 'Vitamin C Brightening Serum',
                'category': cream, 'product_type': 'cosmetics',
                'price': 2499, 'rating': 4.7, 'review_count': 176, 'is_new': True,
                'brand': 'LuminaLab', 'description': '15% Vitamin C serum for a radiant, even skin tone.',
                'material_or_ingredients': 'Ascorbic Acid 15%, Ferulic Acid, Vitamin E, Hyaluronic Acid',
                'is_vegan': True, 'is_cruelty_free': True, 'skin_type': 'all', 'finish': 'Matte',
                'images': [
                    {'url': 'https://images.unsplash.com/photo-1556229174-5e42a09e45af?w=600&h=750&fit=crop', 'type': 'primary'},
                ],
                'variants': [
                    {'shade': 'Original', 'shade_hex': '#FFF3CD', 'volume': '30ml', 'stock': 28},
                ],
                'popular': True,
            },
            {
                'name': 'Soothing Aloe Gel Cream',
                'category': cream, 'product_type': 'cosmetics',
                'price': 1499, 'rating': 4.4, 'review_count': 103,
                'brand': 'AloeVera Pure', 'description': 'Cool, calming aloe vera gel cream for sensitive skin.',
                'material_or_ingredients': 'Aloe Barbadensis Leaf Juice 90%, Allantoin, Panthenol',
                'is_vegan': True, 'is_cruelty_free': True, 'is_hypoallergenic': True,
                'skin_type': 'sensitive', 'finish': 'Matte',
                'images': [
                    {'url': 'https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=600&h=750&fit=crop', 'type': 'primary'},
                ],
                'variants': [
                    {'shade': 'Original', 'shade_hex': '#90EE90', 'volume': '100ml', 'stock': 35},
                    {'shade': 'Original', 'shade_hex': '#90EE90', 'volume': '200ml', 'stock': 20},
                ],
                'popular': False,
            },
        ]

        # ─── CREATE PRODUCTS ─────────────────────────────────────────────────────
        created_products = []
        for idx, data in enumerate(products_data, start=1):
            base_slug = slugify(data['name'])
            sku = f"SKU-{idx:04d}"
            product = Product.objects.create(
                name=data['name'],
                price=data['price'],
                original_price=data.get('original_price'),
                rating=data['rating'],
                review_count=data['review_count'],
                image=data['images'][0]['url'],
                category=data['category'],
                is_new=data.get('is_new', False),
                is_sale=data.get('is_sale', False),
                sale_percentage=data.get('sale_percentage'),
                brand=data.get('brand', ''),
                product_type=data['product_type'],
                description=data['description'],
                material_or_ingredients=data['material_or_ingredients'],
                is_vegan=data.get('is_vegan'),
                is_cruelty_free=data.get('is_cruelty_free'),
                is_hypoallergenic=data.get('is_hypoallergenic'),
                season=data.get('season'),
                fit=data.get('fit'),
                skin_type=data.get('skin_type'),
                finish=data.get('finish'),
                sku=sku,
                slug=base_slug,
            )

            # ─── VARIANTS ───
            for v_idx, v in enumerate(data['variants'], start=1):
                suffix = f"{v_idx:02d}"
                if data['product_type'] == 'clothing':
                    variant = ProductVariant.objects.create(
                        product=product,
                        variant_type='size_color',
                        size=v.get('size'),
                        color=v.get('color'),
                        color_hex=v.get('color_hex'),
                        stock_quantity=v.get('stock', 10),
                        sku_suffix=suffix,
                    )
                else:
                    variant = ProductVariant.objects.create(
                        product=product,
                        variant_type='shade_finish_volume',
                        shade=v.get('shade'),
                        shade_hex=v.get('shade_hex'),
                        volume=v.get('volume'),
                        stock_quantity=v.get('stock', 10),
                        sku_suffix=suffix,
                    )
                # Swatch image for cosmetics variants
                if data['product_type'] == 'cosmetics':
                    hex_code = (v.get('shade_hex') or '#CCCCCC').lstrip('#')
                    ProductImage.objects.create(
                        product=product,
                        variant=variant,
                        image_url=f"https://placehold.co/100x100/{hex_code}/png",
                        image_type='swatch',
                        display_order=99,
                    )

            # ─── IMAGES ───
            for img_idx, img in enumerate(data['images']):
                ProductImage.objects.create(
                    product=product,
                    image_url=img['url'],
                    image_type=img['type'],
                    display_order=img_idx,
                )

            created_products.append({'obj': product, 'popular': data.get('popular', False)})
            self.stdout.write(f"  Created: {product.name}")

        # ─── REVIEWS ────────────────────────────────────────────────────────────
        popular_products = [p['obj'] for p in created_products if p['popular']]
        for product in popular_products:
            n_reviews = random.randint(5, 10)
            for i in range(n_reviews):
                Review.objects.create(
                    product=product,
                    customer=None,
                    rating=random.choice([3, 4, 4, 5, 5, 5]),
                    title=random.choice(REVIEW_TITLES),
                    body=random.choice(REVIEW_BODIES),
                    is_approved=(i < n_reviews // 2),  # first half approved, rest pending
                )

        self.stdout.write(f'Reviews seeded for {len(popular_products)} popular products.')

        # ─── COLLECTIONS ────────────────────────────────────────────────────────
        new_arrivals = Collection.objects.create(
            name='New Arrivals', slug='new-arrivals',
            description='Fresh picks just landed in store.', is_active=True, display_order=1,
        )
        new_arrival_products = [p['obj'] for p in created_products if p['obj'].is_new]
        new_arrivals.products.set(new_arrival_products)

        festive_sale = Collection.objects.create(
            name='Festive Sale', slug='festive-sale',
            description='Big savings for the festive season.', is_active=True, display_order=2,
        )
        sale_products = [p['obj'] for p in created_products if p['obj'].is_sale]
        festive_sale.products.set(sale_products)

        self.stdout.write(f'Collections: New Arrivals ({new_arrivals.products.count()} items), Festive Sale ({festive_sale.products.count()} items).')

        self.stdout.write(self.style.SUCCESS(
            f'\nSuccessfully seeded {len(products_data)} products, '
            f'{len(popular_products)} popular product review sets, '
            f'2 collections, 3 discount rules, and 2 size guides.'
        ))
