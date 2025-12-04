# load_to_tigergraph.py
import os
import json
from datetime import datetime
from loguru import logger

import pandas as pd
import pyTigerGraph as tg
from openai import OpenAI

# ----------------- TigerGraph connection -----------------
TG_URL = "http://localhost"
GRAPH_NAME = "FinancialAdvisor"
AUTH_TOKEN = "REPLACE_WITH_YOUR_TOKEN"

conn = tg.TigerGraphConnection(
    host=TG_URL,
    graphname=GRAPH_NAME,
    apiToken=AUTH_TOKEN,
)

# ----------------- OpenAI embeddings -----------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def get_embedding(text: str, model: str = "text-embedding-3-small"):
    if client is None:
        # Return empty list if no key – keeps loaders working.
        return []
    text = str(text).replace("\n", " ")
    logger.debug(f"Generating embedding for text: {text[:60]}...")
    resp = client.embeddings.create(input=[text], model=model)
    return resp.data[0].embedding


# ----------------- Upsert helpers -----------------
def upsert_vertex(vertex_type: str, primary_id, attributes: dict):
    try:
        res = conn.upsertVertex(vertex_type, str(primary_id), attributes=attributes)
        logger.debug(f"Upserted {vertex_type}({primary_id})")
        return res
    except Exception as e:
        logger.error(f"Failed to upsert {vertex_type}({primary_id}): {e}")
        return None


def upsert_edge(src_type: str, src_id, tgt_type: str, tgt_id, edge_type: str, attributes: dict):
    try:
        res = conn.upsertEdge(
            src_type,
            str(src_id),
            edge_type,
            tgt_type,
            str(tgt_id),
            attributes=attributes,
        )
        logger.debug(f"Upserted {edge_type} {src_type}({src_id}) -> {tgt_type}({tgt_id})")
        return res
    except Exception as e:
        logger.error(
            f"Failed to upsert {edge_type} {src_type}({src_id}) -> {tgt_type}({tgt_id}): {e}"
        )
        return None


DATA_DIR = "data"

# ----------------- CSV loaders -----------------
def load_advisors(with_embeddings: bool = False):
    logger.info("Loading Advisors from CSV...")
    df = pd.read_csv(os.path.join(DATA_DIR, "advisors.csv"))
    logger.info(f"Found {len(df)} advisors to load")

    for idx, row in df.iterrows():
        attrs = {
            "name": row["name"],
            "email": row["email"],
            "phone": row["phone"],
        }
        if with_embeddings:
            text = f"Advisor: {row['name']}, Email: {row['email']}, Phone: {row['phone']}"
            attrs["embedding"] = get_embedding(text)

        upsert_vertex("Advisor", row["advisor_id"], attrs)

    logger.success(f"Completed loading {len(df)} Advisors")


def load_clients(with_embeddings: bool = False):
    logger.info("Loading Clients from CSV...")
    df = pd.read_csv(os.path.join(DATA_DIR, "clients.csv"))
    logger.info(f"Found {len(df)} clients to load")

    for idx, row in df.iterrows():
        attrs = {
            "name": row["name"],
            "email": row["email"],
            "phone": row["phone"],
        }
        if with_embeddings:
            text = (
                f"Client: {row['name']}, Email: {row['email']}, Phone: {row['phone']}"
            )
            attrs["embedding"] = get_embedding(text)

        upsert_vertex("Client", row["client_id"], attrs)
        # ADVISES edge Advisor -> Client
        upsert_edge(
            "Advisor",
            row["advisor_id"],
            "Client",
            row["client_id"],
            "ADVISES",
            {},
        )

    logger.success(f"Completed loading {len(df)} Clients + ADVISES edges")


def load_assets(with_embeddings: bool = False):
    logger.info("Loading Assets/Companies from CSV...")
    df = pd.read_csv(os.path.join(DATA_DIR, "companies.csv"))
    logger.info(f"Found {len(df)} companies to load")

    for idx, row in df.iterrows():
        attrs = {
            "name": row["name"],
            "ticker": row["ticker"],
            "industry": row["industry"],
        }
        if with_embeddings:
            text = (
                f"Asset: {row['name']}, Ticker: {row['ticker']}, "
                f"Industry: {row['industry']}"
            )
            attrs["embedding"] = get_embedding(text)

        # Schema uses vertex type Assets
        upsert_vertex("Assets", row["company_id"], attrs)

    logger.success(f"Completed loading {len(df)} Assets")


def load_investments():
    logger.info("Loading INVESTS_IN edges from CSV...")
    df = pd.read_csv(os.path.join(DATA_DIR, "investments.csv"))
    logger.info(f"Found {len(df)} investments to load")

    for idx, row in df.iterrows():
        attrs = {
            "investment_id": str(row["investment_id"]),
            "amount": float(row["amount"]),
            "currency": row["currency"],
            "invested_at": row["invested_at"],
        }
        upsert_edge(
            "Client",
            row["client_id"],
            "Assets",
            row["company_id"],
            "INVESTS_IN",
            attrs,
        )

    logger.success(f"Completed loading {len(df)} INVESTS_IN edges")


# ----------------- JSON loaders for prebuilt graph -----------------
def load_vertices_json(path: str = os.path.join(DATA_DIR, "all_vertices.json")):
    """Expect list of { '_type': <vertex>, '_id': <pk>, 'attributes': {...} }"""
    logger.info(f"Loading vertices from JSON: {path}")
    with open(path, "r", encoding="utf-8") as f:
        vertices = json.load(f)

    total = len(vertices)
    logger.info(f"Found {total} vertices")

    for idx, v in enumerate(vertices, start=1):
        v_type = v["_type"]
        v_id = v["_id"]
        attrs = v.get("attributes", {}) or {}
        upsert_vertex(v_type, v_id, attrs)

        if idx % 100 == 0 or idx == total:
            logger.debug(f"Loaded {idx}/{total} vertices")

    logger.success("Completed loading vertices from JSON")


def load_edges_json(path: str = os.path.join(DATA_DIR, "all_edges.json")):
    """Expect list of { 'from_type','from_id','to_type','to_id','e_type','attributes' }"""
    logger.info(f"Loading edges from JSON: {path}")
    with open(path, "r", encoding="utf-8") as f:
        edges = json.load(f)

    total = len(edges)
    logger.info(f"Found {total} edges")

    for idx, e in enumerate(edges, start=1):
        upsert_edge(
            e["from_type"],
            e["from_id"],
            e["to_type"],
            e["to_id"],
            e["e_type"],
            e.get("attributes", {}) or {},
        )

        if idx % 100 == 0 or idx == total:
            logger.debug(f"Loaded {idx}/{total} edges")

    logger.success("Completed loading edges from JSON")


# ----------------- main -----------------
if __name__ == "__main__":
    logger.info("Starting data load to TigerGraph...")

    # Option 1: load from CSVs
    # load_advisors(with_embeddings=True)
    # load_clients(with_embeddings=True)
    # load_assets(with_embeddings=True)
    # load_investments()

    # Option 2: load from pre-generated JSON graph
    load_vertices_json()
    load_edges_json()

    logger.success("Data load complete!")


    CREATE VERTEX WebPage (
  PRIMARY_ID id STRING,
  url STRING,
  text STRING,
  images STRING,
  links STRING
  -- , embedding LIST<FLOAT>
);
