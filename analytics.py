import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("failure_history.csv")

df["Time"] = pd.to_datetime(df["Time"])
df["Date"] = df["Time"].dt.date

daily_failures = df.groupby("Date").size()

daily_failures.plot(kind="line")
plt.title("Daily Failures")
plt.show()