import json
import requests


class Translator:
    def __init__(self):
        self.translation_url = "https://api.tartunlp.ai/translation/v2"

    def perform_translation(self, text, src_lang, tgt_lang):
        payload = json.dumps({
            "text": text,
            "src": src_lang,
            "tgt": tgt_lang,
            "domain": "general",
            "application": "Documentation UI"
        })
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url=self.translation_url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            return {"Translated Text": data.get('result', 'No translation found.')}
        else:
            return {"error": "Failed to translate", "message": response.text}
