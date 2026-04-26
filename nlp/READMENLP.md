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

* datos.py permite concatenar los datasets en caso de encontrar nuevos valores que sean asegurados o igualmente se puede usar en combinación de algún servicio de monitoreo con el fin de actualizar la información conforme se descubre.

* Posteriormente usar normal.py con el fin de normalizar los textos para el modelo de IA.
* Entrenar el modelo con: python final/train_model_spacy_tfidf_v2.py . El entrenamiento se guardará en la carpeta models.
* Evaluar el archivo de consultas: python final/evaluar_consultas_riesgo_spacy_tfidf_v2.py --input <archivo .csv de consulta> --output results/predicciones_riesgo.tsv. *Esto será útil en el caso de necesitar el procesamiento de varios datos a la vez o realizar una consulta desde el frontend con la codificación especificada para esta tarea*
* Se puede evaluar el archivo únicamente y guardar el mensaje y riesgo asociado con: python final/evaluar_consultas_riesgo_spacy_tfidf_v2.py --input <archivo .csv de consulta> --output results/predicciones_formato_proyecto.tsv --project-format
* Para evaluar un texto individual: python final/predict_texto_spacy_tfidf_v2.py --text "texto de prueba"