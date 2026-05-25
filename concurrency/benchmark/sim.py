"""Simulated benchmarks B1–B4 — no Ollama required."""

import asyncio
import math
import os
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

import httpx

from .config import (
    CPU_WORKLOAD,
    HTTP_TIMEOUT,
    N_CPU_BATCHES,
    N_HTTP_CALLS,
    N_SIM_CALLS,
    SEM_LIMIT,
    SIM_LATENCY_MS,
)
from .models import BenchResult, W, _header, _row, _summary_row, _table_header
from .viz import _plot_speedup

# ── Shared simulation primitives ──────────────────────────────────────────────


def _sim_call_sync(i: int, latency_ms: float) -> dict:
    time.sleep(latency_ms / 1000)
    return {"id": i}


async def _sim_call_async(i: int, latency_ms: float) -> dict:
    await asyncio.sleep(latency_ms / 1000)
    return {"id": i}


def _cpu_batch(workload: int) -> list[float]:
    return [math.sqrt(i) * math.sin(i) for i in range(workload)][-5:]


def _rerank(scores: list[float]) -> list[float]:
    """CPU-intensive re-ranking — must be at module level for ProcessPool pickling."""
    wl = CPU_WORKLOAD // 10
    total = sum(
        math.log1p(abs(x)) * math.sqrt(i + 1)
        for i, x in enumerate(scores)
        for _ in range(wl // len(scores))
    )
    return [total / len(scores)] * len(scores)


# =============================================================================
# B1 — I/O-Bound: Simulated LLM API Fanout
# =============================================================================


def run_b1() -> list[BenchResult]:
    n, ms = N_SIM_CALLS, SIM_LATENCY_MS
    _header(f"B1 — I/O-Bound: Simulated LLM Fanout  (N={n} calls × {ms} ms)")
    print(f"  Best possible: {ms} ms (all calls in parallel).\n")

    async def _gather() -> float:
        t = time.perf_counter()
        await asyncio.gather(*[_sim_call_async(i, ms) for i in range(n)])
        return time.perf_counter() - t

    async def _semaphore() -> float:
        sem = asyncio.Semaphore(SEM_LIMIT)

        async def _one(i: int) -> dict:
            async with sem:
                return await _sim_call_async(i, ms)

        t = time.perf_counter()
        await asyncio.gather(*[_one(i) for i in range(n)])
        return time.perf_counter() - t

    t = time.perf_counter()
    for i in range(n):
        _sim_call_sync(i, ms)
    r_seq = BenchResult("Sequential", time.perf_counter() - t, n_tasks=n)

    t = time.perf_counter()
    with ThreadPoolExecutor(max_workers=n) as ex:
        list(ex.map(lambda i: _sim_call_sync(i, ms), range(n)))
    r_thr = BenchResult(f"Threading ({n} workers)", time.perf_counter() - t, n_tasks=n)

    r_async = BenchResult("AsyncIO (gather)", asyncio.run(_gather()), n_tasks=n)
    r_sem = BenchResult(
        f"AsyncIO + Semaphore({SEM_LIMIT})", asyncio.run(_semaphore()), n_tasks=n
    )

    baseline = r_seq.seconds
    _table_header()
    for r in (r_seq, r_thr, r_async, r_sem):
        r.speedup = _row(r.label, r.seconds, baseline)
    print()
    return [r_seq, r_thr, r_async, r_sem]


# =============================================================================
# B2 — CPU-Bound: Local Inference Simulation
# =============================================================================


def run_b2() -> list[BenchResult]:
    n, wl = N_CPU_BATCHES, CPU_WORKLOAD
    n_cores = min(n, os.cpu_count() or 4)
    _header(f"B2 — CPU-Bound: Local Inference  (N={n} batches, {wl:,} ops each)")
    print("  GIL blocks threads for CPU work — only processes help.\n")

    t = time.perf_counter()
    for _ in range(n):
        _cpu_batch(wl)
    r_seq = BenchResult("Sequential", time.perf_counter() - t, n_tasks=n)

    t = time.perf_counter()
    with ThreadPoolExecutor(max_workers=n_cores) as ex:
        list(ex.map(_cpu_batch, [wl] * n))
    r_thr = BenchResult(
        f"Threading ({n_cores} workers)", time.perf_counter() - t, n_tasks=n
    )

    t = time.perf_counter()
    with ProcessPoolExecutor(max_workers=n_cores) as ex:
        list(ex.map(_cpu_batch, [wl] * n))
    r_proc = BenchResult(
        f"Multiprocessing ({n_cores} cores)", time.perf_counter() - t, n_tasks=n
    )

    baseline = r_seq.seconds
    _table_header()
    for r in (r_seq, r_thr, r_proc):
        r.speedup = _row(r.label, r.seconds, baseline)
    print()
    return [r_seq, r_thr, r_proc]


# =============================================================================
# B3 — Real HTTP: JSONPlaceholder API
# =============================================================================


def run_b3() -> list[BenchResult]:
    urls = [
        f"https://jsonplaceholder.typicode.com/posts/{i}"
        for i in range(1, N_HTTP_CALLS + 1)
    ]
    _header(f"B3 — Real HTTP: JSONPlaceholder API  (N={N_HTTP_CALLS} requests)")
    print("  Real network latency — proves async wins are not simulation artefacts.\n")

    async def _gather_http() -> float:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            t = time.perf_counter()
            await asyncio.gather(*[client.get(u) for u in urls])
            return time.perf_counter() - t

    t = time.perf_counter()
    for u in urls:
        httpx.get(u, timeout=HTTP_TIMEOUT)
    r_seq = BenchResult("Sequential", time.perf_counter() - t, n_tasks=len(urls))

    t = time.perf_counter()
    with ThreadPoolExecutor(max_workers=len(urls)) as ex:
        list(ex.map(lambda u: httpx.get(u, timeout=HTTP_TIMEOUT), urls))
    r_thr = BenchResult(
        f"Threading ({len(urls)} workers)", time.perf_counter() - t, n_tasks=len(urls)
    )

    r_async = BenchResult(
        "AsyncIO (httpx)", asyncio.run(_gather_http()), n_tasks=len(urls)
    )

    baseline = r_seq.seconds
    _table_header()
    for r in (r_seq, r_thr, r_async):
        r.speedup = _row(r.label, r.seconds, baseline)
    print()
    return [r_seq, r_thr, r_async]


# =============================================================================
# B4 — Hybrid: Async Fanout + ProcessPool Re-ranking
# =============================================================================


def run_b4() -> BenchResult:
    n = N_SIM_CALLS
    n_cores = min(os.cpu_count() or 2, 4)
    _header(f"B4 — Hybrid: Async Fanout + ProcessPool Re-ranking  (N={n} queries)")
    print("  Production pattern: I/O async, CPU offloaded to processes.\n")

    async def _pipeline() -> float:
        loop = asyncio.get_running_loop()
        pool = ProcessPoolExecutor(max_workers=n_cores)

        async def _one(i: int) -> list[float]:
            await asyncio.sleep(SIM_LATENCY_MS / 1000)
            return await loop.run_in_executor(
                pool, _rerank, [float(i * j) for j in range(1, 6)]
            )

        t = time.perf_counter()
        await asyncio.gather(*[_one(i) for i in range(n)])
        pool.shutdown(wait=True)
        return time.perf_counter() - t

    t = time.perf_counter()
    for i in range(n):
        _sim_call_sync(i, SIM_LATENCY_MS)
    r_seq = BenchResult("Sequential", time.perf_counter() - t, n_tasks=n)

    r_hybrid = BenchResult(
        f"Async + ProcessPool ({n_cores} cores)", asyncio.run(_pipeline()), n_tasks=n
    )
    r_hybrid.speedup = r_seq.seconds / r_hybrid.seconds

    _table_header()
    _row(r_seq.label, r_seq.seconds, r_seq.seconds)
    _row(r_hybrid.label, r_hybrid.seconds, r_seq.seconds)
    print()
    return r_hybrid


# =============================================================================
# Orchestrator
# =============================================================================


def run_simulate(plot: bool) -> None:
    import sys

    print(f"\n{'═' * W}")
    print("  PYTHON CONCURRENCY FOR AI — Simulated Benchmark  (no Ollama needed)")
    print(f"  Python {sys.version.split()[0]}  |  Cores: {os.cpu_count()}")
    print(f"{'═' * W}")

    b1 = run_b1()
    b2 = run_b2()
    b3 = run_b3()
    run_b4()

    _header("SUMMARY")
    print(
        f"\n  {'Benchmark':<38} {'Sequential':>10}  {'Best':>10}  {'Speedup':>8}  Winner"
    )
    print("  " + "─" * 74)
    _summary_row(f"B1 I/O-Bound ({N_SIM_CALLS} × {SIM_LATENCY_MS} ms)", b1)
    _summary_row(f"B2 CPU-Bound ({N_CPU_BATCHES} batches)", b2)
    _summary_row(f"B3 Real HTTP ({N_HTTP_CALLS} requests)", b3)

    if plot:
        _plot_speedup(
            [b1[:3], b2, b3],
            [
                "I/O-Bound\n(Simulated)",
                "CPU-Bound\n(Math)",
                "Real HTTP\n(JSONPlaceholder)",
            ],
            "concurrency/images/simulate_benchmark_results.png",
        )
