import pyTigerGraph as tg
import json


TG_URL = "http://localhost"
GRAPH_NAME = "FinancialAdvisor"
AUTH_TOKEN = "ivemac9lptlmiam54il9oh91hub0hgoh"

# Create TigerGraph connection
conn = tg.TigerGraphConnection(
    host=TG_URL,
    graphname=GRAPH_NAME,
    apiToken=AUTH_TOKEN
)
print("conn", conn)
# --- Fetch graph schema ---
schema = conn.getSchema()
print("Hello")
vertex_types = [vt["Name"] for vt in schema["VertexTypes"]]
edge_types = [et["Name"] for et in schema["EdgeTypes"]]

# --- Fetch all vertex data ---
all_vertices = {}
for vtype in vertex_types:
    print(f"Fetching all vertices for type: {vtype}")
    try:
        all_vertices[vtype] = conn.getVertices(vtype, limit=1000000)  # Increase limit as needed
    except Exception as e:
        print(f"Error fetching vertices for type {vtype}: {e}")
        all_vertices[vtype] = []

# --- Fetch all edge data ---
all_edges = {}
for etype in edge_types:
    print(f"Fetching all edges for type: {etype}")
    try:
        all_edges[etype] = conn.getEdgesByType(etype, limit=1000000)  # Increase limit as needed
    except Exception as e:
        print(f"Error fetching edges for type {etype}: {e}")
        all_edges[etype] = []

print("\n=== SAMPLE VERTEX DATA ===")
for vtype in vertex_types:
    print(f"\nType: {vtype}, Number found: {len(all_vertices[vtype])}")
    # if all_vertices[vtype]:
    #     print(json.dumps(all_vertices[vtype][0], indent=2))  # show a sample vertex

print("\n=== SAMPLE EDGE DATA ===")
for etype in edge_types:
    print(f"\nType: {etype}, Number found: {len(all_edges[etype])}")
    # if all_edges[etype]:
    #     print(json.dumps(all_edges[etype][0], indent=2))  # show a sample edge

# Write data to json files ---
with open("all_vertices.json", "w") as f:
    json.dump(all_vertices, f)
with open("all_edges.json", "w") as f:
    json.dump(all_edges, f)