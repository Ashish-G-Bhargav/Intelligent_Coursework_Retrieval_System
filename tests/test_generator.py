"""
Test suite for LLM generator client selection and fallback.
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from generator import get_llm_client


class TestGenerator(unittest.TestCase):

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_keys_raises_value_error(self):
        """Verify clear ValueError when neither GEMINI_API_KEY nor OPEN_ROUTER_API is set."""
        with patch("generator.load_dotenv"):
            with self.assertRaises(ValueError) as ctx:
                get_llm_client()
            self.assertIn("GEMINI_API_KEY", str(ctx.exception))

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test-gemini-key"}, clear=True)
    def test_gemini_client_prioritized(self):
        """Verify Google AI Studio Gemini is selected as primary when key is present."""
        with patch("generator.load_dotenv"):
            client, model, provider = get_llm_client()
            self.assertEqual(provider, "gemini")
            self.assertEqual(model, "gemini-2.5-flash")
            self.assertIn("generativelanguage.googleapis.com", str(client.base_url))

    @patch.dict(os.environ, {"OPEN_ROUTER_API": "test-openrouter-key"}, clear=True)
    def test_openrouter_fallback_when_gemini_absent(self):
        """Verify OpenRouter is selected when only OPEN_ROUTER_API is set."""
        with patch("generator.load_dotenv"):
            client, model, provider = get_llm_client()
            self.assertEqual(provider, "openrouter")
            self.assertIn("openrouter.ai", str(client.base_url))


if __name__ == "__main__":
    unittest.main()

