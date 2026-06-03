import pickle
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "dataset.csv"
MODEL_PATH = BASE_DIR / "model.pkl"

# Load dataset
print("Loading dataset...")
df = pd.read_csv(DATA_PATH)
df = df.drop(columns=["index"], errors='ignore')

# Prepare features and target
X = df.drop(columns=["Result"])
y = df["Result"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)

pipeline = Pipeline([
    ("scaler", StandardScaler()),
    (
        "model",
        RandomForestClassifier(
            n_estimators=250,
            max_depth=18,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),
    ),
])

print("Training model...")
pipeline.fit(X_train, y_train)

print("Evaluating model...")
y_pred = pipeline.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, pos_label=1)
recall = recall_score(y_test, y_pred, pos_label=1)
f1 = f1_score(y_test, y_pred, pos_label=1)

print(f"Accuracy: {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1 Score: {f1:.4f}")
print("Classification Report:")
print(classification_report(y_test, y_pred, digits=4))
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print(f"Saving model to {MODEL_PATH}...")
with open(MODEL_PATH, "wb") as f:
    pickle.dump(pipeline, f)

print("Training completed.")
