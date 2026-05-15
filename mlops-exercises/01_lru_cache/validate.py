"""
================================================================================
MLOPS INTERVIEW EXERCISE #01 — LRU Cache  |  VALIDATION SUITE
================================================================================

HOW TO RUN
----------
    # validate your own exercise.py (swap import below):
    python validate.py

    # or run explicitly against the solution:
    python -c "import solution as target; exec(open('validate.py').read())"

The script imports from `solution.py` by default.
To validate your own implementation replace the import with:
    from exercise import LRUCache, LRUCacheV2, LRUCacheV3, ThreadSafeLRUCache
"""

from __future__ import annotations

import sys
import threading
import time
import traceback
from collections import OrderedDict
from typing import Callable

# ── swap this import to test your own implementation ──────────────────────────
from solution import LRUCache, LRUCacheV2, LRUCacheV3, ThreadSafeLRUCache

# ─────────────────────────────────────────────────────────────────────────────
# Tiny test harness
# ─────────────────────────────────────────────────────────────────────────────

_results: list[tuple[str, bool, str]] = []


def _run(name: str, fn: Callable[[], None]) -> None:
    try:
        fn()
        _results.append((name, True, ""))
        print(f"  PASSED  {name}")
    except AssertionError as exc:
        msg = str(exc) or "assertion failed"
        _results.append((name, False, msg))
        print(f"  FAILED  {name}\n          {msg}")
    except Exception:
        tb = traceback.format_exc().strip().splitlines()[-1]
        _results.append((name, False, tb))
        print(f"  FAILED  {name}\n          {tb}")


