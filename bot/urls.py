from django.urls import path
from .views import ProcessAudio

urlpatterns = [
    path('api/process_audio/', ProcessAudio.as_view(), name='process_audio_api'),
]
