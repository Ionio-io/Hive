import json
import re
from rich import print
from dotenv import load_dotenv
from clients import openai_client
from utils import call_openai
from openai import OpenAI
from PROMPTS import MASTER_AGENT_PROMPT, WORKER_AGENT_PROMPT, report_prompt, FINANCIAL_DATA_ANALYSIS_PROMPT
from tools import get_ticker_data, perplexity_search

load_dotenv()
client = OpenAI()

class MasterAgent:
    def __init__(self):
        self.name = "MasterAgent"
        self.model = "o1-mini"

    def run(self, user_prompt):
        prompt = MASTER_AGENT_PROMPT.replace("__COMPANY_NAME__", user_prompt)
        messages = [{"role": "user", "content": prompt}]
        response_message = call_openai(messages, client=openai_client, model=self.model)
        self.log("MasterAgent initial response received.")
        match = re.search(r'<OUTPUT>(.*?)</OUTPUT>', response_message.content, re.DOTALL)
        if match:
            raw_output = match.group(1).replace('\n', ' ').replace('\r', '').strip()
            try:
                stock_info = json.loads(raw_output)
                ticker_symbol = stock_info.get("ticker_symbol")
                print(f"Stock Symbol: {ticker_symbol}")
                worker_responses = []
                for agent_info in stock_info.get("agents", []):
                    agent_name = agent_info.get("Agent")
                    task_description = agent_info.get("Task")
                    print(f"Instantiating {agent_name} for task: {task_description}")
                    agent_instance = self.instantiate_worker(agent_name, task_description)
                    worker_response = agent_instance.run()
                    worker_responses.append({
                        "agent": agent_instance.name,
                        "task": task_description,
                        "response": worker_response
                    })
                    if agent_name == "AnalystAgent":
                        analyst_agent = AnalystAgent(user_prompt)
                        analyst_response = analyst_agent.run(ticker_symbol)
                        worker_responses.append({
                            "agent": analyst_agent.name,
                            "task": "Financial Analysis",
                            "response": analyst_response
                        })
                    self.generate_report(worker_responses, messages)
            except json.JSONDecodeError as e:
                print("Failed to parse JSON for agent instantiations.")
                print(f"Error: {str(e)}")  
        else:
            print("No agent instantiations found in the response.")
    
    def log(self, message):
        print(f"[MasterAgent]: {message}")

    def instantiate_worker(self, agent_name, task):
        return WorkerAgent(agent_name, task)

    def generate_report(self, worker_responses, messages):
        report_content = "\n\n".join(
            f"Agent: {resp['agent']}\nTask: {resp['task']}\n\nWorker report: {resp['response']}\n"
            for resp in worker_responses
        )
        report_prompt = "Compile the following information into a cohesive report:\n" + report_content
        report_message = call_openai(
            messages + [{"role": "user", "content": report_prompt}],
            client=openai_client,
            model=self.model
        )
        self.log("Report generated.")
        with open("report.md", "w") as report_file:
            report_file.write(report_message.content)
        
        return report_message.content

class AnalystAgent:
    def __init__(self, task):
        self.task = task
        self.name = "AnalystAgent"
        self.model = "gpt-4o"
        self.ticker_data_file = None  

    def run(self, ticker_symbol):
        try:
            finance_data_filename = f"{ticker_symbol}_finance_data.csv"
            print(f"[{self.name}] Fetching financial data for {ticker_symbol}...")
            self.ticker_data_file = get_ticker_data(ticker_symbol, "1y", finance_data_filename)
            if not self.ticker_data_file:
                print(f"[{self.name}] Error: Failed to retrieve data for {ticker_symbol}.")
                return "Failed to retrieve financial data."
            
            print(f"[{self.name}] Data retrieved successfully. Stored at: {self.ticker_data_file}")
            return self.analyse_finance_data(self.ticker_data_file)
        except Exception as e:
            print(f"[{self.name}] Unexpected error analyzing financial data: {e}")
            return f"An unexpected error occurred during financial analysis: {str(e)}"

    def analyse_finance_data(self, filename):
        if not filename:
            return "No data file available for analysis."

        print(f"[{self.name}] Analyzing finance data from {filename}...")
        file = client.files.create(file=open(filename, "rb"), purpose='assistants')
        assistant = client.beta.assistants.create(
            name='Financial analyst',
            description="Analyze the financial data.",
            model=self.model,
            tools=[{"type": "code_interpreter"}],
            tool_resources={"code_interpreter": {"file_ids": [file.id]}}
        )
        thread = client.beta.threads.create(messages=[{"role": "user", "content": FINANCIAL_DATA_ANALYSIS_PROMPT}])
        run = client.beta.threads.runs.create_and_poll(thread_id=thread.id, assistant_id=assistant.id)
        if run.status == 'completed':
            for message in client.beta.threads.messages.list(thread_id=thread.id).data:
                if message.role == 'assistant':
                    return message.content[0].text.value if message.content[0].type == 'text' else ""
        else:
            print(f"[{self.name}] Analysis error: {run.status}")
            return f"Error: {run.status}"
class WorkerAgent:
    def __init__(self, name, task):
        self.name = name
        self.task = task
        self.model = "gpt-4o"

    def run(self, max_messages=3):
        messages = [{"role": "system", "content": WORKER_AGENT_PROMPT.replace("__TASK__", self.task)}]
        
        for current_message_number in range(max_messages):
            response_message = call_openai(messages, client=openai_client, model=self.model, temperature=0.1)
            self.log(response_message.content, current_message_number)
            
            tool_call = re.search(r'<OUTPUT>(.*?)</OUTPUT>', response_message.content, re.DOTALL)
            if tool_call:
                tool_response = self.handle_tool_call(json.loads(tool_call.group(1)))
                messages.append({"role": "user", "content": tool_response})
            
            if "__end_conv__" in response_message.content.lower().strip():
                break
            
            messages.append({"role": "assistant", "content": response_message.content})
        
        return self.generate_report(messages)

    def generate_report(self, messages):
        report_message = call_openai(
            messages + [{"role": "user", "content": report_prompt}],
            client=openai_client,
            model=self.model,
            temperature=0.3
        )
        return report_message.content

    def log(self, message, message_number=None):
        print(f"[green][bold]{self.name}[/bold][/green]: {message_number} - {message}")

    def handle_tool_call(self, tool_call):
        if tool_call["tool_name"] == "perplexity_search":
            return perplexity_search(tool_call["arguments"]['query'])


if __name__ == "__main__":
    master_agent = MasterAgent()
    master_agent.run("IBM")
