import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

logger = logging.getLogger("edurag.generator")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

ROOT_DIR = Path(__file__).resolve().parent.parent

# Default models
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
DEFAULT_OPENROUTER_MODEL = "deepseek/deepseek-chat-v3.1:free"


def get_llm_client():
    """
    Get configured OpenAI-compatible client and target model name.
    Prioritizes Google AI Studio Gemini API (100% free tier: 15 RPM, 1M TPM, 1,500 RPD),
    with seamless fallback to OpenRouter (DeepSeek / Llama free tier).
    """
    load_dotenv(ROOT_DIR / ".env")
    gemini_key = os.getenv("GEMINI_API_KEY")
    openrouter_key = os.getenv("OPEN_ROUTER_API")

    if gemini_key:
        model = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)
        client = OpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=gemini_key,
            timeout=35.0,
        )
        return client, model, "gemini"

    if openrouter_key:
        model = os.getenv("OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL)
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=openrouter_key,
            timeout=45.0,
        )
        return client, model, "openrouter"

    raise ValueError(
        "No LLM API key configured. Please set GEMINI_API_KEY (recommended: free from https://aistudio.google.com/) "
        "or OPEN_ROUTER_API in your .env file."
    )


def generate(prompt: str) -> str:
    """Generation: call the LLM and return the answer text."""
    client, model, provider = get_llm_client()

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        content = response.choices[0].message.content
        return (content or "").strip()
    except Exception as e:
        logger.error(f"Error calling {provider} model '{model}': {e}")
        # If Gemini fails and OpenRouter is configured, attempt automatic fallback
        if provider == "gemini":
            openrouter_key = os.getenv("OPEN_ROUTER_API")
            if openrouter_key:
                logger.info("Attempting automatic fallback to OpenRouter...")
                fb_client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=openrouter_key,
                    timeout=45.0,
                )
                fb_model = os.getenv("OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL)
                fb_resp = fb_client.chat.completions.create(
                    model=fb_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                )
                return (fb_resp.choices[0].message.content or "").strip()
        raise
