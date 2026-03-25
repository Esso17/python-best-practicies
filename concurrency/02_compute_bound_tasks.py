"""
Python Best Practice: Handling Compute-Bound Tasks in Async Applications

The Problem: CPU-intensive tasks (local inference, embeddings, heavy computation)
block the event loop even with async/await. Async only helps with I/O-bound operations.

Solution: Use ProcessPoolExecutor to offload compute to separate processes,
bypassing Python's Global Interpreter Lock (GIL).
"""

import asyncio
import math
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


# Simulate a compute-intensive task (e.g., local ML inference)
def cpu_intensive_task(n: int) -> float:
    """
    Simulates heavy computation like:
    - Local LLM inference
    - Embedding generation
    - Image processing with CLIP
    - Vector similarity calculations
    """
    result = 0
    for i in range(n):
        result += math.sqrt(i) * math.sin(i) * math.cos(i)
    return result


# ❌ BAD: Running CPU-bound work directly in async function
async def compute_blocking_bad(n: int) -> float:
    """
    This blocks the event loop!
    No other async tasks can run while computing.
    """
    return cpu_intensive_task(n)


# ⚠️ STILL BAD: ThreadPoolExecutor doesn't help for CPU-bound work
async def compute_with_threads_bad(n: int) -> float:
    """
    Threads don't help for CPU work due to Python's GIL.
    Multiple threads still execute on one CPU core.
    """
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=4) as executor:
        result = await loop.run_in_executor(executor, cpu_intensive_task, n)
    return result


# ✅ GOOD: ProcessPoolExecutor for CPU-bound work
class ComputeService:
    """Service that properly handles CPU-intensive operations"""

    def __init__(self, max_workers: int = 2):
        """
        max_workers: Number of CPU cores to dedicate
        Rule of thumb: cpu_count() - 1 for FastAPI servers
        """
        self.executor = ProcessPoolExecutor(max_workers=max_workers)

    async def compute(self, n: int) -> float:
        """
        Offload CPU work to separate process.
        Event loop remains free to handle other requests.
        """
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(self.executor, cpu_intensive_task, n)
        return result

    def shutdown(self):
        self.executor.shutdown(wait=True)


# Benchmarks
async def benchmark_blocking_compute(iterations: int, task_size: int):
    """Sequential blocking compute"""
    start = time.perf_counter()
    results = []

    for _ in range(iterations):
        result = await compute_blocking_bad(task_size)
        results.append(result)

    duration = time.perf_counter() - start
    return results, duration


async def benchmark_thread_compute(iterations: int, task_size: int):
    """Using ThreadPoolExecutor (doesn't help for CPU)"""
    start = time.perf_counter()

    tasks = [compute_with_threads_bad(task_size) for _ in range(iterations)]
    results = await asyncio.gather(*tasks)

    duration = time.perf_counter() - start
    return results, duration


async def benchmark_process_compute(iterations: int, task_size: int, workers: int):
    """Using ProcessPoolExecutor (correct approach)"""
    start = time.perf_counter()

    service = ComputeService(max_workers=workers)
    tasks = [service.compute(task_size) for _ in range(iterations)]
    results = await asyncio.gather(*tasks)
    service.shutdown()

    duration = time.perf_counter() - start
    return results, duration


async def main():
    iterations = 8
    task_size = 2_000_000

    print("=" * 70)
    print("BENCHMARK: CPU-Bound Tasks in Async Applications")
    print("=" * 70)
    print(f"Running {iterations} compute tasks (task_size={task_size:,})\n")

    # Test 1: Blocking
    print("❌ BAD: CPU-bound work directly in async function")
    _, blocking_time = await benchmark_blocking_compute(iterations, task_size)
    print(f"   Total time: {blocking_time:.2f}s")
    print("   Note: Blocks event loop, no concurrency\n")

    # Test 2: ThreadPoolExecutor
    print("⚠️  STILL BAD: ThreadPoolExecutor (doesn't help CPU work)")
    _, thread_time = await benchmark_thread_compute(iterations, task_size)
    print(f"   Total time: {thread_time:.2f}s")
    print("   Note: GIL prevents true parallelism\n")

    # Test 3: ProcessPoolExecutor
    print("✅ GOOD: ProcessPoolExecutor (bypasses GIL)")
    workers = 4
    _, process_time = await benchmark_process_compute(iterations, task_size, workers)
    print(f"   Total time: {process_time:.2f}s")
    print(f"   Workers: {workers} processes\n")

    # Results
    improvement = blocking_time / process_time
    print("=" * 70)
    print(f"SPEEDUP: {improvement:.1f}x faster with ProcessPoolExecutor!")
    print(f"Time saved: {blocking_time - process_time:.2f}s")
    print("=" * 70)
    print("\nKEY INSIGHT:")
    print("- async/await: Only helps with I/O-bound operations")
    print("- ProcessPoolExecutor: Required for CPU-bound operations")
    print("- ThreadPoolExecutor: Doesn't help CPU work (GIL limitation)")


if __name__ == "__main__":
    asyncio.run(main())
