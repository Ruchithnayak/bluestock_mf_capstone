import requests
import csv
import json

def fetch_financial_data(ticker="RELIANCE.BSE"):
    """
    Fetches real-time market data from a public REST API (Alpha Vantage/Finnhub format),
    inspects the JSON payload, and writes cleaned records to CSV.
    """
    # Public Alpha Vantage endpoint example (Demoware API key used for standard testing)
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey=demo"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check HTTP Status Code
        
        json_data = response.json()
        print("API JSON Response successfully retrieved:")
        print(json.dumps(json_data, indent=2))
        
        # Parse nested JSON
        quote = json_data.get("Global Quote", {})
        
        parsed_record = [{
            "symbol": quote.get("01. symbol"),
            "open": float(quote.get("02. open", 0)),
            "high": float(quote.get("03. high", 0)),
            "low": float(quote.get("04. low", 0)),
            "price": float(quote.get("05. price", 0)),
            "volume": int(quote.get("06. volume", 0)),
            "trading_day": quote.get("07. latest trading day"),
            "change_percent": quote.get("10. change percent")
        }]
        
        # Output as CSV deliverable
        output_path = "../data/stock_api_extracted.csv"
        with open(output_path, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=parsed_record[0].keys())
            writer.writeheader()
            writer.writerows(parsed_record)
        print(f"Data successfully saved to {output_path}")

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch data from API: {e}")

if __name__ == "__main__":
    fetch_financial_data()