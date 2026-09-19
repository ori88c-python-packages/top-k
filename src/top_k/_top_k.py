from __future__ import annotations

import heapq
from collections.abc import Callable
from typing import NamedTuple


class _HeapItem[T](NamedTuple):
    """One entry in the internal min-heap.

    ``heapq`` compares entries left to right. ``unique_tiebreaker`` is a
    strictly increasing id assigned at insert time, so when two priorities
    are equal the comparison never reaches ``item``. Items therefore do not
    need ``__lt__``.
    """

    priority: int | float
    unique_tiebreaker: int
    item: T


class TopK[T]:
    """Keep the *capacity* highest-priority items in O(k) space.

    Internally this is a min-heap of :class:`_HeapItem` entries. The heap
    root is the **lowest** stored priority — the eviction candidate when
    the structure is full. ``unique_tiebreaker`` is a monotonic id so
    ``heapq`` never falls through to comparing the raw items, which may
    not implement ``__lt__``.

    Usage::

        top_k = TopK[Candidate](10, priority=lambda c: c.score)
        top_k.add(candidate)
        lowest = top_k.smallest
        stored = top_k.items
    """

    def __init__(self, capacity: int, *, priority: Callable[[T], int | float]) -> None:
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        self._capacity = capacity
        self._priority = priority
        self._min_heap: list[_HeapItem[T]] = []
        self._tiebreaker_counter = 0

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    @property
    def capacity(self) -> int:
        """Maximum number of items this instance will store."""
        return self._capacity

    @property
    def smallest(self) -> T | None:
        """Lowest-priority item currently stored, or ``None`` if empty.

        This is the min-heap root — the eviction candidate when the
        structure is at capacity — not the highest-priority item.
        """
        if not self._min_heap:
            return None
        return self._min_heap[0].item

    @property
    def items(self) -> list[T]:
        """Snapshot of stored items in heap order (not sorted by priority).

        Warning: this list holds the same item objects stored internally.
        Changing an item's priority (or any field that ``priority`` reads)
        breaks the heap. Treat those items as read-only.
        """
        return [entry.item for entry in self._min_heap]

    def __len__(self) -> int:
        """Number of items currently stored."""
        return len(self._min_heap)

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def add(self, item: T) -> bool:
        """Consider *item* for inclusion. Return ``True`` if it was stored.

        If the structure is below capacity the item is always stored. If it
        is full, the item replaces the current lowest-priority entry only
        when its priority is **strictly greater**. Equal priorities keep
        the item that is already stored.
        """
        priority = self._priority(item)
        entry = _HeapItem(priority, self._tiebreaker_counter, item)
        if len(self._min_heap) < self._capacity:
            heapq.heappush(self._min_heap, entry)
            self._tiebreaker_counter += 1
            return True
        if priority > self._min_heap[0].priority:
            heapq.heapreplace(self._min_heap, entry)
            self._tiebreaker_counter += 1
            return True
        return False

    def clear(self) -> None:
        """Remove all items and reset the tiebreaker counter to ``0``."""
        self._min_heap.clear()
        self._tiebreaker_counter = 0
