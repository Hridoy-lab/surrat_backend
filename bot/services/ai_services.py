import logging
from .transcribe import Transcriber
from .translate import Translator
from .chat_response import ChatBot

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        self.transcriber = Transcriber()
        self.translator = Translator()
        self.chatbot = ChatBot()

    def process_audio(self, file_data, filename):
        try:
            if filename.lower().endswith(('.mp3', '.wav')):
                # Audio processing
                transcribed_text = self.transcriber.transcribe_voice(file_data)
                print("Transcribe: ", transcribed_text)
                if transcribed_text == 'Transcription failed or "text" key is missing':
                    return {
                        "error": 'Transcription failed or "text" key is missing'
                    }
                logger.info(f"Transcribed text: {transcribed_text}")

                translation_result = self.translator.perform_translation(transcribed_text, 'en', 'en')
                print(translation_result)
                translated_text = translation_result.get("Translated Text", transcribed_text)
                logger.info(f"Translated text: {translated_text}")

                chat_response = self.chatbot.chat_with_openai(translated_text)
                logger.info(f"Chat response: {chat_response}")
                print(chat_response)

                translation_result = self.translator.perform_translation(chat_response, 'en', 'sme')
                print(translation_result)
                translated_chat_response = translation_result.get("Translated Text", chat_response)
                logger.info(f"Translated chat response: {translated_chat_response}")

                final_text = translated_chat_response
                print(translated_chat_response)

                return {
                    'transcribed_text': transcribed_text,
                    'translated_text': translated_text,
                    'chat_response': chat_response,
                    'translated_chat_response': translated_chat_response,
                }

            else:
                return {
                    "error": "Unsupported file format"
                }

        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            return {'error': str(e)}
