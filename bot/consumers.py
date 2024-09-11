import os
import threading
import time
import json
import base64
# from html.parser import incomplete

from django.core.files.base import ContentFile

from users.models import User
from .models import AudioRequest, instruction_per_page
# from channels.generic.websocket import SyncConsumer
from channels.consumer import SyncConsumer, AsyncConsumer

from .services.TTS import tts
from .services.ai_services import ProcessData


class MySyncConsumer(SyncConsumer):

    def websocket_connect(self, event):
        print("WebSocket connected...", event)
        self.send({
            'type': 'websocket.accept',
        })

    def websocket_receive(self, event):
        print("WebSocket received...", event)
        # try:
        #     if 'text' in event:
        #         data = json.loads(event['text'])
        #         page_number = data.get('page_number')
        #         user_email = data.get('email')
        #         audio_file_data = data.get('audio_file')
        #
        #         if isinstance(audio_file_data, str):
        #             audio_bytes = base64.b64decode(audio_file_data)
        #             file_name = f"sound_from_user{time.time()}.mp3"
        #             audio_file_path = f'static/audio/{file_name}'
        #
        #             os.makedirs('static/audio', exist_ok=True)
        #             with open(audio_file_path, 'wb') as audio_file:
        #                 audio_file.write(audio_bytes)
        #
        #             instruction = instruction_per_page.objects.get(page_number=page_number)
        #
        #             process_data = ProcessData(user=data.get('id'))
        #             processed_data = process_data.process_audio({
        #                 "audio_file": open(audio_file_path, 'rb'),
        #                 "instruction": instruction.instruction_text,
        #             })
        #
        #             if "error" in processed_data:
        #                 self.send({
        #                     'type': 'websocket.send',
        #                     'text': json.dumps({"error": processed_data["error"]})
        #                 })
        #                 return
        #
        #             processed_audio_filename = processed_data["filename"]
        #             audio_file_full_path = f'static/audio/{processed_audio_filename}'
        #
        #             if os.path.exists(audio_file_full_path):
        #                 user = User.objects.get(email=user_email)
        #                 audio_request = AudioRequest(
        #                     user=user,
        #                     page_number=page_number,
        #                     instruction=instruction.instruction_text,
        #                     transcribed_text=processed_data["transcribed_text"],
        #                     translated_text=processed_data["translated_text"],
        #                     gpt_response=processed_data["gpt_response"],
        #                     translated_response=processed_data["translated_response"],
        #                 )
        #                 audio_request.audio.save(file_name, ContentFile(audio_bytes))
        #                 with open(audio_file_full_path, 'rb') as response_audio_file:
        #                     audio_request.response_audio.save(processed_audio_filename,
        #                                                       ContentFile(response_audio_file.read()))
        #
        #                 audio_request.save()
        #
        #                 self.send({
        #                     'type': 'websocket.send',
        #                     'text': json.dumps({
        #                         "id": audio_request.id,
        #                         "transcribed_text": audio_request.transcribed_text,
        #                         "translated_text": audio_request.translated_text,
        #                         "gpt_response": audio_request.gpt_response,
        #                         "translated_response": audio_request.translated_response,
        #                         "response_audio": processed_audio_filename,
        #                         "user_audio": audio_request.audio.url if audio_request.audio else None
        #                     })
        #                 })
        #             else:
        #                 self.send({
        #                     'type': 'websocket.send',
        #                     'text': json.dumps({'error': f'File {processed_audio_filename} not found'})
        #                 })
        #         else:
        #             self.send({
        #                 'type': 'websocket.send',
        #                 'text': json.dumps({'error': 'Audio file data is not a valid base64 string'})
        #             })
        # except Exception as e:
        #     self.send({
        #         'type': 'websocket.send',
        #         'text': json.dumps({'error': f'An error occurred: {e}'})
        #     })

