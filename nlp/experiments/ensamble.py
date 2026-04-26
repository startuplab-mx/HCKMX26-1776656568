"""
EXPERIMENTO ENSEMBLE: REGRESIÓN + CLASIFICACIÓN
"""

import pickle
import numpy as np

from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVR
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, f1_score

import warnings
warnings.filterwarnings('ignore')

# Configuración
BEST_NORMALIZATION = 'spacy'
BEST_VECTORIZATION = 'tfidf'
ALPHA = 0.6  # peso de regresión (ajústalo)

print("="*70)
print("ENSEMBLE: REGRESIÓN + CLASIFICACIÓN")
print("="*70)

# Cargar datos
dataset_file = f'pkl/{BEST_NORMALIZATION}_{BEST_VECTORIZATION}.pkl'
with open(dataset_file, 'rb') as f:
    data = pickle.load(f)

X_train = data['X_train']
y_train = data['y_train'].astype(float)
X_test = data['X_test']
y_test = data['y_test'].astype(float)

# -----------------------------------
# 1. MODELO DE REGRESIÓN
# -----------------------------------
reg_model = LinearSVR(max_iter=5000)
reg_model.fit(X_train, y_train)

y_reg_pred = reg_model.predict(X_test)
y_reg_pred = np.clip(y_reg_pred, -5, 10)

# Normalizar a [-1, 1]
y_reg_norm = y_reg_pred / 10.0

# -----------------------------------
# 2. MODELO DE CLASIFICACIÓN
# -----------------------------------
# Convertir a clases binarias
y_train_bin = (y_train > 0).astype(int)
y_test_bin = (y_test > 0).astype(int)

clf_model = LogisticRegression(max_iter=1000)
clf_model.fit(X_train, y_train_bin)

# Probabilidad de positivo
y_clf_prob = clf_model.predict_proba(X_test)[:, 1]

# Convertir a [-1, 1]
y_clf_score = (y_clf_prob * 2) - 1

# -----------------------------------
# 3. ENSEMBLE
# -----------------------------------
y_final_score = ALPHA * y_reg_norm + (1 - ALPHA) * y_clf_score

# Decisión final (signo)
y_final_pred = np.where(y_final_score > 0, 1, -1)
y_true_sign = np.where(y_test > 0, 1, -1)

# -----------------------------------
# 4. MÉTRICAS
# -----------------------------------
def sign_accuracy(y_true, y_pred):
    return np.mean(y_true == y_pred)

sign_acc = sign_accuracy(y_true_sign, y_final_pred)
mae = mean_absolute_error(y_test, y_reg_pred)

print("\n" + "="*70)
print("RESULTADOS ENSEMBLE")
print("="*70)

print(f"✓ Sign Accuracy: {sign_acc:.4f}")
print(f"✓ MAE (regresión): {mae:.4f}")

# Comparación individual
reg_sign = np.where(y_reg_pred > 0, 1, -1)
clf_sign = np.where(y_clf_score > 0, 1, -1)

print("\nComparación:")
print(f"  Solo Regresión: {sign_accuracy(y_true_sign, reg_sign):.4f}")
print(f"  Solo Clasificación: {sign_accuracy(y_true_sign, clf_sign):.4f}")
print(f"  Ensemble: {sign_acc:.4f}")

# Guardar
results = {
    'experiment': 'ensemble_reg_clf',
    'alpha': ALPHA,
    'sign_accuracy': sign_acc,
    'mae': mae,
    'y_pred': y_final_score
}

with open('./results/results_ensemble.pkl', 'wb') as f:
    pickle.dump(results, f)

print("\n✓ Resultados guardados en results_ensemble.pkl")