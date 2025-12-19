import requests

API_KEY = ''  # Replace with your API key
base_url = 'https://api.benzinga.com/api/v1/analyst/insights'
params = {
    'token': API_KEY,
    'symbols': 'AAPL,MSFT,GOOG'   # Add your desired stock symbols (comma-separated)
}

response = requests.get(base_url, params=params)
print("response", response.json())

# Save response to text file
with open('api_response.txt', 'w') as f:
    f.write(str(response.json()))

if response.status_code == 200:
    data = response.json()
    for insight in data.get('insights', []):
        symbol = insight.get('symbol')
        rating = insight.get('rating')
        price_target = insight.get('price_target')
        print(f"Symbol: {symbol}, Rating: {rating}, Price Target: {price_target}")
 