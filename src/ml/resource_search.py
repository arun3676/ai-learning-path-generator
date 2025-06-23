"""OpenAI-powered resource search helper.

This module queries the OpenAI Chat Completion endpoint to retrieve
real, high-quality learning resources (videos, articles, docs) that a user
can click to continue learning. It returns a simple list of dictionaries so
upstream code can map them into `ResourceItem` Pydantic objects.

If the `OPENAI_API_KEY` environment variable is missing, or the API call
fails, we fall back to a single placeholder so the rest of the app
continues to work.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Dict, List

import openai

# Initialize OpenAI with any key available at import time.
# We will refresh this inside each call to ensure the latest env value is used.
openai.api_key = os.getenv("OPENAI_API_KEY")


def _stub_resources() -> List[Dict[str, str]]:
    """Return a static placeholder when real search is unavailable."""
    return [
        {
            "type": "article",
            "url": "https://example.com/placeholder-resource",
            "description": "Add your OpenAI API key to see real learning resources.",
        }
    ]


def search_resources(query: str, k: int = 3, timeout: int = 45) -> List[Dict[str, str]]:
    """Search OpenAI and return up to *k* learning-resource dicts.

    Each dict has keys: `type`, `url`, `description`.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logging.info("OPENAI_API_KEY not set; returning stub resources")
        return _stub_resources()
    # Ensure we use the freshest key for every request
    openai.api_key = api_key

    prompt = (
        "Return ONLY valid JSON array (no markdown) containing the top "
        f"{k} publicly accessible learning resources for the topic: '{query}'. "
        "For each item include keys: type (video, article, etc.), url, description."
    )

    try:
        completion = openai.ChatCompletion.create(
            model=os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo"),
            messages=[
                {"role": "system", "content": "You are a helpful research assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=400,
            request_timeout=timeout,
        )
        content = completion.choices[0].message.content.strip()

        resources: List[Dict[str, str]] = json.loads(content)
        # Basic sanitisation & trimming
        cleaned: List[Dict[str, str]] = []
        for item in resources[:k]:
            cleaned.append(
                {
                    "type": item.get("type", "article"),
                    "url": item.get("url", ""),
                    "description": item.get("description", ""),
                }
            )
        return cleaned or _stub_resources()
    except Exception as exc:  # broad catch – log then stub
        logging.warning("OpenAI resource search failed: %s", exc)
        return _stub_resources()
