from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import RegisterView, CustomTokenObtainPairView, LogoutView, UserDetail, UserList, LogoutAllView, VerifyMe, \
    ActivateView, ResendActivationEmailView, PasswordResetView, PasswordResetConfirmView, sign_in, sign_out, \
    auth_receiver, VerifyOTPView, ResendOTPView

app_name = 'accounts'

urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('api/resend-otp/', ResendOTPView.as_view(), name='resend_otp'),
    path('api/activate/<slug:uidb64>/<slug:token>/', ActivateView.as_view(), name='activate'),
    path('api/resend-activation-email/', ResendActivationEmailView.as_view(), name='resend_activation_email'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/logout_all/', LogoutAllView.as_view(), name='auth_logout_all'),
    path('api/users/', UserList.as_view()),
    path('api/users/<int:pk>/', UserDetail.as_view()),
    path('api/verify-me/', VerifyMe.as_view(), name='verify_me'),
    path('api/password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('api/password-reset-confirm/<slug:uidb64>/<slug:token>/', PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    # path('api/google', GoogleLoginApi.as_view(), name='google_login'),
    # path('api/google', GoogleLoginApi.as_view(), name='google_login'),
    # path('google-login/', google_login, name='google_login_page'),
    path('google/login/callback/', sign_in, name='sign_in'),
    path('sign-out', sign_out, name='sign_out'),
    path('auth-receiver', auth_receiver, name='auth_receiver'),
]
