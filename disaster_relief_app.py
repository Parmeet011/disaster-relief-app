import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx
import random

# ----------------------
# Helper: Dijkstra Shortest Path
# ----------------------
def dijkstra(graph, start):
    import heapq
    distances = {node: float("inf") for node in graph}
    distances[start] = 0
    pq = [(0, start)]
    
    while pq:
        curr_dist, node = heapq.heappop(pq)
        if curr_dist > distances[node]:
            continue
        for neighbor, weight in graph[node]:
            distance = curr_dist + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(pq, (distance, neighbor))
    return distances

# ----------------------
# Relief Allocation Logic
# ----------------------
def allocate_and_route(areas, total_resources, graph, base):
    severity_weight = {"High": 3, "Medium": 2, "Low": 1}
    distances = dijkstra(graph, base)

    # Compute score per area
    area_scores = []
    for name, pop, sev in areas:
        score = pop * severity_weight[sev]
        dist = distances.get(name, 9999)
        area_scores.append((score, dist, name, pop, sev))
    
    area_scores.sort(key=lambda x: (-x[0], x[1]))

    food, water, medicine = total_resources
    total_score = sum(score for score, _, _, _, _ in area_scores)

    allocations = []
    for score, dist, name, pop, sev in area_scores:
        if total_score == 0:
            break
        f = int((score / total_score) * food)
        w = int((score / total_score) * water)
        m = int((score / total_score) * medicine)
        allocations.append((name, f, w, m, dist, sev, pop))
    return allocations

# ----------------------
# Streamlit App
# ----------------------
st.title("🚨 Disaster Relief Resource Allocation App")

st.sidebar.header("⚙️ Input Parameters")
num_areas = st.sidebar.slider("Number of Areas", 2, 6, 3)
food = st.sidebar.slider("Total Food Packets", 500, 2000, 1000, 100)
water = st.sidebar.slider("Total Water Bottles", 500, 2000, 800, 100)
medicine = st.sidebar.slider("Total Medicine Units", 200, 1000, 500, 50)

# Randomly generate areas
areas = []
severities = ["High", "Medium", "Low"]
for i in range(num_areas):
    name = f"Area{i+1}"
    pop = random.randint(100, 1000)
    sev = random.choice(severities)
    areas.append((name, pop, sev))

# Example graph (road network)
graph = {"Base": []}
for i in range(num_areas):
    name = f"Area{i+1}"
    dist = random.randint(5, 30)
    graph["Base"].append((name, dist))
    graph[name] = [("Base", dist)]

allocations = allocate_and_route(areas, (food, water, medicine), graph, "Base")

# Show inputs
st.subheader("📍 Affected Areas")
for a in areas:
    st.write(f"**{a[0]}** → Population: {a[1]}, Severity: {a[2]}")

# Show allocation
st.subheader("📦 Allocation Plan")
for a in allocations:
    st.write(f"- {a[0]} (Pop: {a[6]}, Sev: {a[5]}) → Food={a[1]}, Water={a[2]}, Medicine={a[3]} | Distance={a[4]} km")

# Plot Graph
st.subheader("🛣️ Road Network")
G = nx.Graph()
for node, edges in graph.items():
    for neighbor, dist in edges:
        G.add_edge(node, neighbor, weight=dist)

pos = nx.spring_layout(G, seed=42)
plt.figure(figsize=(6, 4))
nx.draw(G, pos, with_labels=True, node_size=2000, font_size=10)
labels = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
st.pyplot(plt)

# Plot Allocation Bar Chart
st.subheader("📊 Resource Allocation per Area")
areas_names = [a[0] for a in allocations]
food_alloc = [a[1] for a in allocations]
water_alloc = [a[2] for a in allocations]
med_alloc = [a[3] for a in allocations]

plt.figure(figsize=(6, 4))
bar_width = 0.25
x = range(len(areas_names))

plt.bar(x, food_alloc, width=bar_width, label="Food")
plt.bar([p + bar_width for p in x], water_alloc, width=bar_width, label="Water")
plt.bar([p + 2*bar_width for p in x], med_alloc, width=bar_width, label="Medicine")

plt.xticks([p + bar_width for p in x], areas_names)
plt.ylabel("Allocated Resources")
plt.legend()
st.pyplot(plt)