# ====================================Below one is final===========================================
        try:
            if 'text' in event:
                data = json.loads(event['text'])
                page_number = data.get('page_number')
                user_email = data.get('email')
                audio_file_data = data.get('audio_file')

                if isinstance(audio_file_data, str):
                    audio_bytes = base64.b64decode(audio_file_data)
                    file_name = f"sound_from_user{time.time()}.mp3"
                    audio_file_path = f'static/audio/{file_name}'

                    # Create directory if it doesn't exist
                    os.makedirs('static/audio', exist_ok=True)
                    with open(audio_file_path, 'wb') as audio_file:
                        audio_file.write(audio_bytes)

                    instruction = instruction_per_page.objects.get(page_number=page_number)

                    process_data = ProcessData(user=data.get('id'))
                    processed_data = process_data.process_audio({
                        "audio_file": open(audio_file_path, 'rb'),
                        "instruction": instruction.instruction_text,
                    })

                    if "error" in processed_data:
                        self.send({
                            'type': 'websocket.send',
                            'text': json.dumps({"error": processed_data["error"]})
                        })
                        return

                    # processed_audio_filename = processed_data["filename"]
                    # audio_file_full_path = f'static/audio/{processed_audio_filename}'

                    user = User.objects.get(email=user_email)
                    audio_request = AudioRequest(
                        user=user,
                        page_number=page_number,
                        instruction=instruction.instruction_text,
                        transcribed_text=processed_data["transcribed_text"],
                        translated_text=processed_data["translated_text"],
                        gpt_response=processed_data["gpt_response"],
                        translated_response=processed_data["translated_response"],
                    )
                    audio_request.audio.save(file_name, ContentFile(audio_bytes))

                    # Save the request without response_audio
                    audio_request.save()

                    # Send the first response (without response_audio)
                    self.send({
                        'type': 'websocket.send',
                        'text': json.dumps({"type": "incomplete", "data":{
                            "id": audio_request.id,
                            "transcribed_text": audio_request.transcribed_text,
                            "translated_text": audio_request.translated_text,
                            "gpt_response": audio_request.gpt_response,
                            "translated_response": audio_request.translated_response,
                            "audio": self.get_full_url(audio_request.audio.url) if audio_request.audio else None, #user given audio
                            "response_audio": None  # Initially no response audio
                        }})
                    })

                    incomplete_response = {
                        "type": "incomplete",
                        "data":{
                            "id": audio_request.id,
                            "transcribed_text": audio_request.transcribed_text,
                            "translated_text": audio_request.translated_text,
                            "gpt_response": audio_request.gpt_response,
                            "translated_response": audio_request.translated_response,
                            "user_audio": self.get_full_url(audio_request.audio.url) if audio_request.audio else None,
                            "response_audio": None  # Initially no response audio
                        }
                    }

                    print("First response:", json.dumps(incomplete_response, indent=4))

                    timestamp = time.strftime("%Y%m%d_%H%M%S")  # Format timestamp for readability
                    filename = f"Generated_Audio_nor_to_sami_{timestamp}.mp3"

                    try:
                        # tts = self.tts.tts(translated_text, filename)
                        # from .TTS import tts
                        tts(audio_request.translated_response, filename)

                    except Exception as e:
                        return {"error": f"Error during TTS generation: {str(e)}"}

                    # print(f"transcribed_text:  {transcribed_text} , \n"
                    #       f"translated_text: {translated_text}, \n"
                    #       f"gpt_response: {gpt_response}, "
                    #       f"translated_response:  {translated_response}, filename: {filename}")

                    # Function to send the second response after 10 seconds
                    def send_response_audio():
                        time.sleep(10)  # Wait for 10 seconds
                        audio_file_full_path = f'static/audio/{filename}'

                        while not os.path.exists(audio_file_full_path):
                            time.sleep(5)

                            # Ensure the file exists and save it
                        if os.path.exists(audio_file_full_path):
                            with open(audio_file_full_path, 'rb') as response_audio_file:
                                audio_request.response_audio.save(
                                    filename,
                                    ContentFile(response_audio_file.read())
                                )
                            audio_request.save()

                            # Send the second response (with response_audio)
                            self.send({
                                'type': 'websocket.send',
                                'text': json.dumps({"type": "complete", "data":{
                                    "id": audio_request.id,
                                    "transcribed_text": audio_request.transcribed_text,
                                    "translated_text": audio_request.translated_text,
                                    "gpt_response": audio_request.gpt_response,
                                    "translated_response": audio_request.translated_response,
                                    "audio": self.get_full_url(audio_request.audio.url) if audio_request.audio else None, #user given audio
                                    "response_audio": self.get_full_url(audio_request.response_audio.url)  # Include the response audio now
                                }})
                            })

                    # Start a new thread to delay and send the second response
                    threading.Thread(target=send_response_audio).start()

                else:
                    self.send({
                        'type': 'websocket.send',
                        'text': json.dumps({'error': 'Audio file data is not a valid base64 string'})
                    })

        except Exception as e:
            self.send({
                'type': 'websocket.send',
                'text': json.dumps({'error': f'An error occurred: {e}'})
            })


    def get_full_url(self, relative_url):
        # Get the host and protocol from the WebSocket scope
        headers = dict((x.decode(), y.decode()) for x, y in self.scope['headers'])
        domain_name = headers.get('host')
        protocol = headers.get('x-forwarded-proto', 'http')  # Defaults to 'http' if not found
        return f'{protocol}://{domain_name}{relative_url}'




    def websocket_disconnect(self, event):
        print("WebSocket disconnected...", event)

class MyAsyncConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        print("WebSocket connected...", event)

    async def websocket_receive(self, event):
        print("WebSocket received...", event)

    async def websocket_disconnect(self, event):
        print("WebSocket disconnected...", event)

# import json
# from channels.generic.websocket import WebsocketConsumer
#
# class ChatConsumer(WebsocketConsumer):
#     def connect(self):
#         self.accept()
#
#     def disconnect(self, close_code):
#         pass
#
#     def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']
#
#         # Send message back to WebSocket
#         self.send(text_data=json.dumps({
#             'message': message
#         }))
# import time
# from channels.generic.websocket import AsyncWebsocketConsumer
# import json
# # from services.TTS import tts
# #
# #
# class TTSConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.user_id = self.scope['url_route']['kwargs']['user_id']
#         self.page_number = self.scope['url_route']['kwargs']['page_number']
#         self.room_group_name = f'tts_{self.user_id}_{self.page_number}'
#
#         # Join room group
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#         await self.accept()
#
#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )
#
#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         print("here in channel")
#         translated_text = text_data_json['translated_text']
#
#         # Start TTS processing and streaming
#         await self.send(text_data=json.dumps({'status': 'processing'}))
#
#         try:
#             # Start TTS and stream chunks
#             for chunk in tts_stream(translated_text):
#                 await self.send(text_data=json.dumps({'audio_chunk': chunk}))
#
#             # Notify once complete
#             await self.send(text_data=json.dumps({'status': 'completed', 'file_url': '/path/to/downloaded/file'}))
#
#         except Exception as e:
#             await self.send(text_data=json.dumps({'error': str(e)}))
#
#
# # Stream function for TTS
# def tts_stream(translated_text):
#     # Simulate streaming chunks
#     for i in range(5):
#         time.sleep(1)
#         yield f"Chunk {i} of {translated_text}"
#
#     # You can also directly stream API responses if the TTS service supports chunked responses
# class AudioConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.user_id = self.scope['url_route']['kwargs']['user_id']
#         self.page_number = self.scope['url_route']['kwargs']['page_number']
#         self.room_group_name = f"{self.user_id}_{self.page_number}"
#
#         # Join room group
#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)
#         await self.accept()
#
#     async def disconnect(self, close_code):
#         # Leave room group
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
#
#     async def audio_processing_complete(self, event):
#         # Send message to WebSocket
#         message = event['message']
#         file_url = event['file_url']
#         await self.send(text_data=json.dumps({
#             'message': message,
#             'file_url': file_url
#         }))
