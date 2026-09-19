"""Insertion tests: eviction, ties, return value, min-k, and non-comparable items."""

from __future__ import annotations

from conftest import UrlRisk, make_top_k, url_risk, urls_of


def test_below_capacity_always_stores() -> None:
    top_k = make_top_k(3)
    assert top_k.add(url_risk("https://a.example", 10.0)) is True
    assert top_k.add(url_risk("https://b.example", 20.0)) is True
    assert urls_of(top_k) == {"https://a.example", "https://b.example"}
    assert len(top_k) == 2


def test_lower_score_rejected_at_capacity() -> None:
    top_k = make_top_k(2)
    assert top_k.add(url_risk("https://high.example", 80.0)) is True
    assert top_k.add(url_risk("https://mid.example", 50.0)) is True
    assert top_k.add(url_risk("https://low.example", 10.0)) is False
    assert urls_of(top_k) == {"https://high.example", "https://mid.example"}


def test_higher_score_evicts_current_smallest() -> None:
    top_k = make_top_k(2)
    top_k.add(url_risk("https://high.example", 80.0))
    top_k.add(url_risk("https://mid.example", 50.0))
    assert top_k.add(url_risk("https://higher.example", 90.0)) is True
    assert urls_of(top_k) == {"https://high.example", "https://higher.example"}


def test_equal_priority_at_capacity_keeps_existing_item() -> None:
    top_k = make_top_k(2)
    top_k.add(url_risk("https://first.example", 50.0))
    top_k.add(url_risk("https://second.example", 50.0))
    assert top_k.add(url_risk("https://challenger.example", 50.0)) is False
    assert urls_of(top_k) == {"https://first.example", "https://second.example"}


def test_many_inserts_stay_at_capacity(url_risks: list[UrlRisk]) -> None:
    top_k = make_top_k(3)
    stored = [top_k.add(item) for item in url_risks]
    assert len(top_k) == 3
    assert top_k.capacity == 3
    assert any(stored) and not all(stored)
    assert urls_of(top_k) == {
        "https://phish.example/login",
        "https://malware.example/payload",
        "https://steal.example/oauth",
    }


def test_min_k_keeps_lowest_scores(url_risks: list[UrlRisk]) -> None:
    """Negated score keeps the least-risky URLs (e.g. allowlist review)."""
    top_k = make_top_k(3, invert=True)
    for item in url_risks:
        top_k.add(item)
    assert len(top_k) == 3
    assert urls_of(top_k) == {
        "https://status.example/health",
        "https://cdn.example/static",
        "https://docs.example/readme",
    }
    assert top_k.smallest is not None
    # Heap root is the lowest *priority* among kept items: -22 (score 22).
    assert top_k.smallest.url == "https://docs.example/readme"


def test_equal_scores_below_capacity_never_compare_items() -> None:
    top_k = make_top_k(3)
    assert top_k.add(url_risk("https://a.example", 10.0)) is True
    assert top_k.add(url_risk("https://b.example", 10.0)) is True
    assert top_k.add(url_risk("https://c.example", 10.0)) is True
    assert urls_of(top_k) == {
        "https://a.example",
        "https://b.example",
        "https://c.example",
    }
