# take frequency .txt file and create translations for each word

import json
import pandas as pd
import requests
import pickle

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

def save_json_to_df(data, df):
    df.loc[len(df)]

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
    return response.json()

def json_to_line(jsd):
    line = []
    line.append(jsd[0]['normalizedSource'])
    line.append(jsd[0]['displaySource'])

    translations = []
    for tr in jsd[0]['translations']:
        translations.append(tr['normalizedTarget'])
        translations.append(tr['displayTarget'])
        translations.append(tr['posTag'])
        translations.append(tr['confidence'])
        translations.append(tr['prefixWord'])

        back_translations = []
        for back_tr in tr['backTranslations']:
            back_translations.append(back_tr['normalizedText'])
            back_translations.append(back_tr['displayText'])
            back_translations.append(back_tr['numExamples'])
            back_translations.append(back_tr['frequencyCount'])
        
        translations.append(back_translations)
    
    line.append(translations)

    return line


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
def json_to_card(jsd, confidence_explained=0.6, max_translations=5):
    if confidence_explained > 1 or confidence_explained < 0:
        raise ValueError("Confidence explained must be between 0 and 1")

    explained_so_far = 0
    translations = ""
    translations_html = ""
    for tr in jsd[0]['translations'][:max_translations]:
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
            pos_formatted = f" <span style='font-size:{round(0.62 * font_size, 2)}rem'>({pos})</span>"
        else:
            pos_formatted = ""

        translations_html += f"<div style='font-size:{font_size}rem; color:{color};'>{tr['normalizedTarget']}{pos_formatted}</div> "

        explained_so_far += confidence
        # end loop if we have enough translations
        if explained_so_far > confidence_explained:
            break

    source_html = f"<div style='font-size:2em'>{jsd[0]['normalizedSource']}</div>"
    
    return source_html + "|" + translations_html, len(jsd[0]['translations'])

def dictionary_list(key, endpoint, words, source_language="tr", target_language="en"):
    path = '/dictionary/lookup?api-version=3.0'
    params = f'&from={source_language}&to={target_language}'
    constructed_url = endpoint + path + params

    headers = {
        'Ocp-Apim-Subscription-Key': key,
        'Content-type': 'application/json',
        'Ocp-Apim-Subscription-Region': 'westcentralus'
    }

    dictionary_all = []
    with open("tr_en_deck_v0.txt", "w") as f:
        i = 0
        for word in words:
            body = [{"text": word}]
            response = requests.post(constructed_url, headers=headers, json=body)
            response_json = response.json()
            dictionary_all.append(json_to_line(response_json))

            card, _ = json_to_card(response_json, confidence_explained=0.67, max_translations=5)
            # write a line to the card file
            f.write(card + "\n")

            if i % 50 == 0:
                print(f"{i}/{len(words)}: {word} -> {response_json[0]['normalizedSource']}")
            i += 1


    pickle.dump(dictionary_all, open("tr_en_dictionary_all.pkl", "wb"))

    df = pd.DataFrame(dictionary_all, columns=['normalizedSource', 'displaySource', 'translations'])
    print(df)

    pickle.dump(df, open("tr_en_dictionary_all_df.pkl", "wb"))

    return

def main():
    words = []
    with open("wiki_top1000.txt", "r") as f:
        for line in f.readlines():
            words.append(line.strip())

    total_chars = sum([len(word) for word in words])
    if total_chars > 50000:
        print("warning: huge API calls ", total_chars)

    df = pd.DataFrame()

    key, endpoint = authenticate_client()

    dictionary_list(key, endpoint, words, source_language="tr", target_language="en")

if __name__ == "__main__":
    main()
