## PLAN

- [ ] Judge/Master Agent:
---- Recieve the user prompt, and break it down into smaller tasks.
---- Sequential Execution of tasks, determine what should be done first.
---- Stopping criteria, must be defined properly before starting the execution.
---- Assign the tasks to the worker agents.
---- Assess the results.



- [ ] Worker Agents:
---- Execute the tasks assigned by the Judge/Master Agent. - Only do that, do not sidestep, no exploration.
---- Report the results to the Judge/Master Agent. - Report must be precise and detailed.
---- Return the paths of further travel. - Where to look next, what are some interesting leads.
- Has access to tools/databases/knowledge:
  - Perplexity: Online search
  
  - Yahoo Finance: Stock prices
  - AssistantsAPI: Code Interpreter, Wolfram Alpha, etc.





### Worker Agents:


gpt3.5: Summarization, Basic Question Answering

gpt4: Breaking things down

claude-3.5: Amazingly good at generating reports and other writing tasks.






