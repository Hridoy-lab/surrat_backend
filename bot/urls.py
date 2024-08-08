from django.urls import path
from .views import ProcessAudio, Translate

urlpatterns = [
    path("api/process_audio/", ProcessAudio.as_view(), name="process_audio_api"),
    path("api/translate/", Translate.as_view(), name="translate"),
]
