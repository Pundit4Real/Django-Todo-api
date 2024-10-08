import string
import random
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from .utils import send_email_verification_code
from .models import User, UserProfile

User = get_user_model()

def generate_verification_code(length=6):
    return ''.join(random.choices('0123456789', k=length))

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if not email or not password:
            raise ValidationError('Email and password are required.')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed('No account found with this email.')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password.')

        try:
            data = super().validate(attrs)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        try:
            refresh = RefreshToken.for_user(user)
            access = AccessToken.for_user(user)
        except Exception as e:
            raise AuthenticationFailed('Token generation failed.')

        data['message'] = 'Login successful'
        data['tokens'] = {
            'refresh_token': str(refresh),
            'access_token': str(access),
        }
        data['user_data'] = {
            'id': user.id,
            'full_name': user.full_name,
            'username': user.username,
            'email': user.email,
            'phone': user.phone,
            'country': user.country
        }

        data.pop('refresh', None)
        data.pop('access', None)

        return data

class UserRegistrationSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['full_name', 'email', 'username', 'password', 'password_confirm']
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'required': True},
            'email': {'required': True}
        }

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise ValidationError("This username is already taken.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def validate(self, data):
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError("Passwords do not match.")
        
        if data.get('username') == data.get('password'):
            raise serializers.ValidationError("Password cannot be the same as the username.")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        email_verification_code = generate_verification_code()

        validated_data['email_verification_code'] = email_verification_code
        user = User.objects.create_user(**validated_data)

        # Send verification email
        send_email_verification_code(validated_data['email'], email_verification_code, user.username)
        return user

class ResendEmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class ForgotPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class PasswordResetSerializer(serializers.Serializer):
    reset_code = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'username', 'avatar','phone','country']

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'username', 'avatar','phone','country']
