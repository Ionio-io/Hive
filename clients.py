import os
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI

openai_client = OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))