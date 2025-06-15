"""Helpers to fetch real-time job-market data using Perplexity Search API.

The function `get_job_market_stats` queries Perplexity.ai with a carefully
crafted prompt asking for a JSON-only response containing:
  - open_positions: string (e.g. "15,000+")
  - average_salary: string (e.g. "$110,000 - $150,000")
  - trending_employers: array[str] of 3 employer names

If the API or JSON parsing fails, we return the same static fallback used
previously so the UI still renders a snapshot.
"""
from __future__ import annotations

import os
import json
import logging
from typing import Dict, Any

import requests

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

SEARCH_URL = "https://api.perplexity.ai/search"  # hypothetical endpoint

_DEFAULT_SNAPSHOT: Dict[str, Any] = {
    "open_positions": "5,000+",
    "average_salary": "$120,000 - $160,000",
    "trending_employers": ["Big Tech Co", "Innovative Startup", "Data Insights Inc"],
}

PROMPT_TEMPLATE = (
    "Provide current US job-market snapshot for the role '{topic}'. "
    "Return ONLY valid JSON with keys: open_positions (string), "
    "average_salary (string), trending_employers (array of 3 company names)."
)


def _call_perplexity(prompt: str, timeout: int = 45) -> str:
    """Low-level helper to hit Perplexity search completions.

    This assumes a chat-completion-like interface; tweak if API differs.
    """
    if not PERPLEXITY_API_KEY:
        raise RuntimeError("PERPLEXITY_API_KEY env var not set")

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "pplx-70b-chat",  # default free/paid model
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 300,
    }
    resp = requests.post(SEARCH_URL, headers=headers, json=payload, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    return content


def _extract_json(text: str) -> Dict[str, Any]:
    # Attempt direct parse; else strip back-ticks fences
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        if "```" in text:
            inner = text.split("```")[1]
            try:
                return json.loads(inner)
            except json.JSONDecodeError:
                pass
    raise ValueError("Unable to parse JSON from Perplexity response")


def get_job_market_stats(topic: str) -> Dict[str, Any]:
    """Return job-market stats for given topic using Perplexity search.

    Falls back to default snapshot on any failure.
    """
    if topic == "__fallback__":
        return _DEFAULT_SNAPSHOT.copy()
    prompt = PROMPT_TEMPLATE.format(topic=topic)
    try:
        raw = _call_perplexity(prompt)
        data = _extract_json(raw)
        # Basic validation
        if not all(k in data for k in ("open_positions", "average_salary", "trending_employers")):
            raise ValueError("Missing keys in Perplexity JSON")
        return data
    except Exception as exc:  # broad catch – log then fallback
        logging.warning("Perplexity job-market fetch failed: %s", exc)
        return _DEFAULT_SNAPSHOT.copy()
