# top-k

[![CI](https://github.com/ori88c-python-packages/top-k/actions/workflows/ci.yml/badge.svg)](https://github.com/ori88c-python-packages/top-k/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/top-k.svg)](https://pypi.org/project/top-k/)
[![Python versions](https://img.shields.io/pypi/pyversions/top-k.svg)](https://pypi.org/project/top-k/)
[![License](https://img.shields.io/pypi/l/top-k.svg)](LICENSE)

Keep the top-k highest-priority items in O(k) space. Zero runtime dependencies.

Internally, `TopK` maintains a min-heap of `(priority, unique_tiebreaker, item)` entries via the standard-library `heapq`. The heap root is the **lowest** stored priority — the eviction candidate when the structure is full. Each insertion compares the new item's priority against that root and replaces it only when the candidate is strictly better, so memory stays proportional to *k* regardless of how many items you consider.

## Table of Contents

- [Key Features](#key-features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API](#api)
- [Use Case: Streaming Top-K](#use-case-streaming-top-k)
- [Priority Mutation](#priority-mutation)
- [Development](#development)
- [License](#license)

## Key Features

- **High-level abstraction** for "keep the best k items". The priority is a callable on your item type — no need to wrap complex objects in `(score, item)` tuples yourself. Return `-score` to keep the k *least* risky items instead.
- **O(k) space.** Only the current top-k is stored. Additional candidates are either rejected or swapped with the current lowest-priority entry.
- **Generic and fully typed.** `TopK[T]` accepts a `priority` callable of type `Callable[[T], int | float]`, so type checkers can validate that every stored item is a `T`. Ships with a `py.typed` marker ([PEP 561](https://peps.python.org/pep-0561/)). Works out of the box with mypy, pyright, and other type checkers.
- **Items need not be comparable.** A monotonic unique tiebreaker is stored alongside each priority so `heapq` never falls through to `T.__lt__`.
- **Zero runtime dependencies.** The package uses only the Python standard library (`heapq`).
- **Tested** on Python 3.12 through 3.14.

## Installation

```bash
pip install top-k
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add top-k
```

## Quick Start

```python
from dataclasses import dataclass

from top_k import TopK


@dataclass(slots=True)
class UrlRisk:
    url: str
    score: float
    source: str
    confidence: float


top_k = TopK[UrlRisk](3, priority=lambda u: u.score)

for item in (
    UrlRisk("https://phish.example/login", 95.0, "urlhaus", 0.9),
    UrlRisk("https://malware.example/payload", 88.0, "sandbox", 0.8),
    UrlRisk("https://steal.example/oauth", 72.0, "urlhaus", 0.7),
    UrlRisk("https://ads.example/banner", 40.0, "sandbox", 0.6),
    UrlRisk("https://cdn.example/static", 8.0, "sandbox", 0.9),
):
    top_k.add(item)

assert len(top_k) == 3
assert top_k.smallest is not None and top_k.smallest.url == "https://steal.example/oauth"
```

`smallest` is the **lowest** priority among the items currently stored (the heap root), not the highest-scoring URL. `items` yields stored objects in **heap order**, not sorted by priority.

## API

| Member | Kind | Description |
|---|---|---|
| `TopK(capacity, *, priority)` | constructor | Store at most *capacity* items. *priority* maps an item of type `T` to a number. `capacity` must be `>= 1`. |
| `add(item)` | method | Consider *item* for inclusion. Returns `True` if it was stored. At capacity, replaces the current lowest-priority entry only when *item*'s priority is **strictly greater**. O(log k). |
| `smallest` | property | Lowest-priority item currently stored, or `None` if empty. O(1). |
| `capacity` | property | Maximum number of items this instance will store. |
| `len(top_k)` | `len()` | Number of items currently stored. O(1). |
| `items` | property | Snapshot `list` of stored items in heap order (not sorted by priority). O(k). See [Priority Mutation](#priority-mutation). |
| `clear()` | method | Remove all items and reset the tiebreaker counter to `0`. |

## Use Case: Streaming Top-K

[`heapq.nlargest`](https://docs.python.org/3/library/heapq.html#heapq.nlargest) is the right tool when every candidate is already in memory. `TopK` is for an **online** stream — a log file, a socket, or an object-store listing — where lines arrive one at a time and you must not retain the full collection.

```python
from collections.abc import AsyncIterator
from dataclasses import dataclass

from top_k import TopK


@dataclass(slots=True)
class LogLine:
    severity: int
    message: str


async def iter_log_lines(path: str) -> AsyncIterator[LogLine]:
    ...


async def top_errors(path: str) -> TopK[LogLine]:
    chosen = TopK[LogLine](10, priority=lambda line: line.severity)
    async for line in iter_log_lines(path):
        chosen.add(line)
    # At most 10 lines retained, even if the stream has millions.
    return chosen
```

Peak memory is O(k), independent of stream length.

## Priority Mutation

`items` returns the **same item objects** held internally. Changing an item's priority (or any field that `priority` reads) **breaks heap correctness**. Treat those items as read-only.

Stored priorities are computed at `add` time; this structure does not re-sort if you change an item later. The unique tiebreaker prevents `heapq` from comparing the raw items, so in-place changes will not raise `TypeError` — they still corrupt the heap.

## Development

```bash
git clone https://github.com/ori88c-python-packages/top-k.git
cd top-k
uv sync

# Run tests
uv run pytest

# Lint and format
uv run ruff check .
uv run ruff format .

# Type check
uv run mypy src
```

## License

[Apache 2.0](LICENSE)
