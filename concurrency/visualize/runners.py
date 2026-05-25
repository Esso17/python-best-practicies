"""Instrumented benchmark runners — record per-job start/end times for Gantt charts."""

from __future__ import annotations

import asyncio
import math
import os
import threading
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

import httpx

from .config import EMBED_MODEL, GEN_MODEL, OLLAMA, TIMEOUT, C
from .types import JobSpan, StrategyResult


def _prompt(ticket: str) -> str:
    return f'One word — positive, neutral, or negative: "{ticket}"'


# =============================================================================
# I/O — Ticket triage (sequential / threads / async)
# =============================================================================


def run_sequential_timed(tickets: list[str]) -> StrategyResult:
    result = StrategyResult("Sequential", C["seq"])
    with httpx.Client() as client:
        for i, ticket in enumerate(tickets):
            start = time.perf_counter()
            client.post(
                f"{OLLAMA}/api/chat",
                json={
                    "model": GEN_MODEL,
                    "messages": [{"role": "user", "content": _prompt(ticket)}],
                    "stream": False,
                    "options": {"num_predict": 5},
                },
                timeout=TIMEOUT,
            )
            result.spans.append(JobSpan(i, f"Ticket {i}", start, time.perf_counter()))
    return result


def run_threads_timed(tickets: list[str]) -> StrategyResult:
    result = StrategyResult("Threading", C["thread"])
    lock = threading.Lock()

    def _call(args: tuple[int, str]) -> None:
        i, ticket = args
        with httpx.Client() as client:
            start = time.perf_counter()
            client.post(
                f"{OLLAMA}/api/chat",
                json={
                    "model": GEN_MODEL,
                    "messages": [{"role": "user", "content": _prompt(ticket)}],
                    "stream": False,
                    "options": {"num_predict": 5},
                },
                timeout=TIMEOUT,
            )
            end = time.perf_counter()
        worker_id = int(threading.current_thread().name.split("_")[-1]) % len(tickets)
        with lock:
            result.spans.append(JobSpan(i, f"Ticket {i}", start, end, worker_id))

    with ThreadPoolExecutor(max_workers=len(tickets)) as ex:
        list(ex.map(_call, enumerate(tickets)))
    return result


async def _run_async_timed_inner(tickets: list[str]) -> StrategyResult:
    result = StrategyResult("AsyncIO", C["async"])

    async with httpx.AsyncClient() as client:

        async def _one(i: int, ticket: str) -> None:
            start = time.perf_counter()
            await client.post(
                f"{OLLAMA}/api/chat",
                json={
                    "model": GEN_MODEL,
                    "messages": [{"role": "user", "content": _prompt(ticket)}],
                    "stream": False,
                    "options": {"num_predict": 5},
                },
                timeout=TIMEOUT,
            )
            result.spans.append(JobSpan(i, f"Ticket {i}", start, time.perf_counter()))

        await asyncio.gather(*[_one(i, t) for i, t in enumerate(tickets)])
    return result


def run_async_timed(tickets: list[str]) -> StrategyResult:
    return asyncio.run(_run_async_timed_inner(tickets))


# =============================================================================
# I/O — Embedding (sequential / async)
# =============================================================================


def run_embed_sequential_timed(chunks: list[str]) -> StrategyResult:
    result = StrategyResult("Sequential", C["seq"])
    with httpx.Client() as client:
        for i, chunk in enumerate(chunks):
            start = time.perf_counter()
            client.post(
                f"{OLLAMA}/api/embed",
                json={"model": EMBED_MODEL, "input": chunk},
                timeout=TIMEOUT,
            )
            result.spans.append(JobSpan(i, f"Chunk {i}", start, time.perf_counter()))
    return result


async def _run_embed_async_inner(chunks: list[str]) -> StrategyResult:
    result = StrategyResult("AsyncIO", C["async"])

    async with httpx.AsyncClient() as client:

        async def _one(i: int, chunk: str) -> None:
            start = time.perf_counter()
            await client.post(
                f"{OLLAMA}/api/embed",
                json={"model": EMBED_MODEL, "input": chunk},
                timeout=TIMEOUT,
            )
            result.spans.append(JobSpan(i, f"Chunk {i}", start, time.perf_counter()))

        await asyncio.gather(*[_one(i, c) for i, c in enumerate(chunks)])
    return result


def run_embed_async_timed(chunks: list[str]) -> StrategyResult:
    return asyncio.run(_run_embed_async_inner(chunks))


# =============================================================================
# CPU-bound — local inference simulation (sequential / threads / processes)
# _cpu_task must be at module level so ProcessPoolExecutor can pickle it.
# =============================================================================


def _cpu_task(args: tuple[int, int]) -> tuple[int, float, float]:
    i, workload = args
    start = time.perf_counter()
    sum(math.sqrt(j) * math.sin(j) for j in range(workload))
    return i, start, time.perf_counter()


def run_cpu_sequential_timed(n: int, workload: int) -> StrategyResult:
    result = StrategyResult("Sequential", C["seq"])
    for i in range(n):
        job_id, start, end = _cpu_task((i, workload))
        result.spans.append(JobSpan(job_id, f"Batch {job_id}", start, end))
    return result


def run_cpu_threads_timed(n: int, workload: int) -> StrategyResult:
    result = StrategyResult("Threading", C["thread"])
    lock = threading.Lock()

    def _call(i: int) -> None:
        job_id, start, end = _cpu_task((i, workload))
        wid = int(threading.current_thread().name.split("_")[-1]) % n
        with lock:
            result.spans.append(JobSpan(job_id, f"Batch {job_id}", start, end, wid))

    with ThreadPoolExecutor(max_workers=n) as ex:
        list(ex.map(_call, range(n)))
    return result


def run_cpu_processes_timed(n: int, workload: int) -> StrategyResult:
    result = StrategyResult("Multiprocessing", C["proc"])
    with ProcessPoolExecutor(max_workers=min(n, os.cpu_count() or 4)) as ex:
        for job_id, start, end in ex.map(_cpu_task, [(i, workload) for i in range(n)]):
            result.spans.append(JobSpan(job_id, f"Batch {job_id}", start, end))
    return result
