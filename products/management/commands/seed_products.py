from django.core.management.base import BaseCommand
from django.utils.text import slugify
from products.models import Category, Product, ProductVariant, ProductImage, SizeGuide, Collection
from orders.models import DiscountRule
from engagement.models import Review
import random
import shutil
import os

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

COPIES = [
    # BAGS
    ("WhatsApp Image 2026-07-08 at 12.44.19 PM.jpeg",    "bag-brown-small-purse.jpg"),
    ("WhatsApp Image 2026-07-08 at 12.44.21 PM.jpeg",    "bag-tan-crossbody.jpg"),
    ("WhatsApp Image 2026-07-08 at 12.44.23 PM.jpeg",    "bag-beige-large-handbag.jpg"),
    ("WhatsApp Image 2026-07-08 at 12.44.25 PM.jpeg",    "bag-red-glitter-clutch.jpg"),
    ("WhatsApp Image 2026-07-08 at 12.44.27 PM.jpeg",    "bag-tan-canvas-tote.jpg"),
    ("WhatsApp Image 2026-07-08 at 12.44.28 PM.jpeg",    "bag-dark-brown-mini.jpg"),
    ("WhatsApp Image 2026-07-08 at 12.44.31 PM.jpeg",    "bag-burgundy-coach-tote.jpg"),
    ("WhatsApp Image 2026-07-08 at 12.44.35 PM.jpeg",    "bag-gold-crystal-clutch.jpg"),
    ("WhatsApp Image 2026-07-08 at 12.44.39 PM.jpeg",    "bag-maroon-jeweled-clutch.jpg"),
    # MAKEUP / LIP
    ("WhatsApp Image 2026-07-08 at 12.44.11 PM.jpeg",    "makeup-lip-glaze-pink.jpg"),
    ("WhatsApp Image 2026-07-08 at 12.44.13 PM.jpeg",    "makeup-lip-glaze-shelf.jpg"),
    ("WhatsApp Image 2026-07-08 at 12.44.13 PM (1).jpeg","makeup-liquid-lipstick.jpg"),
    ("WhatsApp Image 2026-07-08 at 12.44.16 PM.jpeg",    "makeup-mocha-lip-gloss.jpg"),
    ("WhatsApp Image 2026-07-08 at 12.44.18 PM.jpeg",    "makeup-coloressence-lipstick.jpg"),
    # SKINCARE
    ("WhatsApp Image 2026-07-08 at 12.44.39 PM (1).jpeg","skincare-vaseline-spf50.jpg"),
    ("WhatsApp Image 2026-07-08 at 12.44.40 PM.jpeg",    "skincare-vaseline-lotion.jpg"),
    ("WhatsApp Image 2026-07-08 at 12.44.41 PM.jpeg",    "skincare-dotkey-sunscreen.jpg"),
    ("WhatsApp Image 2026-07-08 at 12.44.43 PM.jpeg",    "skincare-gaga-sun-cream.jpg"),
    ("WhatsApp Image 2026-07-08 at 12.44.43 PM (1).jpeg","skincare-dotkey-moisturizer.jpg"),
]

