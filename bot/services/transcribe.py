import requests
import os
from dotenv import load_dotenv

load_dotenv()


class Transcriber:
    def __init__(self):
        # self.api_url = "https://api-inference.huggingface.co/models/NbAiLab/whisper-large-sme"
        self.api_url = "https://api-inference.huggingface.co/models/openai/whisper-tiny"
        self.headers = {
            "Authorization": f"Bearer {os.environ['HUGGINGFACE_API_KEY']}",
            "language": "en"
        }

    def transcribe_voice(self, audio_data):
        response = requests.post(self.api_url, headers=self.headers, data=audio_data)
        transcription = response.json()
        return transcription.get('text', 'Transcription failed or "text" key is missing')
