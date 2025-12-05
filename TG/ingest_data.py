import os
import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

# Output folder
output_dir = "./data"
os.makedirs(output_dir, exist_ok=True)

NUM_ADVISORS = 5
NUM_COMPANIES = 10

# Generate Advisors
advisors = []
for i in range(NUM_ADVISORS):
    advisors.append({
        "advisor_id": i + 1,
        "name": fake.name(),
        "email": fake.unique.email(),
        "phone": fake.phone_number()
    })
advisors_df = pd.DataFrame(advisors)
advisors_df.to_csv(os.path.join(output_dir, "advisors.csv"), index=False)

# Generate Companies
companies = []
for i in range(NUM_COMPANIES):
    companies.append({
        "company_id": i + 1,
        "name": fake.company(),
        "ticker": fake.lexify(text="???").upper(),
        "industry": fake.job()
    })
companies_df = pd.DataFrame(companies)
companies_df.to_csv(os.path.join(output_dir, "companies.csv"), index=False)

# Generate Clients (5 per advisor)
clients = []
client_id = 1
for advisor in advisors:
    for _ in range(5): # 5 clients per advisor
        clients.append({
            "client_id": client_id,
            "name": fake.name(),
            "email": fake.unique.email(),
            "phone": fake.phone_number(),
            "advisor_id": advisor["advisor_id"]
        })
        client_id += 1
clients_df = pd.DataFrame(clients)
clients_df.to_csv(os.path.join(output_dir, "clients.csv"), index=False)

# Generate Investments (3–6 per client)
investments = []
investment_id = 1
for client in clients:
    num_investments = random.randint(3, 6)
    for _ in range(num_investments):
        company = random.choice(companies)
        investments.append({
            "investment_id": investment_id,
            "client_id": client["client_id"],
            "company_id": company["company_id"],
            "amount": round(random.uniform(1000, 100000), 2),
            "currency": random.choice(["INR", "USD", "EUR"]),
            "invested_at": (datetime.utcnow() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d")
        })
        investment_id += 1
investments_df = pd.DataFrame(investments)
investments_df.to_csv(os.path.join(output_dir, "investments.csv"), index=False)

print(f"✅ Synthetic CSVs generated in '{output_dir}' folder:")
print(f" - Advisors: {len(advisors_df)}")
print(f" - Clients: {len(clients_df)} (5 per advisor)")
print(f" - Companies: {len(companies_df)}")
print(f" - Investments: {len(investments_df)} (3–6 per client)")