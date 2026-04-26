# Dataset de entrada

El dataset de entrada consiste en dos archivos .csv (Pueden tener cualquier nombre que será el que se asigna en datos.py)

# Organización de datos

Para organizar los datos se debe correr datos.py, esto automáticamente generará el dataset original de datos sin normalizaciones que será guardado en **datasets/original_dataset**

# Normalizaciones de textos

Para la normalización de textos, se deberá correr el archivo **normal.py** este archvo creará todos los pkl separando tanto los X de prueba y los y de resultado en una distribución de 80% prueba, 20% entrenamiento para un entrenamiento 5 fold.

# Creación de modelos y experimentos

Para la inicialización de experimentos se deberá correr el archivo correspondiente de la prueba en **experiments/<prueba>.py** se recibirán configuraciones de normalización y lemantización con el fin de encontrar la que genere la mayor puntuación.

Al final se seleccionará el que tenga mayor rendimiento y se guardará su dump de entrenamiento con el fin de solamente procesar el texto con la lemantización y evaluación correspondiente (Del mismo modo que surgieron los datasets originales) y se tendrá la evaluación final con el modelo entrenado.


# Uso del modelo ya entrenado

Para la versión final del modelo se necesita primero generar el caso de prueba a partir del lector de datos.py, estos leeran el valor desde los csv que estarán en la carpeta de datasets.
Para su correcto funcionamiento seleccionar los valores dañinos al malign_dataset.csv
Para los valores comunes adecuados para los niños ingresar dichos valores a good_dataset.csv


# Ejecución y entrenamiento recomendado
* datos.py permite concatenar los datasets en caso de encontrar nuevos valores que sean asegurados o igualmente se puede usar en combinación de algún servicio de monitoreo con el fin de actualizar la información conforme se descubre.

* Posteriormente usar normal.py con el fin de normalizar los textos para el modelo de IA.
* Entrenar el modelo con: python final/train_model_spacy_tfidf_v2.py . El entrenamiento se guardará en la carpeta models.
* Evaluar el archivo de consultas: python final/evaluar_consultas_riesgo_spacy_tfidf_v2.py --input <archivo .csv de consulta> --output results/predicciones_riesgo.tsv. *Esto será útil en el caso de necesitar el procesamiento de varios datos a la vez o realizar una consulta desde el frontend con la codificación especificada para esta tarea*
* Se puede evaluar el archivo únicamente y guardar el mensaje y riesgo asociado con: python final/evaluar_consultas_riesgo_spacy_tfidf_v2.py --input <archivo .csv de consulta> --output results/predicciones_formato_proyecto.tsv --project-format
* Para evaluar un texto individual: python final/predict_texto_spacy_tfidf_v2.py --text "texto de prueba"

# Dependencias
Para correr correctamente el proyecto se deben cargar dependencias de python
Package            Version
------------------ -----------
annotated-doc      0.0.4
annotated-types    0.7.0
anyio              4.13.0
blis               1.3.3
catalogue          2.0.10
certifi            2026.4.22
charset-normalizer 3.4.7
click              8.3.3
cloudpathlib       0.23.0
confection         1.3.3
cymem              2.0.13
es_core_news_sm    3.8.0
h11                0.16.0
httpcore           1.0.9
httpx              0.28.1
idna               3.13
Jinja2             3.1.6
joblib             1.5.3
markdown-it-py     4.0.0
MarkupSafe         3.0.3
mdurl              0.1.2
murmurhash         1.0.15
nltk               3.9.4
numpy              2.4.4
packaging          26.2
pandas             3.0.2
pip                25.1.1
preshed            3.0.13
pydantic           2.13.3
pydantic_core      2.46.3
Pygments           2.20.0
python-dateutil    2.9.0.post0
regex              2026.4.4
requests           2.33.1
rich               15.0.0
scikit-learn       1.8.0
scipy              1.17.1
setuptools         82.0.1
shellingham        1.5.4
six                1.17.0
smart_open         7.6.0
spacy              3.8.14
spacy-legacy       3.0.12
spacy-loggers      1.0.5
srsly              2.5.3
thinc              8.3.13
threadpoolctl      3.6.0
tqdm               4.67.3
typer              0.24.2
typing_extensions  4.15.0
typing-inspection  0.4.2
urllib3            2.6.3
wasabi             1.1.3
weasel             1.0.0
wrapt              2.1.2

Se pueden conseguir la mayoría de dichas dependencias con los siguiente comandos
pip install -U spacy
python -m spacy download es_core_news_sm
pip install pandas
pip install -U scikit-learn