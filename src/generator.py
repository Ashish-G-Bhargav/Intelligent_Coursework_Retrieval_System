import os
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
MODEL = "deepseek/deepseek-chat-v3.1:free"

def generate(prompt):
    """Generation: call the LLM and return the answer text."""
    load_dotenv(ROOT_DIR / ".env")
    api_key = os.getenv("OPEN_ROUTER_API")

    if not api_key:
        raise ValueError("OPEN_ROUTER_API environment variable is not set. Please set it in your .env file.")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()
