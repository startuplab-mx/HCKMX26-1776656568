# ⬇️⬇️⬇️ CÓDIGO COMPLETO CON SPACY AGREGADO ⬇️⬇️⬇️

"""
Script para generar PKLs con diferentes normalizaciones y representaciones vectoriales
Esto ahorra tiempo al no tener que repetir el proceso en cada experimento
"""

import pandas as pd
import pickle
import nltk
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import re
import os
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer

import spacy

# Descargar recursos necesarios de NLTK
print("Descargando recursos de NLTK...")
try:
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)
except:
    pass

# Cargar modelo spaCy español
print("Cargando modelo spaCy para lematización...")
try:
    nlp_spacy = spacy.load("es_core_news_sm")   # puedes usar "lg" si ya lo tienes instalado
    print("  ✓ spaCy cargado correctamente")
except Exception as e:
    print("  ⚠ Error cargando spaCy:", e)
    nlp_spacy = None

# Cargar diccionario LIWC para lematización
def load_liwc_lexicon(file_path='./LIWC2007.dic'):
    """
    Carga el diccionario LIWC y extrae las raíces de palabras
    para usar en lematización
    """
    print("\nCargando diccionario LIWC para lematización...")
    liwc_roots = {}  # palabra_completa -> raíz
    liwc_stems = {}  # raíz (sin *) -> raíz completa con *
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            in_words_section = False
            for line in f:
                line = line.strip()
                
                # Detectar inicio de sección de palabras
                if line == '%' and not in_words_section:
                    in_words_section = True
                    continue
                
                if not in_words_section or not line:
                    continue
                
                parts = line.split('\t')
                if len(parts) < 2:
                    continue
                
                word = parts[0].lower()
                
                # Si la palabra tiene asterisco, es una raíz
                if '*' in word:
                    stem = word.replace('*', '')
                    liwc_stems[stem] = word
                else:
                    # Las palabras completas se mapean a sí mismas
                    liwc_roots[word] = word
        
        print(f"  ✓ LIWC cargado: {len(liwc_roots)} palabras completas, {len(liwc_stems)} raíces")
        return liwc_roots, liwc_stems
    
    except Exception as e:
        print(f"  ⚠ Error cargando LIWC: {e}")
        print("  Se continuará sin lematización LIWC")
        return {}, {}

# Cargar LIWC globalmente
LIWC_ROOTS, LIWC_STEMS = load_liwc_lexicon()

# Configuración
RANDOM_STATE = 0
TEST_SIZE = 0.2

class DatasetPolarity:
    """Clase para almacenar el dataset dividido"""
    def __init__(self, X_train, y_train, X_test, y_test):
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test

def load_and_prepare_data(file_path):
    """
    Carga el dataset y concatena Title + Opinion
    """
    print(f"\nCargando dataset desde {file_path}...")
    df = pd.read_excel(file_path)
    
    # Concatenar Title + Opinion
    df['Text'] = df['Title'].astype(str) + ' ' + df['Opinion'].astype(str)
    X = df['Text']
    y = df['Polarity'].values
    
    print(f"Total de opiniones: {len(X)}")
    print(f"Distribución de clases:")
    print(pd.Series(y).value_counts().sort_index())
    
    # Split 80/20
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, shuffle=True
    )
    
    print(f"\nTrain set: {len(X_train)} opiniones")
    print(f"Test set: {len(X_test)} opiniones")
    
    return DatasetPolarity(X_train, y_train, X_test, y_test)

