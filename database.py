import sqlite3
from datetime import datetime

conn = sqlite3.connect("network.db", check_same_thread=False)
cursor = conn.cursor()

# Table create
cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time TEXT,
    cpu REAL,
    memory REAL,
    risk REAL,
    status TEXT
)
""")

conn.commit()


def insert_log(network, cpu, memory, prediction, risk):
    cursor.execute("""
    INSERT INTO logs (time, cpu, memory, risk, status)
    VALUES (?, ?, ?, ?, ?)
    """, (
        str(datetime.now()),
        cpu,
        memory,
        risk,
        prediction
    ))

    conn.commit()