import pyTigerGraph as tg
import json
# from openai import OpenAI
# from loguru import logger

TG_URL = "http://localhost"
GRAPH_NAME = "FinancialAdvisor"
AUTH_TOKEN = "ivemac9lptlmiam54il9oh91hub0hgoh"

# Create TigerGraph connection
conn = tg.TigerGraphConnection(
    host=TG_URL,
    graphname=GRAPH_NAME,
    apiToken=AUTH_TOKEN
)

vertex_types = ["Advisor", "Client", "Assets"]

# all_vertices = {}

# for vtype in vertex_types:
#     data = conn.getVertices(vtype, limit=1000000)  # Use a very high limit
#     all_vertices[vtype] = data

# print(all_vertices)

schema = conn.getSchema()
vertex_types = [vt["Name"] for vt in schema["VertexTypes"]]
edge_types = [et["Name"] for et in schema["EdgeTypes"]]

# 2. Get all vertices for each vertex type
all_vertices = {}
for vtype in vertex_types:
    print(f"Fetching vertices for {vtype}...")
    try:
        all_vertices[vtype] = conn.getVertices(vtype, limit=100000)
    except Exception as e:
        print(f"Error fetching {vtype}: {e}")
        all_vertices[vtype] = []

# 3. Get all edges for each edge type
all_edges = {}
for etype in edge_types:
    print(f"Fetching edges for {etype}...")
    try:
        all_edges[etype] = conn.getEdgesByType(etype, limit=100000)
    except Exception as e:
        print(f"Error fetching {etype}: {e}")
        all_edges[etype] = []

# 4. Print out a summary (or export as needed)
print("\n=== Vertices Summary ===")
for vtype in vertex_types:
    print(f"{vtype}: {len(all_vertices[vtype])} vertices")

print("\n=== Edges Summary ===")
for etype in edge_types:
    print(f"{etype}: {len(all_edges[etype])} edges")

# Optional: Write to file (uncomment if needed)
with open("vertices.json", "w") as f:
    json.dump(all_vertices, f)
with open("edges.json", "w") as f:
    json.dump(all_edges, f)