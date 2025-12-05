import json
import hashlib
import pyTigerGraph as tg
from openai import OpenAI
from loguru import logger

TG_URL = "http://localhost"
GRAPH_NAME = "FinancialAdvisor"
AUTH_TOKEN = "YOUR_TG_TOKEN_HERE"  # same as in load_to_tigergraph.py

client = OpenAI()

def get_embedding(text: str, model: str = "text-embedding-3-small"):
    resp = client.embeddings.create(input=[text], model=model)
    return resp.data[0].embedding

conn = tg.TigerGraphConnection(
    host=TG_URL,
    graphname=GRAPH_NAME,
    apiToken=AUTH_TOKEN
)

def upsert_vertex(vertex_type, vertex_id, attributes):
    return conn.upsertVertex(vertex_type, vertex_id, attributes)

def load_documents(path="data/data.jsonl", do_embeddings=True):
    logger.info(f"Loading documents from {path}...")
    count = 0

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            record = json.loads(line)
            url = record.get("url", "")
            text = record.get("text", "")
            title = record.get("title", "") or url

            # stable id from url + first 64 chars of text
            raw_id = (url + text[:64]).encode("utf-8", errors="ignore")
            doc_id = hashlib.sha1(raw_id).hexdigest()

            embedding = []
            if do_embeddings and text:
                try:
                    embedding = get_embedding(text)
                except Exception as e:
                    logger.warning(f"Embedding failed for {url}: {e}")

            upsert_vertex("Document", doc_id, {
                "url": url,
                "title": title[:512],
                "text": text[:10000],  # avoid overly huge strings
                "embedding": embedding
            })

            count += 1
            if count % 50 == 0:
                logger.info(f"Inserted {count} documents...")

    logger.success(f"Completed loading {count} documents")

if __name__ == "__main__":
    load_documents()
