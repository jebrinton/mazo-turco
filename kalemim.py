import pickle
import pandas as pd
import random
import deep_translator
import sys, time

LINE_UP = '\033[1A'
LINE_CLEAR = '\x1b[2K'

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

def user_response():
    # esperar la tecla r o e
    # r: sabía la traducción
    # e: no sabía la traducción
    my_input = input()
    if my_input == "s":
        return -1
    elif my_input == "d":
        return 0
    elif my_input == "f":
        return 1
    else:
        time.sleep(0.4)
        print(LINE_UP, end=LINE_CLEAR)
        print("Por favor, pulsa las teclas correctas")
        time.sleep(0.8)
        print(LINE_UP, end=LINE_CLEAR)
        return user_response()

def round_of(cumle, frase):
    # imprimir frase turca
    # cümle
    print(cumle, end="\n")

    # esperar a que se pulse la tecla enter
    my_input = input()
    if my_input == "\n" or my_input == "":
        print(LINE_UP, end=LINE_CLEAR)
    else:
        print(LINE_UP, end=LINE_CLEAR)
        print(LINE_UP, end=LINE_CLEAR)
        print(f"{my_input} -> {translate(my_input.strip())}")
        round_of(cumle, frase)

    # mostrar traducción (frase española)
    print(frase)

    return user_response()

def game(df, src_lang, tgt_lang):
    # elegir oración inicial
    idx = int(len(df) * random.uniform(0.03, 0.077))

    round_num = 0
    while True:
        # hacer una ronda
        sub = df.iloc[idx]

        print(f"difficulty {round(((100 * idx) / len(df)), 1)}")
        
        knew_translation = round_of(sub[src_lang], sub[tgt_lang])

        factor = 0.5 * (0.95 ** round_num + 0.14)
        
        # idea—do something with fitting gaussians to the distributions of what the user knew and didn't know

        # recalcular promedio basado en el resultado (si el usuario sabía la traducción o no)
        if knew_translation == 1:
            idx += int(factor * idx)
        elif knew_translation == 0:
            idx += 1
        else:
            idx -= int(factor * idx)

        if idx >= len(df):
            idx = len(df) - 1

        round_num += 1


def main():
    # load sub_scores.pkl
    df = pd.read_pickle("tatoeba_tr_en/saves/sub_scores.pkl")
    game(df, "tr", "en")
    return

if __name__ == "__main__":
    main()