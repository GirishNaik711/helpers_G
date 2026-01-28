# Financial Insights POC

Simple POC for generating financial insights based on account data.

## Project Structure

```
cc-v3/
├── app.py              # FastAPI endpoints
├── llm.py              # Anthropic Claude integration
├── market_data.py      # Alpha Vantage market data
├── streamlit_app.py    # Streamlit UI
├── static_top_tickers.txt
├── requirements.txt
└── .env.example
```

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create `.env` file with your API keys:
   ```
   ANTHROPIC_API_KEY=your_key
   ALPHAVANTAGE_API_KEY=your_key
   ```

## Running

1. Start FastAPI server:
   ```bash
   uvicorn app:app --reload
   ```

2. Start Streamlit UI (in another terminal):
   ```bash
   streamlit run streamlit_app.py
   ```

## Endpoints

- `POST /generate` - For users with balance (uses their tickers)
- `POST /zero_balance_suggestion` - For zero-balance users (uses static tickers)

## Flow

1. Upload Excel file with account data
2. Select an account_id from dropdown
3. Click "Generate Insights"
   - If `current_balance == 0`: Shows static top ticker suggestions
   - If `current_balance > 0`: Generates personalized insight using their holdings
