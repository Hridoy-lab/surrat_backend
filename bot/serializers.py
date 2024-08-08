from rest_framework import serializers


class AudioFileSerializer(serializers.Serializer):
    file = serializers.FileField()
    lang = serializers.CharField(max_length=10, default="sme", required=False)
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
