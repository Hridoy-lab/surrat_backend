from rest_framework import serializers
from django.core.exceptions import ValidationError
import mimetypes


class AudioFileSerializer(serializers.Serializer):
    file = serializers.FileField()
    lang = serializers.CharField(max_length=10, default="sme", required=False)

    def validate_file(self, value):
        # Validate the file's MIME type to ensure it's an audio file
        mime_type, encoding = mimetypes.guess_type(value.name)
        if not mime_type or not mime_type.startswith("audio"):
            raise ValidationError("Invalid file type. Only audio files are allowed.")
        return value

    # prompt = serializers.CharField(max_length=255, required=False)


class TranslationSerializer(serializers.Serializer):
    source_language = serializers.CharField(
        max_length=10, default="eng", required=False
    )
    target_language = serializers.CharField(
        max_length=10, default="sme", required=False
    )
    text = serializers.CharField()


class TranscriptSerializer(serializers.Serializer):
    file = serializers.FileField()
