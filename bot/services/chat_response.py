import os
from openai import OpenAI
from dotenv import load_dotenv
import requests
from bot.models import AudioRequest

load_dotenv()


class ChatBot:
    def __init__(self):
        self.open_api_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    def chat_with_openai(
        self,
        translated_text,
        instruction="Act you are very helpfully instructor for language learner, who give suggestion how can improve and what he/she done wording. Give me answer in 3 words. Never generate answer "
        "more than 3 words.",
    ):
        if instruction:
            system_content = instruction
            model = "gpt-4-turbo-preview"
        else:
            system_content = "You are a very friendly AI assistant."
            model = "gpt-3.5-turbo"

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": translated_text},
        ]

        response = self.open_api_client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=256,
            temperature=1,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        return (
            response.choices[0].message.content.strip()
            if response.choices
            else "No response generated"
        )

    # def chat_with_openai(self, transcribed_text):
    #     if transcribed_text:
    #         system_content = transcribed_text
    #         model = "gpt-4-turbo-preview"
    #     else:
    #         system_content = "You are a very friendly AI assistant."
    #         model = "gpt-3.5-turbo"
    #
    #     messages = [
    #         {"role": "system", "content": system_content},
    #         {"role": "user", "content": transcribed_text}
    #     ]
    #
    #     response = self.open_api_client.chat.completions.create(
    #         model=model,
    #         messages=messages,
    #         max_tokens=256,
    #         temperature=1,
    #         top_p=1,
    #         frequency_penalty=0,
    #         presence_penalty=0
    #     )
    #
    #     return response.choices[0].message.content.strip() if response.choices else "No response generated"


class GPTResponseHandler:
    def __init__(self, user, model="gpt-3.5-turbo"):
        self.user = user
        self.model = model
        self.open_api_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    def get_conversation_history(self):
        """Retrieve the last few messages for the user to maintain context."""
        conversation = AudioRequest.objects.filter(user=self.user).order_by("-created_at")[:5]
        history = []
        for msg in reversed(conversation):
            if msg.translated_text:
                history.append({"role": "user", "content": msg.translated_text})
            if msg.gpt_response:
                history.append({"role": "assistant", "content": msg.gpt_response})
        return history

    def create_system_prompt(self):
        """Create a system-level instruction for the GPT model."""
        return {
            "role": "system",
            "content": "You are a helpful assistant in Norwegian Bokmål. You will always respond in Norwegian Bokmål, not in any other language. Please assist the user with their queries and images if there are any."
        }

    def create_prompt(self, current_text, instruction):
        """Combine system prompt, history, and current input into a single prompt."""
        prompt = [self.create_system_prompt()]
        prompt.extend(self.get_conversation_history())
        prompt.append({"role": "user", "content": f"{instruction}: {current_text}"})
        return prompt

    def get_gpt_response(self, current_text, instruction, instruction_image=None):
        """Get a response from the GPT model, handling both text and image inputs."""
        try:
            if instruction_image:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"
                }
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful assistant in Norwegian Bokmål. You will always respond in Norwegian Bokmål, not in any other language. Please assist the user with their queries and images if there are any."
                        },
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": current_text},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{instruction_image}"}},
                                {"type": "text", "text": f"instruction: {instruction}"}
                            ]
                        }
                    ]
                }
                response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                response_data = response.json()
                assistant_response = response_data['choices'][0]['message']['content']
                return assistant_response

            messages = self.create_prompt(current_text=current_text, instruction=instruction)
            response = self.open_api_client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=256,
                temperature=1,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
            )
            reply = response.choices[0].message.content.strip() if response.choices else "No response generated"
            return reply

        except Exception as e:
            return "Sorry, I encountered an error. Please try again later."
