from clients import openai_client

class MasterAgent:
    def __init__(self):
        self.name = "MasterAgent"
        self.model = "o1-mini"

    def run(self, user_prompt):
        self.worker.run(user_prompt)




class WorkerAgent:
    pass