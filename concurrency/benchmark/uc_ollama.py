"""Ollama use-case benchmarks: UC1 ticket triage, UC2 embeddings, UC3 dual-model, UC4 RAG."""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

import httpx

from .config import (
    _REVIEW_PROMPT,
    GEN_MODEL,
    KNOWLEDGE_BASE,
    N_CHUNKS,
    N_TICKETS,
    RAG_QUERY,
    REVIEW_CODE,
    REVIEW_MODELS,
    SUPPORT_TICKETS,
)
from .models import BenchResult, W, _header, _row, _sub, _summary_row, _table_header
from .ollama_client import _chat_async, _chat_sync, _cosine, _embed_async, _embed_sync
from .viz import _plot_speedup

# =============================================================================
# UC1 — Support Ticket Triage
# =============================================================================


def _triage_prompt(ticket: str) -> str:
    return f'Classify as positive, neutral, or negative: "{ticket}"'


def uc1_sequential(tickets: list[str]) -> BenchResult:
    with httpx.Client() as client:
        t = time.perf_counter()
        outputs = [_chat_sync(client, _triage_prompt(tk)) for tk in tickets]
    return BenchResult("Sequential", time.perf_counter() - t, outputs=outputs)


def uc1_threads(tickets: list[str]) -> BenchResult:
    def _call(tk: str) -> str:
        with httpx.Client() as c:
            return _chat_sync(c, _triage_prompt(tk))

    t = time.perf_counter()
    with ThreadPoolExecutor(max_workers=len(tickets)) as ex:
        outputs = list(ex.map(_call, tickets))
    return BenchResult(
        f"Threading ({len(tickets)} workers)", time.perf_counter() - t, outputs=outputs
    )


async def _uc1_async(tickets: list[str]) -> tuple[float, list[str]]:
    async with httpx.AsyncClient() as client:
        t = time.perf_counter()
        outputs = await asyncio.gather(
            *[_chat_async(client, _triage_prompt(tk)) for tk in tickets]
        )
    return time.perf_counter() - t, list(outputs)


def uc1_async(tickets: list[str]) -> BenchResult:
    secs, outputs = asyncio.run(_uc1_async(tickets))
    return BenchResult("AsyncIO (gather)", secs, outputs=outputs)


def run_uc1() -> list[BenchResult]:
    _header(f"UC1 — Support Ticket Triage  (N={N_TICKETS} × {GEN_MODEL})")
    print(
        "  Scenario: classify tickets by sentiment — calls are independent.\n"
        "  Pattern : sequential → threading → asyncio\n"
    )
    _sub("Running …")
    r_seq, r_thr, r_async = (
        uc1_sequential(SUPPORT_TICKETS[:N_TICKETS]),
        uc1_threads(SUPPORT_TICKETS[:N_TICKETS]),
        uc1_async(SUPPORT_TICKETS[:N_TICKETS]),
    )
    baseline = r_seq.seconds
    r_thr.speedup = baseline / r_thr.seconds
    r_async.speedup = baseline / r_async.seconds
    _table_header()
    for r in (r_seq, r_thr, r_async):
        _row(r.label, r.seconds, baseline)
    _sub("Sentiment labels")
    for ticket, label in zip(SUPPORT_TICKETS[:N_TICKETS], r_async.outputs):
        print(f"  {ticket[:58]:58s}  → {label.split()[0]}")
    print()
    return [r_seq, r_thr, r_async]


# =============================================================================
# UC2 — Knowledge Base Embedding
# =============================================================================


def uc2_sequential(chunks: list[tuple[str, str]]) -> BenchResult:
    with httpx.Client() as client:
        t = time.perf_counter()
        outputs = [(cid, _embed_sync(client, text)) for cid, text in chunks]
    return BenchResult("Sequential", time.perf_counter() - t, outputs=outputs)


async def _uc2_async(chunks: list[tuple[str, str]]) -> tuple[float, list]:
    async with httpx.AsyncClient() as client:
        t = time.perf_counter()
        embeddings = await asyncio.gather(
            *[_embed_async(client, text) for _, text in chunks]
        )
    secs = time.perf_counter() - t
    return secs, [(cid, emb) for (cid, _), emb in zip(chunks, embeddings)]


def uc2_async(chunks: list[tuple[str, str]]) -> BenchResult:
    secs, outputs = asyncio.run(_uc2_async(chunks))
    return BenchResult("AsyncIO (gather)", secs, outputs=outputs)


def run_uc2() -> list[BenchResult]:
    _header(f"UC2 — Knowledge Base Embedding  (N={N_CHUNKS} × nomic-embed-text)")
    print(
        "  Scenario: embed N chunks before RAG — calls are independent.\n"
        "  Pattern : sequential → asyncio\n"
    )
    _sub("Running …")
    r_seq = uc2_sequential(KNOWLEDGE_BASE[:N_CHUNKS])
    r_async = uc2_async(KNOWLEDGE_BASE[:N_CHUNKS])
    r_async.speedup = r_seq.seconds / r_async.seconds
    _table_header()
    _row(r_seq.label, r_seq.seconds, r_seq.seconds)
    _row(r_async.label, r_async.seconds, r_seq.seconds)
    _sub("Embeddings")
    for cid, emb in r_async.outputs:
        print(f"  {cid}  dim={len(emb)}  [{', '.join(f'{x:.3f}' for x in emb[:3])}, …]")
    print()
    return [r_seq, r_async]


# =============================================================================
# UC3 — Dual-Model Code Review
# =============================================================================


