"""
Python Best Practice: Async/Await - Blocking vs Non-Blocking I/O

The Problem: Using synchronous blocking calls in async functions freezes the event loop,
queuing all other requests behind it.

This example demonstrates the performance difference between blocking and async HTTP calls.
"""

import asyncio
import time
from typing import List

import httpx
import requests


# ❌ BAD: Blocking synchronous call in async function
async def fetch_with_requests_bad(url: str) -> dict:
    """
    This blocks the event loop during I/O wait.
    While waiting for the HTTP response, no other async tasks can run.
    """
    response = requests.get(url, timeout=10)
    return response.json()


# ✅ GOOD: Proper async HTTP call
async def fetch_with_httpx_good(url: str) -> dict:
    """
    This yields control back to the event loop during I/O wait.
    Other tasks can execute while waiting for the HTTP response.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=10.0)
        return response.json()


# Benchmark: Sequential execution
async def benchmark_sequential_blocking(urls: List[str]):
    """Simulate multiple blocking requests"""
    start = time.perf_counter()
    results = []

    for url in urls:
        try:
            result = await fetch_with_requests_bad(url)
            results.append(result)
        except Exception as e:
            results.append({"error": str(e)})

    duration = time.perf_counter() - start
    return results, duration


async def benchmark_concurrent_async(urls: List[str]):
    """Proper concurrent async requests"""
    start = time.perf_counter()

    # All tasks run concurrently
    tasks = [fetch_with_httpx_good(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    duration = time.perf_counter() - start
    return results, duration


async def main():
    # Test with httpbin.org which simulates delays
    urls = [
        "https://httpbin.org/delay/1",  # Each takes ~1 second
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
    ]

    print("=" * 60)
    print("BENCHMARK: Blocking vs Async HTTP Requests")
    print("=" * 60)
    print(f"Testing with {len(urls)} requests (each has 1s delay)\n")

    # Test blocking approach
    print("❌ BAD: Blocking requests in async function")
    _, blocking_time = await benchmark_sequential_blocking(urls)
    print(f"   Total time: {blocking_time:.2f}s")
    print(f"   Expected: ~{len(urls)}s (sequential)\n")

    # Test async approach
    print("✅ GOOD: Proper async/await with httpx")
    _, async_time = await benchmark_concurrent_async(urls)
    print(f"   Total time: {async_time:.2f}s")
    print("   Expected: ~1s (concurrent)\n")

    # Calculate improvement
    improvement = blocking_time / async_time
    print("=" * 60)
    print(f"SPEEDUP: {improvement:.1f}x faster with async!")
    print(f"Time saved: {blocking_time - async_time:.2f}s")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
