import pyTigerGraph as tg
import json, csv
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
res_i = conn.ai.initializeSupportAI()

print("Hi")
# csv_file_path = "data/test_sheet.csv"
# # --- Preview CSV for newline and basic structure ---
# try:
#     with open(csv_file_path, newline='', encoding="utf-8") as csvfile:
#         reader = csv.DictReader(csvfile)
#         rows = list(reader)
#         if not rows:
#             print("CSV file is empty or headers are missing!")
#             exit(1)
#         for row in rows:
#             print("CSV row preview:", row)
# except Exception as csv_err:
#     print("Error reading CSV file:", csv_err)
#     exit(1)

# --- Ingest the CSV into SupportAI/DocAI ---
try:
    res = conn.ai.createDocumentIngest(
    data_source="server",
    data_source_config={"folder_path": "/code/data"},  # Docker volume mount path
    loader_config={},  # Customize as needed
    file_format="multi"  # Implies directory ingestion of multiple files
)
    print("Ingest response:", res)
    conn.ai.runDocumentIngest(res["load_job_id"], res["data_source_id"], res["data_path"])
    print("Ingest job run successfully.")
except Exception as ingest_err:
    print("Error during document ingest:", ingest_err)
    exit(1)