def clean_text(text):
    """Limpieza básica del texto"""
    text = text.lower()
    text = re.sub(r'[^a-záéíóúñü\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def normalize_none(corpus):
    """Sin normalización, solo limpieza básica"""
    print("Aplicando limpieza básica...")
    return [clean_text(text) for text in corpus]

def normalize_no_stopwords(corpus):
    """Remover stopwords"""
    print("Aplicando limpieza + remover stopwords...")
    stop_words = set(stopwords.words('spanish'))
    result = []
    for text in corpus:
        text = clean_text(text)
        words = text.split()
        words = [w for w in words if w not in stop_words]
        result.append(' '.join(words))
    return result

def normalize_stemming(corpus):
    """Aplicar stemming"""
    print("Aplicando limpieza + stemming...")
    stemmer = SnowballStemmer('spanish')
    result = []
    for text in corpus:
        text = clean_text(text)
        words = text.split()
        words = [stemmer.stem(w) for w in words]
        result.append(' '.join(words))
    return result

def normalize_stemming_no_stopwords(corpus):
    """Aplicar stemming y remover stopwords"""
    print("Aplicando limpieza + stemming + sin stopwords...")
    stemmer = SnowballStemmer('spanish')
    stop_words = set(stopwords.words('spanish'))
    result = []
    for text in corpus:
        text = clean_text(text)
        words = text.split()
        words = [stemmer.stem(w) for w in words if w not in stop_words]
        result.append(' '.join(words))
    return result

def lemmatize_word_liwc(word):
    """
    Lematiza una palabra usando el diccionario LIWC
    Busca la raíz más larga que coincida
    """
    # Si la palabra está completa en el diccionario, retornarla
    if word in LIWC_ROOTS:
        return word
    
    # Buscar la raíz más larga que coincida
    best_stem = word
    best_len = 0
    
    for stem in LIWC_STEMS:
        if word.startswith(stem) and len(stem) > best_len:
            best_stem = stem
            best_len = len(stem)
    
    return best_stem

def normalize_liwc(corpus):
    """Lematización usando diccionario LIWC"""
    print("Aplicando limpieza + lematización LIWC...")
    result = []
    for text in corpus:
        text = clean_text(text)
        words = text.split()
        words = [lemmatize_word_liwc(w) for w in words]
        result.append(' '.join(words))
    return result

def normalize_liwc_no_stopwords(corpus):
    """Lematización LIWC + remover stopwords"""
    print("Aplicando limpieza + lematización LIWC + sin stopwords...")
    stop_words = set(stopwords.words('spanish'))
    result = []
    for text in corpus:
        text = clean_text(text)
        words = text.split()
        words = [lemmatize_word_liwc(w) for w in words if w not in stop_words]
        result.append(' '.join(words))
    return result


# =============================
# NUEVAS FUNCIONES: SPACY
# =============================

def normalize_spacy(corpus):
    """Lematización usando spaCy"""
    print("Aplicando limpieza + lematización spaCy...")
    if nlp_spacy is None:
        print("⚠ spaCy no está disponible. Se regresará texto limpio sin lematizar.")
        return [clean_text(text) for text in corpus]
    
    result = []
    for text in corpus:
        text = clean_text(text)
        doc = nlp_spacy(text)
        words = [token.lemma_.lower() for token in doc]
        result.append(' '.join(words))
    return result

def normalize_spacy_no_stopwords(corpus):
    """Lematización spaCy + remover stopwords"""
    print("Aplicando limpieza + lematización spaCy + sin stopwords...")
    if nlp_spacy is None:
        print("⚠ spaCy no está disponible. Se regresará texto limpio sin lematizar.")
        return normalize_no_stopwords(corpus)
    
    stop_words = set(stopwords.words('spanish'))
    result = []
    for text in corpus:
        text = clean_text(text)
        doc = nlp_spacy(text)
        words = [token.lemma_.lower() for token in doc if token.lemma_.lower() not in stop_words]
        result.append(' '.join(words))
    return result


def create_vectorized_datasets(corpus_data, output_dir='datasets'):
    """
    Crea diferentes versiones del dataset con distintas normalizaciones
    y representaciones vectoriales
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Definir las normalizaciones a probar
    normalizations = {
        'none': normalize_none,
        'no_stopwords': normalize_no_stopwords,
        'stemming': normalize_stemming,
        'stemming_no_stopwords': normalize_stemming_no_stopwords,
        'liwc': normalize_liwc,
        'liwc_no_stopwords': normalize_liwc_no_stopwords,

        # NUEVAS OPCIONES SPAcY ⬇️
        'spacy': normalize_spacy,
        'spacy_no_stopwords': normalize_spacy_no_stopwords
    }
    
    # Representaciones vectoriales
    vectorizations = {
        'binary': lambda: CountVectorizer(binary=True),
        'frequency': lambda: CountVectorizer(binary=False),
        'tfidf': lambda: TfidfVectorizer()
    }
    
    datasets = {}
    
    print("\n" + "="*60)
    print("GENERANDO DATASETS CON DIFERENTES CONFIGURACIONES")
    print("="*60)
    
    for norm_name, norm_func in normalizations.items():
        print(f"\n{'='*60}")
        print(f"NORMALIZACIÓN: {norm_name}")
        print(f"{'='*60}")
        
        # Normalizar corpus
        X_train_norm = norm_func(corpus_data.X_train)
        X_test_norm = norm_func(corpus_data.X_test)
        
        for vec_name, vec_func in vectorizations.items():
            print(f"\nCreando: {norm_name} + {vec_name}")
            
            # Crear vectorizador
            vectorizer = vec_func()
            
            # Ajustar y transformar
            X_train_vec = vectorizer.fit_transform(X_train_norm)
            X_test_vec = vectorizer.transform(X_test_norm)
            
            print(f"  Vocabulario: {len(vectorizer.get_feature_names_out())} términos")
            print(f"  Shape train: {X_train_vec.shape}")
            print(f"  Shape test: {X_test_vec.shape}")
            
            # Guardar
            dataset_name = f"{norm_name}_{vec_name}"
            dataset = {
                'X_train': X_train_vec,
                'X_test': X_test_vec,
                'y_train': corpus_data.y_train,
                'y_test': corpus_data.y_test,
                'vectorizer': vectorizer,
                'normalization': norm_name,
                'vectorization': vec_name
            }
            
            file_path = os.path.join(output_dir, f'{dataset_name}.pkl')
            with open(file_path, 'wb') as f:
                pickle.dump(dataset, f)
            
            print(f"  ✓ Guardado en: {file_path}")
            
            datasets[dataset_name] = dataset
    
    return datasets


if __name__ == '__main__':
    print("="*60)
    print("PREPARACIÓN DE DATASETS PARA EXPERIMENTOS")
    print("="*60)
    
    # Cargar datos originales
    corpus_data = load_and_prepare_data('./Rest_Mex_2022.xlsx')
    
    # Guardar corpus base
    print("\nGuardando corpus base...")
    with open('./corpus_base.pkl', 'wb') as f:
        pickle.dump(corpus_data, f)
    print("✓ Corpus base guardado en: datasets/corpus_base.pkl")
    
    # Crear datasets vectorizados
    datasets = create_vectorized_datasets(corpus_data)
    
    print("\n" + "="*60)
    print("PROCESO COMPLETADO")
    print("="*60)
    print(f"\nTotal de datasets generados: {len(datasets)}")
    print("\nDatasets disponibles:")
    for name in sorted(datasets.keys()):
        print(f"  - {name}")
    
    print("\n✓ Todos los datasets están listos en la carpeta 'datasets/'")
    print("  Ahora puedes ejecutar los scripts de experimentación")
