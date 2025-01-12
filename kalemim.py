import sys
import time
import pathlib
import shutil
import pickle

import pandas as pd
import deep_translator
import random
import matplotlib.pyplot as plt

LINE_UP = '\033[1A'
LINE_CLEAR = '\x1b[2K'

UNSET = -999

## TODO:
# keep a dictionary of words and if the user knew them

def translate(word, src_lang="tr", tgt_lang="es"):
    return deep_translator.GoogleTranslator(source=src_lang, target=tgt_lang).translate(word)


def clear_to_start(text):
    lines = text.split('\n') # separate lines
    lines = lines[::-1] # reverse list
    nlines = len(lines) # number of lines

    for i, line in enumerate(lines): # iterate through lines from last to first
        sys.stdout.write('\r') # move to beginning of line
        sys.stdout.write(' ' * len(line)) # replace text with spaces (thus overwriting it)

        if i < nlines - 1: # not first line of text
            sys.stdout.write('\x1b[1A') # move up one line

    sys.stdout.write('\r') # move to beginning of line again


def round_of(cumle, frase):
    # imprimir frase turca
    # cümle
    print(cumle)

    # esperar a que se pulse la tecla enter
    while True:
        my_input = input()
        print(LINE_UP, end=LINE_CLEAR)
        if my_input == "":
            break
        else:
            print(f"{my_input} -> {translate(my_input.strip())}")

    # mostrar traducción (frase española)
    print(frase)

    while True:
        my_input = input()
        print(LINE_UP, end=LINE_CLEAR)
        if my_input == "l":
            print("Marked incorrect")
            return -1
        elif my_input == "ş":
            print("Marked neutral")
            return 0
        elif my_input == "i":
            print("Marked correct")
            return 1
        elif my_input == "":
            print("Por favor presiona las teclas correctas")
            time.sleep(0.8)
            print(LINE_UP, end=LINE_CLEAR)
        else:
            print(f"{my_input} -> {translate(my_input.strip())}")


def game(user : pathlib.Path):
    gamestate = user / "sentence_scores.pkl"
    df = pd.read_pickle(gamestate)

    # elegir oración inicial
    idx = int(len(df) * random.uniform(0.03, 0.077))

    round_num = 0
    while True:
        # hacer una ronda
        sub = df.iloc[idx]

        # for i in range(100):
        #     print(LINE_UP, end=LINE_CLEAR)

        print(f"Zorluk {round(((100 * idx) / len(df)), 2)}")
        
        knew_translation = round_of(sub["src"], sub["tgt"])

        print("q to quit")
        if input() == "q":
            df.to_pickle(gamestate)
            return
        else:
            print(LINE_UP, end=LINE_CLEAR)
            print(LINE_UP, end=LINE_CLEAR)
            print()

        df.loc[idx, 'correct'] = knew_translation

        if round_num % 20 == 7:
            filtered_df = df[df['correct'] != UNSET]
            plot_df(filtered_df)

        factor = 0.5 * (0.95 ** round_num + 0.04)
        
        # idea—do something with fitting gaussians to the distributions of what the user knew and didn't know

        # recalcular promedio basado en el resultado (si el usuario sabía la traducción o no)
        idx += 1 + knew_translation * int(factor * idx)

        if idx >= len(df):
            print("you win")
            idx = len(df) - 1
        if idx < 0:
            print("you lose")
            idx = 0

        round_num += 1


def setup(user : pathlib.Path, resources : pathlib.Path):
    gamestate = user / "sentence_scores.pkl"

    print(resources / "sentence_scores.pkl")

    # Asegúrate de que el directorio del archivo de destino existe
    gamestate.parent.mkdir(parents=True, exist_ok=True)

    shutil.copy(resources / "sentence_scores.pkl", gamestate)

    # add correct column
    df = pd.read_pickle(gamestate)
    df['correct'] = UNSET
    df.to_pickle(gamestate)


def plot_df(df):
    colors = df['correct'].map({-1: 'red', 0: 'blue', 1: 'green'})
    plt.scatter(df['src_num_chars'], df['src_avg'], c=colors, s=8)
    plt.xlabel('Number of Characters in Source Sentence')
    plt.ylabel('Max Freq')
    plt.title('Source Sentence Length vs. Max Frequency')
    plt.show()


def main():
    root = pathlib.Path(".")
    tatoeba_tren = root / "tatoeba_tr_en" / "saves"
    
    print("Enter username: ", end="")
    username = input().strip()

    users_path = root / "users"
    users_path.mkdir(exist_ok=True)

    user = users_path / username
    if not user.exists():
        setup(user, tatoeba_tren)
    game(user)
    return


if __name__ == "__main__":
    main()