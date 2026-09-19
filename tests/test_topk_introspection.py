"""Introspection tests: len, smallest, and items snapshot."""

from __future__ import annotations

from conftest import make_top_k, url_risk, urls_of


def test_len_grows_then_caps_at_capacity() -> None:
    top_k = make_top_k(2)
    assert len(top_k) == 0
    top_k.add(url_risk("https://a.example", 10.0))
    assert len(top_k) == 1
    top_k.add(url_risk("https://b.example", 20.0))
    assert len(top_k) == 2
    top_k.add(url_risk("https://c.example", 30.0))
    assert len(top_k) == 2


def test_smallest_is_lowest_stored_priority() -> None:
    top_k = make_top_k(3)
    top_k.add(url_risk("https://low.example", 10.0))
    top_k.add(url_risk("https://high.example", 90.0))
    top_k.add(url_risk("https://mid.example", 50.0))
    assert top_k.smallest is not None
    assert top_k.smallest.url == "https://low.example"

    top_k.add(url_risk("https://upper.example", 70.0))
    assert top_k.smallest is not None
    assert top_k.smallest.url == "https://mid.example"
    assert urls_of(top_k) == {
        "https://high.example",
        "https://mid.example",
        "https://upper.example",
    }


def test_items_is_list_snapshot_of_same_objects() -> None:
    top_k = make_top_k(3)
    first = url_risk("https://a.example", 10.0)
    second = url_risk("https://b.example", 20.0)
    top_k.add(first)
    top_k.add(second)

    snapshot = top_k.items
    assert isinstance(snapshot, list)
    assert len(snapshot) == 2
    assert any(item is first for item in snapshot)
    assert any(item is second for item in snapshot)

    top_k.add(url_risk("https://c.example", 30.0))
    assert len(snapshot) == 2
    assert len(top_k.items) == 3
