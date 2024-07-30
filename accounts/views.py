import requests
from django.utils import timezone
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
from django.shortcuts import get_object_or_404
from accounts.tokens import account_activation_token
from .models import CustomUser
from .serializers import CustomUserSerializer, LogoutSerializer, ResendActivationEmailSerializer, \
    PasswordResetSerializer, PasswordChangeSerializer, AuthSerializer, VerifyOTPSerializer, ResendOTPSerializer, \
    GoogleLoginSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (AllowAny,)


class VerifyOTPView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'OTP verified'}, status=status.HTTP_200_OK)


class ResendOTPView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = ResendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'New OTP sent'}, status=status.HTTP_200_OK)


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
# Function to get Google user info
def get_google_user_info(access_token):
    print("Hello")
    import requests
    response = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    print("This is response:", response)
    return response.json()


class GoogleAuthAPI(APIView):
    serializer_class = GoogleLoginSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        print("Hello")
        access_token = request.data.get("access_token")
        print(access_token)
        user_info = get_google_user_info(access_token)
        print("User info:", user_info)
        email = user_info.get("email")
        if not user_info or not user_info.get("email"):
            return {"Error": "Authentication failed"}

        # Get or create the user
        user, created = User.objects.get_or_create(email=email)
        if created or not user.is_email_verified:
            user.is_email_verified = True
            user.save()
        # Create JWT token
        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        token = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return Response({"user": user.id, "token": token}, status=status.HTTP_200_OK)
