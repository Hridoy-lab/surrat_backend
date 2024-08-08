import time
import logging
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated

from users.models import ChatHistory
from .services.ai_services import AIService
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from bot.serializers import (
    AudioFileSerializer,
    TranslationSerializer,
    TranscriptSerializer,
)
from subscriptions.permissions import HasActiveSubscription
from bot.services.translate import Translator
from .services.transcribe import Transcriber

# Create your views here.
logger = logging.getLogger(__name__)
ai_service = AIService()


class ProcessAudio(APIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = AudioFileSerializer

    def post(self, request, *args, **kwargs):
        serializer = AudioFileSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data["file"]
            target_lang = serializer.validated_data.get("lang", "sme")
            # chatgpt_prompt = serializer.validated_data.get('prompt', None)

            if file.name.lower().endswith((".mp3", ".wav")):
                audio_data = file.read()
                filename = f"Generated_Audio_{target_lang}_{time.time()}.mp3"
                result = ai_service.process_audio(audio_data, filename)
                print(result)
                if "error" in result:
                    return JsonResponse(result, status=400)

                ChatHistory.objects.create(
                    user=request.user,
                    user_message=result,
                    bot_reply=result["translated_chat_response"],
                )

                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "Unsupported file format"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Translate(APIView):
    serializer_class = TranslationSerializer
    permission_classes = [
        IsAuthenticated,
        HasActiveSubscription,
    ]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            text = serializer.validated_data["text"]
            source_language = serializer.validated_data["source_language"]
            target_language = serializer.validated_data["target_language"]
            translation_object = Translator()
            response = translation_object.perform_translation(
                text=text, src_lang=source_language, tgt_lang=target_language
            )
            return Response(response, status=status.HTTP_200_OK)


class Transcript(APIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = TranscriptSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = serializer.validated_data["file"]
        transcript_object = Transcriber()

        try:
            response = transcript_object.transcribe_voice(audio_data=file.read())
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return JsonResponse({"data": response}, status=status.HTTP_200_OK)
