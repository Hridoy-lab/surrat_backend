from django.urls import path
from .views import ProcessAudio, Translate, Transcript, AudioRequestView, AudioRequestListView

urlpatterns = [
    path("api/process_audio/", ProcessAudio.as_view(), name="process_audio_api"),
    path("api/translate/", Translate.as_view(), name="translate"),
    path("api/transcript/", Transcript.as_view(), name="transcript"),
    path("api/audiorequest/", AudioRequestView.as_view(), name="audiorequest"),
    path('api/all-audio-requests/', AudioRequestListView.as_view(), name='audio-requests-list'),
]
