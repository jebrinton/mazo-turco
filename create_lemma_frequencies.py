import pathlib
from collections import defaultdict
import pickle
import wordfreq

from lemmatizer import lemmatize, get_lemma_dict

# necesitas un mejor lematizador

def create_frequency_dictionaries(subs_path: pathlib.Path) -> tuple[dict, dict]:
    # Crear diccionarios con valores predeterminados de 0
    lemma_counts = defaultdict(int)
    token_counts = defaultdict(int)
    total_lemmas = 0
    total_tokens = 0
    
    # Obtener el diccionario de lematización
    lemma_dict = get_lemma_dict()
    
    print("Procesando subtítulos...")
    
    # Leer el archivo y procesar cada línea
    with subs_path.open('r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            # Mostrar progreso cada 10000 líneas
            if i % 10000 == 0:
                print(f"Procesadas {i} líneas...")
                
            # Tokenizar la línea usando wordfreq
            tokens = wordfreq.tokenize(line.strip(), 'tr')
            
            # Contar tokens y sus lemas
            for token in tokens:
                token = token.lower()
                token_counts[token] += 1
                total_tokens += 1
                
                lemma = lemmatize(token, lemma_dict)
                lemma_counts[lemma] += 1
                total_lemmas += 1

    print(f"\nTotal de lemas procesados: {total_lemmas}")
    print(f"Vocabulario único de lemas: {len(lemma_counts)} lemas")
    print(f"Total de tokens procesados: {total_tokens}")
    print(f"Vocabulario único de tokens: {len(token_counts)} tokens")
    
    # Normalizar las frecuencias
    print("\nNormalizando frecuencias...")
    lemma_frequencies = {
        lemma: count / total_lemmas 
        for lemma, count in lemma_counts.items()
    }
    
    token_frequencies = {
        token: count / total_tokens
        for token, count in token_counts.items()
    }
    
    return lemma_frequencies, token_frequencies

def main():
    # Definir rutas
    root = pathlib.Path(".")
    subs_path = root / "tatoeba_tr_en" / "data" / "sentences.tr"
    lemma_output_path = root / "lemma_dictionaries" / "tr_tatoeba.pkl"
    token_output_path = root / "lemma_dictionaries" / "tr_tatoeba_tokens.pkl"
    
    # Verificar que el archivo de entrada existe
    if not subs_path.exists():
        print(f"Error: No se encuentra el archivo en {subs_path}")
        return
    
    # Crear los diccionarios de frecuencias
    lemma_frequencies, token_frequencies = create_frequency_dictionaries(subs_path)
    
    # Guardar los diccionarios
    print(f"\nGuardando diccionarios...")
    
    with lemma_output_path.open('wb') as f:
        pickle.dump(lemma_frequencies, f)
    print(f"Guardado diccionario de lemas en {lemma_output_path}")
    
    with token_output_path.open('wb') as f:
        pickle.dump(token_frequencies, f)
    print(f"Guardado diccionario de tokens en {token_output_path}")
    
    print("¡Proceso completado!")

if __name__ == "__main__":
    # main()

    root = pathlib.Path(".")
    lemma_frequencies = pickle.load(open(root / "lemma_dictionaries" / "tr_tatoeba_tokens.pkl", "rb"))
    for lemma, freq in list(lemma_frequencies.items())[:300]:
        print(f"{lemma}: {freq:.6f}")