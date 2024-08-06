from django.db import models
# from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from accounts.models import CustomUser


# Create your models here.

# class Subscription(models.Model):
#     DURATION_CHOICES = [
#         (1, 'Free'),
#         (30, '1 Month'),
#         (90, '3 Months'),
#         (180, '6 Months'),
#         (365, '1 Year'),
#     ]
#
#     name = models.CharField(max_length=100)
#     duration_days = models.IntegerField(choices=DURATION_CHOICES)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#
#     def __str__(self):
#         return self.name
#
#
# class UserSubscription(models.Model):
#     user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
#     subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
#     start_date = models.DateTimeField(auto_now_add=True)
#     end_date = models.DateTimeField()
#     is_active = models.BooleanField(default=True)
#
#     # def save(self, *args, **kwargs):
#     #     self.end_date = self.start_date + timedelta(days=self.subscription.duration_days)
#     #     super(UserSubscription, self).save(*args, **kwargs)
#     def check_subscription_status(self):
#         if self.is_active:
#             if self.end_date < timezone.now():
#                 self.is_active = False
#                 self.save()
#                 return False, "You have to renew the subscription package."
#             return True, "You can access the chat API."
#         return False, "You have to renew or buy the subscription package."
#     # def save(self, *args, **kwargs):
#     #     if not self.start_date:
#     #         self.start_date = timezone.now()
#     #     self.end_date = self.start_date + timedelta(days=self.subscription.duration_days)
#     #     super(UserSubscription, self).save(*args, **kwargs)
#     def save(self, *args, **kwargs):
#         if not self.start_date:
#             self.start_date = timezone.now()
#         self.end_date = self.start_date + timedelta(days=self.subscription.duration_days)
#
#         # Update is_active status
#         if self.end_date < timezone.now():
#             self.is_active = False
#
#         super(UserSubscription, self).save(*args, **kwargs)
#
#     def __str__(self):
#         return f"{self.user.email} - {self.subscription.name}"


# from django.db import models
# from django.utils import timezone
# from datetime import timedelta
# from accounts.models import CustomUser
#
# # Create your models here.
#
# class Subscription(models.Model):
#     DURATION_CHOICES = [
#         (1, 'Free'),
#         (5, '5 Minutes'),
#         (30, '1 Month'),
#         (90, '3 Months'),
#         (180, '6 Months'),
#         (365, '1 Year'),
#     ]
#
#     name = models.CharField(max_length=100)
#     duration_days = models.IntegerField(choices=DURATION_CHOICES)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#
#     def __str__(self):
#         return self.name
#
#
# class UserSubscription(models.Model):
#     user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
#     subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
#     start_date = models.DateTimeField(auto_now_add=True)
#     end_date = models.DateTimeField()
#     is_active = models.BooleanField(default=True)
#
#     def check_subscription_status(self):
#         if self.is_active:
#             if self.end_date < timezone.now():
#                 self.is_active = False
#                 self.save()
#                 return False, "You have to renew the subscription package."
#             return True, "You can access the chat API."
#         return False, "You have to renew or buy the subscription package."
#
#     def save(self, *args, **kwargs):
#         if not self.start_date:
#             self.start_date = timezone.now()
#
#         if self.subscription.duration_days == 5:
#             self.end_date = self.start_date + timedelta(minutes=5)
#         else:
#             self.end_date = self.start_date + timedelta(days=self.subscription.duration_days)
#
#         # Update is_active status
#         if self.end_date < timezone.now():
#             self.is_active = False
#
#         super(UserSubscription, self).save(*args, **kwargs)
#
#     def __str__(self):
#         return f"{self.user.email} - {self.subscription.name}"


from django.db import models
from django.utils import timezone
from datetime import timedelta
from accounts.models import CustomUser

class Subscription(models.Model):
    DURATION_CHOICES = [
        (1, 'Free'),
        (5, '5 Minutes'),
        (30, '1 Month'),
        (90, '3 Months'),
        (180, '6 Months'),
        (365, '1 Year'),
    ]

    name = models.CharField(max_length=100)
    duration_days = models.IntegerField(choices=DURATION_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class UserSubscription(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()



    @property
    def is_active(self):
        # Calculate whether the subscription is active
        return self.end_date > timezone.now()

    def check_subscription_status(self):
        if self.is_active:
            return True, "You can access the chat API."
        return False, "You have to renew or buy the subscription package."

    def renew(self, new_subscription):
        """
        Renew the subscription with a new subscription plan.
        """
        self.subscription = new_subscription
        self.start_date = timezone.now()

        if new_subscription.duration_days == 5:
            self.end_date = self.start_date + timedelta(minutes=5)
        else:
            self.end_date = self.start_date + timedelta(days=new_subscription.duration_days)

        self.save()

    def save(self, *args, **kwargs):
        if not self.start_date:
            self.start_date = timezone.now()

        if self.subscription.duration_days == 5:
            self.end_date = self.start_date + timedelta(minutes=5)
        else:
            self.end_date = self.start_date + timedelta(days=self.subscription.duration_days)

        super(UserSubscription, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - {self.subscription.name}"

