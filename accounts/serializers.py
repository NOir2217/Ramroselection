from rest_framework import serializers
from django.contrib.auth.models import User
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
        fields = ('id', 'username', 'email', 'is_staff', 'profile')
        read_only_fields = ('id', 'is_staff')

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        # Create corresponding CustomerProfile
        CustomerProfile.objects.create(user=user, email=validated_data['email'])
        return user
