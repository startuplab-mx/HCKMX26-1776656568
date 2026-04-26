import pickle
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# CONFIG
BEST_NORMALIZATION = 'liwc'
BEST_VECTORIZATION = 'tfidf'

print("="*70)
print("EXPERIMENTO 11: GRID SEARCH (REGRESIÓN)")
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

# 🔴 IMPORTANTE
y_train = np.array(data['y_train']).astype(float)
y_test = np.array(data['y_test']).astype(float)

print(f"Train: {X_train.shape}")
print(f"Test: {X_test.shape}")

# =========================
# 2. Modelo + grid
# =========================
print("\n2. Grid Search...")

base_model = Ridge(random_state=0)

param_grid = {
    'alpha': [0.1, 1.0, 10.0, 50.0],
    'solver': ['auto', 'saga', 'lsqr']
}

grid_search = GridSearchCV(
    base_model,
    param_grid,
    cv=5,
    scoring='neg_mean_squared_error',
    verbose=2,
    n_jobs=-1,
    return_train_score=True
)

grid_search.fit(X_train, y_train)

# =========================
# 3. Resultados
# =========================
print("\n" + "="*70)
print("RESULTADOS DEL GRID SEARCH")
print("="*70)

print(f"\n✓ Mejores hiperparámetros: {grid_search.best_params_}")
print(f"✓ Mejor MSE (CV): {-grid_search.best_score_:.4f}")

# ver todos
results_df = []
for mean_score, std_score, params in zip(
    grid_search.cv_results_['mean_test_score'],
    grid_search.cv_results_['std_test_score'],
    grid_search.cv_results_['params']
):
    print(f"{params}")
    print(f"  MSE: {-mean_score:.4f} (+/- {std_score:.4f})")
    results_df.append({
        'params': params,
        'mean_mse': -mean_score,
        'std': std_score
    })

# =========================
# 4. Mejor modelo
# =========================
best_model = grid_search.best_estimator_

print("\nEntrenando mejor modelo...")
best_model.fit(X_train, y_train)

# =========================
# 5. Evaluación
# =========================
print("\nRESULTADOS FINALES")

y_pred = best_model.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"\nMSE: {mse:.4f}")
print(f"R²: {r2:.4f}")

# =========================
# 6. Evaluación por signo (TU MÉTRICA REAL)
# =========================
def sign_eps(x, eps=0.1):
    if x > eps: return 1
    elif x < -eps: return -1
    else: return 0

sign_vec = np.vectorize(sign_eps)

acc_sign = np.mean(sign_vec(y_pred) == sign_vec(y_test))

print(f"\nAccuracy por signo: {acc_sign:.4f}")

# =========================
# 7. Ejemplos
# =========================
print("\nEjemplos:")
for i in range(5):
    print(f"Real: {y_test[i]:6.2f} | Pred: {y_pred[i]:6.2f} | OK: {sign_vec(y_pred[i]) == sign_vec(y_test[i])}")

# =========================
# 8. Guardar
# =========================
import os
os.makedirs('results', exist_ok=True)
os.makedirs('models', exist_ok=True)

results = {
    'experiment': 'exp11_grid_regression',
    'normalization': BEST_NORMALIZATION,
    'vectorization': BEST_VECTORIZATION,
    'algorithm': 'Ridge',
    'best_params': grid_search.best_params_,
    'cv_mse': -grid_search.best_score_,
    'test_mse': mse,
    'test_r2': r2,
    'sign_accuracy': acc_sign,
    'all_results': results_df
}

with open('./results/results_exp11_regression.pkl', 'wb') as f:
    pickle.dump(results, f)

with open('./models/best_model_exp11_regression.pkl', 'wb') as f:
    pickle.dump(best_model, f)

print("\n✓ Resultados guardados")