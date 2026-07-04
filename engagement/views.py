import uuid
from django.conf import settings
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .models import WishlistItem
from .serializers import WishlistItemSerializer

class WishlistAPIView(APIView):
    permission_classes = [AllowAny]
    
    def get_session_key(self, request):
        session_key = request.COOKIES.get('session_key')
        if not session_key:
            session_key = str(uuid.uuid4())
        return session_key

    def get(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'customerprofile'):
            items = WishlistItem.objects.filter(customer=request.user.customerprofile)
        else:
            session_key = request.COOKIES.get('session_key')
            if not session_key:
                return Response([])
            items = WishlistItem.objects.filter(session_key=session_key)
            
        serializer = WishlistItemSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        product_id = request.data.get('product')
        if not product_id:
            return Response({"error": "Product ID required"}, status=status.HTTP_400_BAD_REQUEST)
            
        is_auth = request.user.is_authenticated and hasattr(request.user, 'customerprofile')
        customer = request.user.customerprofile if is_auth else None
        session_key = self.get_session_key(request) if not is_auth else None
        
        # Check if already exists
        if is_auth:
            exists = WishlistItem.objects.filter(customer=customer, product_id=product_id).exists()
        else:
            exists = WishlistItem.objects.filter(session_key=session_key, product_id=product_id).exists()
            
        if exists:
            return Response({"message": "Already in wishlist"}, status=status.HTTP_200_OK)
            
        try:
            item = WishlistItem.objects.create(
                customer=customer,
                session_key=session_key,
                product_id=product_id
            )
        except IntegrityError:
            return Response({"message": "Already in wishlist"}, status=status.HTTP_200_OK)
        
        serializer = WishlistItemSerializer(item)
        response = Response(serializer.data, status=status.HTTP_201_CREATED)
        
        if not is_auth and not request.COOKIES.get('session_key'):
            response.set_cookie(
                'session_key',
                session_key,
                max_age=60*60*24*30,
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax'
            )
            
        return response

class WishlistItemAPIView(APIView):
    permission_classes = [AllowAny]
    
    def delete(self, request, pk):
        is_auth = request.user.is_authenticated and hasattr(request.user, 'customerprofile')
        try:
            if is_auth:
                item = WishlistItem.objects.get(pk=pk, customer=request.user.customerprofile)
            else:
                session_key = request.COOKIES.get('session_key')
                if not session_key:
                    return Response({"detail": "Session key required."}, status=status.HTTP_400_BAD_REQUEST)
                item = WishlistItem.objects.get(pk=pk, session_key=session_key)
            
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except WishlistItem.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class RecentlyViewedAPIView(APIView):
    """
    GET  /api/recently-viewed/  → last 10 distinct products for this session/user
    POST /api/recently-viewed/  → record a product view (fire-and-forget)
    """
    permission_classes = [AllowAny]

    def _get_session_key(self, request):
        return request.COOKIES.get('session_key') or str(uuid.uuid4())

    def get(self, request):
        from .models import RecentlyViewed
        from products.serializers import ProductSerializer

        if request.user.is_authenticated and hasattr(request.user, 'customerprofile'):
            entries = (
                RecentlyViewed.objects
                .filter(customer=request.user.customerprofile)
                .select_related('product')
                .order_by('-viewed_at')[:10]
            )
        else:
            session_key = request.COOKIES.get('session_key')
            if not session_key:
                return Response([])
            entries = (
                RecentlyViewed.objects
                .filter(session_key=session_key)
                .select_related('product')
                .order_by('-viewed_at')[:10]
            )

        # Deduplicate by product id while preserving order
        seen = set()
        products = []
        for entry in entries:
            if entry.product_id not in seen:
                seen.add(entry.product_id)
                products.append(entry.product)

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        from .models import RecentlyViewed

        product_id = request.data.get('product')
        if not product_id:
            return Response({"error": "Product ID required"}, status=status.HTTP_400_BAD_REQUEST)

        is_auth = request.user.is_authenticated and hasattr(request.user, 'customerprofile')
        customer = request.user.customerprofile if is_auth else None
        session_key = self._get_session_key(request) if not is_auth else None

        # Update or create — auto_now on viewed_at keeps timestamp fresh
        if is_auth:
            obj, _ = RecentlyViewed.objects.update_or_create(
                customer=customer, product_id=product_id,
                defaults={'session_key': None}
            )
        else:
            obj, _ = RecentlyViewed.objects.update_or_create(
                session_key=session_key, product_id=product_id,
                defaults={'customer': None}
            )

        response = Response({"status": "recorded"}, status=status.HTTP_201_CREATED)

        if not is_auth and not request.COOKIES.get('session_key'):
            response.set_cookie(
                'session_key',
                session_key,
                max_age=60*60*24*30,
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax'
            )

        return response
