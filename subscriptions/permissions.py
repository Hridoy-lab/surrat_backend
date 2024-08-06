from rest_framework.permissions import BasePermission
from .models import UserSubscription
from django.utils import timezone


class HasActiveSubscription(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        try:
            user_subscription = UserSubscription.objects.get(user=user)
            if user_subscription:
                return user_subscription.is_active
        except UserSubscription.DoesNotExist:
            return False
        return False
