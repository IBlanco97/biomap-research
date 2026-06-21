from __future__ import annotations

import re

from .models import Article, ArticleAnalysis

GENE_ALIASES = {
    "ABL1",
    "ALK",
    "ATM",
    "BCR",
    "BCR-ABL1",
    "BRCA1",
    "BRCA2",
    "CDKN2A",
    "CEBPA",
    "CREBBP",
    "CRLF2",
    "ETV6",
    "ETV6-RUNX1",
    "FLT3",
    "GATA2",
    "IKZF1",
    "JAK2",
    "KRAS",
    "KMT2A",
    "MLL",
    "NF1",
    "NOTCH1",
    "NRAS",
    "PAX5",
    "PTEN",
    "PTPN11",
    "RB1",
    "RUNX1",
    "SH2B3",
    "TP53",
}

DISEASE_PATTERNS = [
    "acute lymphoblastic leukemia",
    "acute myeloid leukemia",
    "childhood leukemia",
    "pediatric leukemia",
    "leukemia",
    "lymphoma",
    "neuroblastoma",
    "li-fraumeni syndrome",
    "down syndrome",
    "noonan syndrome",
    "fanconi anemia",
    "neurofibromatosis type 1",
    "constitutional mismatch repair deficiency",
    "cancer predisposition syndrome",
    "genetic syndrome",
]

TREATMENT_PATTERNS = [
    "chemotherapy",
    "imatinib",
    "dasatinib",
    "tyrosine kinase inhibitor",
    "stem cell transplantation",
    "hematopoietic stem cell transplantation",
    "bone marrow transplantation",
    "radiotherapy",
    "immunotherapy",
    "CAR T",
    "blinatumomab",
    "inotuzumab",
    "methotrexate",
    "mercaptopurine",
    "glucocorticoid",
    "targeted therapy",
]

OUTCOME_TERMS = [
    "survival",
    "event-free survival",
    "overall survival",
    "remission",
    "relapse",
    "resistance",
    "response",
    "toxicity",
    "prognosis",
    "risk",
    "mortality",
]

FINDING_TERMS = [
    "associated with",
    "linked to",
    "related to",
    "increased risk",
    "poor prognosis",
    "improved survival",
    "predict",
    "mutation",
    "fusion",
    "response",
    "resistance",
]

GENE_TOKEN_RE = re.compile(r"\b(?:[A-Z]{2,}[0-9]{0,2}|[A-Z]+[0-9]+)(?:-[A-Z0-9]+)?\b")
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
FALSE_GENE_TOKENS = {
    "ALL",
    "AML",
    "CAR",
    "DNA",
    "RNA",
    "MRD",
    "PCR",
    "CI",
    "HR",
    "OR",
    "OS",
    "EFS",
    "HSCT",
}


def analyze_articles(articles: list[Article]) -> list[ArticleAnalysis]:
    return [analyze_article(article) for article in articles]


def analyze_article(article: Article) -> ArticleAnalysis:
    text = f"{article.title}. {article.abstract}"
    return ArticleAnalysis(
        article=article,
        genes=_extract_genes(text),
        diseases=_extract_terms(text, DISEASE_PATTERNS),
        treatments=_extract_terms(text, TREATMENT_PATTERNS),
        outcomes=_extract_outcome_sentences(text),
        findings=_extract_finding_sentences(text),
    )


def _extract_genes(text: str) -> list[str]:
    upper_text = text.upper()
    matches = set()

    for alias in GENE_ALIASES:
        if re.search(rf"\b{re.escape(alias)}\b", upper_text):
            matches.add(alias)

    for token in GENE_TOKEN_RE.findall(text):
        if token in FALSE_GENE_TOKENS:
            continue
        if len(token) <= 2 and token not in GENE_ALIASES:
            continue
        if any(char.isdigit() for char in token) or token in GENE_ALIASES:
            matches.add(token)

    return sorted(matches)


def _extract_terms(text: str, terms: list[str]) -> list[str]:
    found = []
    for term in terms:
        if re.search(rf"\b{re.escape(term)}\b", text, flags=re.IGNORECASE):
            found.append(_display_term(term))
    return sorted(set(found))


def _extract_outcome_sentences(text: str) -> list[str]:
    return _sentences_matching(text, OUTCOME_TERMS, limit=4)


def _extract_finding_sentences(text: str) -> list[str]:
    return _sentences_matching(text, FINDING_TERMS, limit=4)


def _sentences_matching(text: str, terms: list[str], limit: int) -> list[str]:
    sentences = [sentence.strip() for sentence in SENTENCE_RE.split(text) if sentence.strip()]
    selected = []
    for sentence in sentences:
        if any(re.search(rf"\b{re.escape(term)}\b", sentence, flags=re.IGNORECASE) for term in terms):
            selected.append(_clean_sentence(sentence))
        if len(selected) >= limit:
            break
    return selected


def _display_term(term: str) -> str:
    special = {"CAR T": "CAR T"}
    return special.get(term, term.title())


def _clean_sentence(sentence: str) -> str:
    sentence = re.sub(r"\s+", " ", sentence).strip()
    return sentence[:320] + "..." if len(sentence) > 320 else sentence
