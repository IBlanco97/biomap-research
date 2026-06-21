from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Article:
    pmid: str
    title: str
    abstract: str
    journal: str = ""
    year: str = ""
    doi: str = ""
    url: str = ""


@dataclass
class ArticleAnalysis:
    article: Article
    genes: list[str] = field(default_factory=list)
    diseases: list[str] = field(default_factory=list)
    treatments: list[str] = field(default_factory=list)
    outcomes: list[str] = field(default_factory=list)
    findings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Relation:
    source: str
    target: str
    relation_type: str
    pmid: str
    evidence: str
