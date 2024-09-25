from clients import ppxl_client
import yfinance as yf
from clients import openai_client

def perplexity_search(query: str) -> str:
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
        {"role": "user", "content": query}
    ]
        

    response = ppxl_client.chat.completions.create(
        model="llama-3.1-sonar-large-128k-online",
        messages=messages,
        temperature=0.3
    )
    
    response_text = response.choices[0].message.content

    return response_text

def get_finance_data(ticker: str, period: str, filename: str):
    ticker = yf.Ticker(ticker)
    try:
        hist = ticker.history(period=period)
        hist.to_csv(filename)  # Save the DataFrame to a CSV file
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None
    
    return hist


def analyse_finance_data(filename: str):
    # Upload a file with an "assistants" purpose
    file = openai_client.files.create(
    file=open(filename, "rb"),
    purpose='assistants'
    )

    # Create an assistant using the file ID
    assistant = openai_client.beta.assistants.create(
    instructions="You are a financial analyst. Your task is to analyze the financial data provided in the CSV file. You should focus on key financial metrics such as revenue, expenses, profit, and cash flow. Additionally, you should identify any trends or patterns in the data and provide insights.",
    model="gpt-4o",
    tools=[{"type": "code_interpreter"}],
    tool_resources={
        "code_interpreter": {
        "file_ids": [file.id]
        }
    }
    )

    thread = openai_client.beta.threads.create(
    messages=[
        {
        "role": "user",
        "content": "Analyse the given financial statements and provide a report with key financial metrics and explanations.",
        "attachments": [
            {
            "file_id": file.id,
            "tools": [{"type": "code_interpreter"}]
            }
        ]
        }
    ]
    )

    return thread