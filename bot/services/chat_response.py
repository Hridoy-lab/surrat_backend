import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class ChatBot:
    def __init__(self):
        self.open_api_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    def chat_with_openai(self, transcribed_text, chatgpt_prompt="Give me answer in 3 words. Never generate answer "
                                                                "more than 3 words."):
        if chatgpt_prompt:
            system_content = chatgpt_prompt
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
