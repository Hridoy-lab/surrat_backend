from django.urls import path
from . import views
from .views import ProcessAudio

urlpatterns = [
    # path('', views.index, name='index'),
    path('transcribe', views.handle_transcription, name='transcribe'),
    path('translate', views.translate_text, name='translate'),
    path('chat', views.chat_with_openai_route, name='chat'),
    path('tts', views.tts_route, name='tts'),
    path('process_audio/', views.process_audio, name='process_audio'),
    path('audio/<str:filename>', views.get_audio, name='get_audio'),

    path('api/process_audio/', ProcessAudio.as_view(), name='process_audio_api'),
]
