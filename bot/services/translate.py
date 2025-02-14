# import json
# import requests
#
# TRANSLATION_URL = "https://api.tartunlp.ai/translation/v2"
#
#
# class Translator:
#     def __init__(self):
#         self.translation_url = TRANSLATION_URL
#
#     def perform_translation(self, text, src_lang, tgt_lang):
#         payload = json.dumps(
#             {
#                 "text": text,
#                 "src": src_lang,
#                 "tgt": tgt_lang,
#                 "domain": "general",
#                 "application": "Documentation UI",
#             }
#         )
#         headers = {"accept": "application/json", "Content-Type": "application/json"}
#         response = requests.request(
#             "POST", url=self.translation_url, headers=headers, data=payload
#         )
#         if response.status_code == 200:
#             data = response.json()
#             return data.get("result", "No translation found.")
#         else:
#             return {"error": "Failed to translate", "message": response.text}

import requests
from bs4 import BeautifulSoup


class Translator:
    def __init__(self):
        pass  # No need to initialize anything

    def perform_translation(self, text, src_lang, tgt_lang):
        # Map language codes to Google Translate codes
        lang_map = {
            "sme": "se",  # Sami to Swedish (Google Translate uses 'se' for Sami)
            "nor": "no",  # Norwegian
            "eng": "en",  # English
            # Add other language mappings as needed
        }

        # Convert source and target languages to Google Translate codes
        src_lang_google = lang_map.get(src_lang, src_lang)
        tgt_lang_google = lang_map.get(tgt_lang, tgt_lang)

        # Construct the Google Translate URL
        url = f"https://translate.google.com/m?sl={src_lang_google}&tl={tgt_lang_google}&q={requests.utils.quote(text)}"
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an error for bad status codes
            soup = BeautifulSoup(response.text, "html.parser")
            translated_text = soup.find("div", class_="result-container").text
            return translated_text
        except requests.exceptions.RequestException as e:
            return {"error": "Failed to translate", "message": str(e)}


if __name__ == '__main__':
    translator = Translator()
    translated_text = translator.perform_translation("Movt manná?", "sme", "nor")
    print("sme to nor: ", "Movt manná? -> " + translated_text)
    translated_text = translator.perform_translation("Hvordan går det?", "nor", "eng")
    print("nor to eng: ", "Hvordan går det?" + " -> " + translated_text)