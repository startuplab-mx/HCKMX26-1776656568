import pandas as pd
import re

import spacy

try:
    nlp_spacy = spacy.load("es_core_news_sm")   # puedes usar "lg" si ya lo tienes instalado
    print("  spaCy cargado correctamente")
except Exception as e:
    print("  Error cargando spaCy:", e)
    nlp_spacy = None


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

    df['Riesgo'] = -5

    df.to_csv('datasets/original_dataset.csv',sep='\t', index=False, encoding='utf-8')
    