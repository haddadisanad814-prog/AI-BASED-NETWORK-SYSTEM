import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import random

st.title("🌐 Network Topology Map")

# Nodes
nodes = {
    "Router": "healthy",
    "Switch": "warning",
    "Server": "healthy",
    "PC1": "failure",
    "PC2": "healthy"
}

# Graph create
G = nx.Graph()

connections = [
    ("Router", "Switch"),
    ("Switch", "Server"),
    ("Switch", "PC1"),
    ("Switch", "PC2")
]

G.add_edges_from(connections)

# Color logic
color_map = []

for node in G.nodes():
    status = nodes.get(node, "healthy")

    if status == "healthy":
        color_map.append("green")
    elif status == "warning":
        color_map.append("orange")
    else:
        color_map.append("red")

# Draw graph
fig, ax = plt.subplots()
nx.draw(G, with_labels=True, node_color=color_map, node_size=2500, font_size=10)

st.pyplot(fig)