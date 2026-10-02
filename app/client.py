import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

openai_client = AsyncOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)