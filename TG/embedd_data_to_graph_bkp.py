import openai
import pyTigerGraph as tg


TG_URL = "http://localhost"
GRAPH_NAME = "FinancialAdvisor"

# Create TigerGraph connection
conn = tg.TigerGraphConnection(
    host=TG_URL,
    graphname=GRAPH_NAME,
    apiToken=AUTH_TOKEN
)
print("conn", conn)

# 1. DESCRIBE VERTEX Document (no USE GRAPH required)
describe_result = conn.gsql('DESCRIBE VERTEX Document')
print("DESCRIBE VERTEX Document output:\n", describe_result)

# 2. Add attribute (no USE GRAPH, must be one line)
alter_result = conn.gsql('ALTER VERTEX Document ADD ATTRIBUTE (content STRING)')
print("ALTER VERTEX output:\n", alter_result)

# 3. Deploy schema change
deploy_result = conn.gsql('RUN SCHEMA_CHANGE JOB')
print("RUN SCHEMA_CHANGE JOB output:\n", deploy_result)

# 4. Re-describe to confirm
describe_result2 = conn.gsql('DESCRIBE VERTEX Document')
print("After deployment, DESCRIBE VERTEX Document output:\n", describe_result2)