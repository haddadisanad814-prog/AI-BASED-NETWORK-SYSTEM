from sklearn.ensemble import RandomForestClassifier
import joblib

# simple training data (CPU, Memory → Failure)
X = [
    [20, 30],
    [40, 50],
    [70, 80],
    [90, 95],
    [10, 20]
]

y = [0, 0, 1, 1, 0]

model = RandomForestClassifier()
model.fit(X, y)

joblib.dump(model, "failure_model.pkl")

print("✅ failure_model.pkl recreated successfully")