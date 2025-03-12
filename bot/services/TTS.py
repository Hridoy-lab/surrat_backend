import os
import urllib.parse as urlparse

import requests
from django.conf import settings
from urllib.parse import quote as urlparse_quote
from .api import login, send_command
# def tts(chatgpt_response, filename):
#
#
    # token = login("tim@valio.no", "8JP9F3ljR4SXc48E")
    # if not token:
    #     print("Login failed")
    #     return
    #
    # text = chatgpt_response
    # voice = "Elle22k_CO"
    # text_quoted = urlparse.quote(text)
    #
    # output = "stream"
    # response = send_command(token, voice, text_quoted, output, type="mp3")
    # if response.status_code != 200:
    #     print("Failed to generate speech:", response.text)
    #     return
    #
    # file_path = f"./static/audio/{filename}"
    # with open(file_path, "wb") as file:
    #     file.write(response.content)
    #
    # return file_path


def tts(chatgpt_response, filename, user):
    """
    Generate TTS audio based on the user's tts_provider and giellalt_voice.

    Args:
        chatgpt_response (str): The text to convert to speech.
        filename (str): The name of the output audio file.
        user (CustomUser): The user object containing tts_provider and giellalt_voice.

    Returns:
        str: Path to the generated audio file, or None if failed.
    """
    # Define the output file path
    # file_path = os.path.join(settings.STATIC_ROOT, "audio", filename)
    # os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Ensure directory exists
    file_path = f"./static/audio/{filename}"
    # Check the user's TTS provider
    if user.tts_provider == 'acapela':
        # Existing Acapela TTS logic
        token = login("tim@valio.no", "8JP9F3ljR4SXc48E")
        if not token:
            print("Login failed")
            return

        text = chatgpt_response
        voice = "Elle22k_CO"
        text_quoted = urlparse.quote(text)

        output = "stream"
        response = send_command(token, voice, text_quoted, output, type="mp3")
        if response.status_code != 200:
            print("Failed to generate speech:", response.text)
            return

        file_path = file_path
        print("*" * 100)
        print("Response from Acapela")
        with open(file_path, "wb") as file:
            file.write(response.content)

        return file_path

    elif user.tts_provider == 'giellalt':
        # GiellaLT TTS logic with voice selection
        # Map giellalt_voice to the API endpoint
        voice = user.giellalt_voice if user.giellalt_voice else 'mahtte'  # Default to 'mahtte' if None
        if voice not in ['biret', 'mahtte']:
            print(f"Invalid GiellaLT voice: {voice}. Defaulting to 'mahtte'.")
            voice = 'mahtte'

        # Construct the URL based on selected voice ('biret' = female, 'mahtte' = male)
        url = f"https://api-giellalt.uit.no/tts/se/{voice}"
        headers = {
            "Content-Type": "application/json",
        }
        payload = {
            "text": chatgpt_response
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            print("*" * 100)
            print("response from GiellaLT")
            if response.status_code == 200:
                with open(file_path, "wb") as file:
                    file.write(response.content)
            else:
                print(f"Failed to generate GiellaLT speech: {response.status_code} - {response.text}")
                return None
        except requests.RequestException as e:
            print(f"Error calling GiellaLT API: {e}")
            return None

    else:
        print(f"Unsupported TTS provider: {user.tts_provider}")
        return None

    return file_path


















# import urllib.parse as urlparse
#
#
#
#
# class TTSGenerator:
#     def __init__(self):
#         self.email = "tim@valio.no"
#         self.password = "8JP9F3ljR4SXc48E"
#         self.token = None
#
#     def login(self):
#         from api import login
#
#         self.token = login(self.email, self.password)
#         if not self.token:
#             print("Login failed")
#         return self.token
#
#     def generate_speech(self, chatgpt_response, voice="Elle22k_CO", output="stream", file_type="mp3"):
#         if not self.token:
#             print("No valid token. Please login first.")
#             return None
#
#         from api import send_command
#
#         text_quoted = urlparse.quote(chatgpt_response)
#         response = send_command(self.token, voice, text_quoted, output, type=file_type)
#
#         if response.status_code != 200:
#             print("Failed to generate speech:", response.text)
#             return None
#
#         return response.content
#
#     def save_to_file(self, file_content, filename):
#         file_path = f"./static/audio/{filename}"
#         with open(file_path, "wb") as file:
#             file.write(file_content)
#         return file_path
#
#     def tts(self, chatgpt_response, filename):
#         if not self.login():
#             return
#
#         audio_content = self.generate_speech(chatgpt_response)
#         if audio_content:
#             return self.save_to_file(audio_content, filename)
#         return None
