from django.urls import path
from Authentication.views import (UserRegistrationView,MyTokenObtainPairView,EmailVerificationView,
                                  ChangePasswordView,ForgotPasswordView,ResetPasswordView,ProfileView,
                                  UserProfileUpdateView
                                  )

urlpatterns = [
        # Auth URLs
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('verify-email/', EmailVerificationView.as_view(), name='email-verification'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    # # User Profile URLs
    path('profile/', ProfileView.as_view(), name='profile'),
    path('update-profile/', UserProfileUpdateView.as_view(), name='update-profile'),
]
