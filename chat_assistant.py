from system_status import status
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------- TRAIN DATA ----------------
training_data = [
    "network status kya hai",
    "internet chal raha hai",
    "wifi working hai kya",
    "router status batao",
    "switch ok hai kya",
    "server status kya hai",
    "server down hai kya",
    "system health check",
    "pc status batao",
    "help kya kar sakte ho"
]

labels = [
    "NETWORK",
    "NETWORK",
    "NETWORK",
    "NETWORK",
    "NETWORK",
    "SERVER",
    "SERVER",
    "SYSTEM",
    "SYSTEM",
    "HELP",
    "highest cpu"
    "highest ram"
    "network score"
    "failure prediction"
    "sla status"
    "device count"
]

# ---------------- NLP MODEL ----------------
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(training_data)


def detect_intent(text):

    text_vec = vectorizer.transform([text])
    similarity = cosine_similarity(text_vec, X)

    index = similarity.argmax()
    score = similarity[0][index]

    # confidence threshold
    if score < 0.25:
        return "UNKNOWN"

    return labels[index]


def handle_query(user_input):

    intent = detect_intent(user_input.lower())

    # ---------------- NETWORK ----------------
    if intent == "NETWORK":
        return {
            "response": f"""
📡 SMART NETWORK REPORT

Internet : {status.get('Router')}
Router   : {status.get('Router')}
Switch   : {status.get('Switch')}
PC1      : {status.get('PC1')}
"""
        }

    # ---------------- SERVER ----------------
    if intent == "SERVER":

        server_status = status.get("Server")

        explanation = ""
        if server_status == "failure":
            explanation = "⚠ Server overloaded ya network issue ho sakta hai"
        elif server_status == "warning":
            explanation = "⚡ Server high load pe hai"
        else:
            explanation = "✅ Server normal hai"

        return {
            "response": f"""
🖥 SMART SERVER REPORT

Status: {server_status}
Reason: {explanation}
"""
        }

    # ---------------- SYSTEM ----------------
    if intent == "SYSTEM":
        return {
            "response": f"""
💻 SYSTEM AI REPORT

PC1     : {status.get('PC1')}
Server  : {status.get('Server')}
Router  : {status.get('Router')}
Switch  : {status.get('Switch')}
"""
        }

    # ---------------- HELP ----------------
    if intent == "HELP":
        return {
            "response": """
🤖 I am Smart Network AI Assistant

You can ask me:
- network status kya hai
- server down hai kya
- system health check
- wifi working hai kya
"""
        }

    # ---------------- UNKNOWN ----------------
    return {
        "response": """
😅 Main exact samajh nahi paya

👉 Try asking:
- network status
- server status
- system health
"""
    }