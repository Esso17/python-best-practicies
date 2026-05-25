"""Entry point: python -m visualize  or  python concurrency/07_visualize_concurrency.py"""

from __future__ import annotations

import argparse

import httpx

from .charts import (
    figure1_io_gantt,
    figure2_cpu_gantt,
    figure3_embed_gantt,
    figure4_rag_waterfall,
    figure5_summary,
)
from .config import CHUNKS, EMBED_MODEL, GEN_MODEL, OLLAMA, TICKETS
from .runners import (
    run_async_timed,
    run_cpu_processes_timed,
    run_cpu_sequential_timed,
    run_cpu_threads_timed,
    run_embed_async_timed,
    run_embed_sequential_timed,
    run_sequential_timed,
    run_threads_timed,
)


def _warmup() -> None:
    print("  Warming up models …", end="", flush=True)
    with httpx.Client() as c:
        c.post(
            f"{OLLAMA}/api/chat",
            json={
                "model": GEN_MODEL,
                "messages": [{"role": "user", "content": "hi"}],
                "stream": False,
                "options": {"num_predict": 1},
            },
            timeout=30.0,
        )
        c.post(
            f"{OLLAMA}/api/embed",
            json={"model": EMBED_MODEL, "input": "warmup"},
            timeout=30.0,
        )
    print(" done.\n")


def main(save: bool) -> None:
    print("\n════════════════════════════════════════════════════")
    print("  Generating concurrency visualisations …")
    print("════════════════════════════════════════════════════\n")

    _warmup()

    print("  [1/3] I/O benchmark — ticket triage (seq / threads / async) …")
    io_seq = run_sequential_timed(TICKETS)
    io_thr = run_threads_timed(TICKETS)
    io_async = run_async_timed(TICKETS)
    io_strats = [io_seq, io_thr, io_async]
    print(
        f"        seq={io_seq.total:.2f}s  thr={io_thr.total:.2f}s  "
        f"async={io_async.total:.2f}s"
    )

    print("  [2/3] CPU benchmark — local inference (seq / threads / processes) …")
    n_cpu, workload = 6, 1_500_000
    cpu_seq = run_cpu_sequential_timed(n_cpu, workload)
    cpu_thr = run_cpu_threads_timed(n_cpu, workload)
    cpu_proc = run_cpu_processes_timed(n_cpu, workload)
    cpu_strats = [cpu_seq, cpu_thr, cpu_proc]
    print(
        f"        seq={cpu_seq.total:.2f}s  thr={cpu_thr.total:.2f}s  "
        f"proc={cpu_proc.total:.2f}s"
    )

    print("  [3/3] Embedding benchmark — knowledge base (seq / async) …")
    emb_seq = run_embed_sequential_timed(CHUNKS)
    emb_async = run_embed_async_timed(CHUNKS)
    emb_strats = [emb_seq, emb_async]
    print(f"        seq={emb_seq.total:.2f}s  async={emb_async.total:.2f}s\n")

    rag_embed_ms = emb_async.total / len(CHUNKS) * 1000
    rag_retrieve_ms = 1.5
    rag_generate_ms = io_async.total / len(TICKETS) * 1000

    print("  Rendering figures …\n")
    figure1_io_gantt(io_strats, save)
    figure2_cpu_gantt(cpu_strats, save)
    figure3_embed_gantt(emb_strats, save)
    figure4_rag_waterfall(rag_embed_ms, rag_retrieve_ms, rag_generate_ms, save)
    figure5_summary(io_strats, cpu_strats, emb_strats, save)

    if save:
        print("\n  All figures saved to concurrency/fig*.png")
    print("\n  Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--save", action="store_true", help="Save figures as PNG files")
    main(save=parser.parse_args().save)
