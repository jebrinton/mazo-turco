import pathlib
import math
import re

import pandas as pd
import wordfreq
import numpy as np

## TODO: add lemmatization

def remove_proper_nouns(sentence):
    # Divide la oración en palabras
    words = sentence.split()
    if not words:
        return sentence  # Devuelve la oración si está vacía
    
    # Mantén la primera palabra y procesa las demás
    first_word = words[0]
    remaining_words = ' '.join(words[1:])

    # Expresión regular para encontrar palabras capitalizadas en el resto
    pattern = r'\b[A-ZÁÉÍÓÚÑÜÖİĞÇŞ][a-záéíóúñüöığçş]*\b'
    cleaned_remaining = re.sub(pattern, '', remaining_words)
    
    # Limpia espacios extra y devuelve el resultado
    result = f"{first_word} {' '.join(cleaned_remaining.split())}"
    return result

def get_sentence_metrics(sentence, lang, frequencies):
    ##
    # you know what, almost the thing that matters most is the hardest word, or at least it should be heavily weighted towards the hardest word
    # otherwise, a sentence such as "bu parlak" is ostensibly easier than "parlak"
    
    tokenized = wordfreq.tokenize(remove_proper_nouns(sentence), lang)
    
    freqs = np.zeros(len(tokenized))
    # freqs = [-math.log10(frequencies.get(word, 1.0e-10)) for word in tokenized]

    for i, word in enumerate(tokenized):
        freqs[i] = -math.log10(frequencies.get(word, 1.0e-10))
        # if frequencies.get(word, 1.0e-10) == 1.0e-10:
        #     print(word)

    num_words = len(freqs)

    if num_words == 0:
        # raise ValueError("Sentence tokenized to 0 words")
        print("Warning: Sentence tokenized to 0 words")
        return 0, 0, 0

    # print(f"avg: {avg}, log_num_words: {math.log10(num_words)}, score: {score}")
    return np.linalg.norm(freqs, ord=np.inf), math.log10(num_words), math.log10(len(sentence))


# get subtitles
def txt_to_column(filepath):
    subtitles = []
    with filepath.open("r") as f:
        for line in f:
            subtitles.append(line.strip())
    return subtitles


def make_sorted_sentences(folder_path : pathlib.Path, l1, l2):
    # get word frequencies
    l1_frequencies = wordfreq.get_frequency_dict(l1, wordlist='best')
    l2_frequencies = wordfreq.get_frequency_dict(l2, wordlist='best')

    print("Done with frequencies")

    # crear rutas usando pathlib
    data_path = folder_path / "data"
    l1_path = data_path / f"sentences.{l1}"
    l2_path = data_path / f"sentences.{l2}"

    if not l1_path.exists() or not l2_path.exists():
        print("Please rename files to 'sentences.{lang code}'")

    # create dataframe of subtitles
    l1_subtitles = txt_to_column(l1_path)
    l2_subtitles = txt_to_column(l2_path)

    print("Done with reading subtitles")

    AVG_COEFF = 7

    # create new column with scores
    l1_metrics = [get_sentence_metrics(sentence, l1, l1_frequencies) for sentence in l1_subtitles]
    l1_avg, l1_num_words, l1_num_chars = zip(*l1_metrics)
    l1_score = [AVG_COEFF * avg + num_words + num_chars for avg, num_words, num_chars in l1_metrics]
    print("Done with scoring " + l1)

    l2_metrics = [get_sentence_metrics(sentence, l2, l2_frequencies) for sentence in l2_subtitles]
    l2_avg, l2_num_words, l2_num_chars = zip(*l2_metrics)
    l2_score = [AVG_COEFF * avg + num_words + num_chars for avg, num_words, num_chars in l2_metrics]
    print("Done with scoring " + l2)

    df = pd.DataFrame({"src": l1_subtitles, "src_avg": l1_avg, "src_num_words": l1_num_words, "src_num_chars": l1_num_chars, "src_score": l1_score,
                        "tgt": l2_subtitles, "tgt_avg": l2_avg, "tgt_num_words": l2_num_words, "tgt_num_chars": l2_num_chars, "tgt_score": l2_score})

    # drop duplicates
    df = df.drop_duplicates(subset="src", keep=False)
    df = df.drop_duplicates(subset="tgt", keep=False)

    df["score"] = round(df["src_score"] + df["tgt_score"], 2)
    
    # sort by scores
    df = df.sort_values("score")

    print("Done with sorting")

    pd.set_option('display.max_rows', None)
    print("First 300")
    print(df.head(300))

    size_to_print = int(df.size / 300)
    print("Filtered 300")
    print(df.iloc[::size_to_print])
    
    # save to pickle, csv
    saves_path = folder_path / "saves"
    df.to_pickle(saves_path / "sentence_scores.pkl")
    df.to_csv(saves_path / "sentence_scores.csv")


if __name__ == "__main__":
    root = pathlib.Path(".")
    make_sorted_sentences(root / "tatoeba_tr_en", "tr", "en")
