import json
import re

from rich import print
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI
from clients import openai_client
from utils import call_openai
from PROMPTS import MASTER_AGENT_PROMPT, WORKER_AGENT_PROMPT
from tools import get_ticker_data, analyse_finance_data, perplexity_search
client = OpenAI()

class MasterAgent:
    def __init__(self):
        self.name = "MasterAgent"
        self.model = "o1-mini"

    def run(self, user_prompt):
        prompt = MASTER_AGENT_PROMPT.replace("__COMPANY_NAME__", user_prompt)
        messages = [
            {"role": "user", "content": prompt}
        ]
        response_message = call_openai(messages, client=openai_client, model=self.model)
        
        stock_info_match = re.search(r'<OUTPUT>(.*?)</OUTPUT>', response_message.content, re.DOTALL)
        if stock_info_match:
            stock_info = json.loads(stock_info_match.group(1))
            
            if isinstance(stock_info, dict) and "stock_symbol" in stock_info:
                stock_symbol = stock_info["stock_symbol"]
                print(f"Stock Symbol: {stock_symbol}")
            
        self.log(response_message.content + "\n\n")

        agent_instantiations_match = re.search(r'<OUTPUT>(.*?)</OUTPUT>', response_message.content, re.DOTALL)
        if agent_instantiations_match:
            try:
                agent_instantiations = json.loads(agent_instantiations_match.group(1))
                
                if isinstance(agent_instantiations, dict) and "agents" in agent_instantiations:
                    worker_responses = []
                    for agent in agent_instantiations["agents"]:
                        worker_agent = self.instantiate_worker(agent["Agent"], agent["Task"])
                        worker_response = worker_agent.run()
                        worker_responses.append({
                            "agent": worker_agent.name,
                            "task": agent["Task"],
                            "response": worker_response
                        })
                    
                    analyst_agent = AnalystAgent(user_prompt) 
                    analyst_response = analyst_agent.run(stock_info["stock_symbol"])
                    worker_responses.append({
                        "agent": analyst_agent.name,
                        "task": "Financial Analysis",
                        "response": analyst_response
                    })
                    self.generate_report(worker_responses, messages)
                else:
                    print("Unexpected format in agent instantiations.")
            except json.JSONDecodeError:
                print("Failed to parse JSON for agent instantiations.")
        else:
            print("No agent instantiations found in the response.")

        self.generate_report(worker_responses, messages)
    
    def log(self, message):
        print(f"[red][bold]{self.name}[/bold][/red]: {message}")
    
    def instantiate_worker(self, agent_name, task):
        if agent_name == "AnalystAgent":
            return AnalystAgent(task)
        else:
            return WorkerAgent(agent_name, task)

    
    def generate_report(self, worker_responses, messages):
        worker_responses = [f"Agent: {worker_response['agent']}\nTask: {worker_response['task']}\n\nWorker report: {worker_response['response']} \n\n\n" for worker_response in worker_responses]
        
        report_prompt = f"""
        You are a report generation agent now. 
        
        KEEP YOUR ORIGINAL TASK IN MIND. - That is still your task.
        
        Forget your past format. And generate the report directly.
        
        Look at all the past messages and tool call responses.
        
        You can no longer call new agents, all you have to do is analyze the information you have been given.
        Generate an report.
        
        
        When generating the report, you have to generate it in a way that is EXTREMELY DETAILED.
        Point to specific information in the report.
        VERY SPECIFIC, DO NOT SUMMARIZE.
        
        Make sure you write in a way that is EXTREMELY DETAILED.
        Use all the information you have been given to generate the report.
        Do not miss a single detail, and do not miss a single fact.
        Write in-depth, infer things, point to specific and VERY SPECIFIC information in the report.
        
        Do not over depend on bullet points.
        Write in a way that is EXTREMELY DETAILED.
        
        You are writing a report, and you are an expert at writing reports.
        
        Go.
        """
        messages = messages + [{"role": "user", "content": report_prompt}]
        
        self.log("Generating report...")
        
        report_message = call_openai(messages, client=openai_client, model=self.model)
        
        self.log("Report generated.")
        with open("report.md", "w") as report_file:
            report_file.write(report_message.content)
        
        return report_message.content
        
