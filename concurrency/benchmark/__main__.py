"""Entry point: python -m benchmark  or  python concurrency/06_ollama_concurrency_benchmark.py

Requires Python 3.11+  |  pip install httpx matplotlib
"""

import argparse

from .sim import run_simulate
from .uc_ollama import run_ollama

_GUIDE = """
╔══════════════════════════════════════════════════════════════════════════════╗
║           CONCURRENCY DECISION GUIDE FOR AI / LLM APPLICATIONS             ║
╠══════════════════╦══════════════════════╦═══════════════════════════════════╣
║  Task            ║  Right tool          ║  AI/ML examples                  ║
╠══════════════════╬══════════════════════╬═══════════════════════════════════╣
║  LLM API N×      ║  asyncio.gather()    ║  OpenAI / Anthropic / Ollama     ║
║  (independent)   ║  + httpx.AsyncClient ║  Batch generation, fanout        ║
╠══════════════════╬══════════════════════╬═══════════════════════════════════╣
║  LLM API N×      ║  asyncio.Semaphore   ║  Respect provider rate limits    ║
║  (rate-limited)  ║  + asyncio.gather()  ║  Cap concurrent requests         ║
╠══════════════════╬══════════════════════╬═══════════════════════════════════╣
║  Local inference ║  ProcessPoolExecutor ║  sentence-transformers, Whisper  ║
║  (CPU-bound)     ║  run_in_executor()   ║  CLIP, tokenisation, FAISS       ║
╠══════════════════╬══════════════════════╬═══════════════════════════════════╣
║  Embed N docs    ║  asyncio.gather()    ║  Ollama / OpenAI / Cohere embed  ║
║  (via API)       ║  + httpx.AsyncClient ║  Build vector store for RAG      ║
╠══════════════════╬══════════════════════╬═══════════════════════════════════╣
║  Legacy sync lib ║  ThreadPoolExecutor  ║  boto3, psycopg2, sync ML SDKs   ║
║  (blocking I/O)  ║  run_in_executor()   ║  GIL released during I/O waits   ║
╠══════════════════╬══════════════════════╬═══════════════════════════════════╣
║  RAG pipeline    ║  Async I/O +         ║  embed → retrieve → generate     ║
║  (end-to-end)    ║  in-process CPU      ║  retrieval stays in-process      ║
╚══════════════════╩══════════════════════╩═══════════════════════════════════╝

  GOLDEN RULES
  1. LLM API calls are I/O — always use async, never threads for speed.
  2. Local inference is CPU — always use ProcessPool, not async.
  3. Never call time.sleep() or requests.get() inside async def.
  4. Create httpx.AsyncClient once — not per request (avoids TCP overhead).
  5. Add asyncio.Semaphore before going to production (rate-limit safety).
"""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Python concurrency benchmark for AI/API workloads"
    )
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Run synthetic benchmarks (no Ollama required)",
    )
    parser.add_argument(
        "--plot", action="store_true", help="Save a speedup chart as PNG"
    )
    args = parser.parse_args()

    if args.simulate:
        run_simulate(args.plot)
    else:
        run_ollama(args.plot)

    print(_GUIDE)


if __name__ == "__main__":
    main()
