from clients import ppxl_client
import yfinance as yf
from clients import openai_client
from dotenv import load_dotenv
from openai import OpenAI
import json
import time

load_dotenv()
client = OpenAI()

def perplexity_search(query: str, additional_info: str) -> str:
    system_message = """
    You are a helpful assistant that can answer questions.
    You are an expert at searching the internet for information.
    You have to search for what the user tells you in detail.
    
    Format your responses in a way that is easy to understand.
    
    Your responses are to be detailed, go very wide, and gather as much information as possible.
    If you think there are interesting things the user can learn more about, you can mention them.
    
    Please keep in mind you have to research in depth. And in-width, search for as much information as possible.
    Search for connections between different things.
    Search for the latest information.
    
    Your responses are to be detailed, go very wide, and gather as much information as possible.
    Extensive responses are encouraged.
    """
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": query},
    ]
    if additional_info:
        messages.append({"role": "assistant", "content": additional_info})
    
    response = ppxl_client.chat.completions.create(
        model="llama-3.1-sonar-large-128k-online",
        messages=messages,
        temperature=0.3
    )
    
    response_text = response.choices[0].message.content
    return response_text

def get_finance_data(ticker: str, period: str, filename: str):
    ticker = yf.Ticker(ticker)
    news = ticker.news
    with open('news_data.json', 'w') as json_file:
        json.dump(news, json_file, indent=4)
    
    try:
        hist = ticker.history(period=period)
        hist.to_csv(filename) 
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None
    
    return hist

def load_news_from_file(filename='news_data.json') -> str:
    with open(filename, 'r') as json_file:
        news_data = json.load(json_file)
    return json.dumps(news_data, indent=4)
def analyse_finance_data(filename: str, news_data: str):
    file = client.files.create(
        file=open(filename, "rb"),
        purpose='assistants'
    )

    assistant = openai_client.beta.assistants.create(
        name='Financial analyst',
        description='''You are a financial analyst. Your task is 
        to analyze the financial data provided in the CSV file. 
        You should focus on key financial metrics such as revenue,
        expenses, profit, and cash flow. Additionally,
        you should identify any trends or patterns 
        in the data and provide insights, especially considering 
        the related news provided.''', 
        model="gpt-4o",
        tools=[{"type": "code_interpreter"}],
        tool_resources={
            "code_interpreter": {
                "file_ids": [file.id]
            }
        }
    )

    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": f"Analyze the financial data provided in the CSV file and provide insights and explanations, considering the following news data: {news_data}. Create and show visualisations",  
                "attachments": [
                    {
                        "file_id": file.id,
                        "tools": [{"type": "code_interpreter"}]
                    }
                ]
            }
        ]
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )
    
    if run.status == 'completed': 
        messages = client.beta.threads.messages.list(
        thread_id=thread.id
  )
        for message in messages.data:
            if message.role == 'assistant':
                for content_block in message.content:
                    if content_block.type == 'text':
                        print(content_block.text.value)


    else:
        print(run.status)

