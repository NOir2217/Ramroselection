import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
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

        variant = get_object_or_404(ProductVariant, id=variant_id)
        
        cart_item, created = CartItem.objects.get_or_create(cart=cart, variant=variant, defaults={'quantity': quantity})
        if not created:
            cart_item.quantity += int(quantity)
            cart_item.save()

        serializer = CartSerializer(cart)
        response = Response(serializer.data, status=status.HTTP_201_CREATED)
        if not request.user.is_authenticated:
            # In cartItem view, we have to duplicate the cookie helper or abstract it
            response.set_cookie('cart_token', str(cart.id), max_age=60*60*24*30, httponly=True, samesite='Lax')
        return response

class CartItemDetailAPIView(APIView):
    permission_classes = [AllowAny]
    
    def patch(self, request, pk):
        cart_item = get_object_or_404(CartItem, id=pk)
        quantity = request.data.get('quantity')
        if quantity is not None:
            if int(quantity) <= 0:
                cart_item.delete()
            else:
                cart_item.quantity = int(quantity)
                cart_item.save()
        return Response(CartSerializer(cart_item.cart).data)

    def delete(self, request, pk):
        cart_item = get_object_or_404(CartItem, id=pk)
        cart = cart_item.cart
        cart_item.delete()
        return Response(CartSerializer(cart).data)

from django.db import transaction
from .models import Order, OrderItem
from accounts.models import Address, CustomerProfile

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
        
        # Calculate totals
        subtotal = sum(
            item.quantity * (item.variant.product.price + item.variant.extra_price)
            for item in cart.items.all()
        )
        
        shipping_fee = 10.00 # hardcoded placeholder
        total = float(subtotal) + shipping_fee
        
        # Create Guest info or use authenticated user
        guest_email = request.data.get('email')
        
        order = Order.objects.create(
            customer=request.user.customerprofile if request.user.is_authenticated else None,
            guest_email=guest_email if not request.user.is_authenticated else None,
            status='pending_payment',
            subtotal=subtotal,
            shipping_fee=shipping_fee,
            total=total,
        )
        
        # Transfer cart items to order items and decrement stock
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                variant=item.variant,
                quantity=item.quantity,
                unit_price=item.variant.product.price + item.variant.extra_price
            )
            item.variant.stock_quantity -= item.quantity
            item.variant.save()
            
        # Clear cart
        cart.items.all().delete()
        
        response = Response({
            "order_number": order.order_number,
            "total": total,
            "status": "pending_payment"
        }, status=status.HTTP_201_CREATED)
        
        return response

from .models import ReturnRequest
from .serializers import OrderSerializer, ReturnRequestSerializer

class OrderListAPIView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        orders = Order.objects.filter(customer=request.user.customerprofile).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

class OrderRetrieveAPIView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, order_number):
        order = get_object_or_404(Order, order_number=order_number)
        
        # Verify access
        if order.customer:
            if not request.user.is_authenticated or request.user.customerprofile != order.customer:
                return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
                
        serializer = OrderSerializer(order)
        return Response(serializer.data)

class OrderReturnAPIView(APIView):
    def post(self, request, item_id):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
            
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
