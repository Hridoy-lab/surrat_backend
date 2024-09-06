import os
from openai import OpenAI
from dotenv import load_dotenv

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
        # Retrieve the last few messages for the user to maintain the context
        conversation = AudioRequest.objects.filter(user=self.user).order_by(
            "-created_at"
        )[:5]
        history = []
        for msg in reversed(conversation):  # Reverse to maintain chronological order
            if msg.translated_text is not None:
                history.append({"role": "user", "content": msg.translated_text})
            if msg.gpt_response is not None:
                history.append({"role": "assistant", "content": msg.gpt_response})
        return history

    def create_system_prompt(self):
        # Here, you can include any system-level instructions that guide the conversation.
        return {
            "role": "system",
            "content": "You are a helpful assistant. Please assist the user with their queries and images if image have."
        }

    def create_prompt(self, current_text, instruction):
        # Combine the history with the current instruction to create the final prompt.
        prompt = [self.create_system_prompt()]
        prompt.extend(self.get_conversation_history())
        prompt.append({"role": "user", "content": f"{instruction}: {current_text}"})
        return prompt

    def get_gpt_response(self, current_text, instruction):
        # Prepare the prompt for the GPT model
        messages = self.create_prompt(
            current_text=current_text, instruction=instruction
        )
        print(f"prompt: {messages}")

        # Send the request to OpenAI API
        response = self.open_api_client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=256,
            temperature=1,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        reply = (
            response.choices[0].message.content.strip()
            if response.choices
            else "No response generated"
        )
        return reply
