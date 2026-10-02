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
    """Writes every LLM request and reply to the terminal and to server/logs/llm.log.

    How much is written depends on the environment variable LLM_LOG_LEVEL
    (DEBUG, INFO or WARNING, see the top of this file).
    """

    def __init__(self, name="llm"):
        """Set up the logger, and its file and terminal outputs the first time.

        Args:
            name: the name of the Python logger. All LLMLogger objects with the
                same name share one logger, so the outputs are added only once.
        """
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
        """Log a request before it is sent: one line (INFO) and the full payload (DEBUG).

        Images in the payload are replaced by a short note (see _hide_images).

        Args:
            payload: the dict that is sent to the LLM (model, messages, ...).
        """
        self.logger.info("REQUEST  -> %s", payload.get("model"))
        self.logger.debug("Request payload:\n%s", self._to_json(self._hide_images(payload)))

    def log_response(self, model, content, usage, seconds):
        """Log the model's reply: one line with time and tokens (INFO) and the full text (DEBUG).

        Args:
            model: the model ID, e.g. "openai/gpt-5-mini".
            content: the raw text the model sent back, before JSON parsing.
            usage: the token counts from the response (prompt_tokens,
                completion_tokens), or None if the provider sent none.
            seconds: how long the call took.
        """
        tokens = f"{usage.prompt_tokens} in / {usage.completion_tokens} out" if usage else "unknown"
        self.logger.info("RESPONSE <- %s | %.1f s | tokens: %s", model, seconds, tokens)
        self.logger.debug("Response content:\n%s", self._pretty(content))

    def log_rate_limited(self, model, message):
        """Log that guard 4 stopped a call before it was sent (WARNING).

        Args:
            model: the model ID the call was meant for.
            message: the rate limit message shown to the user.
        """
        self.logger.warning("RATE LIMITED -> %s | %s", model, message)

    def log_out_of_scope(self, model, reason):
        """Log that guard 3 refused a request (WARNING): not an error of the app, but worth seeing.

        Args:
            model: the model ID that refused.
            reason: the model's explanation for the user.
        """
        self.logger.warning("OUT OF SCOPE <- %s | %s", model, reason)

    def log_error(self, error, content=None):
        """Log an error of an LLM call (ERROR), and the raw reply if there was one.

        Args:
            error: the exception that happened.
            content: the raw reply text, if there was one (e.g. when it was not
                valid JSON), otherwise None.
        """
        self.logger.error("ERROR: %s: %s", type(error).__name__, error)
        if content is not None:
            self.logger.error("Raw content:\n%s", content)

    @classmethod
    def _hide_images(cls, data):
        """Return a copy of the data where every image data URL is replaced by a short note.

        A note looks like "[image/png, 69 KB]". One screenshot as base64 is
        hundreds of KB and would fill the 1 MB log file after a few calls. The
        function goes through dicts and lists inside each other (recursively).

        Args:
            data: a request payload, or any part of it (dict, list, str, ...).

        Returns:
            The same structure, with image data URLs replaced. The original is not
            changed.
        """
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
        """Turn data into readable JSON text, indented, with characters like ä or – kept as they are.

        Args:
            data: a dict, list or other value that JSON can store.

        Returns:
            The JSON text (str).
        """
        return json.dumps(data, indent=2, ensure_ascii=False)

    @classmethod
    def _pretty(cls, text):
        """Format the model's reply for the log: as indented JSON if possible, otherwise as it is.

        Args:
            text: the raw reply text (can be None).

        Returns:
            The formatted text (str).
        """
        try:
            return cls._to_json(json.loads(text))
        except (TypeError, ValueError):
            return str(text)
