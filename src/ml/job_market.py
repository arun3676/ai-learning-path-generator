"""Helpers to fetch real-time job-market data using OpenAI API.

The function `get_job_market_stats` queries OpenAI with a carefully
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

import openai

# Initialize OpenAI with any key available at import time.
# We will refresh this inside each call to ensure the latest env value is used.
openai.api_key = os.getenv("OPENAI_API_KEY")

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


def _call_openai(prompt: str, timeout: int = 45) -> str:
    """Low-level helper to hit OpenAI chat completions."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY env var not set")
    
    # Ensure we use the freshest key for every request
    openai.api_key = api_key

    completion = openai.ChatCompletion.create(
        model=os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo"),
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=300,
        request_timeout=timeout,
    )
    content = completion.choices[0].message.content
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
    raise ValueError("Unable to parse JSON from OpenAI response")


def get_job_market_stats(topic: str) -> Dict[str, Any]:
    """Return job-market stats for given topic using OpenAI search.

    Falls back to default snapshot on any failure.
    """
    if topic == "__fallback__":
        return _DEFAULT_SNAPSHOT.copy()
    prompt = PROMPT_TEMPLATE.format(topic=topic)
    try:
        raw = _call_openai(prompt)
        data = _extract_json(raw)
        # Basic validation
        if not all(k in data for k in ("open_positions", "average_salary", "trending_employers")):
            raise ValueError("Missing keys in OpenAI JSON")
        return data
    except Exception as exc:  # broad catch – log then fallback
        logging.warning("OpenAI job-market fetch failed: %s", exc)
        return _DEFAULT_SNAPSHOT.copy()
