import pickle
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_validate
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# CONFIG
BEST_NORMALIZATION = 'liwc'
BEST_VECTORIZATION = 'frequency'

print("="*70)
print("EXPERIMENTO 9: RANDOM FOREST (REGRESIÓN)")
print("="*70)
print("Configuración:")
print(f"  - Normalización: {BEST_NORMALIZATION}")
print(f"  - Vectorización: {BEST_VECTORIZATION}")
print("  - Algoritmo: RandomForestRegressor")
print("="*70)

# =========================
# 1. Cargar dataset
# =========================
print("\n1. Cargando dataset...")
dataset_file = f'pkl/{BEST_NORMALIZATION}_{BEST_VECTORIZATION}.pkl'

with open(dataset_file, 'rb') as f:
    data = pickle.load(f)

X_train = data['X_train']
X_test = data['X_test']

# 🔴 convertir a float (clave)
y_train = np.array(data['y_train']).astype(float)
y_test = np.array(data['y_test']).astype(float)

print(f"Train: {X_train.shape}")
print(f"Test: {X_test.shape}")

# =========================
# 2. Modelo
# =========================
print("\n2. Cross-validation...")
print("   (Puede tardar bastante con Random Forest)")

model = RandomForestRegressor(
    n_estimators=100,
    max_depth=50,
    random_state=0,
    n_jobs=-1
)

cv_results = cross_validate(
    model,
    X_train,
    y_train,
    cv=5,
    scoring=('neg_mean_squared_error', 'r2'),
    n_jobs=-1,
    verbose=1
)

print(f"\nMSE promedio: {-cv_results['test_neg_mean_squared_error'].mean():.4f}")
print(f"R2 promedio: {cv_results['test_r2'].mean():.4f}")

# =========================
# 3. Entrenar final
# =========================
print("\n3. Entrenando modelo final...")
model.fit(X_train, y_train)

# =========================
# 4. Evaluación
# =========================
print("\nRESULTADOS FINALES")

y_pred = model.predict(X_test)

# métricas
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"\nMSE: {mse:.4f}")
print(f"R²: {r2:.4f}")

# =========================
# 5. Evaluación por signo
# =========================
def sign_eps(x, eps=0.1):
    if x > eps: return 1
    elif x < -eps: return -1
    else: return 0

sign_vec = np.vectorize(sign_eps)

acc_sign = np.mean(sign_vec(y_pred) == sign_vec(y_test))

print(f"\nAccuracy por signo: {acc_sign:.4f}")

# =========================
# 6. Ejemplos
# =========================
print("\nEjemplos:")
for i in range(5):
    print(f"Real: {y_test[i]:6.2f} | Pred: {y_pred[i]:6.2f} | OK: {sign_vec(y_pred[i]) == sign_vec(y_test[i])}")

# =========================
# 7. Guardar
# =========================
import os
os.makedirs('results', exist_ok=True)

results = {
    'experiment': 'exp09_random_forest_regression',
    'normalization': BEST_NORMALIZATION,
    'vectorization': BEST_VECTORIZATION,
    'algorithm': 'RandomForestRegressor',
    'cv_mse': -cv_results['test_neg_mean_squared_error'],
    'cv_r2': cv_results['test_r2'],
    'test_mse': mse,
    'test_r2': r2,
    'sign_accuracy': acc_sign
}

with open('./results/results_exp09_regression.pkl', 'wb') as f:
    pickle.dump(results, f)

print("\n✓ Guardado en results_exp09_regression.pkl")