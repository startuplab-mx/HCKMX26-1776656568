import pandas as pd
import re
import nltk
import spacy
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import re
import os
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer


try:
    nlp_spacy = spacy.load("es_core_news_sm")   # puedes usar "lg" si ya lo tienes instalado
    print("  spaCy cargado correctamente")
except Exception as e:
    print("  Error cargando spaCy:", e)
    nlp_spacy = None

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

def create_vectorized_datasets(test_data, output_dir = 'pkl'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Definir las normalizaciones a probar
    normalizations = {
        'spacy': normalize_spacy,
    }
    
    vectorizations = {
        'tfidf': lambda: TfidfVectorizer()
    }

    datasets = {}
    
    for norm_name, norm_func in normalizations.items():

        # Normalizar corpus
        X_train_norm = norm_func(test_data)

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

def divide_text(text):
    splitted = []

    texts = re.split(r'\|,|-->|<--', text)

    for t in texts:
        splitted.append(t[re.search(r':', t).start()+1:])
    return splitted

def clean_text(text):
    text = text.lower();

    return text

def cut_messages(texts, msgs):
    for txt in texts['user_comments'].tolist():
        txt = divide_text(txt)
        for t in txt:
            msgs.append(t.strip())

def clean_msgs(msg):
    for i in range(len(msg)):
        msg[i] = clean_text(msg[i])


if __name__ == '__main__':
    texts = pd.read_csv('msgs.csv', sep='\t')
    msgs = []
    cut_messages(texts, msgs)

    columna = ['Mensaje']
    df = pd.DataFrame(data = msgs, columns = columna)

    print(df)