from __future__ import annotations

from .models import Article

SAMPLE_ARTICLES = [
    Article(
        pmid="00000001",
        title="TP53 alterations in pediatric acute lymphoblastic leukemia and cancer predisposition syndromes",
        abstract=(
            "TP53 mutations are associated with Li-Fraumeni syndrome and increased risk of childhood leukemia. "
            "Several cohorts report poor prognosis, therapy resistance, and higher relapse risk after chemotherapy. "
            "Genomic screening may identify patients who need adapted surveillance and treatment strategies."
        ),
        journal="Demo Journal of Pediatric Oncology",
        year="2024",
        url="https://pubmed.ncbi.nlm.nih.gov/00000001/",
    ),
    Article(
        pmid="00000002",
        title="Down syndrome acute lymphoblastic leukemia and treatment toxicity",
        abstract=(
            "Down syndrome is linked to pediatric leukemia and distinctive chemotherapy toxicity. "
            "Children with acute lymphoblastic leukemia show variable remission rates and elevated treatment-related mortality. "
            "Methotrexate dosing and supportive care are frequent topics in outcome studies."
        ),
        journal="Demo Blood Research",
        year="2023",
        url="https://pubmed.ncbi.nlm.nih.gov/00000002/",
    ),
    Article(
        pmid="00000003",
        title="ETV6-RUNX1 fusion and outcomes after chemotherapy in childhood leukemia",
        abstract=(
            "The ETV6-RUNX1 fusion is common in acute lymphoblastic leukemia and is associated with favorable survival. "
            "Minimal residual disease and relapse remain important outcome measures after chemotherapy. "
            "Targeted risk stratification may improve treatment selection."
        ),
        journal="Demo Hematology Reports",
        year="2022",
        url="https://pubmed.ncbi.nlm.nih.gov/00000003/",
    ),
]
