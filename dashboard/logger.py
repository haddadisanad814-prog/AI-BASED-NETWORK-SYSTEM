import pandas as pd
import os

def log_data(time, network, cpu, ram, prediction, risk):

    file = "network_logs.csv"

    new_data = pd.DataFrame([{
        "Time": time,
        "Network Status": network,
        "CPU Usage": cpu,
        "Memory Usage": ram,
        "AI Prediction": prediction,
        "Risk": risk
    }])

    if os.path.exists(file):
        new_data.to_csv(file, mode="a", header=False, index=False)
    else:
        new_data.to_csv(file, index=False)
        