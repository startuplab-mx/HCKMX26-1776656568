import pickle
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score, make_scorer
import warnings
warnings.filterwarnings('ignore')

# CONFIG
BEST_NORMALIZATION = 'liwc'
BEST_VECTORIZATION = 'tfidf'

print("="*70)
print("EXPERIMENTO: RANDOM FOREST + GRID SEARCH (REGRESIÓN)")
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

y_train = np.array(data['y_train']).astype(float)
y_test = np.array(data['y_test']).astype(float)

print(f"Train: {X_train.shape}")
print(f"Test: {X_test.shape}")

# =========================
# 2. Métrica de signo (clave)
# =========================
def sign_eps(x, eps=0.1):
    if x > eps: return 1
    elif x < -eps: return -1
    else: return 0

def sign_accuracy_metric(y_true, y_pred):
    y_true_s = np.array([sign_eps(x) for x in y_true])
    y_pred_s = np.array([sign_eps(x) for x in y_pred])
    return np.mean(y_true_s == y_pred_s)

sign_scorer = make_scorer(sign_accuracy_metric)

# =========================
# 3. Modelo base
# =========================
model = RandomForestRegressor(
    random_state=0,
    n_jobs=-1
)

# =========================
# 4. Grid de hiperparámetros
# =========================
param_grid = {
    'n_estimators': [100, 200],
    'max_depth': [None, 30, 50],
    'min_samples_split': [2, 5],
    'min_samples_leaf': [1, 2],
    'max_features': ['sqrt']
}

# =========================
# 5. Grid Search
# =========================
print("\n2. Ejecutando Grid Search...")
print("   (Puede tardar bastante...)")

grid_search = GridSearchCV(
    model,
    param_grid,
    cv=5,
    scoring={
        'mse': 'neg_mean_squared_error',
        'sign': sign_scorer
    },
    refit='sign',  # 🔥 optimiza lo que te importa
    verbose=2,
    n_jobs=-1
)

grid_search.fit(X_train, y_train)

# =========================
# 6. Resultados
# =========================
print("\n" + "="*70)
print("RESULTADOS GRID SEARCH")
print("="*70)

print(f"\n✓ Mejores hiperparámetros: {grid_search.best_params_}")
print(f"✓ Mejor score (sign accuracy CV): {grid_search.best_score_:.4f}")

# =========================
# 7. Modelo final
# =========================
best_model = grid_search.best_estimator_

print("\nEntrenando modelo final...")
best_model.fit(X_train, y_train)

# =========================
# 8. Evaluación
# =========================
print("\nRESULTADOS FINALES")

y_pred = best_model.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
sign_acc = sign_accuracy_metric(y_test, y_pred)

print(f"\nMSE: {mse:.4f}")
print(f"R²: {r2:.4f}")
print(f"Accuracy por signo: {sign_acc:.4f}")

# =========================
# 9. Ejemplos
# =========================
print("\nEjemplos:")
for i in range(5):
    print(f"Real: {y_test[i]:6.2f} | Pred: {y_pred[i]:6.2f} | OK: {sign_eps(y_test[i]) == sign_eps(y_pred[i])}")

# =========================
# 10. Guardar
# =========================
import os
os.makedirs('results', exist_ok=True)
os.makedirs('models', exist_ok=True)

results = {
    'experiment': 'rf_grid_regression',
    'best_params': grid_search.best_params_,
    'cv_sign_score': grid_search.best_score_,
    'test_mse': mse,
    'test_r2': r2,
    'test_sign_accuracy': sign_acc
}

with open('./results/results_rf_grid.pkl', 'wb') as f:
    pickle.dump(results, f)

with open('./models/best_rf_model.pkl', 'wb') as f:
    pickle.dump(best_model, f)

print("\n✓ Resultados guardados en results_rf_grid.pkl")
print("✓ Modelo guardado en best_rf_model.pkl")