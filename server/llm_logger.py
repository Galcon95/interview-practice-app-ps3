# Debug log for everything sent to and received from the LLM.
# Writes to the terminal and to server/logs/llm.log (not committed to git).
#
# Turn it off or make it quieter with the environment variable LLM_LOG_LEVEL:
#   DEBUG (default) = full request and response JSON
#   INFO            = one short line per call (model, time, tokens)
#   WARNING         = only errors

import json
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path(__file__).parent / "logs"
LOG_FILE = LOG_DIR / "llm.log"
LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(message)s"


class LLMLogger:
    def __init__(self, name="llm"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(os.getenv("LLM_LOG_LEVEL", "DEBUG").upper())
        self.logger.propagate = False  # don't print everything twice via Streamlit's logger

        # Streamlit reruns the code often. Add the handlers only once,
        # otherwise every log line would appear several times.
        if not self.logger.handlers:
            LOG_DIR.mkdir(exist_ok=True)
            formatter = logging.Formatter(LOG_FORMAT)

            # File: max 1 MB per file, keeps 3 old files (llm.log.1, .2, .3)
            file_handler = RotatingFileHandler(
                LOG_FILE, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
            )
            console_handler = logging.StreamHandler()  # the terminal running Streamlit

            for handler in (file_handler, console_handler):
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)

    def log_request(self, payload):
        # payload: the dict that is sent to the LLM (model, messages, ...)
        self.logger.info("REQUEST  -> %s", payload.get("model"))
        self.logger.debug("Request payload:\n%s", self._to_json(self._hide_images(payload)))

    def log_response(self, model, content, usage, seconds):
        # content: the raw text the model sent back (before JSON parsing)
        tokens = f"{usage.prompt_tokens} in / {usage.completion_tokens} out" if usage else "unknown"
        self.logger.info("RESPONSE <- %s | %.1f s | tokens: %s", model, seconds, tokens)
        self.logger.debug("Response content:\n%s", self._pretty(content))

    def log_error(self, error, content=None):
        # content: the raw reply, if there was one (e.g. when it was not valid JSON)
        self.logger.error("ERROR: %s: %s", type(error).__name__, error)
        if content is not None:
            self.logger.error("Raw content:\n%s", content)

    @classmethod
    def _hide_images(cls, data):
        # Returns a copy of the payload where every image data URL is replaced by a short
        # note like "[image/png, 69 KB]". One screenshot as base64 is hundreds of KB and
        # would fill the 1 MB log file after a few calls.
        if isinstance(data, dict):
            return {key: cls._hide_images(value) for key, value in data.items()}
        if isinstance(data, list):
            return [cls._hide_images(item) for item in data]
        if isinstance(data, str) and data.startswith("data:") and ";base64," in data:
            header, encoded = data.split(",", 1)
            mime_type = header[5:].split(";")[0]
            return f"[{mime_type}, {len(encoded) * 3 // 4 // 1024} KB]"
        return data

    @staticmethod
    def _to_json(data):
        # ensure_ascii=False keeps characters like ä or – readable
        return json.dumps(data, indent=2, ensure_ascii=False)

    @classmethod
    def _pretty(cls, text):
        # Pretty-print the reply if it is JSON, otherwise log it as it is.
        try:
            return cls._to_json(json.loads(text))
        except (TypeError, ValueError):
            return str(text)
