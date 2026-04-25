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

    texts = re.split(r'\|,|-->', text)

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
    texts = pd.read_csv('cositas.csv', sep='\t')
    msgs = []
    cut_messages(texts, msgs)

    columna = ['Mensaje']

    df = pd.DataFrame(data = msgs, columns = columna)

    df['Riesgo'] = 5
    print(df)

    df_sure = pd.read_csv('frases.csv', sep='\t', index_col=False)
    print(df_sure)


    texts = pd.read_csv('pacificos.csv', sep='\t')
    msgs2 = []
    cut_messages(texts, msgs2)

    columna = ['Mensaje']

    df3 = pd.DataFrame(data = msgs2, columns = columna)

    df3['Riesgo'] = -5

    print(df)


    df = pd.concat([df, df3, df_sure],axis = 0, ignore_index = True)

    df.to_csv('datasets/original_dataset.csv',sep='\t', index=False, encoding='utf-8')
