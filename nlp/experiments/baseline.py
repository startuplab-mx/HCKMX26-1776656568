import pickle
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_validate
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("EXPERIMENTO 1: REGRESIÓN + SIGNO (CORREGIDO)")
print("="*70)

# =========================
# 1. Cargar dataset
# =========================
print("\n1. Cargando dataset...")
with open('pkl/none_binary.pkl', 'rb') as f:
    data = pickle.load(f)

X_train = data['X_train']
X_test = data['X_test']

# 🔴 CORRECCIÓN CLAVE AQUÍ
y_train = np.array(data['y_train']).astype(float)
y_test = np.array(data['y_test']).astype(float)

print(f"Train: {X_train.shape}")
print(f"Test: {X_test.shape}")

print("\nDEBUG:")
print("Tipo y_train:", type(y_train), y_train.dtype)
print("Ejemplo y_train:", y_train[:5])

# =========================
# 2. Modelo
# =========================
print("\n2. Cross-validation...")

model = Ridge(random_state=0)

cv_results = cross_validate(
    model, X_train, y_train,
    cv=5,
    scoring=('neg_mean_squared_error', 'r2'),
    n_jobs=-1
)

print(f"\nMSE promedio: {-cv_results['test_neg_mean_squared_error'].mean():.4f}")
print(f"R2 promedio: {cv_results['test_r2'].mean():.4f}")

# =========================
# 3. Entrenar modelo final
# =========================
print("\n3. Entrenando modelo final...")
model.fit(X_train, y_train)

# =========================
# 4. Predicción
# =========================
print("\n4. Evaluando...")

y_pred = model.predict(X_test)

# =========================
# 5. Evaluación por signo
# =========================
def sign_eps(x, eps=0.1):
    if x > eps:
        return 1
    elif x < -eps:
        return -1
    else:
        return 0

sign_vec = np.vectorize(sign_eps)

y_pred_sign = sign_vec(y_pred)
y_test_sign = sign_vec(y_test)

accuracy_sign = np.mean(y_pred_sign == y_test_sign)

print(f"\n✓ Accuracy por signo: {accuracy_sign:.4f}")

# =========================
# 6. Métricas reales
# =========================
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"MSE: {mse:.4f}")
print(f"R²: {r2:.4f}")

# =========================
# 7. Ejemplos
# =========================
#print("\nEjemplos:")
#for i in range(10):
#    print(f"Real: {y_test[i]:6.2f} | Pred: {y_pred[i]:6.2f} | OK: {y_pred_sign[i] == y_test_sign[i]}")

# =========================
# 8. Guardar resultados
# =========================
import os
os.makedirs('results', exist_ok=True)

results = {
    'model': 'Ridge',
    'sign_accuracy': accuracy_sign,
    'mse': mse,
    'r2': r2
}

with open('results/results_exp01_regression.pkl', 'wb') as f:
    pickle.dump(results, f)

print("\n✓ Guardado en results/results_exp01_regression.pkl")
print("="*70)