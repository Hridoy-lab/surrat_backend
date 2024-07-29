# from django.conf import settings
# from django.db import models
#
#
# class ChatHistory(models.Model):
#     USER = 'USER'
#     BOT = 'BOT'
#
#     SENDER_CHOICES = [
#         (USER, 'User'),
#         (BOT, 'Bot'),
#     ]
#
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_histories')
#     message = models.TextField()
#     sender = models.CharField(max_length=4, choices=SENDER_CHOICES, default=USER)
#     timestamp = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f'{self.user.email} - {self.timestamp} - {self.sender}'


from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_message = models.TextField()
    bot_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email}: {self.user_message[:50]} - {self.bot_reply[:50]}"
