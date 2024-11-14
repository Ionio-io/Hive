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


from openai import OpenAI

client = OpenAI()

def analyze_data(filename, model, prompt):
    try:
        print(f"Analyzing finance data from {filename}...")
        file = client.files.create(file=open(filename, "rb"), purpose='assistants')

        assistant = client.beta.assistants.create(
            name="Data visualizer",
            description="You analyze data present in .csv files, understand trends, and come up with data visualizations relevant to those trends. You also share a brief text summary of the trends observed, while also creating hypotheses about future trends and showing the metrics via visualizations.",
            model=model, 
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
                    "content": prompt,  # Use the passed prompt parameter
                    "attachments": [
                        {
                            "file_id": file.id,
                            "tools": [{"type": "code_interpreter"}]
                        }
                    ]
                }
            ]
        )

        # Run the assistant and wait for completion
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id,
            model=model,
            tools=[{"type": "code_interpreter"}, {"type": "file_search"}]
        )

        if run.status == 'completed': 
            messages = client.beta.threads.messages.list(thread_id=thread.id)

            # Get the response from the first message
            r = messages.data[0]

            # Download the content of the image file if it exists
            if r.content and r.content[0].type == 'image_file':
                api_response = client.files.content(r.content[0].image_file.file_id)

                if api_response:
                    content = api_response.content
                    with open('image.png', 'wb') as f:
                        f.write(content)
                    print('Visualizations have been downloaded successfully. Kindly refer to the same.')

            # Print all assistant messages
            for message in messages.data:
                if message.role == 'assistant' and message.content and message.content[0].type == 'text':
                    print(message.content[0].text.value)

            return "Analysis completed successfully."

        else:
            return run.status

    except Exception as e:
        print(f"[analyze_data] Unexpected error analyzing financial data: {e}")
        return f"An unexpected error occurred during financial analysis: {str(e)}"


def main():
    # Define parameters
    ticker = "AAPL"
    period = "1y"  # Get data for the last 1 year
    filename = "AAPL_data.csv"
    model = "gpt-4o"  # Use OpenAI's text-davinci-002 model
    prompt = FINANCIAL_DATA_ANALYSIS_PROMPT  # Use the predefined prompt for financial data analysis

    # Get ticker data and save it to a CSV file
    filepath = get_ticker_data(ticker, period, filename)
    if filepath is not None:
        # Analyze the data using OpenAI
        analysis_result = analyze_data(filepath, model, prompt)
        print(analysis_result)
    else:
        print("Failed to get ticker data.")

if __name__ == "__main__":
    main()