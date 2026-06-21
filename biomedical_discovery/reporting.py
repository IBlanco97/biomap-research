from __future__ import annotations

import csv
import io

from .graphing import relation_rows
from .hypothesis import generate_hypotheses
from .models import ArticleAnalysis, Relation


def build_report(
    analyses: list[ArticleAnalysis],
    relations: list[Relation],
    query: str,
    max_results: int,
    source: str,
) -> dict[str, object]:
    genes = sorted({gene for item in analyses for gene in item.genes})
    diseases = sorted({disease for item in analyses for disease in item.diseases})
    treatments = sorted({treatment for item in analyses for treatment in item.treatments})

    return {
        "query": query,
        "max_results": max_results,
        "source": source,
        "summary": {
            "article_count": len(analyses),
            "gene_count": len(genes),
            "condition_count": len(diseases),
            "treatment_count": len(treatments),
            "relation_count": len(relation_rows(relations)),
        },
        "entities": {
            "genes": genes,
            "conditions": diseases,
            "treatments": treatments,
        },
        "articles": [_analysis_to_dict(analysis) for analysis in analyses],
        "relations": relation_rows(relations),
        "hypotheses": generate_hypotheses(relations),
    }


def relations_to_csv(relations: list[Relation]) -> str:
    output = io.StringIO()
    fieldnames = ["source", "target", "type", "article_count", "pmids", "evidence"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(relation_rows(relations))
    return output.getvalue()


def _analysis_to_dict(analysis: ArticleAnalysis) -> dict[str, object]:
    article = analysis.article
    return {
        "pmid": article.pmid,
        "title": article.title,
        "abstract": article.abstract,
        "journal": article.journal,
        "year": article.year,
        "doi": article.doi,
        "url": article.url,
        "genes": analysis.genes,
        "conditions": analysis.diseases,
        "treatments": analysis.treatments,
        "outcomes": analysis.outcomes,
        "findings": analysis.findings,
    }