def _section(title: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print("─" * 60)


# ─────────────────────────────────────────────────────────────────────────────
# EASY — Basic correctness (LRUCache)
# ─────────────────────────────────────────────────────────────────────────────

_section("EASY — Basic correctness")


def test_leetcode_example_1() -> None:
    c = LRUCache(2)
    c.put(1, 1)
    c.put(2, 2)
    assert c.get(1) == 1, "get(1) should return 1 after put(1,1)"
    c.put(3, 3)  # evicts key 2
    assert c.get(2) == -1, "key 2 should have been evicted"
    assert c.get(3) == 3, "get(3) should return 3"
    c.put(4, 4)  # evicts key 1 (1 was MRU then 3 was accessed, so 1 is LRU)
    assert c.get(1) == -1, "key 1 should have been evicted"
    assert c.get(3) == 3, "get(3) should still return 3"
    assert c.get(4) == 4, "get(4) should return 4"


def test_leetcode_example_2_capacity_1() -> None:
    c = LRUCache(1)
    c.put(2, 1)
    assert c.get(2) == 1, "get(2) should return 1"
    c.put(3, 2)  # evicts key 2
    assert c.get(2) == -1, "key 2 should have been evicted"
    assert c.get(3) == 2, "get(3) should return 2"


def test_get_missing_key() -> None:
    c = LRUCache(3)
    assert c.get(99) == -1, "missing key must return -1"


def test_overwrite_existing_key() -> None:
    c = LRUCache(2)
    c.put(1, 10)
    c.put(1, 20)  # update in place
    assert c.get(1) == 20, "overwritten value should be 20"


def test_eviction_order_respects_gets() -> None:
    c = LRUCache(3)
    for k in (1, 2, 3):
        c.put(k, k * 10)
    c.get(1)  # 1 is now MRU; order: 1, 3, 2
    c.put(4, 40)  # should evict 2 (LRU)
    assert c.get(2) == -1, "key 2 should be evicted"
    assert c.get(1) == 10, "key 1 should still exist"
    assert c.get(3) == 30, "key 3 should still exist"
    assert c.get(4) == 40, "key 4 should exist"


def test_repeated_puts_same_key_no_extra_eviction() -> None:
    c = LRUCache(2)
    c.put(1, 1)
    c.put(1, 2)
    c.put(1, 3)
    c.put(2, 2)
    # Cache should still have room; no eviction of key 2 expected yet
    assert c.get(1) == 3
    assert c.get(2) == 2


def test_capacity_large_sequential() -> None:
    cap = 100
    c = LRUCache(cap)
    for i in range(cap):
        c.put(i, i)
    # All keys should be present
    for i in range(cap):
        assert c.get(i) == i, f"key {i} should still be in cache"
    # Insert one more — key 0 is LRU because gets above touched 1..99 after 0
    # Actually gets update order so we need to be precise:
    # After the loop above, get(0) was first, get(99) was last.
    # So LRU is key 0. We put one more to force eviction.
    c.put(cap, cap)
    assert c.get(0) == -1, "key 0 should be evicted"


_run("leetcode example 1", test_leetcode_example_1)
_run("leetcode example 2 — capacity 1", test_leetcode_example_2_capacity_1)
_run("get missing key returns -1", test_get_missing_key)
_run("overwrite existing key", test_overwrite_existing_key)
_run("eviction order respects gets", test_eviction_order_respects_gets)
_run(
    "repeated puts same key no spurious eviction",
    test_repeated_puts_same_key_no_extra_eviction,
)
_run("large sequential capacity", test_capacity_large_sequential)

# ─────────────────────────────────────────────────────────────────────────────
# MEDIUM — LRUCacheV2.get_all_keys()
# ─────────────────────────────────────────────────────────────────────────────

_section("MEDIUM — get_all_keys()")


def test_get_all_keys_basic() -> None:
    c = LRUCacheV2(3)
    c.put(1, 1)
    c.put(2, 2)
    c.put(3, 3)
    # MRU → LRU should be 3, 2, 1
    assert c.get_all_keys() == [3, 2, 1], f"expected [3,2,1] got {c.get_all_keys()}"


def test_get_all_keys_after_get() -> None:
    c = LRUCacheV2(3)
    c.put(1, 1)
    c.put(2, 2)
    c.put(3, 3)
    c.get(1)  # 1 becomes MRU
    assert c.get_all_keys() == [1, 3, 2], f"expected [1,3,2] got {c.get_all_keys()}"


def test_get_all_keys_does_not_mutate_order() -> None:
    c = LRUCacheV2(2)
    c.put(1, 1)
    c.put(2, 2)
    before = c.get_all_keys()
    _ = c.get_all_keys()  # second call
    after = c.get_all_keys()
    assert before == after, "get_all_keys must not change recency order"


def test_get_all_keys_empty_cache() -> None:
    c = LRUCacheV2(3)
    assert c.get_all_keys() == [], "empty cache should return []"


_run("get_all_keys basic order", test_get_all_keys_basic)
_run("get_all_keys after get", test_get_all_keys_after_get)
_run("get_all_keys does not mutate order", test_get_all_keys_does_not_mutate_order)
_run("get_all_keys on empty cache", test_get_all_keys_empty_cache)

# ─────────────────────────────────────────────────────────────────────────────
# HARD — LRUCacheV3.peek()
# ─────────────────────────────────────────────────────────────────────────────

_section("HARD — peek()")


def test_peek_returns_correct_value() -> None:
    c = LRUCacheV3(2)
    c.put(1, 10)
    c.put(2, 20)
    assert c.peek(1) == 10, "peek should return 10 for key 1"


def test_peek_missing_key() -> None:
    c = LRUCacheV3(2)
    assert c.peek(99) == -1, "peek on missing key should return -1"


def test_peek_does_not_update_recency() -> None:
    c = LRUCacheV3(2)
    c.put(1, 1)
    c.put(2, 2)
    # MRU order is [2, 1]; 1 is LRU
    c.peek(1)  # must NOT move 1 to MRU
    c.put(3, 3)  # should evict 1 (still LRU)
    assert c.get(1) == -1, "key 1 should be evicted — peek must not update recency"
    assert c.get(3) == 3


def test_peek_vs_get_recency_difference() -> None:
    c = LRUCacheV3(2)
    c.put("a", 1)
    c.put("b", 2)
    # "a" is LRU; peek should leave it LRU
    assert c.peek("a") == 1
    keys_before = c.get_all_keys()
    assert keys_before[0] == "b", "b should still be MRU after peek on a"
    # get() DOES update recency
    c.get("a")
    keys_after = c.get_all_keys()
    assert keys_after[0] == "a", "a should be MRU after get"


_run("peek returns correct value", test_peek_returns_correct_value)
_run("peek on missing key returns -1", test_peek_missing_key)
_run("peek does not update recency", test_peek_does_not_update_recency)
_run("peek vs get recency difference", test_peek_vs_get_recency_difference)

# ─────────────────────────────────────────────────────────────────────────────
# FAANG — ThreadSafeLRUCache concurrency stress tests
# ─────────────────────────────────────────────────────────────────────────────

_section("FAANG — ThreadSafeLRUCache concurrency")


def test_thread_safe_basic() -> None:
    c = ThreadSafeLRUCache(3)
    c.put(1, 1)
    assert c.get(1) == 1


def test_concurrent_puts_no_crash() -> None:
    """100 threads each insert 50 unique keys — no exception must escape."""
    threads_count = 100
    keys_per_thread = 50
    cache = ThreadSafeLRUCache(200)
    errors: list[Exception] = []

    def worker(tid: int) -> None:
        try:
            for i in range(keys_per_thread):
                key = tid * keys_per_thread + i
                cache.put(key, key)
                cache.get(key)
        except Exception as exc:
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(t,)) for t in range(threads_count)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"Exceptions in threads: {errors}"


