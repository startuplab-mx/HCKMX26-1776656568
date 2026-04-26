# Dataset de entrada

El dataset de entrada consiste en dos archivos .csv (Pueden tener cualquier nombre que será el que se asigna en datos.py)

# Organización de datos

Para organizar los datos se debe correr datos.py, esto automáticamente generará el dataset original de datos sin normalizaciones que será guardado en **datasets/original_dataset**

# Normalizaciones de textos

Para la normalización de textos, se deberá correr el archivo **normal.py** este archvo creará todos los pkl separando tanto los X de prueba y los y de resultado en una distribución de 80% prueba, 20% entrenamiento para un entrenamiento 5 fold.

# Creación de modelos y experimentos

Para la inicialización de experimentos se deberá correr el archivo correspondiente de la prueba en **experiments/<prueba>.py** se recibirán configuraciones de normalización y lemantización con el fin de encontrar la que genere la mayor puntuación.

Al final se seleccionará el que tenga mayor rendimiento y se guardará su dump de entrenamiento con el fin de solamente procesar el texto con la lemantización y evaluación correspondiente (Del mismo modo que surgieron los datasets originales) y se tendrá la evaluación final con el modelo entrenado.