# take frequency .txt file and create translations for each word

import json
import math
import requests

def authenticate_client():
    with open("azure_key.txt", "r") as file:
        key = file.read().strip()
    endpoint = "https://api.cognitive.microsofttranslator.com/"
    return key, endpoint

def translate_word(key, endpoint, word, source_language="tr", target_language="es"):
    path = '/translate?api-version=3.0'
    params = f'&from={source_language}&to={target_language}'
    constructed_url = endpoint + path + params

    headers = {
        'Ocp-Apim-Subscription-Key': key,
        'Content-type': 'application/json',
        'Ocp-Apim-Subscription-Region': 'westcentralus'
    }
    body = [{
        'text': word
    }]
    response = requests.post(constructed_url, headers=headers, json=body)
    response_json = response.json()
    print(response_json)
    return response_json[0]['translations'][0]['text']

def save_json_to_file(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4, separators=(',', ': '))

def dictionary_word(key, endpoint, word, source_language="tr", target_language="en"):
    path = '/dictionary/lookup?api-version=3.0'
    params = f'&from={source_language}&to={target_language}'
    constructed_url = endpoint + path + params

    headers = {
        'Ocp-Apim-Subscription-Key': key,
        'Content-type': 'application/json',
        'Ocp-Apim-Subscription-Region': 'westcentralus'
    }
    body = [{
        'text': word
    }]
    response = requests.post(constructed_url, headers=headers, json=body)
    response_json = response.json()
    save_json_to_file(response_json, f'samples/{word}_dictionary.json')
    return response_json

words = []
with open("wiki_frequency.txt", "r") as f:
    for line in f.readlines():
        words.append(line.split()[0])

with open("samples/aç_dictionary.json") as sample_dict:
    jsd = json.load(sample_dict)

pos_tag_dict = {
    "ADJ": "adj",
    "ADV": "adv",
    "CONJ": "conj",
    "DET": "det",
    "MODAL": "modal",
    "NOUN": "n",
    "PREP": "prep",
    "PRON": "pro",
    "VERB": "v",
    "OTHER": ""
}

def pos_tag_map(pos_tag):
    return pos_tag_dict.get(pos_tag, "")

# jsd = JSon Data
def json_to_card(jsd, confidence_explained=0.6):
    if confidence_explained > 1 or confidence_explained < 0:
        raise ValueError("Confidence explained must be between 0 and 1")

    explained_so_far = 0
    translations = ""
    translations_html = ""
    for tr in jsd[0]['translations']:
        confidence = tr['confidence']
        translations += f"{tr['displayTarget']} {pos_tag_map(tr['posTag'])} {confidence} "
        
        # Calculate color gradient based on confidence
        green = int(min(255, 255 * (confidence + 0.76)))
        red = int(min(255, 255 * (1.24 - confidence)))
        blue = int(max(148, int(148 * (confidence + 0.18))))
        color = f'rgb({red},{green},{blue})'

        # Calculate font size based on confidence
        font_size = round(1.5 + confidence, 2)

        pos = pos_tag_map(tr['posTag'])
        if pos != "":
            pos_formatted = f" <span style='font-size:{0.62 * font_size}em'>({pos})</span>"
        else:
            pos_formatted = ""

        translations_html += f"<div style='font-size:{font_size}em; color:{color}'>{tr['displayTarget']}{pos_formatted}</div> "

        explained_so_far += confidence
        # end loop if we have enough translations
        if explained_so_far > confidence_explained:
            break

    source_html = f"<div style='font-size:2em'>{jsd[0]['displaySource']}</div>"
    
    return source_html + "|" + translations_html

if __name__ == "__main__":
    key, endpoint = authenticate_client()

    # open card file
    # with open("turco_deck.txt", "w") as f:
    #     words = [
    #         "at",
    #         "yemek",
    #         "var",
    #         "siz",
    #         "yürümek",
    #         "geç",
    #     ]

    #     for word in words:
    #         # get the json of the word
    #         # done above
    #         jsd = dictionary_word(key, endpoint, word)
    #         card = json_to_card(jsd)

    #         # write a line to the card file
    #         f.write(card + "\n")

    with open("test_tr_en_html.txt", "w") as f:
        words = [
            "esperar",
            "mañana",
            "tener",
            "hacer",
            "en",
            "total",
        ]

        words = [
            "at",
            "yemek",
            "var",
            "siz",
            "yürümek",
            "geç",
        ]

        for word in words:
            # get the json of the word
            jsd = json.load(open(f"samples/{word}_dictionary.json"))

            card = json_to_card(jsd)

            # write a line to the card file
            f.write(card + "\n")