from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from users.views import (
    RegisterView,
    ForgotPasswordView,
    ResetPasswordView,
    ChangePasswordView,
    CustomTokenObtainPairView,
    LogoutView,
    UserProfileView,
    UserBadgesView,
)

app_name = 'users'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', UserProfileView.as_view(), name='me'),
    path('me/badges/', UserBadgesView.as_view(), name='me_badges'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
]
