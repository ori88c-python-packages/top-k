"""top-k — keep the highest-priority k items in O(k) space."""

from __future__ import annotations

from importlib.metadata import version

from top_k._top_k import TopK

__version__ = version("top-k")

__all__ = ["TopK"]
