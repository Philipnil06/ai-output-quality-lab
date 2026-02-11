from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, List

from openai import OpenAI, APIError


DEFAULT_MODEL = "gpt-4.1-mini"
DEFAULT_JUDGE_MODEL = "gpt-4.1-mini"


@dataclass
class OpenAIClientConfig:
    api_key: str | None
    model: str = DEFAULT_MODEL
    timeout: float = 30.0


class LLMClient:
    def __init__(self, config: OpenAIClientConfig):
        if not config.api_key:
            raise ValueError("OPENAI_API_KEY is required for real generation.")
        self.client = OpenAI(api_key=config.api_key)
        self.model = config.model
        self.timeout = config.timeout

    def generate(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        attempt = 0
        while True:
            attempt += 1
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=600,
                    timeout=self.timeout,
                )
                return resp.choices[0].message.content or ""
            except APIError:
                if attempt >= 2:
                    raise
                time.sleep(1.0)