class Command(BaseCommand):
    help = 'Seeds the database with realistic dummy data for products, variants, images, reviews, size guides, discounts, and collections'

    def handle(self, *args, **kwargs):
        # ─── COPY DUMMY IMAGES ────────────────────────────────────────────────
        self.stdout.write('Copying dummy images to media directories...')
        src_dir = "dummy-images"
        primary_dst = "media/products/primary"
        gallery_dst = "media/products/gallery"
        
        os.makedirs(primary_dst, exist_ok=True)
        os.makedirs(gallery_dst, exist_ok=True)

        for src_name, dst_name in COPIES:
            src_path = os.path.join(src_dir, src_name)
            if os.path.exists(src_path):
                shutil.copy2(src_path, os.path.join(primary_dst, dst_name))
                shutil.copy2(src_path, os.path.join(gallery_dst, dst_name))
                self.stdout.write(f"  Copied {dst_name}")
            else:
                self.stdout.write(self.style.WARNING(f"  Warning: Source image {src_name} not found in {src_dir}"))

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
        bags_root = Category.objects.create(name='Bags', slug='bags')
        cosmetics = Category.objects.create(name='Cosmetics', slug='cosmetics')

        handbags = Category.objects.create(name='Handbags', slug='handbags', parent=bags_root)
        backpacks = Category.objects.create(name='Backpacks', slug='backpacks', parent=bags_root)
        clutches = Category.objects.create(name='Clutches', slug='clutches', parent=bags_root)

        makeup = Category.objects.create(name='Makeup', slug='makeup', parent=cosmetics)
        haircare = Category.objects.create(name='Haircare', slug='haircare', parent=cosmetics)
        nails = Category.objects.create(name='Nails', slug='nails', parent=cosmetics)
        skincare = Category.objects.create(name='Skincare', slug='skincare', parent=cosmetics)

        self.stdout.write('Categories created.')

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
        self.stdout.write('Discount rules created.')

        # ─── PRODUCTS ───────────────────────────────────────────────────────────
        products_data = [
            # ── BAGS ──
            {
                'name': 'Burgundy Coach Leather Tote',
                'category': handbags, 'product_type': 'bags',
                'price': 24999, 'original_price': 29999, 'rating': 4.8, 'review_count': 128,
                'is_sale': True, 'sale_percentage': 16,
                'brand': 'Coach', 'description': 'A premium leather tote bag from Coach, featuring dual top handles and spacious compartments.',
                'material_or_ingredients': '100% Genuine Pebbled Leather',
                'material': 'leather', 'closure_type': 'zipper',
                'image': 'products/primary/bag-burgundy-coach-tote.jpg',
                'images': [
                    {'url': 'products/gallery/bag-burgundy-coach-tote.jpg', 'type': 'primary'},
                ],
                'variants': [
                    {'size': 'Large', 'color': 'Burgundy', 'color_hex': '#800020', 'stock': 12},
                ],
                'popular': True,
            },
            {
                'name': 'Classic Tan Canvas Tote',
                'category': handbags, 'product_type': 'bags',
                'price': 4999, 'rating': 4.5, 'review_count': 98,
                'brand': 'Luxe Story', 'description': 'A durable cotton canvas tote bag with contrast leather handles and accents.',
                'material_or_ingredients': '100% Cotton Canvas, Leather Trims',
                'material': 'canvas', 'closure_type': 'zipper',
                'image': 'products/primary/bag-tan-canvas-tote.jpg',
                'images': [
                    {'url': 'products/gallery/bag-tan-canvas-tote.jpg', 'type': 'primary'},
                ],
                'variants': [
                    {'size': 'Medium', 'color': 'Tan', 'color_hex': '#D2B48C', 'stock': 20},
                ],
                'popular': True,
            },
            {
                'name': 'Gold Crystal Party Clutch',
                'category': clutches, 'product_type': 'bags',
                'price': 8999, 'rating': 4.9, 'review_count': 45, 'is_new': True,
                'brand': 'Glamour', 'description': 'An elegant party clutch covered in sparkling gold crystals, featuring a detachable chain shoulder strap.',
                'material_or_ingredients': 'Synthetic Satin, Crystal Mesh, Gold-Tone Hardware',
                'material': 'satin', 'closure_type': 'magnetic',
                'image': 'products/primary/bag-gold-crystal-clutch.jpg',
                'images': [
                    {'url': 'products/gallery/bag-gold-crystal-clutch.jpg', 'type': 'primary'},
                ],
                'variants': [
                    {'size': 'Small', 'color': 'Gold', 'color_hex': '#FFD700', 'stock': 8},
                ],
                'popular': True,
            },
            {
                'name': 'Red Glitter Evening Clutch',
                'category': clutches, 'product_type': 'bags',
                'price': 7499, 'original_price': 8999, 'rating': 4.7, 'review_count': 64,
                'is_sale': True, 'sale_percentage': 16,
                'brand': 'Glamour', 'description': 'Showstopper red glitter evening clutch bag with a sleek metallic closure and chain strap.',
                'material_or_ingredients': 'Glitter Fabric, Metal Frame, Satin Lining',
                'material': 'satin', 'closure_type': 'magnetic',
                'image': 'products/primary/bag-red-glitter-clutch.jpg',
                'images': [
                    {'url': 'products/gallery/bag-red-glitter-clutch.jpg', 'type': 'primary'},
                ],
                'variants': [
                    {'size': 'Small', 'color': 'Red', 'color_hex': '#FF0000', 'stock': 10},
                ],
                'popular': False,
            },
            {
                'name': 'Maroon Jeweled Evening Purse',
                'category': clutches, 'product_type': 'bags',
                'price': 9499, 'rating': 4.6, 'review_count': 32, 'is_new': True,
                'brand': 'Glamour', 'description': 'Luxury evening purse featuring a rich maroon fabric base encrusted with sparkling teardrop crystals.',
                'material_or_ingredients': 'Velvet, Premium Rhinestones, Metal Hardware',
                'material': 'velvet', 'closure_type': 'magnetic',
                'image': 'products/primary/bag-maroon-jeweled-clutch.jpg',
                'images': [
                    {'url': 'products/gallery/bag-maroon-jeweled-clutch.jpg', 'type': 'primary'},
                ],
                'variants': [
                    {'size': 'Small', 'color': 'Maroon', 'color_hex': '#800000', 'stock': 5},
                ],
                'popular': False,
            },
            {
                'name': 'Tan Leather Crossbody Bag',
                'category': handbags, 'product_type': 'bags',
                'price': 6799, 'rating': 4.4, 'review_count': 156,
                'brand': 'Maison Edit', 'description': 'A structured crossbody bag with premium details and magnetic flap closure.',
                'material_or_ingredients': '100% Genuine Calf Leather',
                'material': 'leather', 'closure_type': 'magnetic',
                'image': 'products/primary/bag-tan-crossbody.jpg',
                'images': [
                    {'url': 'products/gallery/bag-tan-crossbody.jpg', 'type': 'primary'},
                ],
                'variants': [
                    {'size': 'Medium', 'color': 'Tan', 'color_hex': '#9A463D', 'stock': 15},
                ],
                'popular': False,
            },
            {
                'name': 'Beige Large Handbag',
                'category': handbags, 'product_type': 'bags',
                'price': 12999, 'rating': 4.3, 'review_count': 42,
                'brand': 'Luxe Leather Co.', 'description': 'Spacious and elegant beige handbag with a silk ribbon tie detail on the handle.',
                'material_or_ingredients': 'Vegan Pebbled Leather, Silk Scarf Handle Wrap',
                'material': 'leather', 'closure_type': 'zipper',
                'image': 'products/primary/bag-beige-large-handbag.jpg',
                'images': [
                    {'url': 'products/gallery/bag-beige-large-handbag.jpg', 'type': 'primary'},
                ],
                'variants': [
                    {'size': 'Large', 'color': 'Beige', 'color_hex': '#F5F5DC', 'stock': 10},
                ],
                'popular': False,
            },
            {
                'name': 'Dark Brown Mini Clutch',
                'category': clutches, 'product_type': 'bags',
                'price': 5499, 'rating': 4.2, 'review_count': 64,
                'brand': 'Soft Suede', 'description': 'Slouchy minimal clutch bag in rich dark brown leather with an elegant G-hook gold lock.',
                'material_or_ingredients': 'Soft Lambskin Leather, Polished Gold Hardware',
                'material': 'leather', 'closure_type': 'magnetic',
                'image': 'products/primary/bag-dark-brown-mini.jpg',
                'images': [
                    {'url': 'products/gallery/bag-dark-brown-mini.jpg', 'type': 'primary'},
                ],
                'variants': [
                    {'size': 'Small', 'color': 'Dark Brown', 'color_hex': '#3D2314', 'stock': 8},
                ],
                'popular': False,
            },
            {
                'name': 'Brown Small Leather Purse',
                'category': clutches, 'product_type': 'bags',
                'price': 3999, 'rating': 4.1, 'review_count': 22,
                'brand': 'Maison Edit', 'description': 'A small brown leather handbag with custom hardware lock details.',
                'material_or_ingredients': 'Pebbled Calf Leather, Nylon Lining',
                'material': 'leather', 'closure_type': 'magnetic',
                'image': 'products/primary/bag-brown-small-purse.jpg',
                'images': [
                    {'url': 'products/gallery/bag-brown-small-purse.jpg', 'type': 'primary'},
                ],
                'variants': [
                    {'size': 'Small', 'color': 'Brown', 'color_hex': '#8B4513', 'stock': 14},
                ],
                'popular': False,
            },
            # ── COSMETICS ──
            {
                'name': '3Q Beauty Mirror Lip Glaze',
                'category': makeup, 'product_type': 'cosmetics',
                'price': 1199, 'rating': 4.6, 'review_count': 210, 'is_new': True,
                'brand': '3Q Beauty', 'description': 'High-gloss moisturizing mirror lip glaze that leaves your lips plump and hydrated all day.',
                'material_or_ingredients': 'Castor Oil, Vitamin E, Hyaluronic Acid, Pigments',
                'is_vegan': True, 'is_cruelty_free': True, 'finish': 'Glossy',
                'image': 'products/primary/makeup-lip-glaze-pink.jpg',
                'images': [
                    {'url': 'products/gallery/makeup-lip-glaze-pink.jpg', 'type': 'primary'},
                ],
                'variants': [
                    {'shade': 'Glaze Pink', 'shade_hex': '#D4A574', 'volume': '5g', 'stock': 25},
                ],
                'popular': True,
            },
            {
                'name': 'Beutivia Liquid Lipstick',
                'category': makeup, 'product_type': 'cosmetics',
                'price': 1299, 'rating': 4.4, 'review_count': 87,
                'brand': 'Beutivia', 'description': 'Long-lasting transferproof liquid lipstick with a comfortable matte finish.',
                'material_or_ingredients': 'Isododecane, Castor Oil, Vitamin E',
                'is_vegan': True, 'is_cruelty_free': True, 'finish': 'Matte',
                'image': 'products/primary/makeup-liquid-lipstick.jpg',
                'images': [
                    {'url': 'products/gallery/makeup-liquid-lipstick.jpg', 'type': 'primary'},
                ],
                'variants': [
                    {'shade': 'Rose Nude', 'shade_hex': '#C0392B', 'volume': '5ml', 'stock': 22},
                ],
                'popular': False,
            },
            {
                'name': 'Mocha Matte Lip Gloss',
                'category': makeup, 'product_type': 'cosmetics',
                'price': 999, 'rating': 4.5, 'review_count': 130, 'is_new': True,
                'brand': 'Mita', 'description': 'Beautiful mocha shade lip gloss offering full coverage matte finish and 8 hours of wear.',
                'material_or_ingredients': 'Castor Oil, Candelilla Wax, Niacinamide',
                'is_vegan': True, 'is_cruelty_free': True, 'finish': 'Matte',
                'image': 'products/primary/makeup-mocha-lip-gloss.jpg',
                'images': [
                    {'url': 'products/gallery/makeup-mocha-lip-gloss.jpg', 'type': 'primary'},
                ],
                'variants': [
                    {'shade': 'LTP-23 Mocha', 'shade_hex': '#8E44AD', 'volume': '6ml', 'stock': 35},
                ],
                'popular': True,
            },
            {
                'name': 'Coloressence 12hr Stay Liquid Lipstick',
                'category': makeup, 'product_type': 'cosmetics',
                'price': 1499, 'rating': 4.8, 'review_count': 234,
                'brand': 'Coloressence', 'description': 'Transferproof 12 hour stay liquid lipstick with intense pigment payoff and comfortable formula.',
                'material_or_ingredients': 'Isododecane, Castor Oil, Pigments',
                'is_vegan': True, 'is_cruelty_free': True, 'finish': 'Matte',
                'image': 'products/primary/makeup-coloressence-lipstick.jpg',
                'images': [
                    {'url': 'products/gallery/makeup-coloressence-lipstick.jpg', 'type': 'primary'},
                ],
                'variants': [
                    {'shade': 'Wine Stain', 'shade_hex': '#800020', 'volume': '5ml', 'stock': 40},
                ],
                'popular': True,
            },
            {
                'name': 'Vaseline Gluta-Hya Sunscreen SPF 50',
                'category': skincare, 'product_type': 'cosmetics',
                'price': 1999, 'rating': 4.7, 'review_count': 114, 'is_new': True,
                'brand': 'Vaseline', 'description': 'Broad spectrum hydration sunscreen lotion with Gluta-Hya for glowing skin without a white cast.',
                'material_or_ingredients': 'Zinc Oxide, Gluta-Glow, Hyaluron, Niacinamide',
                'is_vegan': True, 'is_cruelty_free': True, 'skin_type': 'all', 'finish': 'Dewy',
                'image': 'products/primary/skincare-vaseline-spf50.jpg',
                'images': [
                    {'url': 'products/gallery/skincare-vaseline-spf50.jpg', 'type': 'primary'},
                ],
                'variants': [
                    {'shade': 'Transparent', 'shade_hex': '#FFFFFF', 'volume': '70ml', 'stock': 40},
                ],
                'popular': True,
            },
            {
                'name': 'Vaseline Gluta-Hya Dewy Radiance Lotion',
                'category': skincare, 'product_type': 'cosmetics',
                'price': 1799, 'rating': 4.4, 'review_count': 92,
                'brand': 'Vaseline', 'description': 'Dewy radiance serum-in-lotion containing gluta-glow and hyaluronic acid for skin whitening and hydration.',
                'material_or_ingredients': 'Glutaglow, Hyaluron, Niacinamide, Vitamin C',
                'is_vegan': True, 'is_cruelty_free': True, 'skin_type': 'all', 'finish': 'Dewy',
                'image': 'products/primary/skincare-vaseline-lotion.jpg',
                'images': [
                    {'url': 'products/gallery/skincare-vaseline-lotion.jpg', 'type': 'primary'},
                ],
                'variants': [
                    {'shade': 'Transparent', 'shade_hex': '#FFFFFF', 'volume': '100ml', 'stock': 30},
                ],
                'popular': False,
            },
            {
                'name': 'Dot & Key Watermelon Cooling Sunscreen',
                'category': skincare, 'product_type': 'cosmetics',
                'price': 2199, 'original_price': 2499, 'rating': 4.3, 'review_count': 67,
                'is_sale': True, 'sale_percentage': 12,
                'brand': 'Dot & Key', 'description': 'Broad spectrum SPF 50+ cooling sunscreen with watermelon extract and hyaluronic acid.',
                'material_or_ingredients': 'Watermelon Extract, Hyaluronic Acid, UV Filters',
                'is_vegan': True, 'is_cruelty_free': True, 'skin_type': 'sensitive', 'finish': 'Dewy',
                'image': 'products/primary/skincare-dotkey-sunscreen.jpg',
                'images': [
                    {'url': 'products/gallery/skincare-dotkey-sunscreen.jpg', 'type': 'primary'},
                ],
                'variants': [
                    {'shade': 'Watermelon Fresh', 'shade_hex': '#FFB7B2', 'volume': '50g', 'stock': 20},
                ],
                'popular': True,
            },
            {
                'name': 'Gaga Sun Protection Cream SPF 50',
                'category': skincare, 'product_type': 'cosmetics',
                'price': 1599, 'rating': 4.6, 'review_count': 92, 'is_new': True,
                'brand': 'Gaga', 'description': 'Long-lasting UVA/UVB filters, enriched with Vitamin C and E. Waterproof and sweatproof formula.',
                'material_or_ingredients': 'Zinc Oxide, Vitamin C, Vitamin E',
                'is_vegan': True, 'is_cruelty_free': True, 'skin_type': 'dry', 'finish': 'Matte',
                'image': 'products/primary/skincare-gaga-sun-cream.jpg',
                'images': [
                    {'url': 'products/gallery/skincare-gaga-sun-cream.jpg', 'type': 'primary'},
                ],
                'variants': [
                    {'shade': 'Original', 'shade_hex': '#FFF5E6', 'volume': '50ml', 'stock': 15},
                ],
                'popular': True,
            },
            {
                'name': 'Dot & Key Barrier Repair Moisturizer',
                'category': skincare, 'product_type': 'cosmetics',
                'price': 2499, 'rating': 4.7, 'review_count': 114, 'is_new': True,
                'brand': 'Dot & Key', 'description': 'Ceramides and hyaluronic barrier repair moisturizer with pH 5.5 and probiotics/rice water for deep hydration.',
                'material_or_ingredients': '5 Essential Ceramides, Probiotics, Rice Water, Hyaluronic Acid',
                'is_vegan': True, 'is_cruelty_free': True, 'skin_type': 'dry', 'finish': 'Dewy',
                'image': 'products/primary/skincare-dotkey-moisturizer.jpg',
                'images': [
                    {'url': 'products/gallery/skincare-dotkey-moisturizer.jpg', 'type': 'primary'},
                ],
                'variants': [
                    {'shade': 'Original', 'shade_hex': '#FFFFFF', 'volume': '120g', 'stock': 40},
                ],
                'popular': True,
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
                image=data['image'],
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
                closure_type=data.get('closure_type'),
                material=data.get('material'),
                sku=sku,
                slug=base_slug,
            )

            # ─── VARIANTS ───
            for v_idx, v in enumerate(data['variants'], start=1):
                suffix = f"{v_idx:02d}"
                if data['product_type'] == 'bags':
                    variant = ProductVariant.objects.create(
                        product=product,
                        variant_type='size_color',
                        size=v.get('size', 'One Size'),
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
            f'2 collections, and 2 discount rules.'
        ))
