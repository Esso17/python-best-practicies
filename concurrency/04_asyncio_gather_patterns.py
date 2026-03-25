"""
Python Best Practice: asyncio.gather() Patterns and Pitfalls

Demonstrates proper use of asyncio.gather() for concurrent operations,
including error handling, cancellation, and performance optimization.
"""

import asyncio
import random
import time
from typing import Any, Dict, List


# Simulated async operations
async def fetch_user(user_id: int) -> Dict[str, Any]:
    """Simulate fetching user data from database"""
    await asyncio.sleep(0.1)
    return {"id": user_id, "name": f"User {user_id}"}


async def fetch_posts(user_id: int) -> List[Dict[str, Any]]:
    """Simulate fetching user's posts"""
    await asyncio.sleep(0.15)
    return [{"id": i, "title": f"Post {i}"} for i in range(3)]


async def fetch_followers(user_id: int) -> int:
    """Simulate fetching follower count"""
    await asyncio.sleep(0.12)
    return random.randint(100, 1000)


async def risky_operation(task_id: int) -> str:
    """Simulates operation that might fail"""
    await asyncio.sleep(0.1)
    if task_id == 3:
        raise ValueError(f"Task {task_id} failed!")
    return f"Task {task_id} completed"


# =============================================================================
# Pattern 1: Basic Concurrent Execution
# =============================================================================


async def pattern_basic_gather():
    """
    ✅ GOOD: Run independent I/O operations concurrently.
    All tasks execute in parallel, wait for all to complete.
    """
    print("\n" + "=" * 60)
    print("Pattern 1: Basic Concurrent Execution")
    print("=" * 60)

    user_id = 123

    # Sequential (BAD)
    start = time.perf_counter()
    user = await fetch_user(user_id)
    posts = await fetch_posts(user_id)
    followers = await fetch_followers(user_id)
    sequential_time = time.perf_counter() - start

    print(f"❌ Sequential: {sequential_time:.3f}s")

    # Concurrent (GOOD)
    start = time.perf_counter()
    user, posts, followers = await asyncio.gather(
        fetch_user(user_id), fetch_posts(user_id), fetch_followers(user_id)
    )
    concurrent_time = time.perf_counter() - start

    print(f"✅ Concurrent: {concurrent_time:.3f}s")
    print(f"   Speedup: {sequential_time/concurrent_time:.1f}x faster")


# =============================================================================
# Pattern 2: Error Handling
# =============================================================================


async def pattern_error_handling():
    """
    Demonstrates error handling strategies with gather().
    """
    print("\n" + "=" * 60)
    print("Pattern 2: Error Handling")
    print("=" * 60)

    # ❌ BAD: One failure stops everything
    print("\n❌ Default behavior (return_exceptions=False):")
    try:
        results = await asyncio.gather(
            risky_operation(1),
            risky_operation(2),
            risky_operation(3),  # This will fail
            risky_operation(4),
        )
        print(f"   Results: {results}")
    except ValueError as e:
        print(f"   Exception raised: {e}")
        print("   All tasks cancelled, no partial results!")

    # ✅ GOOD: Handle errors gracefully
    print("\n✅ Graceful error handling (return_exceptions=True):")
    results = await asyncio.gather(
        risky_operation(1),
        risky_operation(2),
        risky_operation(3),  # This will fail
        risky_operation(4),
        return_exceptions=True,
    )

    # Process results and errors separately
    successes = [r for r in results if not isinstance(r, Exception)]
    errors = [r for r in results if isinstance(r, Exception)]

    print(f"   Successes: {len(successes)}")
    print(f"   Errors: {len(errors)}")
    print("   Got partial results even with failures!")


# =============================================================================
# Pattern 3: Dynamic Task Lists
# =============================================================================


async def pattern_dynamic_tasks():
    """
    ✅ GOOD: Build task lists dynamically based on data.
    """
    print("\n" + "=" * 60)
    print("Pattern 3: Dynamic Task Lists")
    print("=" * 60)

    user_ids = [1, 2, 3, 4, 5]

    # Create tasks dynamically
    tasks = [fetch_user(user_id) for user_id in user_ids]

    start = time.perf_counter()
    users = await asyncio.gather(*tasks)
    duration = time.perf_counter() - start

    print(f"✅ Fetched {len(users)} users concurrently")
    print(f"   Time: {duration:.3f}s")
    print(f"   Sequential would take: ~{len(users) * 0.1:.1f}s")


# =============================================================================
# Pattern 4: Mixed Dependencies
# =============================================================================


async def pattern_mixed_dependencies():
    """
    Handle cases where some tasks depend on others.
    """
    print("\n" + "=" * 60)
    print("Pattern 4: Mixed Dependencies")
    print("=" * 60)

    user_id = 123

    # ✅ GOOD: Separate dependent and independent tasks
    start = time.perf_counter()

    # Phase 1: Get user first (required for next steps)
    user = await fetch_user(user_id)

    # Phase 2: Fetch dependent data concurrently
    posts, followers = await asyncio.gather(
        fetch_posts(user["id"]), fetch_followers(user["id"])
    )

    duration = time.perf_counter() - start

    print(f"✅ Two-phase execution: {duration:.3f}s")
    print("   Phase 1: Fetch user")
    print("   Phase 2: Fetch posts + followers concurrently")


