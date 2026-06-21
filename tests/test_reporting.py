from biomedical_discovery.extraction import analyze_article
from biomedical_discovery.graphing import build_relations
from biomedical_discovery.models import Article
from biomedical_discovery.reporting import build_report, relations_to_csv


def test_build_report_contains_summary_entities_and_hypotheses():
    article = Article(
        pmid="789",
        title="RUNX1 and childhood leukemia treatment response",
        abstract=(
            "RUNX1 mutation is associated with acute lymphoblastic leukemia. "
            "Chemotherapy response and survival were evaluated in childhood leukemia cohorts."
        ),
    )
    analysis = analyze_article(article)
    relations = build_relations([analysis])

    report = build_report([analysis], relations, "RUNX1 leukemia", 10, "demo")

    assert report["query"] == "RUNX1 leukemia"
    assert report["summary"]["article_count"] == 1
    assert "RUNX1" in report["entities"]["genes"]
    assert report["articles"][0]["pmid"] == "789"
    assert report["relations"]
    assert report["hypotheses"]


def test_relations_to_csv_includes_header_and_relation_type():
    article = Article(
        pmid="101",
        title="TP53 in Li-Fraumeni syndrome",
        abstract=(
            "TP53 mutations are associated with Li-Fraumeni syndrome and childhood leukemia. "
            "Chemotherapy response was reported."
        ),
    )
    analysis = analyze_article(article)
    relations = build_relations([analysis])

    csv_output = relations_to_csv(relations)

    assert csv_output.startswith("source,target,type,article_count,pmids,evidence")
    assert "gene-disease" in csv_output
