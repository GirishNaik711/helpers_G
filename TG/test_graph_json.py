import pyTigerGraph as tg
import json
# We first create a connection to the database
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
conn.ai.configureGraphRAGHost(f"{TG_URL}:8000")
# res_i = conn.ai.initializeSupportAI()

print("Hi")
# Validate JSON and ingest
file_path = "data/data.jsonl"
# # --- Preview JSON for structure ---
# try:
#     with open(file_path, encoding="utf-8") as jsonfile:
#         docs = json.load(jsonfile)
#         if not docs or not isinstance(docs, list):
#             print("JSON must be a non-empty array of objects!")
#             exit(1)
#         for doc in docs:
#             print("JSON doc preview:", doc)
# except Exception as json_err:
#     print("Error reading JSON file:", json_err)
#     exit(1)
# --- Ingest the JSON into SupportAI/DocAI ---
try:
    res = conn.ai.createDocumentIngest(
        data_source="local",
        data_source_config={
            "data_path": file_path
            # No separator needed for JSON
        },
        loader_config={
            "doc_id_field": "doc_id",
            "content_field": "content",
            "doc_type": "markdown"
        },
        file_format="json",
    )
    print("Ingest response:", res)
except Exception as ingest_err:
    print("Error during document ingest:", ingest_err)
    exit(1)