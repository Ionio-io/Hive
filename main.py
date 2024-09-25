from rich import print

from clients import openai_client
from utils import call_openai
from PROMPTS import MASTER_AGENT_PROMPT, WORKER_AGENT_PROMPT, PERPLEXITY_SEARCH_PROMPT
from tools import perplexity_search

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
        return response_message.content
    
    def log(self, message):
        print(f"[red][bold]{self.name}[/bold][/red]: {message}")
    
    def instantiate_worker(self):
        return WorkerAgent()
    
    def start(self, user_prompt):
        self.log(f"Analyzing company: {user_prompt}")
        response_message = self.run(user_prompt)
        print(response_message)
        

class WorkerAgent:
    def __init__(self, name, prompt):
        self.name = name
        self.prompt = prompt
        
    def run(self, task, max_messages=3):
        prompt = WORKER_AGENT_PROMPT.replace("__TASK__", task).replace("__MESSAGE_NUMBER__", str(self.message_number))
        messages = [
            {"role": "user", "content": prompt}
        ]
        current_message_number = 0
        while current_message_number < max_messages:
            response_message = call_openai(messages, client=openai_client, model=self.model)
            if response_message.content.lower().strip() == "__end_conv__":
                break
            messages.append({"role": "assistant", "content": response_message.content})
            self.message_number += 1
        return response_message.content
        
        


if __name__ == "__main__":
    master_agent = MasterAgent()
    master_agent.start("Apple")

