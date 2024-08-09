from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class AudioRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    page_number = models.PositiveIntegerField(null=True, blank=True)
    audio = models.FileField(upload_to="audio/", null=True, blank=True)
    instruction = models.TextField(null=True, blank=True)
    transcribed_text = models.TextField(blank=True, null=True)
    translated_text = models.TextField(blank=True, null=True)
    gpt_response = models.TextField(blank=True, null=True)
    translated_response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request by {self.user.email} on {self.created_at}"
