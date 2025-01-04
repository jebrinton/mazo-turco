import math
import re
import pandas as pd
import wordfreq

## TODO: add lemmatization

# some metric to score a sentence
def score_sentence(sentence, lang, frequencies):
    sum = 0
    num_words = 0
    tokenized = wordfreq.tokenize(sentence, lang)
    for word in tokenized:
        # print(f"frequencies[{word}]: {frequencies.get(word, 0)}, -log10: {-math.log10(frequencies.get(word, 1.0e-10))}")
        sum += -math.log10(frequencies.get(word, 1.0e-10))
        num_words += 1

    if num_words == 0:
        return 0.07
    avg = sum / num_words

    score = avg + 7 * math.log10(num_words)
    # print(f"avg: {avg}, log_num_words: {math.log10(num_words)}, score: {score}")
    return round(score, 4)


# get subtitles
def txt_to_column(filepath):
    subtitles = []
    with open(filepath, "r") as f:
        for line in f:  # Iterar línea por línea
            subtitles.append(line.strip())
    return subtitles


def make_sorted_sentences(folder_name, l1, l2):
    # get word frequencies
    l1_frequencies = wordfreq.get_frequency_dict(l1, wordlist='small')
    l2_frequencies = wordfreq.get_frequency_dict(l2, wordlist='small')

    print("Done with frequencies")

    # create dataframe of subtitles
    path = folder_name + "/data/sentences."
    l1_subtitles = txt_to_column(path + l1)
    l2_subtitles = txt_to_column(path + l2)

    print("Done with reading subtitles")

    # create new column with scores
    l1_scores = [score_sentence(sentence, l1, l1_frequencies) for sentence in l1_subtitles]
    print("Done with scoring " + l1)

    l2_scores = [score_sentence(sentence, l2, l2_frequencies) for sentence in l2_subtitles]
    print("Done with scoring " + l2)

    l1_scores_name = l1 + "_score"
    l2_scores_name = l2 + "_score"

    df = pd.DataFrame({l1: l1_subtitles, l1_scores_name: l1_scores, l2: l2_subtitles, l2_scores_name: l2_scores})

    # drop duplicates
    df = df.drop_duplicates(subset=l1_scores_name, keep=False)
    df = df.drop_duplicates(subset=l2_scores_name, keep=False)

    df["score"] = round(2 * df[l1_scores_name] + df[l2_scores_name], 2)
    
    # sort by scores
    df = df.sort_values("score")

    print("Done with sorting")

    pd.set_option('display.max_rows', None)
    print("First 300")
    print(df.head(300))

    size_to_print = int(df.size / 300)
    print("Filtered 300")
    print(df.iloc[::size_to_print])
    
    # save to pickle
    save_path = folder_name + "/saves/sub_scores."

    df.to_pickle(save_path + "pkl")

    # save to csv
    df.to_csv(save_path + "csv")


if __name__ == "__main__":
    make_sorted_sentences("tatoeba_tr_en", "tr", "en")
    


