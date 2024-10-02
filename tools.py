from clients import ppxl_client
import yfinance as yf
from clients import openai_client
from dotenv import load_dotenv
from openai import OpenAI
import os
from PROMPTS import FINANCIAL_DATA_ANALYSIS_PROMPT, system_message_tools

load_dotenv()
client = OpenAI()

def perplexity_search(query: str) -> str:
    messages = [
        {"role": "system", "content": system_message_tools},
        {"role": "user", "content": query},
    ]
    
    response = ppxl_client.chat.completions.create(
        model="llama-3.1-sonar-large-128k-online",
        messages=messages,
        temperature=0.3
    )
    
    response_text = response.choices[0].message.content
    return response_text

def get_ticker_data(ticker: str, period: str, filename: str):
    ticker_obj = yf.Ticker(ticker)
    try:
        hist = ticker_obj.history(period=period)
        subdirectory = f"Tickerdata/{ticker}" ### creating a folder, sub folder with the name of the ticker _< storing its stock trends
        os.makedirs(subdirectory, exist_ok=True)
        filepath = os.path.join(subdirectory, filename)
        hist.to_csv(filepath)
        return filepath  
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def analyse_finance_data(filename: str):
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
        in the data and provide insights''', 
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
                "content": FINANCIAL_DATA_ANALYSIS_PROMPT,
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
