import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier

print("===== TRAINING AI MODEL =====")

# Load dataset
data = pd.read_csv("network_logs.csv")

# Clean data
data = data.dropna()

# Convert AI Prediction to numbers
data["AI Prediction"] = data["AI Prediction"].map({
    "Normal": 0,
    "Failure": 1
})

# Remove invalid rows
data = data.dropna()

# Features
X = data[["CPU Usage", "Memory Usage"]]

# Target
y = data["AI Prediction"]

# Model
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=8,
    random_state=42
)

# Train
model.fit(X, y)

# Save
joblib.dump(model, "failure_model.pkl")

print("✅ Model Trained Successfully!")
print("✅ failure_model.pkl Created")