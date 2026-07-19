import uuid
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from products.models import ProductVariant
from .serializers import CartSerializer

class CartAPIView(APIView):
    permission_classes = [AllowAny]

    def get_cart(self, request):
        if request.user.is_authenticated:
            # Authenticated user
            cart, _ = Cart.objects.get_or_create(customer=request.user.customerprofile)
        else:
            # Guest user via session/cookie token
            cart_token = request.COOKIES.get('cart_token')
            if cart_token:
                try:
                    cart = Cart.objects.get(id=cart_token, customer__isnull=True)
                except (Cart.DoesNotExist, ValueError):
                    cart = Cart.objects.create()
            else:
                cart = Cart.objects.create()
        return cart

    def set_cart_cookie(self, response, cart_id):
        # Only set if it's a guest cart to keep track of it
        response.set_cookie('cart_token', str(cart_id), max_age=60*60*24*30, httponly=True, samesite='Lax')

    def get(self, request):
        cart = self.get_cart(request)
        # Prefetch items→variant→product to avoid N+1 in serializer
        cart = Cart.objects.prefetch_related(
            'items__variant__product',
        ).get(pk=cart.pk)
        serializer = CartSerializer(cart)
        response = Response(serializer.data)
        if not request.user.is_authenticated:
            self.set_cart_cookie(response, cart.id)
        return response

