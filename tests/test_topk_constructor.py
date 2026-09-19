"""Constructor tests: capacity validation, empty state, and the capacity property."""

from __future__ import annotations

import pytest
from conftest import make_top_k


def test_capacity_one_is_valid() -> None:
    top_k = make_top_k(1)
    assert top_k.capacity == 1
    assert len(top_k) == 0


@pytest.mark.parametrize("capacity", [0, -1, -10])
def test_capacity_below_one_raises(capacity: int) -> None:
    with pytest.raises(ValueError, match="capacity must be >= 1"):
        make_top_k(capacity)


def test_capacity_property_matches_constructor() -> None:
    top_k = make_top_k(7)
    assert top_k.capacity == 7


def test_empty_state() -> None:
    top_k = make_top_k(5)
    assert len(top_k) == 0
    assert top_k.smallest is None
    assert top_k.items == []
    assert not top_k
