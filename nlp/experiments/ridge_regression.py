import pickle
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_validate, StratifiedKFold
from sklearn.metrics import accuracy_score, roc_auc_score
import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("CLASIFICACIÓN POR SIGNO (OPTIMIZADA)")
print("="*70)

# =========================
# 1. Cargar dataset
# =========================
with open('pkl/spacy_tfidf.pkl', 'rb') as f:
    data = pickle.load(f)

X_train = data['X_train']
X_test = data['X_test']

y_train = np.array(data['y_train']).astype(float)
y_test = np.array(data['y_test']).astype(float)

# =========================
# 2. Convertir a signo
# =========================
y_train_bin = (y_train > 0).astype(int)
y_test_bin = (y_test > 0).astype(int)

print("Distribución train:", np.bincount(y_train_bin))

# =========================
# 3. Modelo
# =========================
model = LogisticRegression(max_iter=1000, n_jobs=-1)

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)

cv_results = cross_validate(
    model,
    X_train,
    y_train_bin,
    cv=cv,
    scoring=('accuracy', 'roc_auc'),
    n_jobs=-1
)

print("\nAccuracy CV:", cv_results['test_accuracy'].mean())
print("ROC-AUC CV:", cv_results['test_roc_auc'].mean())

# =========================
# 4. Entrenar final
# =========================
model.fit(X_train, y_train_bin)

# =========================
# 5. Predicción
# =========================
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

accuracy = accuracy_score(y_test_bin, y_pred)
roc = roc_auc_score(y_test_bin, y_prob)

print("\nRESULTADOS:")
print(f"Accuracy: {accuracy:.4f}")
print(f"ROC-AUC: {roc:.4f}")

# =========================
# 6. Interpretación (clave)
# =========================
print("\nEjemplos:")
for i in range(5):
    print(f"Real: {y_test[i]:6.2f} | Prob+: {y_prob[i]:.3f} | Pred: {y_pred[i]}")