# =============================================================================
# Pattern 5: Timeout Handling
# =============================================================================


async def slow_operation(delay: float) -> str:
    """Simulates a slow operation"""
    await asyncio.sleep(delay)
    return f"Completed after {delay}s"


async def pattern_timeout():
    """
    ✅ GOOD: Add timeouts to prevent hanging forever.
    """
    print("\n" + "=" * 60)
    print("Pattern 5: Timeout Handling")
    print("=" * 60)

    # ❌ BAD: No timeout, could hang forever
    print("\n❌ Without timeout (would hang if server is down):")
    print("   (skipping this example...)")

    # ✅ GOOD: Wrap with timeout
    print("\n✅ With timeout protection:")
    try:
        results = await asyncio.wait_for(
            asyncio.gather(
                slow_operation(0.1),
                slow_operation(0.2),
                slow_operation(5.0),  # Too slow
            ),
            timeout=1.0,
        )
        print(f"   Results: {results}")
    except asyncio.TimeoutError:
        print("   Timeout! Cancelled slow operations.")
        print("   Prevents hanging indefinitely.")


# =============================================================================
# Pattern 6: Batch Processing with Semaphore
# =============================================================================


async def pattern_rate_limiting():
    """
    ✅ GOOD: Limit concurrent operations to avoid overwhelming resources.
    """
    print("\n" + "=" * 60)
    print("Pattern 6: Rate Limiting with Semaphore")
    print("=" * 60)

    # Limit to 3 concurrent operations
    semaphore = asyncio.Semaphore(3)

    async def limited_fetch(user_id: int) -> Dict[str, Any]:
        async with semaphore:
            print(f"   Fetching user {user_id}...")
            return await fetch_user(user_id)

    user_ids = range(1, 11)  # 10 users

    start = time.perf_counter()
    users = await asyncio.gather(*[limited_fetch(uid) for uid in user_ids])
    duration = time.perf_counter() - start

    print(f"\n✅ Processed {len(users)} users with max 3 concurrent")
    print(f"   Time: {duration:.3f}s")
    print("   Prevents overwhelming database/API")


# =============================================================================
# Pattern 7: Early Exit with as_completed
# =============================================================================


async def pattern_early_exit():
    """
    When you need the first available result, not all results.
    """
    print("\n" + "=" * 60)
    print("Pattern 7: Early Exit (First Result)")
    print("=" * 60)

    # Different response times
    tasks = [
        slow_operation(0.3),
        slow_operation(0.1),  # Fastest
        slow_operation(0.5),
    ]

    print("✅ Using asyncio.wait with FIRST_COMPLETED:")
    start = time.perf_counter()

    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    duration = time.perf_counter() - start
    first_result = done.pop().result()

    # Cancel remaining tasks
    for task in pending:
        task.cancel()

    print(f"   First result: '{first_result}'")
    print(f"   Time: {duration:.3f}s")
    print(f"   Cancelled {len(pending)} pending tasks")


# =============================================================================
# Benchmark: gather() vs Sequential
# =============================================================================


async def benchmark_gather_vs_sequential():
    """
    Comprehensive benchmark showing gather() performance benefits.
    """
    print("\n" + "=" * 60)
    print("BENCHMARK: gather() vs Sequential Execution")
    print("=" * 60)

    num_operations = 20
    operation_time = 0.05  # 50ms each

    # Sequential
    start = time.perf_counter()
    for _ in range(num_operations):
        await slow_operation(operation_time)
    sequential_time = time.perf_counter() - start

    print(f"\n❌ Sequential: {sequential_time:.3f}s")

    # Concurrent with gather
    start = time.perf_counter()
    await asyncio.gather(
        *[slow_operation(operation_time) for _ in range(num_operations)]
    )
    concurrent_time = time.perf_counter() - start

    print(f"✅ Concurrent: {concurrent_time:.3f}s")

    # Results
    speedup = sequential_time / concurrent_time
    print(f"\n{'=' * 60}")
    print(f"SPEEDUP: {speedup:.1f}x faster!")
    print(f"Time saved: {sequential_time - concurrent_time:.3f}s")
    print(f"{'=' * 60}")


# =============================================================================
# Main
# =============================================================================


async def main():
    """Run all pattern demonstrations"""
    print("\n" + "=" * 60)
    print("ASYNCIO.GATHER() BEST PRACTICES")
    print("=" * 60)

    await pattern_basic_gather()
    await pattern_error_handling()
    await pattern_dynamic_tasks()
    await pattern_mixed_dependencies()
    await pattern_timeout()
    await pattern_rate_limiting()
    await pattern_early_exit()
    await benchmark_gather_vs_sequential()

    print("\n" + "=" * 60)
    print("KEY TAKEAWAYS:")
    print("=" * 60)
    print("1. Use gather() for independent I/O-bound operations")
    print("2. Add return_exceptions=True for graceful error handling")
    print("3. Use Semaphore to limit concurrent operations")
    print("4. Add timeouts to prevent hanging")
    print("5. Separate dependent and independent tasks")
    print("6. Use wait() with FIRST_COMPLETED for early exit")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
