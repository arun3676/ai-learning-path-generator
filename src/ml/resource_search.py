"""Perplexity-powered resource search helper.

This module queries the Perplexity Chat Completion endpoint to retrieve
real, high-quality learning resources (videos, articles, docs) that a user
can click to continue learning. It returns a simple list of dictionaries so
upstream code can map them into `ResourceItem` Pydantic objects.

If the `PERPLEXITY_API_KEY` environment variable is missing, or the API call
fails, we fall back to a single placeholder so the rest of the app
continues to work.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Dict, List

import requests

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

# NOTE: The public docs currently describe the chat-completions endpoint.
# We reuse the same endpoint that our job-market helper uses.
SEARCH_URL = "https://api.perplexity.ai/chat/completions"


def _stub_resources() -> List[Dict[str, str]]:
    """Return a static placeholder when real search is unavailable."""
    return [
        {
            "type": "article",
            "url": "https://example.com/placeholder-resource",
            "description": "Sample resource – add your PERPLEXITY_API_KEY for real links.",
        }
    ]


def search_resources(query: str, k: int = 3, timeout: int = 45) -> List[Dict[str, str]]:
    """Search Perplexity and return up to *k* learning-resource dicts.

    Each dict has keys: `type`, `url`, `description`.
    """
    if not PERPLEXITY_API_KEY:
        logging.info("PERPLEXITY_API_KEY not set; returning stub resources")
        return _stub_resources()

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
    }

    prompt = (
        "Return ONLY valid JSON array (no markdown) containing the top "
        f"{k} publicly accessible learning resources for the topic: '{query}'. "
        "For each item include keys: type (video, article, etc.), url, description."
    )

    payload = {
        "model": os.getenv("PERPLEXITY_MODEL", "pplx-7b-online"),
        "messages": [
            {"role": "system", "content": "You are a helpful research assistant."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 400,
    }

    try:
        resp = requests.post(SEARCH_URL, headers=headers, json=payload, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"].strip()

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
        logging.warning("Perplexity resource search failed: %s", exc)
        return _stub_resources()
