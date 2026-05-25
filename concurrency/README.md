# Python Concurrency for AI Engineers

Benchmarks and visualisations accompanying the Medium article
**"Python Concurrency for AI Engineers — What Actually Matters"**.

## Structure

```
concurrency/
  benchmark/           — benchmark suite (UC1–UC4 real Ollama + B1–B4 simulated)
    config.py          — constants and sample data
    types.py           — BenchResult dataclass + print helpers
    ollama_client.py   — low-level HTTP helpers (chat, embed, cosine)
    uc_ollama.py       — UC1 ticket triage · UC2 embeddings · UC3 dual-model · UC4 RAG
    sim.py             — B1 I/O · B2 CPU · B3 real HTTP · B4 hybrid (no Ollama needed)
    viz.py             — speedup bar chart
    __main__.py        — CLI entry point + decision guide

  visualize/           — publication-ready Gantt and waterfall charts (requires Ollama)
    config.py          — Ollama config, colour palette, sample data
    types.py           — JobSpan, StrategyResult dataclasses
    runners.py         — instrumented runners (record per-job start/end for Gantt)
    charts.py          — figure1_io_gantt … figure5_summary
    __main__.py        — CLI entry point

  images/
    fig1_io_gantt.png    — Gantt: support ticket triage
    fig2_cpu_gantt.png   — Gantt: CPU GIL trap
    fig3_embed_gantt.png — Gantt: knowledge base embedding
    fig4_rag_waterfall.png — RAG pipeline waterfall
    fig5_summary.png     — grand summary bar chart
  MEDIUM_ARTICLE.md    — full article source
  requirements.txt
```

## Quick Start

```bash
# Python 3.11+
pip install httpx matplotlib
```

### Benchmark (no Ollama needed)

```bash
cd concurrency
python3 -m benchmark --simulate
```

### Benchmark (real Ollama)

```bash
ollama pull phi3.5
ollama pull nomic-embed-text
ollama pull mistral

cd concurrency
python3 -m benchmark
```

### Regenerate charts

```bash
cd concurrency
python3 -m visualize --save
```

## Concurrency decision guide

| Task | Right tool | Why |
|------|-----------|-----|
| LLM API calls N× (independent) | `asyncio.gather()` + `httpx.AsyncClient` | Pure I/O — event loop fires all at once |
| LLM API calls N× (rate-limited) | `asyncio.Semaphore` + `asyncio.gather()` | Respect provider rate limits |
| Local model inference | `ProcessPoolExecutor` + `run_in_executor()` | CPU-bound — GIL blocks threads |
| Embed N docs via API | `asyncio.gather()` + `httpx.AsyncClient` | Same as LLM API fanout |
| Legacy blocking library | `ThreadPoolExecutor` + `run_in_executor()` | I/O releases GIL in threads |
| RAG pipeline | Async I/O + in-process CPU | API calls async, retrieval stays in-process |

**Golden rules**
1. LLM API calls are I/O — use async, not threads.
2. Local inference is CPU — use `ProcessPool`, not async.
3. Never call `time.sleep()` or `requests.get()` inside `async def`.
4. Create `httpx.AsyncClient` once per session, not per request.
5. Add `asyncio.Semaphore` before going to production.