class AnalystAgent:
    def __init__(self, task):
        self.task = task
        self.name = "AnalystAgent"
        self.model = "gpt-4o"

    def run(self, stock_symbol=None):
        try:
            finance_data_filename = f"{stock_symbol}_finance_data.csv" if stock_symbol else None
            print(f"Processing finance data for {stock_symbol}...")
            full_file_path = get_ticker_data(stock_symbol, "1y", finance_data_filename)    
            if full_file_path:
                analysis_result = analyse_finance_data(full_file_path)
                print(analysis_result)
                return analysis_result
            else:
                return "Failed to process finance data due to an error."
            
        
        except IndexError as e:
            print(f"Error analyzing financial data: {e}")
            return f"An error occurred during financial analysis. Please try again with valid input."
        
        except Exception as e:
            print(f"Unexpected error analyzing financial data: {e}")
            return f"An unexpected error occurred during financial analysis: {str(e)}"



class WorkerAgent:
    def __init__(self, name, task):
        self.name = name
        self.task = task
        self.model = "gpt-4o"
        
    def run(self, max_messages=3):
        current_message_number = 0
        task = self.task
        
        prompt = WORKER_AGENT_PROMPT.replace("__TASK__", task).replace("__MESSAGE_NUMBER__", str(current_message_number))
        messages = [
            {"role": "system", "content": prompt}
        ]
        
        while current_message_number <= max_messages:
            messages[0]["content"] = WORKER_AGENT_PROMPT.replace("__TASK__", task)\
                .replace("__MESSAGE_NUMBER__", str(current_message_number))\
                .replace("__MAX_MESSAGES__", str(max_messages))
                
            response_message = call_openai(messages, client=openai_client, model=self.model, temperature=0.1)
            
            self.log(response_message.content, current_message_number)
            
            output_text = re.search(r'<OUTPUT>(.*?)</OUTPUT>', response_message.content, re.DOTALL)
            tool_call = output_text.group(1) if output_text else None
            
            if "__end_conv__" in response_message.content.lower().strip():
                break
            
            tool_call = json.loads(tool_call)
            tool_response  = self.handle_tool_call(tool_call)
            messages.append({"role": "user", "content": tool_response})
            
            if response_message.content.lower().strip() == "__end_conv__":
                break
            messages.append({"role": "assistant", "content": response_message.content})
            current_message_number += 1
        
        report = self.generate_report(messages)
        
        return report
    
    def generate_report(self, messages):
        self.log("Generating report...")
        self.log(messages)
        
        report_prompt = f"""
        You are a report generation agent now. 
        
        KEEP YOUR ORIGINAL TASK IN MIND. - That is still your task.
        
        Forget your past format. And generate the report directly.
        
        Look at all the past messages and tool call responses
        
        The report should be in a markdown format, and should be EXTREMELY DETAILED.
        You will be given a list of messages, and you will need to generate a report.
        The report should be in a markdown format, and should be EXTREMELY DETAILED.
        
        Do not miss a single detail, and do not miss a single fact.
        
        Please, be very detailed.
        Please infer the information from the past messages and tool call responses.
        Connect different dots, uncover the truth. - This is important.
        
        Create a detailed report of all your findings.
        """
        
        messages = messages + [{"role": "user", "content": report_prompt}]
        
        report_message = call_openai(messages, client=openai_client, model=self.model, temperature=0.3)
        return report_message.content
    
    def log(self, message, message_number=None):
        print(f"[green][bold]{self.name}[/bold][/green]: {message_number} - \n\n{message}\n\n")
        
    def handle_tool_call(self, tool_call):
        if tool_call["tool_name"] == "perplexity_search":
            return perplexity_search(tool_call["arguments"]['query'])
    
if __name__ == "__main__":
    master_agent = MasterAgent()
    master_agent.run("Microsoft")       
