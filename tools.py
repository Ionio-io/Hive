from clients import ppxl_client
import yfinance as yf
from dotenv import load_dotenv
import os
from PROMPTS import FINANCIAL_DATA_ANALYSIS_PROMPT, PERPLEXITY_MESSAGE_TOOL
from openai import OpenAI
load_dotenv()
key = os.getenv("OPEN_AI_API_KEY")
# Initialize OpenAI client and load environment variables
client = OpenAI(api_key=key)


def perplexity_search(query: str) -> str:
    messages = [
        {"role": "system", "content": PERPLEXITY_MESSAGE_TOOL},
        {"role": "user", "content": query},
    ]
    
    response = ppxl_client.chat.completions.create(
        model="llama-3.1-sonar-large-128k-online",
        messages=messages,
        temperature=0.3
    )
    
    response_text = response.choices[0].message.content
    return response_text

def get_ticker_data(ticker: str, period: str, filename: str) -> str:
    ticker_obj = yf.Ticker(ticker)
    try:
        hist = ticker_obj.history(period=period)
        subdirectory = f"Tickerdata/{ticker}"  # Create a subdirectory for the ticker data
        os.makedirs(subdirectory, exist_ok=True)
        filepath = os.path.join(subdirectory, filename)
        hist.to_csv(filepath)  # Save the historical data to CSV
        return filepath  
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None
    