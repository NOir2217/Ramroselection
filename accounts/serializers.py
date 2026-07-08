from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import CustomerProfile

class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ('id', 'email', 'default_size', 'skin_type', 'is_vip', 'phone')
        read_only_fields = ('id', 'is_vip', 'email')

class UserSerializer(serializers.ModelSerializer):
    profile = CustomerProfileSerializer(source='customerprofile', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'profile')
        read_only_fields = ('id', 'is_staff')

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password')
        extra_kwargs = {'username': {'required': False}}

    def validate_email(self, value):
        """Reject duplicate emails with a clear error — never silently allow two accounts with the same email."""
        normalized = value.lower().strip()
        if User.objects.filter(email__iexact=normalized).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return normalized

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def create(self, validated_data):
        import uuid
        base_username = validated_data['email'].split('@')[0].lower()
        # Remove non-alphanumeric characters to keep username valid
        base_username = ''.join(c for c in base_username if c.isalnum() or c in ('_', '.', '-'))[:30] or 'user'
        username = base_username
        # Only resolve username collisions (different email, same prefix) — not email collisions (caught above)
        if User.objects.filter(username=username).exists():
            username = f"{base_username}_{uuid.uuid4().hex[:6]}"

        user = User.objects.create_user(
            username=username,
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password']
        )
        CustomerProfile.objects.create(user=user, email=validated_data['email'])
        return user
