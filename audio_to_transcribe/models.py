from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth import get_user_model
from bot.services.ai_services import ExternalProcessData
from bot.services.transcribe import Transcriber

User = get_user_model()

transcriber = Transcriber()

class audio_to_text(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    audio = models.FileField(upload_to="audio/", null=True, blank=True)
    transcribed_text = models.TextField(blank=True, null=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request by {self.user.email} on {self.created_at}"

    def save(self, *args, **kwargs):
        """Override the save method to handle audio transcription before saving."""
        # Save the object initially to ensure the audio file is uploaded.
        super().save(*args, **kwargs)

        # Proceed only if an audio file is present and the text has not been transcribed yet.
        if self.audio:
            self._transcribe_audio()

        super().save(*args, **kwargs)  # Save the updated instance with transcribed text.

    def _transcribe_audio(self):
        """
        Transcribe the uploaded audio file using ExternalProcessData.
        Raises a ValidationError if transcription fails.
        """
        processor = ExternalProcessData(self.user)
        data = {
            "audio_file": self.audio,
        }

        # Attempt to process and transcribe the audio file.
        result = processor.process_audio(data)

        if "error" in result:
            raise ValidationError(result["error"])

        # Set the transcribed text on the model.
        self.transcribed_text = result["transcribed_text"]

    class Meta:
        verbose_name = "Audio to Text"  # Singular name in admin
        verbose_name_plural = "Audio to Text"  # Plural name in admin


