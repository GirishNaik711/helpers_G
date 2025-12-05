import openai
import pyTigerGraph as tg

# # === OpenAI (v2.x) - Get Embedding ===
# client = openai.OpenAI()
input_text = "This is your document text to be embedded."
# response = client.embeddings.create(
#     input=input_text,
#     model="text-embedding-ada-002"
# )
# embedding = response.data[0].embedding
embedding = [-0.011309836059808731, 0.017004577443003654, -0.006803158670663834, -0.011489041149616241, -0.005644962191581726]

print("Sample embedding values:", embedding[:5])
# === TIGERGRAPH Part: Store Document + Embedding ===

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

vertex_type = "Document"
doc_id = "test_sheet"

# Upsert the vertex with both the raw text and the embedding vector
res = conn.upsertVertex(
    vertex_type,
    doc_id,
    {
        "content": input_text,
        # "embedding": embedding  # Embedding as a LIST<FLOAT> property in TigerGraph
    }
)
print("Upsert result:", res)

# === OPTIONAL: Retrieve it back and display ===

doc_data = conn.getVertexData(vertex_type, doc_id)
if isinstance(doc_data, list) and doc_data:
    doc_data = doc_data[0]
retrieved_emb = doc_data.get('attributes', {}).get('embedding')
print("Retrieved embedding (first 5 floats):", retrieved_emb[:5] if retrieved_emb else None)