from django.core.exceptions import ValidationError
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


class instruction_per_page(models.Model):
    page_number = models.PositiveIntegerField(unique=True, null=True, blank=True)
    instruction_text = models.TextField(null=True, blank=True)
    # instruction_image = models.ImageField(upload_to='instructions/', null=True, blank=True)

    def __str__(self):
        return f"Page {self.page_number}"

    # def clean(self):
    #     super().clean()
    #     if not self.instruction_text and not self.instruction_image:
    #         raise ValidationError("You must provide either an instruction text or an instruction image.")
    #     if self.instruction_text and self.instruction_image:
    #         raise ValidationError("You can only provide either an instruction text or an instruction image, not both.")
