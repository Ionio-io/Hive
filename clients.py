import os
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI

openai_client = OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))
ppxl_client = OpenAI(api_key=os.getenv("PERPLEXITY_API_KEY"), base_url="https://api.perplexity.ai/")