import math
import re
import pandas as pd

## TODO: add lemmatization

# some metric to score a sentence
def score_sentence(sentence, word_frequencies):
    sentence_no_punctuation = re.sub(r'[^\w\s]', '', sentence)

    sum = 0
    num_words = 0
    for i, word in enumerate(sentence_no_punctuation.split()):
        # ignore proper nouns
        if i == 0 or word[0].islower():
            word = word.lower()
            sum += math.log(word_frequencies.get(word, 5000))
            num_words += 1
        else:
            sum += 5.7

    if num_words == 0:
        return 0.07
    avg = sum / num_words

    score = 5 * avg + 2 * math.log(num_words)
    return round(score, 4)

# get word frequencies
def get_word_frequencies(filepath):
    word_frequencies = {}
    with open(filepath, "r") as f:
        for i, line in enumerate(f.readlines()):
            word = line.split()[0]
            word_frequencies[word] = i+1
    return word_frequencies

# get subtitles
def txt_to_column(filepath):
    subtitles = []
    with open(filepath, "r") as f:
        for line in f:  # Iterar línea por línea
            subtitles.append(line.strip())
    return subtitles


if __name__ == "__main__":
    # get word frequencies
    tr_frequencies = get_word_frequencies("data/wiki_frequency.txt")
    es_frequencies = get_word_frequencies("data/subs_frequency_es.txt")

    print("done w frequencies")

    # create dataframe of subtitles
    tr_subtitles = txt_to_column("data/subtitles.tr")
    es_subtitles = txt_to_column("data/subtitles.es")

    print("done w reading subtitles")

    # create new column with scores
    tr_scores = [score_sentence(sentence, tr_frequencies) for sentence in tr_subtitles]
    print("done w scoring TURK LANGUAGE")

    es_scores = [score_sentence(sentence, es_frequencies) for sentence in es_subtitles]
    print("done w scoring ESPAñ")

    df = pd.DataFrame({"tr": tr_subtitles, "tr_score": tr_scores, "es": es_subtitles, "es_score": es_scores})

    # drop duplicates
    df = df.drop_duplicates(subset='tr_score', keep=False)
    df = df.drop_duplicates(subset='es_score', keep=False)

    df["score"] = round(2 * df["tr_score"] + df["es_score"], 2)
    
    # sort by scores
    df = df.sort_values("score")

    print("done w sorting")

    pd.set_option('display.max_rows', None)
    print("First 300")
    print(df.head(300))

    size_to_print = int(df.size / 300)
    print("Filtered 300")
    print(df.iloc[::size_to_print])
    
    # save to pickle
    df.to_pickle("sub_scores.pkl")

    # save to csv
    df.to_csv("sub_scores.csv")


