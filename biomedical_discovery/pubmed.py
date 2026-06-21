from __future__ import annotations

import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from .models import Article

NCBI_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


class PubMedError(RuntimeError):
    pass


def search_pubmed(query: str, max_results: int = 20, email: str | None = None) -> list[str]:
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "xml",
        "retmax": str(max_results),
        "sort": "relevance",
    }
    if email:
        params["email"] = email

    root = _get_xml("esearch.fcgi", params)
    ids = [node.text for node in root.findall(".//Id") if node.text]
    return ids


def fetch_articles(pmids: list[str], email: str | None = None) -> list[Article]:
    if not pmids:
        return []

    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
    }
    if email:
        params["email"] = email

    root = _get_xml("efetch.fcgi", params)
    return [_parse_article(node) for node in root.findall(".//PubmedArticle")]


def search_and_fetch(query: str, max_results: int = 20, email: str | None = None) -> list[Article]:
    pmids = search_pubmed(query, max_results=max_results, email=email)
    time.sleep(0.34)
    return fetch_articles(pmids, email=email)


def _get_xml(endpoint: str, params: dict[str, str]) -> ET.Element:
    url = f"{NCBI_BASE}/{endpoint}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={"User-Agent": "busqueda-bioedica-mvp/0.1"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = response.read()
    except OSError as exc:
        raise PubMedError(f"No se pudo consultar PubMed: {exc}") from exc

    try:
        return ET.fromstring(payload)
    except ET.ParseError as exc:
        raise PubMedError("PubMed devolvio XML invalido") from exc


def _parse_article(node: ET.Element) -> Article:
    pmid = _text(node.find(".//MedlineCitation/PMID"))
    title = _text(node.find(".//ArticleTitle"))
    abstract_parts = [
        "".join(part.itertext()).strip()
        for part in node.findall(".//Abstract/AbstractText")
        if "".join(part.itertext()).strip()
    ]
    journal = _text(node.find(".//Journal/Title"))
    year = _first_text(
        node,
        [
            ".//PubDate/Year",
            ".//ArticleDate/Year",
            ".//DateCompleted/Year",
        ],
    )
    doi = ""
    for article_id in node.findall(".//ArticleId"):
        if article_id.attrib.get("IdType") == "doi" and article_id.text:
            doi = article_id.text.strip()
            break

    return Article(
        pmid=pmid,
        title=title,
        abstract=" ".join(abstract_parts),
        journal=journal,
        year=year,
        doi=doi,
        url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "",
    )


def _text(node: ET.Element | None) -> str:
    return "".join(node.itertext()).strip() if node is not None else ""


def _first_text(root: ET.Element, paths: list[str]) -> str:
    for path in paths:
        value = _text(root.find(path))
        if value:
            return value
    return ""
