import pickle
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_validate
from sklearn.metrics import classification_report, confusion_matrix, f1_score
import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("EXPERIMENTO 14: LIWC + SIN STOPWORDS (BINARIO POR SIGNO)")
print("="*70)

# =========================
# 1. Cargar dataset
# =========================
print("\n1. Cargando dataset...")
with open('pkl/liwc_no_stopwords_binary.pkl', 'rb') as f:
    data = pickle.load(f)

X_train = data['X_train']
X_test = data['X_test']

y_train = np.array(data['y_train']).astype(float)
y_test = np.array(data['y_test']).astype(float)

print(f"Train: {X_train.shape}")
print(f"Test: {X_test.shape}")

# =========================
# 🔥 CONVERSIÓN CLAVE
# =========================
y_train_bin = (y_train > 0).astype(int)
y_test_bin  = (y_test > 0).astype(int)

print(f"\nDistribución clases train:")
print(f"Negativos: {(y_train_bin == 0).sum()}")
print(f"Positivos: {(y_train_bin == 1).sum()}")

# =========================
# 2. Modelo
# =========================
model = LogisticRegression(max_iter=1000, random_state=0, n_jobs=-1)

# =========================
# 3. Cross-validation
# =========================
print("\n2. Cross-validation (5-fold)...")

cv_results = cross_validate(
    model,
    X_train,
    y_train_bin,
    cv=5,
    scoring='f1',  # 🔥 ya es binario
    return_train_score=True,
    n_jobs=-1
)

print(f"\nF1 por fold: {cv_results['test_score']}")
print(f"✓ F1 promedio: {cv_results['test_score'].mean():.4f}")

# =========================
# 4. Entrenamiento final
# =========================
print("\n3. Entrenando modelo final...")
model.fit(X_train, y_train_bin)

# =========================
# 5. Evaluación
# =========================
print("\nRESULTADOS FINALES")

y_pred = model.predict(X_test)

f1_test = f1_score(y_test_bin, y_pred)

print(f"\nF1 TEST: {f1_test:.4f}")

print("\nClassification Report:")
print(classification_report(y_test_bin, y_pred, digits=4))

print("Confusion Matrix:")
print(confusion_matrix(y_test_bin, y_pred))

# =========================
# 6. Guardar
# =========================
results = {
    'experiment': 'exp14_binary_sign',
    'normalization': 'liwc_no_stopwords',
    'vectorization': 'binary',
    'algorithm': 'LogisticRegression',
    'cv_f1_mean': cv_results['test_score'].mean(),
    'test_f1': f1_test
}

with open('./results/results_exp14_binary.pkl', 'wb') as f:
    pickle.dump(results, f)

print("\n✓ Resultados guardados en results_exp14_binary.pkl")