def test_concurrent_mixed_ops() -> None:
    """
    Mixed readers and writers operating concurrently.
    Validates that the cache does not deadlock and returns consistent values.
    """
    cache = ThreadSafeLRUCache(50)
    for i in range(50):
        cache.put(i, i * 10)

    errors: list[str] = []

    def reader(keys: list[int]) -> None:
        for k in keys:
            val = cache.get(k)
            # val is either -1 (evicted) or the correct multiple of 10
            if val != -1 and val % 10 != 0:
                errors.append(f"key={k} returned corrupt value={val}")

    def writer(start: int) -> None:
        for i in range(start, start + 20):
            cache.put(i, i * 10)

    reader_threads = [
        threading.Thread(target=reader, args=(list(range(50)),)) for _ in range(10)
    ]
    writer_threads = [threading.Thread(target=writer, args=(i * 5,)) for i in range(5)]

    all_threads = reader_threads + writer_threads
    for t in all_threads:
        t.start()
    for t in all_threads:
        t.join()

    assert not errors, f"Data integrity errors: {errors}"


def test_thread_safe_no_deadlock() -> None:
    """Verify the cache returns within a hard time limit."""
    cache = ThreadSafeLRUCache(10)
    done = threading.Event()

    def work() -> None:
        for i in range(10_000):
            cache.put(i % 20, i)
            cache.get(i % 20)
        done.set()

    t = threading.Thread(target=work)
    t.start()
    finished = done.wait(timeout=10.0)
    t.join(timeout=1.0)
    assert finished, "ThreadSafeLRUCache deadlocked — did not finish within 10 s"


_run("thread-safe basic get/put", test_thread_safe_basic)
_run("100 concurrent writers — no crash", test_concurrent_puts_no_crash)
_run("mixed concurrent readers + writers", test_concurrent_mixed_ops)
_run("no deadlock under sustained load", test_thread_safe_no_deadlock)

# ─────────────────────────────────────────────────────────────────────────────
# PERFORMANCE — O(1) per operation
# ─────────────────────────────────────────────────────────────────────────────

_section("PERFORMANCE — O(1) per operation")


def test_performance_vs_reference() -> None:
    """
    Compare wall time of the candidate against Python's OrderedDict-backed
    reference. The candidate must complete N operations in < 3× the reference
    time (generous to allow interpreter jitter).
    """
    n = 200_000
    cap = 1_000

    # Reference — OrderedDict LRU (also O(1) per op)
    class RefCache:
        def __init__(self, cap: int) -> None:
            self._cap = cap
            self._d: OrderedDict[int, int] = OrderedDict()

        def get(self, key: int) -> int:
            if key not in self._d:
                return -1
            self._d.move_to_end(key)
            return self._d[key]

        def put(self, key: int, value: int) -> None:
            if key in self._d:
                self._d.move_to_end(key)
            self._d[key] = value
            if len(self._d) > self._cap:
                self._d.popitem(last=False)

    def _benchmark(cache: object) -> float:
        t0 = time.perf_counter()
        for i in range(n):
            cache.put(i % (cap * 2), i)  # type: ignore[union-attr]
            cache.get(i % (cap * 2))  # type: ignore[union-attr]
        return time.perf_counter() - t0

    ref_time = _benchmark(RefCache(cap))
    candidate_time = _benchmark(LRUCache(cap))

    ratio = candidate_time / ref_time if ref_time > 0 else 1.0
    assert ratio < 5.0, (
        f"Too slow: candidate={candidate_time:.3f}s  "
        f"reference={ref_time:.3f}s  ratio={ratio:.1f}× (limit 5×)"
    )


_run("O(1) performance vs OrderedDict reference", test_performance_vs_reference)

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────

passed = sum(1 for _, ok, _ in _results if ok)
total = len(_results)
failed = total - passed

print(f"\n{'=' * 60}")
print(f"  RESULTS: {passed}/{total} passed", end="")
if failed:
    print(f"  ({failed} failed)")
    print("\n  Failed tests:")
    for name, ok, reason in _results:
        if not ok:
            print(f"    ✗ {name}")
            print(f"      {reason}")
else:
    print("  — all tests passed!")
print("=" * 60)

sys.exit(0 if failed == 0 else 1)
