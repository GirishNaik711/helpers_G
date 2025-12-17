import pandas as pd
import pyTigerGraph as tg
from openai import OpenAI
from loguru import logger

TG_URL = "http://localhost"
GRAPH_NAME = "FinancialAdvisor"

# Create TigerGraph connection
conn = tg.TigerGraphConnection(
    host=TG_URL,
    graphname=GRAPH_NAME,
    apiToken=AUTH_TOKEN
)

client = OpenAI()  


def get_embedding(text, model="text-embedding-3-small"):
    """Generate embedding for given text using OpenAI API"""
    text = str(text).replace("\n", " ")
    logger.debug(f"Generating embedding for text: {text[:50]}...")
    response = client.embeddings.create(input=[text], model=model)
    return response.data[0].embedding

def upsert_vertex(vertex_type, primary_id, attributes):
    try:
        result = conn.upsertVertex(vertex_type, str(primary_id), attributes=attributes)
        logger.success(f"Upserted {vertex_type}: {primary_id}")
        return result
    except Exception as e:
        logger.error(f"Failed to upsert {vertex_type}({primary_id}): {e}")
        return None

def upsert_edge(src_type, src_id, tgt_type, tgt_id, edge_type, attributes):
    try:
        result = conn.upsertEdge(src_type, str(src_id), edge_type, tgt_type, str(tgt_id), attributes=attributes)
        logger.success(f"Created edge {edge_type}: {src_id} -> {tgt_id}")
        return result
    except Exception as e:
        logger.error(f"Failed {edge_type}({src_id}->{tgt_id}): {e}")
        return None

def load_advisors():
    """Load advisors from CSV into TigerGraph"""
    logger.info("Loading Advisors...")
    advisors = pd.read_csv("data/advisors.csv")
    logger.info(f"Found {len(advisors)} advisors to load")
    
    for idx, row in advisors.iterrows():
        logger.debug(f"Processing advisor {idx+1}/{len(advisors)}: {row['name']}")
        # text_for_embedding = f"Advisor: {row['name']}, Email: {row['email']}, Phone: {row['phone']}"
        # embedding = get_embedding(text_for_embedding)
        upsert_vertex("Advisor", row["advisor_id"], {
            "name": row["name"],
            "email": row["email"],
            "phone": row["phone"],
            # "embedding": embedding
        })
    logger.success(f"Completed loading {len(advisors)} advisors")

def load_clients():
    """Load clients from CSV into TigerGraph"""
    logger.info("Loading Clients...")
    clients = pd.read_csv("data/clients.csv")
    logger.info(f"Found {len(clients)} clients to load")
    
    for idx, row in clients.iterrows():
        logger.debug(f"Processing client {idx+1}/{len(clients)}: {row['name']}")
        # text_for_embedding = f"Client: {row['name']}, Email: {row['email']}, Phone: {row['phone']}"
        # embedding = get_embedding(text_for_embedding)
        
        upsert_vertex("Client", row["client_id"], {
            "name": row["name"],
            "email": row["email"],
            "phone": row["phone"],
            # "embedding": embedding
        })
        upsert_edge("Advisor", row["advisor_id"], "Client", row["client_id"], "ADVISES", {})
    logger.success(f"Completed loading {len(clients)} clients")

def load_companies():
    """Load companies/assets from CSV into TigerGraph"""
    logger.info("Loading Companies/Assets...")
    companies = pd.read_csv("data/companies.csv")
    logger.info(f"Found {len(companies)} companies to load")
    
    for idx, row in companies.iterrows():
        logger.debug(f"Processing company {idx+1}/{len(companies)}: {row['name']} ({row['ticker']})")
        # text_for_embedding = f"Assets: {row['name']}, Ticker: {row['ticker']}, Industry: {row['industry']}"
        # embedding = get_embedding(text_for_embedding)
        
        upsert_vertex("Assets", row["company_id"], {
            "name": row["name"],
            "ticker": row["ticker"],
            "industry": row["industry"],
            # "embedding": embedding
        })
    logger.success(f"Completed loading {len(companies)} companies")

def load_investments():
    """Load investments from CSV into TigerGraph"""
    logger.info("Loading Investments...")
    investments = pd.read_csv("data/investments.csv")
    logger.info(f"Found {len(investments)} investments to load")
    
    for idx, row in investments.iterrows():
        logger.debug(f"Processing investment {idx+1}/{len(investments)}: {row['investment_id']}")
        upsert_edge(
            "Client", row["client_id"],
            "Assets", row["company_id"],
            "INVESTS_IN",
            {
                "investment_id": str(row["investment_id"]),
                "amount": float(row["amount"]),
                "currency": row["currency"],
                "invested_at": row["invested_at"]
            }
        )
    logger.success(f"Completed loading {len(investments)} investments")

if __name__ == "__main__":
    logger.info("Starting data load to TigerGraph...")
    load_advisors()
    load_clients()
    load_companies()
    load_investments()
    logger.success("Data load complete!")