async def _uc3_async(code: str) -> tuple[float, str, str]:
    prompt = _REVIEW_PROMPT.format(code=code)
    async with httpx.AsyncClient() as client:
        t = time.perf_counter()
        phi_out, mis_out = await asyncio.gather(
            _chat_async(client, prompt, model=REVIEW_MODELS[0], max_tokens=20),
            _chat_async(client, prompt, model=REVIEW_MODELS[1], max_tokens=20),
        )
    return time.perf_counter() - t, phi_out, mis_out


def _uc3_sequential(code: str) -> tuple[float, str, str]:
    prompt = _REVIEW_PROMPT.format(code=code)
    with httpx.Client() as client:
        t = time.perf_counter()
        phi_out = _chat_sync(client, prompt, model=REVIEW_MODELS[0], max_tokens=20)
        mis_out = _chat_sync(client, prompt, model=REVIEW_MODELS[1], max_tokens=20)
    return time.perf_counter() - t, phi_out, mis_out


def run_uc3() -> list[BenchResult]:
    _header(f"UC3 — Dual-Model Code Review  ({REVIEW_MODELS[0]} + {REVIEW_MODELS[1]})")
    print(
        "  Scenario: two models review the same code independently.\n"
        "  Pattern : sequential → asyncio.gather\n"
    )
    _sub("Code under review")
    print(f"  {REVIEW_CODE.strip()}\n")
    _sub("Running …")
    seq_t, phi_seq, mis_seq = _uc3_sequential(REVIEW_CODE)
    async_t, phi_out, mis_out = asyncio.run(_uc3_async(REVIEW_CODE))
    r_seq = BenchResult("Sequential (phi → mistral)", seq_t)
    r_async = BenchResult("AsyncIO (phi || mistral)", async_t, speedup=seq_t / async_t)
    _table_header()
    _row(r_seq.label, r_seq.seconds, seq_t)
    _row(r_async.label, r_async.seconds, seq_t)
    _sub("Reviews")
    print(f"  phi3.5   → {phi_out[:80]}")
    print(f"  mistral  → {mis_out[:80]}\n")
    return [r_seq, r_async]


# =============================================================================
# UC4 — End-to-End RAG Pipeline
# =============================================================================


def run_uc4(kb_embeddings: list[tuple[str, list[float]]]) -> None:
    _header("UC4 — End-to-End RAG Pipeline  (embed → retrieve → generate)")
    print(f'  Query: "{RAG_QUERY}"\n')

    async def _pipeline() -> tuple[float, float, float, str, list]:
        async with httpx.AsyncClient() as client:
            t1 = time.perf_counter()
            q_emb = await _embed_async(client, RAG_QUERY)
            embed_ms = (time.perf_counter() - t1) * 1000

            t2 = time.perf_counter()
            top3 = sorted(
                [(cid, _cosine(q_emb, emb)) for cid, emb in kb_embeddings],
                key=lambda x: x[1],
                reverse=True,
            )[:3]
            retrieve_ms = (time.perf_counter() - t2) * 1000

            context = "\n".join(
                text
                for cid, _ in top3
                for kb_cid, text in KNOWLEDGE_BASE
                if kb_cid == cid
            )
            t3 = time.perf_counter()
            answer = await _chat_async(
                client,
                f"Answer in 2 sentences using only this context:\n{context}\n\nQ: {RAG_QUERY}",
                max_tokens=60,
            )
            generate_ms = (time.perf_counter() - t3) * 1000

        return embed_ms, retrieve_ms, generate_ms, answer, top3

    embed_ms, retrieve_ms, generate_ms, answer, top3 = asyncio.run(_pipeline())
    total = embed_ms + retrieve_ms + generate_ms
    _sub("Timings")
    print(f"  Step 1 — Embed query      : {embed_ms:>7.1f} ms")
    print(f"  Step 2 — Cosine retrieval : {retrieve_ms:>7.1f} ms  (in-process)")
    print(f"  Step 3 — Generate answer  : {generate_ms:>7.1f} ms")
    print(f"  {'─' * 38}")
    print(f"  Total                     : {total:>7.1f} ms")
    _sub("Top-3 chunks")
    for cid, score in top3:
        text = next(t for c, t in KNOWLEDGE_BASE if c == cid)
        print(f"  [{cid}]  sim={score:.3f}  {text[:65]}…")
    _sub("Answer")
    print(f"  {answer}\n")


# =============================================================================
# Orchestrator
# =============================================================================


def _warmup() -> None:
    _header("WARMUP — loading models")
    print("  Sending one request to each model …", end="", flush=True)
    with httpx.Client() as c:
        _chat_sync(c, "Hi", max_tokens=1)
        _embed_sync(c, "warmup")
    print(" done.\n")


def run_ollama(plot: bool) -> None:
    print(f"\n{'═' * W}")
    print("  PYTHON CONCURRENCY FOR AI — Ollama Benchmark")
    print(f"  Models: {GEN_MODEL}  |  nomic-embed-text")
    print(f"{'═' * W}")

    _warmup()
    uc1 = run_uc1()
    uc2 = run_uc2()
    uc3 = run_uc3()
    run_uc4(list(uc2[1].outputs))

    _header("SUMMARY")
    print(
        f"\n  {'Use Case':<38} {'Sequential':>10}  {'Best':>10}  {'Speedup':>8}  Winner"
    )
    print("  " + "─" * 74)
    _summary_row(f"UC1 Ticket Triage ({N_TICKETS} tickets)", uc1)
    _summary_row(f"UC2 KB Embedding ({N_CHUNKS} chunks)", uc2)
    _summary_row("UC3 Dual-Model Code Review", uc3)

    if plot:
        _plot_speedup(
            [uc1, uc2, uc3],
            [
                f"Ticket Triage\n(N={N_TICKETS})",
                f"KB Embedding\n(N={N_CHUNKS})",
                "Dual-Model\nCode Review",
            ],
            "concurrency/images/ollama_benchmark_results.png",
        )
