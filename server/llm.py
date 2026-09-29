# Everything that talks to the LLM provider lives here.
# We use OpenRouter, which speaks the same API as OpenAI, so we use the openai package.
# The API key is read from server/.env and never sent to the front end.

import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from server.llm_logger import LLMLogger

load_dotenv(Path(__file__).parent / ".env")  # puts the values from server/.env into os.environ

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "openai/gpt-5-mini"


class LLMClient:
    def __init__(self, model=DEFAULT_MODEL):
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY is missing. Add it to server/.env.")
        self.client = OpenAI(base_url=OPENROUTER_BASE_URL, api_key=api_key)
        self.model = model
        self.log = LLMLogger()

    def complete_json(self, system_prompt, user_prompt):
        # Sends one request and returns the model's reply as a Python dict.
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},  # ask the model for valid JSON
        }
        self.log.log_request(payload)

        content = None
        start = time.perf_counter()
        try:
            response = self.client.chat.completions.create(**payload)  # ** unpacks the dict
            content = response.choices[0].message.content
            self.log.log_response(self.model, content, response.usage, time.perf_counter() - start)
            return json.loads(content)
        except Exception as error:
            self.log.log_error(error, content)
            raise  # pass the error on, so the page can still show it
