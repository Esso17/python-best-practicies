"""
================================================================================
MLOPS INTERVIEW EXERCISE #01 — LRU Cache from Scratch
================================================================================

DIFFICULTY: Easy → Medium → Hard → FAANG Extension

PROBLEM STATEMENT
-----------------
Implement a Least Recently Used (LRU) Cache from scratch in Python.

An LRU cache evicts the least recently used item when it reaches capacity.
Both get and put operations must count as a "use" (i.e., they update recency).

CONSTRAINTS
-----------
- 1 <= capacity <= 3_000
- O(1) average time complexity for get()
- O(1) average time complexity for put()
- -∞ <= key, value <= ∞  (any hashable key, any value)
- Do NOT use OrderedDict (that would defeat the purpose)
- You MUST implement your own doubly linked list + hashmap

INTERFACE
---------
class LRUCache:
    def __init__(self, capacity: int) -> None
    def get(self, key: int) -> int          # return -1 if not found
    def put(self, key: int, value: int) -> None

EXAMPLES
--------
Example 1:
    cache = LRUCache(2)
    cache.put(1, 1)     # cache: {1=1}
    cache.put(2, 2)     # cache: {1=1, 2=2}
    cache.get(1)        # returns 1, cache: {2=2, 1=1}  (1 is now most recent)
    cache.put(3, 3)     # evicts key 2, cache: {1=1, 3=3}
    cache.get(2)        # returns -1 (not found)
    cache.get(3)        # returns 3
    cache.put(4, 4)     # evicts key 1, cache: {3=3, 4=4}
    cache.get(1)        # returns -1 (not found)
    cache.get(3)        # returns 3
    cache.get(4)        # returns 4

Example 2 (edge case — capacity 1):
    cache = LRUCache(1)
    cache.put(2, 1)     # cache: {2=1}
    cache.get(2)        # returns 1
    cache.put(3, 2)     # evicts key 2, cache: {3=2}
    cache.get(2)        # returns -1
    cache.get(3)        # returns 2

COMPLEXITY TARGETS
------------------
    get()  → O(1) time, O(1) space
    put()  → O(1) time, O(1) space
    Total space → O(capacity)

DIFFICULTY LEVELS
-----------------
Easy      : Implement basic LRUCache (get + put, O(1))
Medium    : Add get_all_keys() returning keys from most-recent to least-recent
Hard      : Add peek(key) that reads WITHOUT updating recency
FAANG Ext.: Implement ThreadSafeLRUCache using locks — must pass concurrent stress tests

================================================================================
YOUR TASK
================================================================================
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# EASY  — Basic LRU Cache
# ─────────────────────────────────────────────────────────────────────────────


class Node:
    """Doubly linked list node."""

    def __init__(self, key: int = 0, value: int = 0) -> None:
        # TODO: store key, value, and pointers to prev/next nodes
        pass


class LRUCache:
    """
    LRU Cache backed by a doubly linked list + hashmap.

    Sentinel head/tail nodes simplify edge cases — no null checks needed.
    head.next  = most recently used
    tail.prev  = least recently used
    """

    def __init__(self, capacity: int) -> None:
        # TODO: initialise capacity, hashmap, and sentinel head/tail nodes
        pass

    # ── internal helpers ──────────────────────────────────────────────────────

    def _remove(self, node: Node) -> None:
        """Detach a node from the linked list."""
        # TODO: unlink node from its neighbours
        pass

    def _insert_front(self, node: Node) -> None:
        """Insert node right after the sentinel head (= most recently used)."""
        # TODO: splice node in between head and head.next
        pass

    # ── public API ────────────────────────────────────────────────────────────

    def get(self, key: int) -> int:
        """Return value for key, or -1 if absent. Marks key as most recently used."""
        # TODO: look up key in hashmap
        # TODO: if found, move node to front and return value
        # TODO: if not found, return -1
        pass

    def put(self, key: int, value: int) -> None:
        """Insert or update key/value. Evict LRU item if over capacity."""
        # TODO: if key exists, update value and move to front
        # TODO: if key is new, create node and insert at front
        # TODO: if over capacity, remove the node at tail.prev and delete from hashmap
        pass


# ─────────────────────────────────────────────────────────────────────────────
# MEDIUM  — Ordered inspection
# ─────────────────────────────────────────────────────────────────────────────


class LRUCacheV2(LRUCache):
    """Extends LRUCache with an ordered key inspection method."""

    def get_all_keys(self) -> list[int]:
        """
        Return all keys from most-recently-used to least-recently-used.

        Does NOT modify recency order.
        """
        # TODO: traverse the linked list from head.next to tail.prev
        # TODO: collect and return keys in that order
        pass


# ─────────────────────────────────────────────────────────────────────────────
# HARD  — Non-mutating peek
# ─────────────────────────────────────────────────────────────────────────────


class LRUCacheV3(LRUCacheV2):
    """Extends LRUCacheV2 with a peek operation that does not affect recency."""

    def peek(self, key: int) -> int:
        """
        Return value for key WITHOUT updating its recency, or -1 if absent.

        Use case: cache warming / monitoring probes that must not pollute LRU order.
        """
        # TODO: look up key in hashmap WITHOUT moving node to front
        pass


# ─────────────────────────────────────────────────────────────────────────────
# FAANG EXTENSION  — Thread-safe LRU Cache
# ─────────────────────────────────────────────────────────────────────────────


class ThreadSafeLRUCache:
    """
    Thread-safe LRU Cache.

    Requirements:
    - All public methods must be safe to call from multiple threads simultaneously.
    - Use the smallest lock scope that maintains correctness.
    - Prefer RLock over Lock to allow re-entrant calls from within the class.
    """

    def __init__(self, capacity: int) -> None:
        # TODO: wrap an LRUCache instance
        # TODO: initialise a threading.RLock
        pass

    def get(self, key: int) -> int:
        # TODO: acquire lock, delegate to inner cache, release lock
        pass

    def put(self, key: int, value: int) -> None:
        # TODO: acquire lock, delegate to inner cache, release lock
        pass
