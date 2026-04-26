"""
EXPERIMENTO 8 (REGRESIÓN): SVM → LinearSVR
- Predicción continua [-5, 10]
- Evaluación por signo
"""

import pickle
import numpy as np
from sklearn.svm import LinearSVR
from sklearn.model_selection import cross_validate
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

# Configuración
BEST_NORMALIZATION = 'spacy'  
BEST_VECTORIZATION = 'tfidf'

print("="*70)
print("EXPERIMENTO 8: SVM REGRESIÓN (LinearSVR)")
print("="*70)

# Cargar dataset
print("\n1. Cargando dataset...")
dataset_file = f'pkl/{BEST_NORMALIZATION}_{BEST_VECTORIZATION}.pkl'
with open(dataset_file, 'rb') as f:
    data = pickle.load(f)

X_train = data['X_train']
y_train = data['y_train'].astype(float)
X_test = data['X_test']
y_test = data['y_test'].astype(float)

print(f"   Train: {X_train.shape}")
print(f"   Test: {X_test.shape}")

# Modelo (REGRESIÓN)
print("\n2. Entrenando modelo con Cross-Validation...")
model = LinearSVR(
    C=1.0,
    max_iter=5000,
    random_state=0
)

# Cross-validation (métricas de regresión)
cv_results = cross_validate(
    model, X_train, y_train,
    cv=5,
    scoring=('neg_mean_absolute_error', 'neg_mean_squared_error'),
    return_train_score=True,
    n_jobs=-1
)

mae_cv = -cv_results['test_neg_mean_absolute_error']
mse_cv = -cv_results['test_neg_mean_squared_error']

print(f"\n   MAE por fold: {mae_cv}")
print(f"   ✓ MAE promedio: {mae_cv.mean():.4f}")

print(f"\n   MSE por fold: {mse_cv}")
print(f"   ✓ MSE promedio: {mse_cv.mean():.4f}")

# Entrenar modelo final
print("\n3. Entrenando modelo final...")
model.fit(X_train, y_train)

# Predicciones
y_train_pred = model.predict(X_train)
y_test_pred = model.predict(X_test)

# Clip al rango [-5, 10]
y_test_pred = np.clip(y_test_pred, -5, 10)

# ---------------------------
# Evaluación por signo
# ---------------------------
def sign_accuracy(y_true, y_pred):
    correct = np.sum(np.sign(y_true) == np.sign(y_pred))
    return correct / len(y_true)

sign_acc_train = sign_accuracy(y_train, y_train_pred)
sign_acc_test = sign_accuracy(y_test, y_test_pred)

# Métricas de regresión
mae_test = mean_absolute_error(y_test, y_test_pred)
mse_test = mean_squared_error(y_test, y_test_pred)

print("\n" + "="*70)
print("RESULTADOS FINALES")
print("="*70)

print(f"\n   ✓ MAE TEST: {mae_test:.4f}")
print(f"   ✓ MSE TEST: {mse_test:.4f}")
print(f"   ✓ SIGN ACCURACY TEST: {sign_acc_test:.4f}")

print("\nEjemplo predicciones:")
for i in range(5):
    print(f"Real: {y_test.iloc[i]:6.2f} | Pred: {y_test_pred[i]:6.2f} | "
          f"Signo OK: {np.sign(y_test.iloc[i]) == np.sign(y_test_pred[i])}")

# Guardar resultados
results = {
    'experiment': 'exp08_svm_regression',
    'normalization': BEST_NORMALIZATION,
    'vectorization': BEST_VECTORIZATION,
    'algorithm': 'LinearSVR',
    'cv_mae': mae_cv,
    'cv_mse': mse_cv,
    'test_mae': mae_test,
    'test_mse': mse_test,
    'sign_accuracy_test': sign_acc_test,
    'y_pred': y_test_pred
}

with open('./results/results_exp08_regression.pkl', 'wb') as f:
    pickle.dump(results, f)

print("\n✓ Resultados guardados en: results_exp08_regression.pkl")