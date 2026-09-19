"""Shared SOC-style URL-risk items and TopK factories for unit tests."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from top_k import TopK


@dataclass(slots=True)
class UrlRisk:
    """A URL scored by a detector or threat-intel feed.

    Fields are typical of a SOC enrichment record: the indicator, a 0-100
    risk score, the producing source, and that source's confidence.
    """

    url: str
    score: float
    source: str
    confidence: float

    def __lt__(self, other: object) -> bool:
        raise TypeError("UrlRisk is not ordered")


def url_risk(
    url: str,
    score: float,
    source: str = "sandbox",
    confidence: float = 1.0,
) -> UrlRisk:
    return UrlRisk(url=url, score=score, source=source, confidence=confidence)


def by_score(item: UrlRisk) -> float:
    return item.score


def by_negated_score(item: UrlRisk) -> float:
    return -item.score


def make_top_k(capacity: int, *, invert: bool = False) -> TopK[UrlRisk]:
    """Build a ``TopK[UrlRisk]``.

    Default keeps the *highest* risk scores. ``invert=True`` negates the
    score so the structure keeps the *lowest* risk scores (min-k).
    """
    priority = by_negated_score if invert else by_score
    return TopK[UrlRisk](capacity, priority=priority)


def urls_of(top_k: TopK[UrlRisk]) -> set[str]:
    return {item.url for item in top_k.items}


@pytest.fixture
def url_risks() -> list[UrlRisk]:
    """Distinct ``*.example`` URLs with a spread of risk scores."""
    return [
        url_risk("https://phish.example/login", 95.0, source="urlhaus"),
        url_risk("https://malware.example/payload", 88.0, source="sandbox"),
        url_risk("https://steal.example/oauth", 72.0, source="urlhaus"),
        url_risk("https://ads.example/banner", 40.0, source="sandbox"),
        url_risk("https://docs.example/readme", 22.0, source="sandbox"),
        url_risk("https://cdn.example/static", 8.0, source="sandbox"),
        url_risk("https://status.example/health", 3.0, source="sandbox"),
    ]
