from rest_framework import serializers


class AudioFileSerializer(serializers.Serializer):
    file = serializers.FileField()
    lang = serializers.CharField(max_length=10, default='sme', required=False)
    # prompt = serializers.CharField(max_length=255, required=False)
