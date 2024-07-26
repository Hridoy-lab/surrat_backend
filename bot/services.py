import json
import requests
from openai import OpenAI
import urllib.parse as urlparse
from dotenv import load_dotenv
import threading
import logging
import os
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
import base64

logger = logging.getLogger(__name__)
load_dotenv()


class AIService:
    def __init__(self):
        self.open_api_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.api_url = "https://api-inference.huggingface.co/models/NbAiLab/whisper-large-sme"
        self.headers = {
            "Authorization": f"Bearer {os.environ['HUGGINGFACE_API_KEY']}",
            "language": "en"
        }
        self.translation_url = "https://api.tartunlp.ai/translation/v2"

    def transcribe_voice(self, audio_data):
        response = requests.post(self.api_url, headers=self.headers, data=audio_data)
        transcription = response.json()
        return transcription.get('text', 'Transcription failed or "text" key is missing')

    def perform_translation(self, text, src_lang, tgt_lang):
        payload = {
            "text": text,
            "src": src_lang,
            "tgt": tgt_lang
        }
        response = requests.post(self.translation_url, headers={'Content-Type': 'application/json'}, json=payload)

        if response.status_code == 200:
            data = response.json()
            return {"Translated Text": data.get('result', 'No translation found.')}
        else:
            return {"error": "Failed to translate", "message": response.text}

    def detect_language(self, text):
        try:
            language = detect(text)
            return language
        except LangDetectException as e:
            return f"Error detecting language: {str(e)}"

    def chat_with_openai(self, transcribed_text):
        if transcribed_text:
            system_content = transcribed_text
            model = "gpt-4-turbo-preview"
        else:
            system_content = "You are a very friendly AI assistant."
            model = "gpt-3.5-turbo"

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": transcribed_text}
        ]

        response = self.open_api_client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=256,
            temperature=1,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        return response.choices[0].message.content.strip() if response.choices else "No response generated"

    def tts(self, chatgpt_response, filename):
        from .api import login, send_command

        token = login("tim@valio.no", "8JP9F3ljR4SXc48E")
        if not token:
            print("Login failed")
            return

        text = chatgpt_response
        voice = "Elle22k_CO"
        text_quoted = urlparse.quote("hello")

        output = "stream"
        response = send_command(token, voice, text_quoted, output, type="mp3")
        if response.status_code != 200:
            print("Failed to generate speech:", response.text)
            return

        file_path = f"./static/audio/{filename}"
        with open(file_path, "wb") as file:
            file.write(response.content)

        return file_path

    # def tts(self, chatgpt_response, filename, lang='en'):
    #     tts = gTTS(text=chatgpt_response, lang=lang)
    #     file_path = f"./static/audio/{filename}"
    #     tts.save(file_path)
    #     return file_path

    # def process_audio_in_thread(self, audio_data, target_lang, filename):
    #     def process():
    #         try:
    #             # Transcribe the audio
    #             time.sleep(1)
    #             transcribed_text = self.transcribe_voice(audio_data)
    #             print(f"Transcribed text: {transcribed_text}")
    #
    #             # Detect the language of the transcription
    #             detected_lang = self.detect_language(transcribed_text)
    #             print(f"Detected language: {detected_lang}")
    #
    #             # Translate the transcription to English if it's not already in English
    #             if detected_lang != 'en':
    #                 translation_result = self.perform_translation(transcribed_text, detected_lang, 'en')
    #                 transcribed_text = translation_result.get("Translated Text", transcribed_text)
    #                 print(f"Translated text: {transcribed_text}")
    #
    #             # Get chat response from OpenAI
    #             chat_response = self.chat_with_openai(transcribed_text)
    #             print(f"Chat response: {chat_response}")
    #
    #             # Translate the chat response to the target language if it's not English
    #             if target_lang != 'en':
    #                 translation_result = self.perform_translation(chat_response, 'en', target_lang)
    #                 chat_response = translation_result.get("Translated Text", chat_response)
    #                 print(f"Translated text: {chat_response}")
    #
    #             # Convert the response to speech in the target language
    #             audio_file_path = self.tts(chat_response, filename)
    #
    #         except Exception as e:
    #             print(f"Error processing audio: {str(e)}")
    #
    #     # Start the process in a new thread
    #     thread = threading.Thread(target=process)
    #     thread.start()
    #     return {'message': 'Text generation processing started, please wait...', 'filename': filename}
    # def process_audio(self, audio_data, filename, chatgpt_prompt):
    #     try:
    #         # Transcribe the audio
    #         transcribed_text = self.transcribe_voice(audio_data)
    #         if transcribed_text == 'Transcription failed or "text" key is missing':
    #             return {
    #                 "error": 'Transcription failed or "text" key is missing'
    #             }
    #         logger.info(f"Transcribed text: {transcribed_text}")
    #
    #         # # Translate the transcription to English if it's not already in English
    #
    #         translation_result = self.perform_translation(transcribed_text, 'sme', 'en')
    #         translated_text = translation_result.get("Translated Text", transcribed_text)
    #         logger.info(f"Translated text: {translated_text}")
    #
    #         # Get chat response from OpenAI
    #         chat_response = self.chat_with_openai(translated_text, chatgpt_prompt)
    #         logger.info(f"Chat response: {chat_response}")
    #
    #         translation_result = self.perform_translation(chat_response, 'en', 'sme')
    #         translated_chat_response = translation_result.get("Translated Text", chat_response)
    #         logger.info(f"Translated chat response: {translated_chat_response}")
    #
    #         # Convert the response to speech in the target language
    #         final_text = translated_chat_response
    #         audio_file_path = self.tts(final_text, filename)
    #
    #         return {
    #             'transcribed_text': transcribed_text,
    #             'translated_text': translated_text,
    #             'chat_response': chat_response,
    #             'translated_chat_response': translated_chat_response,
    #             'filename': filename
    #         }
    #
    #     except Exception as e:
    #         logger.error(f"Error processing audio: {str(e)}")
    #         return {'error': str(e)}
    def process_audio(self, file_data, filename):
        try:
            if filename.lower().endswith(('.mp3', '.wav')):
                # Audio processing
                transcribed_text = self.transcribe_voice(file_data)
                print("Transcribe: ", transcribed_text)
                if transcribed_text == 'Transcription failed or "text" key is missing':
                    return {
                        "error": 'Transcription failed or "text" key is missing'
                    }
                logger.info(f"Transcribed text: {transcribed_text}")

                translation_result = self.perform_translation(transcribed_text, 'sme', 'en')
                print(translation_result)
                translated_text = translation_result.get("Translated Text", transcribed_text)
                logger.info(f"Translated text: {translated_text}")

                chat_response = self.chat_with_openai(translated_text)
                logger.info(f"Chat response: {chat_response}")
                print(chat_response)

                translation_result = self.perform_translation(chat_response, 'en', 'sme')
                print(translation_result)
                translated_chat_response = translation_result.get("Translated Text", chat_response)
                logger.info(f"Translated chat response: {translated_chat_response}")

                final_text = translated_chat_response
                print(translated_chat_response)
                # audio_file_path = self.tts(final_text, filename)
                print("aisi 2")

                return {
                    'transcribed_text': transcribed_text,
                    'translated_text': translated_text,
                    'chat_response': chat_response,
                    'translated_chat_response': translated_chat_response,
                    # 'filename': filename
                }

            else:
                return {
                    "error": "Unsupported file format"
                }

        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            return {'error': str(e)}
