from __future__ import annotations

from collections import Counter, defaultdict

import networkx as nx

from .models import ArticleAnalysis, Relation


def build_relations(analyses: list[ArticleAnalysis]) -> list[Relation]:
    relations: list[Relation] = []
    for analysis in analyses:
        article = analysis.article
        evidence = analysis.findings[0] if analysis.findings else article.title

        for gene in analysis.genes:
            for disease in analysis.diseases:
                relations.append(Relation(gene, disease, "gene-disease", article.pmid, evidence))

        for disease in analysis.diseases:
            for treatment in analysis.treatments:
                relations.append(Relation(disease, treatment, "disease-treatment", article.pmid, evidence))

        for treatment in analysis.treatments:
            for outcome in analysis.outcomes[:2]:
                relations.append(Relation(treatment, outcome, "treatment-outcome", article.pmid, outcome))

    return relations


def relation_rows(relations: list[Relation]) -> list[dict[str, str | int]]:
    grouped: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    evidence: dict[tuple[str, str, str], str] = {}
    for relation in relations:
        key = (relation.source, relation.target, relation.relation_type)
        grouped[key].add(relation.pmid)
        evidence.setdefault(key, relation.evidence)

    rows = []
    for (source, target, relation_type), pmids in grouped.items():
        rows.append(
            {
                "source": source,
                "target": target,
                "type": relation_type,
                "article_count": len(pmids),
                "pmids": ", ".join(sorted(pmids)),
                "evidence": evidence[(source, target, relation_type)],
            }
        )
    return sorted(rows, key=lambda row: (-int(row["article_count"]), str(row["type"]), str(row["source"])))


def build_network(relations: list[Relation]) -> nx.Graph:
    graph = nx.Graph()
    weights = Counter((relation.source, relation.target, relation.relation_type) for relation in relations)

    for (source, target, relation_type), weight in weights.items():
        graph.add_node(source)
        graph.add_node(target)
        graph.add_edge(source, target, weight=weight, relation_type=relation_type)

    return graph


def to_graphviz_dot(relations: list[Relation], max_edges: int = 45) -> str:
    rows = relation_rows(relations)[:max_edges]
    lines = [
        "graph G {",
        "  graph [rankdir=LR, bgcolor=\"transparent\", overlap=false, splines=true];",
        "  node [shape=box, style=\"rounded,filled\", fillcolor=\"#f8fafc\", color=\"#94a3b8\", fontname=\"Arial\", fontsize=10];",
        "  edge [color=\"#64748b\", fontname=\"Arial\", fontsize=9];",
    ]
    for row in rows:
        source = _dot_escape(str(row["source"]))
        target = _dot_escape(str(row["target"]))
        label = _dot_escape(f"{row['type']} ({row['article_count']})")
        lines.append(f"  \"{source}\" -- \"{target}\" [label=\"{label}\"];")
    lines.append("}")
    return "\n".join(lines)


def _dot_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')
