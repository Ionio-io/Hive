from tavily import TavilyClient
from dotenv import load_dotenv
import os

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

def call_openai(messages, tools):
    pass

def call_tavily_search(query):
    tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    response = tavily_client.search(query=query)

    results = response.results
    text = ""
    
    for result in results:
        title = result["title"]
        content = result["content"]
        text += f"{title.upper()}\n{content}\n\n"

    return text