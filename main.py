


class MasterAgent:
    def __init__(self):
        self.judge = JudgeAgent()
        self.worker = WorkerAgent()

    def run(self, user_prompt):
        self.judge.run(user_prompt)
        self.worker.run(self.judge.tasks)




class WorkerAgent:




class AnalystAgent:

