# Everything that talks to the LLM provider lives here.
# We use OpenRouter, which speaks the same API as OpenAI, so we use the openai package.
# The API key is read from server/.env and never sent to the front end.

import base64
import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from server.llm_logger import LLMLogger

load_dotenv(Path(__file__).parent / ".env")  # puts the values from server/.env into os.environ

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Models the user can choose from in the settings.
# "temperature": whether the model supports it (GPT-5 models are reasoning
# models and ignore it). Prices are USD per 1 million input / output tokens.
MODELS = {
    "openai/gpt-5-mini": {"label": "GPT-5 mini ($0.25 / $2)", "temperature": False},
    "openai/gpt-5-nano": {"label": "GPT-5 nano ($0.05 / $0.40)", "temperature": False},
    "openai/gpt-4.1-mini": {"label": "GPT-4.1 mini ($0.40 / $1.60)", "temperature": True},
    "openai/gpt-4o-mini": {"label": "GPT-4o mini ($0.15 / $0.60)", "temperature": True},
    "google/gemini-2.5-flash": {"label": "Gemini 2.5 Flash ($0.30 / $2.50)", "temperature": True},
    "anthropic/claude-haiku-4.5": {"label": "Claude Haiku 4.5 ($1 / $5)", "temperature": True},
}
DEFAULT_MODEL = "openai/gpt-5-mini"
DEFAULT_TEMPERATURE = 0.7
# GPT-5 models count their hidden "thinking" in max_tokens too, so keep this generous.
DEFAULT_MAX_TOKENS = 4000


def parse_json(text):
    # Turns the model's reply into a dict. GPT models return pure JSON, but some
    # models (e.g. Claude) wrap it in a Markdown code block: ```json { ... } ```
    # So we take only the part from the first "{" to the last "}".
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("The model's reply contains no JSON object.")
    return json.loads(text[start : end + 1])


class LLMClient:
    def __init__(self, model=DEFAULT_MODEL, temperature=DEFAULT_TEMPERATURE, max_tokens=DEFAULT_MAX_TOKENS):
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY is missing. Add it to server/.env.")
        self.client = OpenAI(base_url=OPENROUTER_BASE_URL, api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.log = LLMLogger()

    def complete_json(self, system_prompt, user_prompt, images=None):
        # Sends one request and returns the model's reply as a Python dict.
        # images: optional list of (data, mime_type), e.g. [(png_bytes, "image/png")].
        #         Only for models that can see images (vision models).
        user_content = user_prompt
        if images:
            # With images, the message content is a list of parts: the text, then each image
            # as a data URL ("data:image/png;base64,iVBOR..."), the format the OpenAI API expects.
            user_content = [{"type": "text", "text": user_prompt}]
            for data, mime_type in images:
                data_url = f"data:{mime_type};base64,{base64.b64encode(data).decode()}"
                user_content.append({"type": "image_url", "image_url": {"url": data_url}})

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "response_format": {"type": "json_object"},  # ask the model for valid JSON
            "max_tokens": self.max_tokens,
        }
        if MODELS.get(self.model, {}).get("temperature"):
            payload["temperature"] = self.temperature  # only sent if the model supports it
        self.log.log_request(payload)

        content = None
        start = time.perf_counter()
        try:
            response = self.client.chat.completions.create(**payload)  # ** unpacks the dict
            content = response.choices[0].message.content
            self.log.log_response(self.model, content, response.usage, time.perf_counter() - start)
            if response.choices[0].finish_reason == "length":
                raise RuntimeError(
                    f"The reply was cut off at {self.max_tokens} max tokens. "
                    "Increase 'Max tokens' in the sidebar settings."
                )
            return parse_json(content)
        except Exception as error:
            self.log.log_error(error, content)
            raise  # pass the error on, so the page can still show it
