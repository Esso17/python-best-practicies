"""
================================================================================
MLOPS INTERVIEW EXERCISE #01 — LRU Cache from Scratch  |  SOLUTION
================================================================================

APPROACH
--------
Two data structures work together:

  hashmap   : key → Node          O(1) lookup
  DLL       : ordered by recency  O(1) move-to-front and remove-tail

Sentinel head/tail nodes eliminate null checks on every insert/remove:

    head ↔ [most recent] ↔ … ↔ [least recent] ↔ tail

COMPLEXITY
----------
  get()   O(1) time  |  O(1) extra space
  put()   O(1) time  |  O(1) extra space
  Space   O(capacity) total
"""

from __future__ import annotations

import threading

# ─────────────────────────────────────────────────────────────────────────────
# Shared node type
# ─────────────────────────────────────────────────────────────────────────────


class Node:
    """Doubly linked list node carrying a cache key-value pair."""

    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key: int = 0, value: int = 0) -> None:
        self.key = key
        self.value = value
        self.prev: Node | None = None
        self.next: Node | None = None


# ─────────────────────────────────────────────────────────────────────────────
# EASY — Basic LRU Cache
# ─────────────────────────────────────────────────────────────────────────────


class LRUCache:
    """
    LRU Cache — O(1) get and put.

    Internal layout (sentinels never hold real data):

        head <-> [MRU] <-> ... <-> [LRU] <-> tail

    get  : hashmap lookup → move-to-front
    put  : update-or-create at front; evict from tail when over capacity
    """

    def __init__(self, capacity: int) -> None:
        self._cap: int = capacity
        self._map: dict[int, Node] = {}

        # Sentinels — avoids None checks on every link/unlink
        self._head = Node()
        self._tail = Node()
        self._head.next = self._tail
        self._tail.prev = self._head

    # ── private helpers ───────────────────────────────────────────────────────

    def _remove(self, node: Node) -> None:
        """O(1) — detach node from wherever it sits in the list."""
        prev, nxt = node.prev, node.next
        prev.next = nxt  # type: ignore[union-attr]
        nxt.prev = prev  # type: ignore[union-attr]

    def _insert_front(self, node: Node) -> None:
        """O(1) — splice node in as the most-recently-used position."""
        node.prev = self._head
        node.next = self._head.next
        self._head.next.prev = node  # type: ignore[union-attr]
        self._head.next = node

    # ── public API ────────────────────────────────────────────────────────────

    def get(self, key: int) -> int:
        """Return cached value or -1; updates recency."""
        if key not in self._map:
            return -1
        node = self._map[key]
        # Move to front — O(1)
        self._remove(node)
        self._insert_front(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        """Insert/update key; evicts LRU entry when capacity is exceeded."""
        if key in self._map:
            node = self._map[key]
            node.value = value
            self._remove(node)
            self._insert_front(node)
            return

        # New entry
        node = Node(key, value)
        self._map[key] = node
        self._insert_front(node)

        if len(self._map) > self._cap:
            # Evict least-recently-used (node just before tail sentinel)
            lru = self._tail.prev
            self._remove(lru)  # type: ignore[arg-type]
            del self._map[lru.key]  # type: ignore[union-attr]


# ─────────────────────────────────────────────────────────────────────────────
# MEDIUM — Ordered inspection
# ─────────────────────────────────────────────────────────────────────────────


class LRUCacheV2(LRUCache):
    """Adds ordered key inspection — does not mutate recency order."""

    def get_all_keys(self) -> list[int]:
        """
        Return keys sorted from most-recently-used to least-recently-used.

        O(n) time — traverses the doubly linked list once.
        """
        keys: list[int] = []
        cur = self._head.next
        while cur is not self._tail:
            keys.append(cur.key)  # type: ignore[union-attr]
            cur = cur.next  # type: ignore[union-attr]
        return keys


# ─────────────────────────────────────────────────────────────────────────────
# HARD — Non-mutating peek
# ─────────────────────────────────────────────────────────────────────────────


class LRUCacheV3(LRUCacheV2):
    """Adds peek — reads a value without touching recency order."""

    def peek(self, key: int) -> int:
        """
        Return value for key WITHOUT updating recency, or -1 if absent.

        Useful for observability probes that must not distort eviction behaviour.
        O(1) time.
        """
        node = self._map.get(key)
        return node.value if node is not None else -1


# ─────────────────────────────────────────────────────────────────────────────
# FAANG EXTENSION — Thread-safe LRU Cache
# ─────────────────────────────────────────────────────────────────────────────


class ThreadSafeLRUCache:
    """
    Thread-safe LRU Cache.

    Wraps LRUCacheV3 with an RLock so get/put can be called from any number
    of concurrent threads without data races.

    Design notes
    ------------
    - RLock (re-entrant) allows the same thread to acquire the lock multiple
      times — useful if put() internally calls get() or vice-versa.
    - The lock is held for the entire duration of each public method to keep
      the list + hashmap consistent as one atomic unit.
    - For higher concurrency under read-heavy workloads you could use a
      read-write lock (e.g. `rwlock` package), but that adds complexity and
      is rarely needed in an interview setting.
    """

    def __init__(self, capacity: int) -> None:
        self._cache = LRUCacheV3(capacity)
        self._lock = threading.RLock()

    def get(self, key: int) -> int:
        with self._lock:
            return self._cache.get(key)

    def put(self, key: int, value: int) -> None:
        with self._lock:
            self._cache.put(key, value)

    def peek(self, key: int) -> int:
        with self._lock:
            return self._cache.peek(key)

    def get_all_keys(self) -> list[int]:
        with self._lock:
            return self._cache.get_all_keys()
