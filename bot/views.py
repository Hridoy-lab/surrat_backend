from django.shortcuts import render
import os
import time
import json
import logging
import threading
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from users.models import ChatHistory
from .services import AIService
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .serializers import AudioFileSerializer

# Create your views here.
logger = logging.getLogger(__name__)
ai_service = AIService()


# def index(request):
#     return render(request, 'index.html')

@csrf_exempt
def handle_transcription(request):
    if request.method == 'POST':
        if 'file' not in request.FILES:
            logger.error("No file part in the request")
            return JsonResponse({"error": "No file part"}, status=400)
        file = request.FILES['file']
        if not file.name:
            logger.error("No file selected for uploading")
            return JsonResponse({"error": "No selected file"}, status=400)
        if file:
            audio_data = file.read()
            transcribed_text = ai_service.transcribe_voice(audio_data)
            logger.info(transcribed_text)
            logger.info("Transcription successful")
            return JsonResponse({"Transcribed Text": transcribed_text})
    return JsonResponse({"error": "Invalid request method"}, status=400)


@csrf_exempt
def translate_text(request):
    if request.method == 'POST':
        content = json.loads(request.body)
        text = content.get('text')
        src_lang = content.get('source_lang')
        tgt_lang = content.get('target_lang')
        logger.info(f"Source Language: {src_lang}, Target Language: {tgt_lang}")

        intermediate_lang = "sme"
        if (src_lang == "nor" and tgt_lang == "eng") or (src_lang == "eng" and tgt_lang == "nor"):
            first_translation = ai_service.perform_translation(text, src_lang, tgt_lang)
            if 'error' in first_translation:
                logger.error(f"Translation error: {first_translation}")
                return JsonResponse(first_translation, status=400)

            second_translation = ai_service.perform_translation(first_translation['Translated Text'], intermediate_lang,
                                                                tgt_lang)
            if 'error' in second_translation:
                logger.error(f"Second translation error: {second_translation}")
                return JsonResponse(second_translation, status=400)

            return JsonResponse({"Translated Text": second_translation['Translated Text']})
        else:
            result = ai_service.perform_translation(text, src_lang, tgt_lang)
            if 'error' in result:
                logger.error(f"Translation error: {result}")
                return JsonResponse(result, status=400)
            return JsonResponse({"Translated Text": result['Translated Text']})
    return JsonResponse({"error": "Invalid request method"}, status=400)


@csrf_exempt
def chat_with_openai_route(request):
    if request.method == 'POST':
        content = json.loads(request.body)
        transcribed_text = content.get('text')
        if not transcribed_text:
            logger.error("No text provided for chat")
            return JsonResponse({'error': 'No text provided'}, status=400)

        chat_response = ai_service.chat_with_openai(transcribed_text)
        logger.info(f"ChatGPT Response: {chat_response}")

        return JsonResponse({"ChatGPT Response": chat_response})
    return JsonResponse({"error": "Invalid request method"}, status=400)


@csrf_exempt
def tts_route(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        text = data.get('text')
        if not text:
            logger.error("No text provided for TTS")
            return JsonResponse({'error': 'No text provided'}, status=400)

        filename = f'Generated_Audio_{time.time()}.mp3'
        threading.Thread(target=ai_service.tts, args=(text, filename)).start()
        logger.info("TTS processing started")
        return JsonResponse({'message': 'TTS processing started, please wait...', 'filename': filename})
    return JsonResponse({"error": "Invalid request method"}, status=400)


@csrf_exempt
def process_audio(request):
    if request.method == 'POST':

        if 'file' not in request.FILES:
            logger.error("No file part in the request")
            return JsonResponse({"error": "No file part"}, status=400)

        file = request.FILES['file']
        if not file.name:
            logger.error("No file selected for uploading")
            return JsonResponse({"error": "No selected file"}, status=400)

        logger.info(file.name)
        if file:
            if file.name.lower().endswith(('.mp3', '.wav')):
                audio_data = file.read()
                target_lang = request.POST.get('lang', 'sme')
                # chatgpt_prompt = request.POST.get('prompt', None)
                filename = f'Generated_Audio_{target_lang}_{time.time()}.mp3'
                result = ai_service.process_audio(audio_data, filename)
                print(result)
                if 'error' in result:
                    return JsonResponse(result, status=400)

                    # Save the original user message and the bot response
                ChatHistory.objects.create(user=request.user, message=result['transcribed_text'],
                                           sender=ChatHistory.USER)
                ChatHistory.objects.create(user=request.user, message=result['translated_chat_response'],
                                           sender=ChatHistory.BOT)

                return JsonResponse(result)

            # elif file.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            #     image_data = file.read()
            #     target_lang = request.POST.get('lang', 'sme')
            #     chatgpt_prompt = request.POST.get('prompt', None)
            #     filename = f'Generated_Image_{target_lang}_{time.time()}.jpg'
            #     result = ai_service.process_audio(image_data, filename, chatgpt_prompt)
            #     logger.info(chatgpt_prompt)
            #     logger.info(result)
            #     return JsonResponse(result)

            else:
                return JsonResponse({"error": "Unsupported file format"}, status=400)

    return render(request, 'process_audio_chat.html')


class ProcessAudio(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = AudioFileSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
            target_lang = serializer.validated_data.get('lang', 'sme')
            # chatgpt_prompt = serializer.validated_data.get('prompt', None)

            if file.name.lower().endswith(('.mp3', '.wav')):
                audio_data = file.read()
                filename = f'Generated_Audio_{target_lang}_{time.time()}.mp3'
                result = ai_service.process_audio(audio_data, filename)
                print(result)
                if 'error' in result:
                    return JsonResponse(result, status=400)

                    # Save the original user message and the bot response
                # ChatHistory.objects.create(user=request.user, message=result['transcribed_text'], sender=ChatHistory.USER)
                # ChatHistory.objects.create(user=request.user, message=result['translated_chat_response'],
                #                            sender=ChatHistory.BOT)
                ChatHistory.objects.create(
                    user=request.user,
                    user_message=result,
                    bot_reply=result['translated_chat_response']
                )

                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Unsupported file format"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_audio(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, 'audio', filename)
    return FileResponse(open(file_path, 'rb'), as_attachment=True)
