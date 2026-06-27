"""Thin wrapper around the OpenAI Chat Completions API."""

from __future__ import annotations

import logging

from django.conf import settings

logger = logging.getLogger(__name__)

# Caps to keep latency and cost predictable. Max tokens is env-configurable so it
# can be tuned to the provider account's budget without a code change.
DEFAULT_MAX_TOKENS = 500
TEMPERATURE = 0.3


class AssistantError(Exception):
    """Raised when a reply cannot be generated (missing key / provider error)."""


def generate_reply(system_prompt: str, history: list[dict]) -> str:
    """Call OpenAI with the system prompt + conversation history, return the text.

    ``history`` is a list of ``{"role": "user"|"assistant", "content": str}``.
    """
    api_key = getattr(settings, "OPENAI_API_KEY", "")
    if not api_key:
        msg = "OPENAI_API_KEY is not configured."
        raise AssistantError(msg)

    try:
        # Imported lazily so the app loads even if the dependency is absent.
        from openai import OpenAI
    except ImportError as exc:  # pragma: no cover - defensive
        msg = "The 'openai' package is not installed."
        raise AssistantError(msg) from exc

    messages = [{"role": "system", "content": system_prompt}, *history]

    try:
        base_url = getattr(settings, "OPENAI_BASE_URL", "") or None
        client = OpenAI(api_key=api_key, base_url=base_url)
        completion = client.chat.completions.create(
            model=getattr(settings, "OPENAI_MODEL", "gpt-4o-mini"),
            messages=messages,
            max_tokens=getattr(settings, "OPENAI_MAX_TOKENS", DEFAULT_MAX_TOKENS),
            temperature=TEMPERATURE,
        )
    except Exception as exc:
        logger.exception("Assistant provider call failed")
        msg = "The assistant provider call failed."
        raise AssistantError(msg) from exc

    reply = (completion.choices[0].message.content or "").strip()
    if not reply:
        msg = "The assistant returned an empty reply."
        raise AssistantError(msg)
    return reply
