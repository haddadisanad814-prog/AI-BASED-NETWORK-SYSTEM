import joblib, os

model = None
if os.path.exists("failure_model.pkl"):
    try:
        model = joblib.load("failure_model.pkl")
    except:
        model = None