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

from server.guards.rate_limit import check_rate_limit
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


class RateLimitError(ValueError):
    """Raised when too many LLM calls are made in a short time (guard 4).

    A ValueError, so the pages show it like any other bad input.
    """


class OutOfScopeError(ValueError):
    """Raised when the model refuses a request as outside the app's scope (guard 3).

    A ValueError, so the pages show it like any other bad input.

    Attributes:
        reason: the model's short explanation for the user.
    """

    def __init__(self, reason):
        """Create the error with the message "Out of scope: <reason>".

        Args:
            reason: the model's short explanation, from its reply
                {"out_of_scope": true, "reason": "..."}.
        """
        super().__init__(f"Out of scope: {reason}")
        self.reason = reason


def parse_json(text):
    """Turn the model's reply text into a Python dict.

    GPT models return pure JSON, but some models (e.g. Claude) wrap it in a
    Markdown code block (```json { ... } ```), so only the part from the first
    "{" to the last "}" is read.

    Args:
        text: the raw reply text of the model.

    Returns:
        The reply as a dict.

    Raises:
        ValueError: the text contains no JSON object, or the JSON is not valid
            (json.JSONDecodeError is a ValueError).
    """
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("The model's reply contains no JSON object.")
    return json.loads(text[start : end + 1])


class LLMClient:
    """Sends requests to an LLM through OpenRouter and returns JSON replies.

    Every request is checked by the rate limit first (guard 4), logged by
    LLMLogger, and checked for an out-of-scope reply (guard 3).

    Usage:
        reply = LLMClient(**settings).complete_json(system_prompt, user_prompt)
    """

    def __init__(self, model=DEFAULT_MODEL, temperature=DEFAULT_TEMPERATURE, max_tokens=DEFAULT_MAX_TOKENS):
        """Prepare a client for one model.

        Args:
            model: the OpenRouter model ID, e.g. "openai/gpt-5-mini" (see MODELS).
            temperature: how creative the replies are (0 = always the same answer).
                Only sent to models that support it (see MODELS).
            max_tokens: the most tokens the reply may have. Reasoning models
                (GPT-5) count their hidden thinking too, so keep it high.

        Raises:
            RuntimeError: OPENROUTER_API_KEY is not set in server/.env or in the
                Windows environment variables.
        """
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY is missing. Add it to server/.env.")
        self.client = OpenAI(base_url=OPENROUTER_BASE_URL, api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.log = LLMLogger()

    def complete_json(self, system_prompt, user_prompt, images=None):
        """Send one request to the model and return its reply as a dict.

        Steps: rate limit check, build the request, log it, send it, log the
        reply, parse the JSON, check for an out-of-scope reply.

        Args:
            system_prompt: the instructions for the model, from load_prompt().
            user_prompt: the user's input, e.g. the role and level, or a job description.
            images: optional list of (data, mime_type) pairs, e.g.
                [(png_bytes, "image/png")]. Only for models that can see images
                (vision models).

        Returns:
            The model's reply as a dict, in the format its system prompt asks for.

        Raises:
            RateLimitError: too many calls in a short time; the request was not sent.
            OutOfScopeError: the model refused the request as out of scope.
            RuntimeError: the reply was cut off at max_tokens.
            ValueError: the reply is not valid JSON.
            openai.APIError: the request failed (e.g. network problem, wrong API key).
        """
        error = check_rate_limit()  # guard 4, before the paid call
        if error:
            self.log.log_rate_limited(self.model, error)
            raise RateLimitError(error)

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
            reply = parse_json(content)
        except Exception as error:
            self.log.log_error(error, content)
            raise  # pass the error on, so the page can still show it

        # Guard 3: every system prompt ends with prompts/guardrail.md, which tells the model
        # to reply {"out_of_scope": true, "reason": ...} instead of doing an off-topic task.
        if reply.get("out_of_scope") is True:
            reason = reply.get("reason") or "This app only helps with interview preparation for IT jobs."
            self.log.log_out_of_scope(self.model, reason)
            raise OutOfScopeError(reason)
        return reply
