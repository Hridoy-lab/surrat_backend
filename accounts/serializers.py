from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site

from accounts.models import CustomUser
from accounts.tokens import account_activation_token
from accounts.utils import set_otp

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)

        if settings.ACCOUNT_EMAIL_VERIFICATION == 'mandatory':
            user.is_active = False
            otp = set_otp(user)
            mail_subject = 'SI OTP Code'
            message = f'Your OTP code is {otp}. It is valid for 10 minutes.'
            send_mail(mail_subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        user.save()
        #     current_site = get_current_site(self.context['request'])
        #     mail_subject = 'Activate your account.'
        #     uid = urlsafe_base64_encode(force_bytes(user.pk))
        #     token = account_activation_token.make_token(user)
        #     # activation_link = reverse('activate', kwargs={'uidb64': uid, 'token': token})
        #     # activate_url = f'http://{current_site.domain}{activation_link}'
        #     # print(uid, type(uid), token, type(token))
        #     message = render_to_string('accounts/activation_email.html', {
        #         'user': user,
        #         'domain': current_site.domain,
        #         'uid': uid,
        #         'token': token,
        #     })
        #     send_mail(mail_subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        # user.save()

        return user


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data.get('email')
        otp = data.get('otp')
        user = get_object_or_404(CustomUser, email=email)

        if user.otp != otp:
            raise serializers.ValidationError('Invalid OTP.')
        if user.otp_expiration < timezone.now():
            raise serializers.ValidationError('OTP has expired.')

        return data

    def save(self):
        email = self.validated_data['email']
        user = get_object_or_404(User, email=email)
        user.is_email_verified = True
        user.is_active = True
        user.otp = None
        user.otp_expiration = None
        user.save()
        return user


class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        user = get_object_or_404(CustomUser, email=value)
        if user.is_email_verified:
            raise serializers.ValidationError('Email is already verified.')
        return value

    def save(self):
        email = self.validated_data['email']
        user = get_object_or_404(User, email=email)
        otp = set_otp(user)
        mail_subject = 'Your new OTP Code'
        message = f'Your new OTP code is {otp}. It is valid for 10 minutes.'
        send_mail(mail_subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        return user


class ResendActivationEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        user = get_user_model().objects.filter(email=value).first()
        if user and user.is_email_verified:
            raise serializers.ValidationError('Email is already verified.')
        if settings.ACCOUNT_EMAIL_VERIFICATION != 'mandatory':
            raise serializers.ValidationError('No need to verify email.')
        return value

    def save(self):
        request = self.context.get('request')
        email = self.validated_data['email']
        user = get_user_model().objects.filter(email=email).first()

        if user:
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            # activation_link = reverse('activate', kwargs={'uidb64': uid, 'token': token})
            # activate_url = f'http://{current_site.domain}{activation_link}'
            message = render_to_string('accounts/activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': uid,
                'token': token,
            })
            send_mail(mail_subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        user = User.objects.filter(email=value).first()
        if not user:
            raise serializers.ValidationError('There is no user registered with this email address.')
        return value

    def save(self):
        request = self.context.get('request')
        email = self.validated_data['email']
        user = User.objects.filter(email=email).first()

        if user:
            current_site = get_current_site(request)
            mail_subject = 'Reset your password.'
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            # reset_link = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            # reset_url = f'http://{current_site.domain}{reset_link}'
            message = render_to_string('accounts/password_reset_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': uid,
                'token': token,
            })
            send_mail(mail_subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


class LogoutSerializer(serializers.Serializer):
    pass


class PasswordChangeSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)


class AuthSerializer(serializers.Serializer):
    code = serializers.CharField(required=False)
    error = serializers.CharField(required=False)
