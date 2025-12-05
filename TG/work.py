import pyTigerGraph as tg
import json

# --- Settings ---
TG_URL = "http://localhost"            # Use :9000 for REST++ on local/TigerGraph VM
GRAPH_NAME = "FinancialAdvisor"
# USERNAME = "tigergraph"                     # If you need to generate token
# PASSWORD = "tigergraph"                  # Replace with your TigerGraph password

# --- Create TigerGraph connection ---
conn = tg.TigerGraphConnection(
    host=TG_URL,
    graphname=GRAPH_NAME,
    apiToken="ivemac9lptlmiam54il9oh91hub0hgoh"
)

# --- Generate API token (valid for 24 hours by default) ---
# try:
#     AUTH_TOKEN = conn.getToken(PASSWORD)[0]
# except Exception as e:
#     print(f"Token generation failed: {e}")
#     raise
# conn.apiToken = AUTH_TOKEN

# --- Test connection ---
try:
    schema = conn.getSchema()
except Exception as e:
    print(f"Unable to fetch schema. Check connection, URL, and token. Error: {e}")
    raise

print("Connected to TigerGraph. Schema fetched.")

vertex_types = [vt["Name"] for vt in schema["VertexTypes"]]
edge_types = [et["Name"] for et in schema["EdgeTypes"]]

# --- Fetch all vertex data ---
all_vertices = {}
for vtype in vertex_types:
    print(f"Fetching all vertices for type: {vtype}")
    try:
        all_vertices[vtype] = conn.getVertices(vtype, limit=1000000)
    except Exception as e:
        print(f"Error fetching vertices for type {vtype}: {e}")
        all_vertices[vtype] = []

# --- Fetch all edge data ---
all_edges = {}
for etype in edge_types:
    print(f"Fetching all edges for type: {etype}")
    try:
        all_edges[etype] = conn.getEdgesByType(etype, limit=1000000)
    except Exception as e:
        print(f"Error fetching edges for type {etype}: {e}")
        all_edges[etype] = []

print("\n=== SAMPLE VERTEX DATA ===")
for vtype in vertex_types:
    print(f"\nType: {vtype}, Number found: {len(all_vertices[vtype])}")

print("\n=== SAMPLE EDGE DATA ===")
for etype in edge_types:
    print(f"\nType: {etype}, Number found: {len(all_edges[etype])}")

# --- Write data to json files ---
with open("all_vertices.json", "w") as f:
    json.dump(all_vertices, f)
with open("all_edges.json", "w") as f:
    json.dump(all_edges, f)