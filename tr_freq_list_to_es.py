from deep_translator import GoogleTranslator

with open("wiki_frequency.txt", "r") as f:
    words = [line.split()[0] for line in f.readlines()[:2000]]

def translate_word(word, source_lang='tr', target_lang='es'):
    translator = GoogleTranslator(source=source_lang, target=target_lang)
    return translator.translate(word)

def create_deck():
    with open("tr_to_es_deck.txt", "w") as f:
        for word in words:
            translation = translate_word(word, "tr", "es")
            print(f"{word} -> {translation}")
            f.write(f"{word}|{translation}\n")

if __name__ == "__main__":
    
    # with open("tr_to_es_deck.txt", "r") as in_f:
    #     with open("tr_to_es_deck_out.txt", "w") as out_f:
    #         for line in in_f.readlines():
    #             out_f.write(line.lower())