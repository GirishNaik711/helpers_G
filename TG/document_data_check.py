import pyTigerGraph as tg
import sys
import pandas as pd
# We first cr
# eate a connection to the database
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
# --- Step 1: Print Document Schema ---
schema = conn.getSchema()
print("schema", schema)
doc_attrs = None
for vt in schema['VertexTypes']:
    if vt['Name'] == 'Document':
        doc_attrs = [attr['AttributeName'] for attr in vt.get('Attributes',[])]
        print("Document vertex attributes:", doc_attrs)

# --- Step 2: Retrieve Document Data ---
documents = conn.getVertices("Document", limit=10000)  # Adjust limit as needed
if not documents:
    print("No Document vertices found.")
else:
    print("Sample Document vertex:", documents[0])

# --- Step 3: Attempt to Extract and Display Content ---
# Replace 'content' with the correct attribute from your schema!
content_field = 'content'   # CHANGE THIS if your field is named differently

flattened = []
for doc in documents:
    # Grabs 'content' plus all other available fields
    flat = {'v_id': doc['v_id']}
    for attr in doc['attributes']:
        flat[attr] = doc['attributes'][attr]
    flattened.append(flat)

df = pd.DataFrame(flattened)
if content_field in df.columns:
    print("\nSample of Documents' Content Field:")
    print(df[[content_field]].head())
else:
    print(f"\nThe attribute '{content_field}' was NOT found in your Document schema or data.")
    print("Available columns are:", df.columns.tolist())
    print("Please update 'content_field' to the actual field with your document data.")

# --- Optional: Export to CSV ---
# df.to_csv("document_data.csv", index=False)



sys.exit(1)



# 3. List all vertex types (to discover schema)
vertex_types = conn.getVertexTypes()
print("hello")
print("Vertex Types:", vertex_types)

# 4. List all edge types
edge_types = conn.getEdgeTypes()
print("Edge Types:", edge_types)

# 5. Fetch example vertices (replace 'Document' if your type is different)
print("\nFetching some Document vertices...")
try:
    docs = conn.getVertices("Document")
    print("Sample Document Vertices:", docs[:2])     # Print first 2 for preview
except Exception as e:
    print(f"Could not fetch 'Document' vertices: {e}")

# # 6. If you want a DataFrame (requires pandas)
# try:
    
#     docs_df = conn.getVerticesDataFrame("Document")
#     print("Document DataFrame Preview:")
#     print(docs_df.head())
# except Exception as e:
#     print(f"Could not create DataFrame: {e}")

# sys.exit(1)
# 7. Fetch edges for a specific Document vertex (replace 'doc_id' and edge type)
try:
    vertex_type = "Document"
    document_id = "data"           # Use a real vertex primary id
    # sample_edge_type = edge_types[0] if edge_types else "EdgeTypeHere"
    # edges = conn.getEdges("Document", document_id, sample_edge_type)
    # print(f"Edges of Document {document_id}:", edges)
    doc_data = conn.getVertexData(vertex_type, document_id)
    print(f"Data for document '{document_id}':\n{doc_data}\n")
except Exception as e:
    print(f"Could not fetch edges: {e}")

# 8. General: run an installed GSQL query (optional, if you have queries installed)
# result = conn.runInstalledQuery("YourQueryName", params={})
# print("Query Result:", result)