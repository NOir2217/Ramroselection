from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .serializers import RegisterSerializer, UserSerializer, AddressSerializer, CustomerProfileSerializer
from .models import Address
from django.contrib.auth.models import User

def set_jwt_cookies(response, refresh_token):
    """Helper to set refresh token in an HttpOnly cookie."""
    response.set_cookie(
        key=settings.JWT_COOKIE_NAME,
        value=str(refresh_token),
        httponly=settings.JWT_COOKIE_HTTPONLY,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()
    )

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Login endpoint. Returns access token in body, sets refresh token in HttpOnly cookie.
    """
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        # Get the user instance from serializer
        user = serializer.user
        response = Response(
            {
                "access": serializer.validated_data.get("access"),
                "user": UserSerializer(user).data
            },
            status=status.HTTP_200_OK
        )
        refresh_token = serializer.validated_data.get("refresh")
        set_jwt_cookies(response, refresh_token)
        return response

class CustomTokenRefreshView(TokenRefreshView):
    """
    Refresh endpoint. Reads refresh token from HttpOnly cookie, returns new access token.
    """
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get(settings.JWT_COOKIE_NAME)
        if not refresh_token:
            return Response(
                {"detail": "Refresh token cookie not found."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Inject cookie into request data so the serializer can find it
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        data['refresh'] = refresh_token
        
        serializer = self.get_serializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        # Get user details from the refresh token payload
        try:
            token = RefreshToken(refresh_token)
            user_id = token.payload.get('user_id')
            user = User.objects.get(id=user_id)
            serialized_user = UserSerializer(user).data
        except Exception:
            serialized_user = None

        response = Response(
            {
                "access": serializer.validated_data.get("access"),
                "user": serialized_user
            },
            status=status.HTTP_200_OK
        )
        
        # If ROTATE_REFRESH_TOKENS is True, SimpleJWT returns a new refresh token
        new_refresh = serializer.validated_data.get("refresh")
        if new_refresh:
            set_jwt_cookies(response, new_refresh)
            
        return response

class LogoutView(APIView):
    """
    Logout endpoint. Blacklists the refresh token and clears the cookie.
    """
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        try:
            refresh_token = request.COOKIES.get(settings.JWT_COOKIE_NAME)
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                
            response = Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
            response.delete_cookie(settings.JWT_COOKIE_NAME, samesite=settings.JWT_COOKIE_SAMESITE)
            return response
        except Exception as e:
            return Response({"detail": "An error occurred during logout."}, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(APIView):
    """
    Registration endpoint. Creates user/profile, returns access token, sets refresh cookie.
    """
    permission_classes = (AllowAny,)
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate tokens for the new user
            refresh = RefreshToken.for_user(user)
            
            response = Response({
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token)
            }, status=status.HTTP_201_CREATED)
            
            set_jwt_cookies(response, refresh)
            return response
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfilePreferencesView(APIView):
    """
    GET  /api/auth/preferences/ → returns default_size, skin_type, phone
    PATCH /api/auth/preferences/ → updates default_size, skin_type, phone
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.customerprofile
        serializer = CustomerProfileSerializer(profile)
        return Response(serializer.data)

    @transaction.atomic
    def patch(self, request):
        profile = request.user.customerprofile
        serializer = CustomerProfileSerializer(
            profile, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class AddressListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        if request.user.is_authenticated:
            profile = request.user.customerprofile
            addresses = Address.objects.filter(profile=profile).order_by('-is_default', 'id')
            serializer = AddressSerializer(addresses, many=True)
            return Response(serializer.data)
        else:
            guest_addresses = request.session.get('guest_addresses', [])
            return Response(guest_addresses)

    def post(self, request):
        serializer = AddressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        is_default = serializer.validated_data.get('is_default', False)
        
        if request.user.is_authenticated:
            profile = request.user.customerprofile
            if is_default:
                Address.objects.filter(profile=profile).update(is_default=False)
            address = serializer.save(profile=profile)
            return Response(AddressSerializer(address).data, status=status.HTTP_201_CREATED)
        else:
            guest_addresses = request.session.get('guest_addresses', [])
            new_id = max([addr.get('id', 0) for addr in guest_addresses] + [0]) + 1
            
            new_address = {
                'id': new_id,
                'full_name': serializer.validated_data.get('full_name'),
                'phone': serializer.validated_data.get('phone'),
                'street': serializer.validated_data.get('street'),
                'city': serializer.validated_data.get('city'),
                'postal_code': serializer.validated_data.get('postal_code'),
                'country': serializer.validated_data.get('country'),
                'is_default': is_default
            }
            
            if is_default:
                for addr in guest_addresses:
                    addr['is_default'] = False
                    
            guest_addresses.append(new_address)
            request.session['guest_addresses'] = guest_addresses
            request.session.modified = True
            return Response(new_address, status=status.HTTP_201_CREATED)

class AddressDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get_address_or_404(self, request, pk):
        if request.user.is_authenticated:
            profile = request.user.customerprofile
            try:
                return Address.objects.get(pk=pk, profile=profile)
            except Address.DoesNotExist:
                return None
        else:
            guest_addresses = request.session.get('guest_addresses', [])
            for addr in guest_addresses:
                if addr.get('id') == pk:
                    return addr
            return None

    def get(self, request, pk):
        addr = self.get_address_or_404(request, pk)
        if addr is None:
            return Response({"detail": "Address not found."}, status=status.HTTP_404_NOT_FOUND)
        if request.user.is_authenticated:
            return Response(AddressSerializer(addr).data)
        return Response(addr)

    def patch(self, request, pk):
        addr = self.get_address_or_404(request, pk)
        if addr is None:
            return Response({"detail": "Address not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.user.is_authenticated:
            serializer = AddressSerializer(addr, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            is_default = serializer.validated_data.get('is_default', False)
            if is_default:
                Address.objects.filter(profile=request.user.customerprofile).exclude(pk=pk).update(is_default=False)
            updated_addr = serializer.save()
            return Response(AddressSerializer(updated_addr).data)
        else:
            guest_addresses = request.session.get('guest_addresses', [])
            for idx, item in enumerate(guest_addresses):
                if item.get('id') == pk:
                    serializer = AddressSerializer(data=request.data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    
                    for field in ['full_name', 'phone', 'street', 'city', 'postal_code', 'country', 'is_default']:
                        if field in serializer.validated_data:
                            item[field] = serializer.validated_data[field]
                            
                    is_default = item.get('is_default', False)
                    if is_default:
                        for other in guest_addresses:
                            if other.get('id') != pk:
                                other['is_default'] = False
                                
                    request.session['guest_addresses'] = guest_addresses
                    request.session.modified = True
                    return Response(item)
            return Response({"detail": "Address not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        if request.user.is_authenticated:
            profile = request.user.customerprofile
            try:
                addr = Address.objects.get(pk=pk, profile=profile)
                addr.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Address.DoesNotExist:
                return Response({"detail": "Address not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            guest_addresses = request.session.get('guest_addresses', [])
            filtered_addresses = [addr for addr in guest_addresses if addr.get('id') != pk]
            if len(filtered_addresses) == len(guest_addresses):
                return Response({"detail": "Address not found."}, status=status.HTTP_404_NOT_FOUND)
            request.session['guest_addresses'] = filtered_addresses
            request.session.modified = True
            return Response(status=status.HTTP_204_NO_CONTENT)

