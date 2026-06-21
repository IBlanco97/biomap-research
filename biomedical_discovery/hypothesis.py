from __future__ import annotations

from collections import defaultdict

from .graphing import relation_rows
from .models import Relation


def generate_hypotheses(relations: list[Relation], limit: int = 8) -> list[str]:
    rows = relation_rows(relations)
    by_type = defaultdict(list)
    for row in rows:
        by_type[row["type"]].append(row)

    hypotheses: list[str] = []
    for row in by_type["gene-disease"][:limit]:
        hypotheses.append(
            f"Revisar si {row['source']} podria estratificar riesgo o respuesta en {row['target']} "
            f"({row['article_count']} articulo(s): {row['pmids']})."
        )

    for row in by_type["disease-treatment"][:limit]:
        hypotheses.append(
            f"Comparar resultados reportados de {row['target']} en pacientes con {row['source']} "
            f"({row['article_count']} articulo(s): {row['pmids']})."
        )

    for row in by_type["treatment-outcome"][:limit]:
        hypotheses.append(
            f"Evaluar evidencia sobre {row['source']} y el resultado reportado: \"{row['target']}\" "
            f"({row['article_count']} articulo(s): {row['pmids']})."
        )

    return hypotheses[:limit]
