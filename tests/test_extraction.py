from biomedical_discovery.extraction import analyze_article
from biomedical_discovery.graphing import build_relations, relation_rows
from biomedical_discovery.hypothesis import generate_hypotheses
from biomedical_discovery.models import Article


def test_analyze_article_extracts_core_entities():
    article = Article(
        pmid="123",
        title="TP53 in Li-Fraumeni syndrome and childhood leukemia",
        abstract=(
            "TP53 mutations are associated with Li-Fraumeni syndrome and acute lymphoblastic leukemia. "
            "Chemotherapy response and relapse risk were reported in pediatric cohorts."
        ),
    )

    analysis = analyze_article(article)

    assert "TP53" in analysis.genes
    assert "Li-Fraumeni Syndrome" in analysis.diseases
    assert "Acute Lymphoblastic Leukemia" in analysis.diseases
    assert "Chemotherapy" in analysis.treatments
    assert analysis.outcomes


def test_relations_and_hypotheses_are_generated():
    article = Article(
        pmid="456",
        title="ETV6-RUNX1 and chemotherapy outcomes in acute lymphoblastic leukemia",
        abstract=(
            "The ETV6-RUNX1 fusion is associated with acute lymphoblastic leukemia. "
            "Chemotherapy is linked to favorable survival and lower relapse in selected cohorts."
        ),
    )
    analysis = analyze_article(article)

    relations = build_relations([analysis])
    rows = relation_rows(relations)
    hypotheses = generate_hypotheses(relations)

    assert any(row["type"] == "gene-disease" for row in rows)
    assert any("ETV6-RUNX1" in hypothesis for hypothesis in hypotheses)
