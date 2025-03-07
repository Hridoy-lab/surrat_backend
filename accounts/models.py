from datetime import timedelta

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.timezone import now
from stripe import client_id

from accounts.managers import CustomUserManager
from utils.google_drive_refreshtoken import authenticate_google_drive


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True, blank=False, null=False)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    hints = models.BooleanField(default=False, blank=True, null=True)
    transcribed = models.BooleanField(default=False, blank=True, null=True)
    allow_data_for_training = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_expiration = models.DateTimeField(blank=True, null=True)
    otp_resend_attempts = models.PositiveIntegerField(default=0)
    otp_resend_last_attempt = models.DateTimeField(blank=True, null=True)
    otp_resend_cooldown_period = models.DurationField(
        default=timezone.timedelta(hours=2)
    )

    # TTS Provider Choices
    TTS_PROVIDER_CHOICES = (
        ('acapela', 'Acapela'),
        ('giellalt', 'GiellaLT'),
    )
    tts_provider = models.CharField(
        max_length=10,
        choices=TTS_PROVIDER_CHOICES,
        default='acapela',
        help_text="Select the TTS provider."
    )

    # GiellaLT Voice Choices
    GIELLALT_VOICE_CHOICES = (
        ('biret', 'Biret (Female)'),
        ('mahtte', 'Mahtte (Male)'),
    )
    giellalt_voice = models.CharField(
        max_length=10,
        choices=GIELLALT_VOICE_CHOICES,
        default='biret',
        blank=True,
        null=True,
        help_text="Select the GiellaLT voice (applies only if GiellaLT is chosen)."
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        """
        Ensure that the instance is saved before checking many-to-many fields.
        """
        # Check if the instance is new
        is_new = self._state.adding  # True if the instance is being created

        super().save(*args, **kwargs)  # Save the user first

        # if not is_new:  # Only check permissions after the user has an ID
        if self.user_permissions.exists() or self.groups.exists():
            self.is_staff = True

            # Save again to update is_staff if needed
            super().save(update_fields=['is_staff'])

        # Ensure giellalt_voice is null if tts_provider is not GiellaLT
        if self.tts_provider != 'giellalt' and self.giellalt_voice is not None:
            self.giellalt_voice = None
            super().save(update_fields=['giellalt_voice'])

    def __str__(self):
        return self.email


class GoogleDriveCredentials(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    client_id = models.CharField(max_length=512, blank=True, null=True)
    client_secret = models.CharField(max_length=512, blank=True, null=True)
    refresh_token = models.CharField(max_length=512, blank=True, null=True)
    access_token = models.CharField(max_length=512, blank=True, null=True)  # Added
    token_expiry = models.DateTimeField(null=True, blank=True)  # Added
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user',)  # Ensures one credential set per user
        verbose_name = "Google Drive Credential"
        verbose_name_plural = "Google Drive Credentials"

    def __str__(self):
        return f"Credentials for {self.user}"


    def save(self, *args, **kwargs):
        """
        If credentials are new or client details changed, authenticate and save tokens.
        """
        if not self.refresh_token and self.client_id and self.client_secret:
            creds = authenticate_google_drive(self.client_id, self.client_secret)

            if creds:
                self.access_token = creds.token
                self.refresh_token = creds.refresh_token
                # self.token_expiry = now() + timedelta(seconds=creds.expiry.timestamp() - now().timestamp())

        super().save(*args, **kwargs)

