"""Clear tests: empty reset, capacity preserved, and tiebreaker reset."""

from __future__ import annotations

from conftest import make_top_k, url_risk, urls_of


def test_clear_on_empty_is_a_no_op() -> None:
    top_k = make_top_k(3)
    top_k.clear()
    assert len(top_k) == 0
    assert top_k.smallest is None
    assert top_k.items == []
    assert top_k.capacity == 3


def test_clear_drops_items_and_preserves_capacity() -> None:
    top_k = make_top_k(3)
    top_k.add(url_risk("https://a.example", 10.0))
    top_k.add(url_risk("https://b.example", 90.0))
    top_k.clear()
    assert len(top_k) == 0
    assert top_k.smallest is None
    assert top_k.items == []
    assert top_k.capacity == 3
    assert not top_k


def test_can_fill_after_clear() -> None:
    top_k = make_top_k(2)
    top_k.add(url_risk("https://old.example", 99.0))
    top_k.clear()
    assert top_k.add(url_risk("https://new-a.example", 15.0)) is True
    assert top_k.add(url_risk("https://new-b.example", 25.0)) is True
    assert urls_of(top_k) == {"https://new-a.example", "https://new-b.example"}


def test_equal_scores_after_clear_never_compare_items() -> None:
    top_k = make_top_k(2)
    top_k.add(url_risk("https://a.example", 5.0))
    top_k.add(url_risk("https://b.example", 5.0))
    top_k.clear()
    assert top_k.add(url_risk("https://c.example", 5.0)) is True
    assert top_k.add(url_risk("https://d.example", 5.0)) is True
    assert urls_of(top_k) == {"https://c.example", "https://d.example"}