class CartItemAPIView(APIView):
    permission_classes = [AllowAny]

    def get_cart(self, request):
        # Repeated helper
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(customer=request.user.customerprofile)
        else:
            cart_token = request.COOKIES.get('cart_token')
            if cart_token:
                try:
                    cart = Cart.objects.get(id=cart_token, customer__isnull=True)
                except (Cart.DoesNotExist, ValueError):
                    cart = Cart.objects.create()
            else:
                cart = Cart.objects.create()
        return cart

    def post(self, request):
        cart = self.get_cart(request)
        variant_id = request.data.get('variantId')
        quantity = request.data.get('quantity', 1)

        try:
            qty_int = int(quantity)
            if qty_int <= 0:
                return Response({"detail": "Quantity must be greater than 0."}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({"detail": "Invalid quantity value."}, status=status.HTTP_400_BAD_REQUEST)

        variant = get_object_or_404(ProductVariant, id=variant_id)
        
        cart_item, created = CartItem.objects.get_or_create(cart=cart, variant=variant, defaults={'quantity': qty_int})
        if not created:
            cart_item.quantity += qty_int
            cart_item.save()

        serializer = CartSerializer(cart)
        response = Response(serializer.data, status=status.HTTP_201_CREATED)
        if not request.user.is_authenticated:
            # In cartItem view, we have to duplicate the cookie helper or abstract it
            response.set_cookie('cart_token', str(cart.id), max_age=60*60*24*30, httponly=True, samesite='Lax')
        return response

class CartItemDetailAPIView(APIView):
    permission_classes = [AllowAny]
    
    def get_cart(self, request):
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(customer=request.user.customerprofile)
        else:
            cart_token = request.COOKIES.get('cart_token')
            if cart_token:
                try:
                    cart = Cart.objects.get(id=cart_token, customer__isnull=True)
                except (Cart.DoesNotExist, ValueError):
                    cart = Cart.objects.create()
            else:
                cart = Cart.objects.create()
        return cart
    
    def patch(self, request, pk):
        cart = self.get_cart(request)
        cart_item = get_object_or_404(CartItem, id=pk, cart=cart)
        quantity = request.data.get('quantity')
        if quantity is not None:
            try:
                qty_int = int(quantity)
                if qty_int <= 0:
                    cart_item.delete()
                else:
                    cart_item.quantity = qty_int
                    cart_item.save()
            except (ValueError, TypeError):
                return Response({"detail": "Invalid quantity value."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(CartSerializer(cart).data)

    def delete(self, request, pk):
        cart = self.get_cart(request)
        cart_item = get_object_or_404(CartItem, id=pk, cart=cart)
        cart_item.delete()
        return Response(CartSerializer(cart).data)

from django.db import transaction
from .models import Order, OrderItem
from accounts.models import Address, CustomerProfile
from accounts.serializers import AddressSerializer

class CheckoutAPIView(APIView):
    permission_classes = [AllowAny]
    
    def get_cart(self, request):
        if request.user.is_authenticated:
            try:
                return Cart.objects.get(customer=request.user.customerprofile)
            except Cart.DoesNotExist:
                return None
        else:
            cart_token = request.COOKIES.get('cart_token')
            if cart_token:
                try:
                    return Cart.objects.get(id=cart_token, customer__isnull=True)
                except (Cart.DoesNotExist, ValueError):
                    return None
        return None

    @transaction.atomic
    def post(self, request):
        cart = self.get_cart(request)
        if not cart or not cart.items.exists():
            return Response({"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)
        
        guest_email = request.data.get('email')
        if not request.user.is_authenticated and not guest_email:
            return Response({"detail": "Email is required for guest checkout."}, status=status.HTTP_400_BAD_REQUEST)

        shipping_address_id = request.data.get('shipping_address_id')
        shipping_info = request.data.get('shipping_info')
        
        shipping_address = None
        
        if shipping_address_id:
            if request.user.is_authenticated:
                try:
                    shipping_address = Address.objects.get(id=shipping_address_id, profile=request.user.customerprofile)
                except Address.DoesNotExist:
                    return Response({"detail": "Invalid shipping address ID."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                guest_addresses = request.session.get('guest_addresses', [])
                guest_addr_dict = None
                for addr in guest_addresses:
                    if addr.get('id') == shipping_address_id:
                        guest_addr_dict = addr
                        break
                if not guest_addr_dict:
                    return Response({"detail": "Invalid shipping address ID."}, status=status.HTTP_400_BAD_REQUEST)
                shipping_address = Address.objects.create(
                    profile=None,
                    full_name=guest_addr_dict.get('full_name', ''),
                    phone=guest_addr_dict.get('phone', ''),
                    street=guest_addr_dict.get('street', ''),
                    city=guest_addr_dict.get('city', ''),
                    postal_code=guest_addr_dict.get('postal_code', ''),
                    country=guest_addr_dict.get('country', 'Nepal')
                )
        elif shipping_info:
            first_name = shipping_info.get('firstName', '')
            last_name = shipping_info.get('lastName', '')
            full_name = shipping_info.get('fullName', f"{first_name} {last_name}".strip())
            
            addr_data = {
                'full_name': full_name,
                'phone': shipping_info.get('phone', ''),
                'street': shipping_info.get('address', shipping_info.get('street', '')),
                'city': shipping_info.get('city', ''),
                'postal_code': shipping_info.get('postalCode', shipping_info.get('postal_code', '')),
                'country': shipping_info.get('country', 'Nepal'),
            }
            
            serializer = AddressSerializer(data=addr_data)
            serializer.is_valid(raise_exception=True)
            
            if request.user.is_authenticated:
                profile = request.user.customerprofile
                existing = Address.objects.filter(
                    profile=profile,
                    full_name=addr_data['full_name'],
                    street=addr_data['street'],
                    city=addr_data['city']
                ).first()
                if existing:
                    shipping_address = existing
                else:
                    shipping_address = serializer.save(profile=profile)
            else:
                shipping_address = serializer.save(profile=None)
        else:
            return Response({"detail": "Shipping address is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Sort items by variant id to lock them in a deterministic order and prevent deadlocks
        items_sorted = sorted(cart.items.all(), key=lambda x: x.variant.id)
        
        # Lock rows and validate stock first
        subtotal = Decimal('0.00')
        locked_variants = []
        
        for item in items_sorted:
            variant = ProductVariant.objects.select_for_update().get(id=item.variant.id)
            if variant.stock_quantity < item.quantity:
                return Response(
                    {"detail": f"Insufficient stock for {variant.product.name} ({variant.size or ''} {variant.color or ''}). Available: {variant.stock_quantity}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            locked_variants.append((variant, item.quantity))
            subtotal += item.quantity * (variant.product.price + variant.extra_price)
            
        shipping_fee = Decimal('10.00')
        total = subtotal + shipping_fee
        
        order = Order.objects.create(
            customer=request.user.customerprofile if request.user.is_authenticated else None,
            guest_email=guest_email if not request.user.is_authenticated else None,
            status='pending_payment',
            shipping_address=shipping_address,
            subtotal=subtotal,
            shipping_fee=shipping_fee,
            total=total,
        )
        
        # Transfer cart items to order items and decrement stock
        for variant, quantity in locked_variants:
            OrderItem.objects.create(
                order=order,
                variant=variant,
                quantity=quantity,
                unit_price=variant.product.price + variant.extra_price
            )
            variant.stock_quantity -= quantity
            variant.save()
            
        # Clear cart
        cart.items.all().delete()
        
        # Store guest order in session for authorization
        if not request.user.is_authenticated:
            placed_orders = request.session.get('placed_orders', [])
            placed_orders.append(order.order_number)
            request.session['placed_orders'] = placed_orders
            request.session.modified = True
        
        response = Response({
            "order_number": order.order_number,
            "total": str(total),
            "status": "pending_payment"
        }, status=status.HTTP_201_CREATED)
        
        return response

class CartMergeAPIView(APIView):
    """
    POST /api/cart/merge/
    Called after login to merge guest cart (identified by cart_token cookie) into the
    authenticated user's cart. Idempotent — safe to call multiple times.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart_token = request.COOKIES.get('cart_token')
        if not cart_token:
            return Response({"detail": "No guest cart to merge."}, status=status.HTTP_200_OK)

        try:
            guest_cart = Cart.objects.get(id=cart_token, customer__isnull=True)
        except (Cart.DoesNotExist, ValueError):
            return Response({"detail": "No guest cart found."}, status=status.HTTP_200_OK)

        # Get or create the authenticated user's cart
        user_cart, _ = Cart.objects.get_or_create(customer=request.user.customerprofile)

        for guest_item in guest_cart.items.all():
            existing, created = CartItem.objects.get_or_create(
                cart=user_cart,
                variant=guest_item.variant,
                defaults={'quantity': guest_item.quantity}
            )
            if not created:
                existing.quantity += guest_item.quantity
                existing.save()

        # Delete the guest cart now that it's merged
        guest_cart.delete()

        serializer = CartSerializer(user_cart)
        response = Response(serializer.data, status=status.HTTP_200_OK)
        # Clear the guest cart cookie
        response.delete_cookie('cart_token')
        return response

from .models import ReturnRequest, DiscountRule, Cart
from .serializers import OrderSerializer, ReturnRequestSerializer, DiscountRuleSerializer

class OrderListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        orders = Order.objects.filter(
            customer=request.user.customerprofile
        ).prefetch_related(
            'items__variant__product', 'items__return_requests',
        ).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

class OrderRetrieveAPIView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, order_number):
        order = get_object_or_404(
            Order.objects.prefetch_related(
                'items__variant__product', 'items__return_requests',
            ),
            order_number=order_number,
        )
        
        # Verify access
        if order.customer:
            if not request.user.is_authenticated or request.user.customerprofile != order.customer:
                return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Guest order: verify it was placed in the current session
            placed_orders = request.session.get('placed_orders', [])
            if order.order_number not in placed_orders:
                return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
                
        serializer = OrderSerializer(order)
        return Response(serializer.data)

class OrderReturnAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, item_id):
        reason = request.data.get('reason')
        if not reason:
            return Response({"error": "Reason required"}, status=status.HTTP_400_BAD_REQUEST)
            
        order_item = get_object_or_404(OrderItem, id=item_id)
        
        # Verify ownership
        if order_item.order.customer != request.user.customerprofile:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
            
        if order_item.order.status != 'delivered':
            return Response({"error": "Only delivered items can be returned"}, status=status.HTTP_400_BAD_REQUEST)
            
        return_req, created = ReturnRequest.objects.get_or_create(
            order_item=order_item,
            defaults={'reason': reason, 'status': 'requested'}
        )
        
        serializer = ReturnRequestSerializer(return_req)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 7 — Admin API Views
# ─────────────────────────────────────────────────────────────────────────────

from django.utils import timezone
from django.db.models import Count, Sum, Q, F
from django.contrib.auth.models import User
from datetime import timedelta
from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff


class AdminDashboardStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)

        total_orders = Order.objects.count()
        recent_orders = Order.objects.filter(created_at__gte=thirty_days_ago).count()
        total_revenue = Order.objects.filter(
            status__in=['processing', 'ready_for_dispatch', 'out_for_delivery', 'delivered']
        ).aggregate(total=Sum('total'))['total'] or 0
        total_customers = CustomerProfile.objects.filter(user__isnull=False).count()
        pending_returns = ReturnRequest.objects.filter(status='requested').count()

        orders_by_status = dict(
            Order.objects.values_list('status').annotate(count=Count('id')).values_list('status', 'count')
        )

        return Response({
            'totalOrders': total_orders,
            'recentOrders': recent_orders,
            'totalRevenue': float(total_revenue),
            'totalCustomers': total_customers,
            'pendingReturns': pending_returns,
            'ordersByStatus': orders_by_status,
        })


class AdminOrderListAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        status_filter = request.GET.get('status')
        search = request.GET.get('search', '')

        orders = Order.objects.select_related(
            'customer', 'customer__user',
        ).prefetch_related(
            'items__variant__product', 'items__return_requests',
        ).order_by('-created_at')

        if status_filter:
            orders = orders.filter(status=status_filter)

        if search:
            orders = orders.filter(
                Q(order_number__icontains=search) |
                Q(guest_email__icontains=search) |
                Q(customer__email__icontains=search) |
                Q(customer__user__username__icontains=search)
            )

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class AdminOrderStatusUpdateAPIView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        order = get_object_or_404(Order, id=pk)
        new_status = request.data.get('status')

        valid_statuses = [c[0] for c in Order.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response({'error': f'Invalid status. Choose from: {valid_statuses}'}, status=status.HTTP_400_BAD_REQUEST)

        old_status = order.status
        order.status = new_status

        order.tracking_history = order.tracking_history or []
        order.tracking_history.append({
            'status': new_status,
            'timestamp': timezone.now().isoformat(),
            'note': f'Status changed from {old_status} to {new_status} by admin',
        })

        order.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)


class AdminLowStockAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        from products.models import ProductVariant
        from products.serializers import ProductVariantSerializer

        try:
            threshold = int(request.GET.get('threshold', 5))
        except (ValueError, TypeError):
            threshold = 5
        variants = ProductVariant.objects.filter(
            stock_quantity__lte=threshold,
            stock_quantity__gte=0,
        ).select_related('product').order_by('stock_quantity')

        data = []
        for v in variants:
            data.append({
                'id': v.id,
                'productName': v.product.name,
                'productSlug': v.product.slug,
                'size': v.size,
                'color': v.color,
                'shade': v.shade,
                'volume': v.volume,
                'stockQuantity': v.stock_quantity,
                'lowStockThreshold': v.low_stock_threshold,
                'sku': f"{v.product.sku}-{v.sku_suffix}",
                'isExpired': bool(v.expiration_date and v.expiration_date < timezone.now().date()),
            })

        return Response(data)


class AdminExpiringProductsAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        from products.models import ProductVariant

        try:
            days = int(request.GET.get('days', 30))
        except (ValueError, TypeError):
            days = 30
        cutoff = timezone.now().date() + timedelta(days=days)

        variants = ProductVariant.objects.filter(
            expiration_date__isnull=False,
            expiration_date__lte=cutoff,
            stock_quantity__gt=0,
        ).select_related('product').order_by('expiration_date')

        data = []
        for v in variants:
            data.append({
                'id': v.id,
                'productName': v.product.name,
                'productSlug': v.product.slug,
                'shade': v.shade,
                'volume': v.volume,
                'batchNumber': v.batch_number,
                'expirationDate': v.expiration_date.isoformat(),
                'stockQuantity': v.stock_quantity,
                'isExpired': v.expiration_date < timezone.now().date(),
            })

        return Response(data)


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 8.2 — Admin Discount Rule Views
# ─────────────────────────────────────────────────────────────────────────────

class AdminDiscountListAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        rules = DiscountRule.objects.all().order_by('-is_active', 'code')
        serializer = DiscountRuleSerializer(rules, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DiscountRuleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminDiscountDetailAPIView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        rule = get_object_or_404(DiscountRule, id=pk)
        serializer = DiscountRuleSerializer(rule, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        rule = get_object_or_404(DiscountRule, id=pk)
        rule.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 8.3 — Admin Abandoned Cart Views
# ─────────────────────────────────────────────────────────────────────────────

class AdminAbandonedCartsAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            days = int(request.GET.get('days', 3))
        except (ValueError, TypeError):
            days = 3
        days_ago = timezone.now() - timedelta(days=days)

        carts = Cart.objects.filter(
            updated_at__lte=days_ago,
            items__isnull=False,
        ).select_related(
            'customer', 'customer__user'
        ).annotate(
            item_count=Count('items'),
            cart_total=Sum(
                (F('items__variant__product__price') + F('items__variant__extra_price'))
                * F('items__quantity')
            ),
        ).prefetch_related('items__variant__product').order_by('-updated_at')

        data = []
        for c in carts:
            info = {
                'id': str(c.id),
                'customerEmail': c.customer.email if c.customer else None,
                'customerName': c.customer.user.username if c.customer and c.customer.user else None,
                'itemCount': c.item_count,
                'cartTotal': float(c.cart_total or 0),
                'lastUpdated': c.updated_at.isoformat(),
                'items': [],
            }
            for item in c.items.all():
                info['items'].append({
                    'productName': item.variant.product.name,
                    'quantity': item.quantity,
                    'unitPrice': float(item.variant.product.price + item.variant.extra_price),
                    'size': item.variant.size,
                    'color': item.variant.color,
                    'shade': item.variant.shade,
                })
            data.append(info)

        return Response(data)


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 9 — Admin Analytics & Reporting
# ─────────────────────────────────────────────────────────────────────────────

class AdminAnalyticsAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        period = request.GET.get('period', 'monthly')
        days_map = {'daily': 30, 'weekly': 90, 'monthly': 365, 'yearly': 1825}
        num_days = days_map.get(period, 365)
        since = timezone.now() - timedelta(days=num_days)

        # ── Revenue over time ──
        revenue_qs = OrderItem.objects.filter(
            order__created_at__gte=since,
            order__status__in=['processing', 'ready_for_dispatch', 'out_for_delivery', 'delivered'],
        ).annotate(
            date=F('order__created_at'),
            line_total=F('quantity') * F('unit_price'),
        ).values('date').annotate(
            revenue=Sum('line_total')
        ).order_by('date')

        bucket_map = {}
        for row in revenue_qs:
            dt = row['date']
            key = self._bucket_key(dt, period)
            bucket_map[key] = bucket_map.get(key, 0) + float(row['revenue'])
        revenue_over_time = [{'label': k, 'value': round(v, 2)} for k, v in sorted(bucket_map.items())]

        # ── Top selling products ──
        top_products = (
            OrderItem.objects.filter(
                order__status__in=['processing', 'ready_for_dispatch', 'out_for_delivery', 'delivered'],
            )
            .values('variant__product__name', 'variant__product__id')
            .annotate(total_qty=Sum('quantity'), total_revenue=Sum(F('quantity') * F('unit_price')))
            .order_by('-total_revenue')[:10]
        )
        top_products_data = [
            {
                'productName': p['variant__product__name'],
                'productId': p['variant__product__id'],
                'totalSold': p['total_qty'],
                'totalRevenue': round(float(p['total_revenue']), 2),
            }
            for p in top_products
        ]

        # ── Revenue by category ──
        category_revenue = (
            OrderItem.objects.filter(
                order__status__in=['processing', 'ready_for_dispatch', 'out_for_delivery', 'delivered'],
            )
            .values('variant__product__category__name')
            .annotate(revenue=Sum(F('quantity') * F('unit_price')))
            .order_by('-revenue')
        )
        category_data = [
            {'category': c['variant__product__category__name'] or 'Uncategorized', 'revenue': round(float(c['revenue']), 2)}
            for c in category_revenue
        ]

        # ── Customer growth ──
        user_qs = User.objects.filter(
            date_joined__gte=since, is_staff=False,
        ).values('date_joined').order_by('date_joined')

        c_bucket_map = {}
        for u in user_qs:
            key = self._bucket_key(u['date_joined'], period)
            c_bucket_map[key] = c_bucket_map.get(key, 0) + 1

        running_total = 0
        customer_growth = []
        for k in sorted(c_bucket_map.keys()):
            running_total += c_bucket_map[k]
            customer_growth.append({'label': k, 'newCustomers': c_bucket_map[k], 'totalCustomers': running_total})

        # ── Order volume trends ──
        vol_qs = Order.objects.filter(created_at__gte=since).values('created_at', 'total').order_by('created_at')
        vol_bucket_map = {}
        for row in vol_qs:
            key = self._bucket_key(row['created_at'], period)
            if key not in vol_bucket_map:
                vol_bucket_map[key] = {'count': 0, 'revenue': 0.0}
            vol_bucket_map[key]['count'] += 1
            vol_bucket_map[key]['revenue'] += float(row['total'])

        order_volume = []
        for k in sorted(vol_bucket_map.keys()):
            b = vol_bucket_map[k]
            order_volume.append({'label': k, 'orderCount': b['count'], 'revenue': round(b['revenue'], 2)})

        # ── Average order value ──
        valid_orders = Order.objects.filter(
            created_at__gte=since,
            status__in=['processing', 'ready_for_dispatch', 'out_for_delivery', 'delivered'],
        )
        order_count = valid_orders.count()
        aov = 0.0
        if order_count > 0:
            total = valid_orders.aggregate(s=Sum('total'))['s'] or 0
            aov = round(float(total) / order_count, 2)

        # ── AOV over time ──
        aov_qs = valid_orders.values('created_at', 'total').order_by('created_at')
        aov_bucket_map = {}
        for row in aov_qs:
            key = self._bucket_key(row['created_at'], period)
            if key not in aov_bucket_map:
                aov_bucket_map[key] = {'total': 0.0, 'count': 0}
            aov_bucket_map[key]['total'] += float(row['total'])
            aov_bucket_map[key]['count'] += 1

        aov_over_time = []
        for k in sorted(aov_bucket_map.keys()):
            b = aov_bucket_map[k]
            aov_over_time.append({
                'label': k,
                'avgOrderValue': round(b['total'] / b['count'], 2) if b['count'] > 0 else 0,
            })

        return Response({
            'revenueOverTime': revenue_over_time,
            'topProducts': top_products_data,
            'revenueByCategory': category_data,
            'customerGrowth': customer_growth,
            'orderVolume': order_volume,
            'averageOrderValue': aov,
            'aovOverTime': aov_over_time,
            'period': period,
        })

    @staticmethod
    def _bucket_key(dt, period):
        if period == 'daily':
            return dt.strftime('%Y-%m-%d')
        elif period == 'weekly':
            iso = dt.isocalendar()
            return f"{iso[0]}-W{iso[1]:02d}"
        elif period == 'yearly':
            return dt.strftime('%Y')
        else:
            return dt.strftime('%Y-%m')
