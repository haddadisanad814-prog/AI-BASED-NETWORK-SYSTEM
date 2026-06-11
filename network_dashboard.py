import matplotlib.pyplot as plt
import matplotlib.animation as animation
from system_status import status
import time

# -----------------------------
# NODE POSITIONS (Cisco Map)
# -----------------------------
nodes = {
    "Router": (0, 2),
    "Switch": (2, 2),
    "Server": (2, 0),
    "PC1": (4, 2),
    "PC2": (4, 0)
}

# -----------------------------
# COLOR LOGIC
# -----------------------------
def get_color(state):
    if state == "healthy":
        return "green"
    elif state == "warning":
        return "orange"
    else:
        return "red"

# -----------------------------
# DRAW FUNCTION
# -----------------------------
def update(frame):
    plt.clf()

    plt.title("🌐 Cisco Style Network Topology (Live)")

    # Draw connections
    connections = [
        ("Router", "Switch"),
        ("Switch", "Server"),
        ("Switch", "PC1"),
        ("Switch", "PC2")
    ]

    for a, b in connections:
        x1, y1 = nodes[a]
        x2, y2 = nodes[b]
        plt.plot([x1, x2], [y1, y2], "gray")

    # Draw nodes
    for node, (x, y) in nodes.items():
        state = status.get(node, "healthy")
        color = get_color(state)

        plt.scatter(x, y, s=800, c=color)
        plt.text(x, y + 0.2, f"{node}\n{state}", ha="center")

    plt.xlim(-1, 5)
    plt.ylim(-1, 3)
    plt.axis("off")

# -----------------------------
# RUN ANIMATION
# -----------------------------
fig = plt.figure()
ani = animation.FuncAnimation(fig, update, interval=1000)

plt.show()