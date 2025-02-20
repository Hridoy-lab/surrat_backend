from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from accounts.managers import CustomUserManager


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

        if not is_new:  # Only check permissions after the user has an ID
            if self.user_permissions.exists() or self.groups.exists():
                self.is_staff = True
            else:
                self.is_staff = False

            # Save again to update is_staff if needed
            super().save(update_fields=['is_staff'])

    def __str__(self):
        return self.email
