import random
from django.conf import settings
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import update_session_auth_hash
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from Authentication.models import PasswordResetCode
from Authentication.utils import send_password_reset_code,send_email_verification_code
from Authentication.serializers import (UserRegistrationSerializer,MyTokenObtainPairSerializer,
                                        ChangePasswordSerializer,ForgotPasswordEmailSerializer,
                                        PasswordResetSerializer,UserProfileSerializer,UserProfileUpdateSerializer,
                                        ResendEmailVerificationSerializer,generate_verification_code
                                        )
# Create your views here.

User = get_user_model()

class UserRegistrationView(APIView):
    def post(self, request):
        try:
            with transaction.atomic():
                # Begin a transaction
                serializer = UserRegistrationSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                
                # Only save after validation is passed
                user = serializer.save()

                response_data = {
                    'full_name': user.full_name,
                    'username': user.username,
                    'email': user.email,
                    'email_verification_code': user.email_verification_code,
                }

            # Commit the transaction and return success response
            return Response({'message': 'User registered successfully', 'response_data': response_data}, status=status.HTTP_201_CREATED)
        except serializer.ValidationError as e:
            # If validation fails, the user will not be created
            return Response({'error': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Catch any other exceptions and rollback transaction
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        
class EmailVerificationView(APIView):
    def post(self, request):
        verification_code = request.data.get('verification_code')
        email = request.data.get('email')

        if not verification_code or not email:
            return Response({'message': 'Verification code and email are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email_verification_code=verification_code, email=email,is_active=False)
        except User.DoesNotExist:
            return Response({'message': 'Invalid verification code.'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.is_active = True
        user.email_verification_code = ''
        user.save()

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Return response with tokens and user data
        return Response({
            'message': 'Email verified successfully',
            'access_token': access_token,
            'refresh_token': str(refresh),
            'user_data': {
                'full_name': user.full_name,
                'username': user.username,
                'email': user.email,
                'is_active': user.is_active,

            }
        }, status=status.HTTP_200_OK)

class ResendEmailVerificationView(APIView):

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'message': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'No account found with this email.'}, status=status.HTTP_404_NOT_FOUND)

        # if user.is_verified:
        #     return Response({'message': 'This account is already verified.'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate a new verification code
        email_verification_code = generate_verification_code()
        user.email_verification_code = email_verification_code
        user.save()

        # Send verification email
        send_email_verification_code(user.email, email_verification_code, user.username)

        return Response({'message': 'Verification email sent successfully.'}, status=status.HTTP_200_OK)
   
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user
            old_password = serializer.data.get('old_password')
            new_password = serializer.data.get('new_password')

            # Check if the new password is the same as the old one
            if user.check_password(new_password):
                return Response({'error': 'New password cannot be the same as the old one.'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the old password is correct
            if user.check_password(old_password):
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Incorrect old password.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class ForgotPasswordView(APIView):
    def generate_numeric_code(self):
        # Generate a 6-digit numeric code
        return ''.join(random.choices('0123456789', k=6))

    def post(self, request):
        serializer = ForgotPasswordEmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({'detail': 'No user with this email address exist.'}, status=status.HTTP_404_NOT_FOUND)

            # Generate and store a unique 6-digit numeric code
            code = self.generate_numeric_code()
            PasswordResetCode.objects.create(user=user, code=code)

            try:
                # send the email
                send_password_reset_code(user.email, code, user.username)
                return Response({'detail': 'An email with a reset code has been sent to your email address.'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'detail': 'Failed to send the reset code. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            reset_code = serializer.validated_data['reset_code']
            new_password = serializer.validated_data['new_password']

            try:
                password_reset_code = PasswordResetCode.objects.get(code=reset_code)

                # Check if the reset code is expired
                if password_reset_code.is_expired:
                    return Response({'detail': 'The reset code has expired.'}, status=status.HTTP_400_BAD_REQUEST)
                
                user = password_reset_code.user
                
                # Check if the reset code is associated with a user
                user = password_reset_code.user
                if user:
                    # Check if the user's email matches the requester's email
                    if user.email != request.data.get('email'):
                        return Response({'detail': 'Invalid email for this reset code.'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'detail': 'Invalid reset code.'}, status=status.HTTP_400_BAD_REQUEST)

                # Check if the new password is different from the old one
                if user.check_password(new_password):
                    return Response({'detail': 'New password cannot be the same as the old one.'}, status=status.HTTP_400_BAD_REQUEST)
                # Set and save the new password
                user.set_password(new_password)
                user.save()
                # Delete the reset code after successful password reset
                password_reset_code.delete()

                return Response({'detail': 'Password reset successfully.'}, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                return Response({'detail': 'Invalid reset code.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer 

    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.filter(email=user.email)
        return queryset  
             
class UserProfileUpdateView(APIView):
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)