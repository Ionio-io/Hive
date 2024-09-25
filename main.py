from rich import print

from clients import openai_client
from utils import call_openai
from PROMPTS import MASTER_AGENT_PROMPT


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


if __name__ == "__main__":
    master_agent = MasterAgent()
    master_agent.start("Apple")

