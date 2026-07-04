from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .serializers import RegisterSerializer, UserSerializer

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

        response = Response(
            {"access": serializer.validated_data.get("access")},
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

        response = Response(
            {"access": serializer.validated_data.get("access")},
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
    GET  /api/auth/preferences/ → returns default_size, skin_type
    PATCH /api/auth/preferences/ → updates default_size, skin_type
    """

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        profile = request.user.customerprofile
        return Response({
            "default_size": profile.default_size,
            "skin_type": profile.skin_type,
            "phone": profile.phone,
        })

    def patch(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        profile = request.user.customerprofile
        allowed_fields = ['default_size', 'skin_type', 'phone']

        for field in allowed_fields:
            if field in request.data:
                setattr(profile, field, request.data[field])

        profile.save()
        return Response({
            "default_size": profile.default_size,
            "skin_type": profile.skin_type,
            "phone": profile.phone,
        })
