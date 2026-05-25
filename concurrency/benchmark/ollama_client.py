"""Low-level HTTP helpers for talking to a local Ollama instance."""

from __future__ import annotations

import math

import httpx

from .config import EMBED_MODEL, GEN_MODEL, MAX_TOKENS, OLLAMA_BASE, TIMEOUT


def _chat_sync(
    client: httpx.Client,
    prompt: str,
    model: str = GEN_MODEL,
    max_tokens: int = MAX_TOKENS,
) -> str:
    r = client.post(
        f"{OLLAMA_BASE}/api/chat",
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"num_predict": max_tokens},
        },
        timeout=TIMEOUT,
    )
    return r.json().get("message", {}).get("content", "").strip()


async def _chat_async(
    client: httpx.AsyncClient,
    prompt: str,
    model: str = GEN_MODEL,
    max_tokens: int = MAX_TOKENS,
) -> str:
    r = await client.post(
        f"{OLLAMA_BASE}/api/chat",
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"num_predict": max_tokens},
        },
        timeout=TIMEOUT,
    )
    return r.json().get("message", {}).get("content", "").strip()


def _embed_sync(client: httpx.Client, text: str) -> list[float]:
    r = client.post(
        f"{OLLAMA_BASE}/api/embed",
        json={"model": EMBED_MODEL, "input": text},
        timeout=TIMEOUT,
    )
    return r.json().get("embeddings", [[]])[0]


async def _embed_async(client: httpx.AsyncClient, text: str) -> list[float]:
    r = await client.post(
        f"{OLLAMA_BASE}/api/embed",
        json={"model": EMBED_MODEL, "input": text},
        timeout=TIMEOUT,
    )
    return r.json().get("embeddings", [[]])[0]


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0
