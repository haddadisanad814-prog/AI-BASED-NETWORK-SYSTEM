import pandas as pd

data = pd.read_csv("network_logs.csv")

print("===== DAILY REPORT =====")

print("Total Records :", len(data))

print("Average CPU :", round(data["CPU Usage"].mean(), 2))

print("Average Memory :", round(data["Memory Usage"].mean(), 2))

print("Failures Detected :",
      len(data[data["AI Prediction"] == "Failure"]))