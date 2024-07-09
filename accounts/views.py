import requests
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404, render
from .services import get_user_data
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth import login
from accounts.tokens import account_activation_token
from .models import CustomUser
from .serializers import CustomUserSerializer, LogoutSerializer, ResendActivationEmailSerializer, \
    PasswordResetSerializer, PasswordChangeSerializer, AuthSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (AllowAny,)


class ActivateView(APIView):
    serializer_class = LogoutSerializer
    permission_classes = (AllowAny,)

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(User, pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_email_verified = True
            user.is_active = True
            user.save()
            return Response({'status': 'account activated'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'activation link is invalid'}, status=status.HTTP_400_BAD_REQUEST)


class ResendActivationEmailView(generics.GenericAPIView):
    serializer_class = ResendActivationEmailSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'activation email resent'}, status=status.HTTP_200_OK)


class CustomTokenObtainPairView(TokenObtainPairView):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token


class LogoutView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class LogoutAllView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = LogoutSerializer

    def post(self, request):
        tokens = OutstandingToken.objects.filter(user_id=request.user.id)
        for token in tokens:
            t, _ = BlacklistedToken.objects.get_or_create(token=token)

        return Response(status=status.HTTP_205_RESET_CONTENT)


class UserList(generics.ListAPIView):
    queryset = User.objects.all().order_by('pk')
    serializer_class = CustomUserSerializer
    page_size = 1


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer


class VerifyMe(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CustomUserSerializer

    def get(self, request, *args, **kwargs):
        serializer = CustomUserSerializer(request.user)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'password reset email sent'}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = (AllowAny,)

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(User, pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            password = request.data.get('password')
            password_confirm = request.data.get('password_confirm')

            if password and password_confirm and password == password_confirm:
                user.set_password(password)
                user.save()
                return Response({'status': 'password reset complete'}, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'status': 'reset link is invalid'}, status=status.HTTP_400_BAD_REQUEST)


# ================================================Social Authentication================================================

# class GoogleLoginApi(APIView):
#     def get(self, request, *args, **kwargs):
#         auth_serializer = AuthSerializer(data=request.GET)
#         auth_serializer.is_valid(raise_exception=True)
#
#         validated_data = auth_serializer.validated_data
#         user_data = get_user_data(validated_data)
#
#         user = User.objects.get(email=user_data['email'])
#         login(request, user)
#
#         return redirect(settings.BASE_APP_URL)


# class GoogleLoginApi(APIView):
#     def get(self, request, *args, **kwargs):
#         auth_serializer = AuthSerializer(data=request.GET)
#         auth_serializer.is_valid(raise_exception=True)
#
#         validated_data = auth_serializer.validated_data
#         user_data = get_user_data(validated_data['token'])
#
#         user, created = User.objects.get_or_create(email=user_data['email'])
#         if created:
#             user.first_name = user_data.get('given_name', '')
#             user.last_name = user_data.get('family_name', '')
#             user.is_active = True
#             user.save()
#
#         login(request, user)
#
#         return Response({'redirect': settings.BASE_APP_URL})
# class GoogleLoginApi(APIView):
#     permission_classes = (AllowAny,)
#
#     def get(self, request, *args, **kwargs):
#         token = request.GET.get('token')
#         if not token:
#             return Response({'error': 'Token not provided'}, status=status.HTTP_400_BAD_REQUEST)
#
#         payload = {'access_token': token}
#         r = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', params=payload)
#         user_data = r.json()
#
#         if 'error' in user_data:
#             return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
#
#         email = user_data.get('email')
#         if not email:
#             return Response({'error': 'Email not found'}, status=status.HTTP_400_BAD_REQUEST)
#
#         user, created = User.objects.get_or_create(email=email)
#         if created:
#             user.username = email
#             user.save()
#
#         login(request, user)
#         return redirect(settings.BASE_APP_URL)
#
#
# def google_login(request):
#     return render(request, 'accounts/google_login.html')


import os

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests
import jwt


def sign_in(request):
    return render(request, 'accounts/google_login.html')


@csrf_exempt
def auth_receiver(request):
    """
    Google calls this URL after the user has signed in with their Google account.
    """
    token = request.POST['credential']

    try:
        user_data = id_token.verify_oauth2_token(
            token, requests.Request(), os.environ['GOOGLE_OAUTH_CLIENT_ID']
        )
    except ValueError:
        return HttpResponse(status=403)

    # In a real app, I'd also save any new user here to the database. See below for a real example I wrote for Photon Designer.
    # You could also authenticate the user here using the details from Google (https://docs.djangoproject.com/en/4.2/topics/auth/default/#how-to-log-a-user-in)
    request.session['user_data'] = user_data

    return redirect('sign_in')


def sign_out(request):
    del request.session['user_data']
    return redirect('sign_in')

