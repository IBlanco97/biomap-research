from __future__ import annotations

import html
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

from biomedical_discovery.extraction import analyze_articles
from biomedical_discovery.graphing import build_relations, relation_rows
from biomedical_discovery.hypothesis import generate_hypotheses
from biomedical_discovery.pubmed import PubMedError, search_and_fetch
from biomedical_discovery.sample_data import SAMPLE_ARTICLES

HOST = os.getenv("BIOMAP_HOST", "127.0.0.1")
PORT = int(os.getenv("BIOMAP_PORT", "8501"))


class AppHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self._send_html(render_page())

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        form = parse_qs(body)

        query = form.get("query", ["genetic syndromes childhood leukemia treatment outcomes"])[0]
        max_results = int(form.get("max_results", ["12"])[0])
        use_sample = form.get("use_sample", ["off"])[0] == "on"
        email = form.get("email", [""])[0].strip() or None

        error = ""
        try:
            articles = SAMPLE_ARTICLES if use_sample else search_and_fetch(query, max_results=max_results, email=email)
        except PubMedError as exc:
            articles = SAMPLE_ARTICLES
            error = f"{exc}. Mostrando datos demo."

        analyses = analyze_articles(articles)
        relations = build_relations(analyses)
        self._send_html(render_page(query, max_results, use_sample, email or "", analyses, relations, error))

    def log_message(self, format: str, *args: object) -> None:
        return

    def _send_html(self, content: str) -> None:
        payload = content.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def render_page(
    query: str = "genetic syndromes childhood leukemia treatment outcomes",
    max_results: int = 12,
    use_sample: bool = True,
    email: str = "",
    analyses=None,
    relations=None,
    error: str = "",
) -> str:
    analyses = analyses if analyses is not None else analyze_articles(SAMPLE_ARTICLES)
    relations = relations if relations is not None else build_relations(analyses)
    rows = relation_rows(relations)
    hypotheses = generate_hypotheses(relations)

    genes = sorted({gene for item in analyses for gene in item.genes})
    diseases = sorted({disease for item in analyses for disease in item.diseases})
    treatments = sorted({treatment for item in analyses for treatment in item.treatments})

    return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Busqueda Bioedica</title>
  <style>
    :root {{
      --bg: #f7f7f2;
      --panel: #ffffff;
      --ink: #17201c;
      --muted: #5b675f;
      --line: #d9ded6;
      --accent: #0f766e;
      --accent-2: #b45309;
      --soft: #e8f3ef;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.5;
    }}
    header {{
      padding: 28px 32px 18px;
      border-bottom: 1px solid var(--line);
      background: #fbfbf8;
    }}
    h1 {{ margin: 0 0 6px; font-size: clamp(30px, 4vw, 48px); line-height: 1.05; letter-spacing: 0; }}
    h2 {{ margin: 0 0 14px; font-size: 20px; }}
    p {{ margin: 0; color: var(--muted); }}
    main {{ display: grid; grid-template-columns: 340px minmax(0, 1fr); gap: 20px; padding: 20px; }}
    aside, section {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: 0 10px 24px rgba(23, 32, 28, 0.05);
    }}
    aside {{ padding: 18px; align-self: start; position: sticky; top: 16px; }}
    section {{ padding: 18px; margin-bottom: 18px; overflow: hidden; }}
    label {{ display: block; margin: 14px 0 6px; font-size: 13px; font-weight: 700; color: #2f3b35; }}
    textarea, input, select {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px 11px;
      font: inherit;
      background: #fff;
      color: var(--ink);
    }}
    textarea {{ min-height: 110px; resize: vertical; }}
    button {{
      width: 100%;
      margin-top: 16px;
      border: 0;
      border-radius: 6px;
      padding: 11px 14px;
      background: var(--accent);
      color: white;
      font-weight: 800;
      cursor: pointer;
    }}
    .note {{ margin-top: 12px; padding: 12px; border-radius: 6px; background: var(--soft); color: #23443f; font-size: 13px; }}
    .error {{ margin: 0 0 16px; padding: 12px; border-radius: 6px; background: #fff1e6; color: #7c2d12; }}
    .metrics {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin-bottom: 18px; }}
    .metric {{ padding: 14px; background: #fff; border: 1px solid var(--line); border-radius: 8px; }}
    .metric strong {{ display: block; font-size: 26px; line-height: 1; }}
    .metric span {{ color: var(--muted); font-size: 13px; }}
    .chips {{ display: flex; flex-wrap: wrap; gap: 8px; }}
    .chip {{ padding: 5px 9px; border-radius: 999px; background: var(--soft); color: #17443f; font-size: 13px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ padding: 10px 8px; border-bottom: 1px solid var(--line); vertical-align: top; text-align: left; }}
    th {{ color: #33413a; font-size: 12px; text-transform: uppercase; letter-spacing: .04em; }}
    a {{ color: var(--accent); }}
    ol {{ margin: 0; padding-left: 22px; }}
    li {{ margin: 10px 0; }}
    .graph {{ width: 100%; overflow: auto; border: 1px solid var(--line); border-radius: 8px; background: #fbfbf8; }}
    svg {{ min-width: 820px; display: block; }}
    @media (max-width: 900px) {{
      main {{ grid-template-columns: 1fr; padding: 14px; }}
      aside {{ position: static; }}
      .metrics {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Busqueda Bioedica</h1>
    <p>Explora PubMed, detecta genes, sindromes, tratamientos y resultados, y convierte literatura publica en hipotesis revisables.</p>
  </header>
  <main>
    <aside>
      <form method="post">
        <h2>Consulta</h2>
        <label for="query">Tema biomedico</label>
        <textarea id="query" name="query">{html.escape(query)}</textarea>
        <label for="max_results">Articulos maximos</label>
        <select id="max_results" name="max_results">{render_options(max_results)}</select>
        <label for="email">Email NCBI opcional</label>
        <input id="email" name="email" value="{html.escape(email)}" placeholder="tu@email.com">
        <label><input type="checkbox" name="use_sample" {"checked" if use_sample else ""}> Usar datos demo sin internet</label>
        <button type="submit">Analizar literatura</button>
        <div class="note">No diagnostica ni recomienda tratamientos. Organiza literatura publica para investigacion.</div>
      </form>
    </aside>
    <div>
      {f'<div class="error">{html.escape(error)}</div>' if error else ''}
      <div class="metrics">
        <div class="metric"><strong>{len(analyses)}</strong><span>Articulos</span></div>
        <div class="metric"><strong>{len(genes)}</strong><span>Genes</span></div>
        <div class="metric"><strong>{len(diseases)}</strong><span>Condiciones</span></div>
        <div class="metric"><strong>{len(rows)}</strong><span>Relaciones</span></div>
      </div>
      <section>
        <h2>Entidades detectadas</h2>
        <p>Genes</p><div class="chips">{render_chips(genes)}</div>
        <p style="margin-top:14px">Condiciones</p><div class="chips">{render_chips(diseases)}</div>
        <p style="margin-top:14px">Tratamientos</p><div class="chips">{render_chips(treatments)}</div>
      </section>
      <section>
        <h2>Mapa de relaciones</h2>
        <div class="graph">{render_svg(rows[:18])}</div>
      </section>
      <section>
        <h2>Hipotesis para revisar</h2>
        <ol>{''.join(f'<li>{html.escape(item)}</li>' for item in hypotheses)}</ol>
      </section>
      <section>
        <h2>Relaciones</h2>
        {render_relation_table(rows)}
      </section>
      <section>
        <h2>Articulos</h2>
        {render_article_table(analyses)}
      </section>
    </div>
  </main>
</body>
</html>"""


def render_options(selected: int) -> str:
    values = [5, 10, 12, 20, 30, 50]
    return "".join(
        f'<option value="{value}" {"selected" if value == selected else ""}>{value}</option>' for value in values
    )


def render_chips(values: list[str]) -> str:
    if not values:
        return '<span class="chip">Sin detecciones</span>'
    return "".join(f'<span class="chip">{html.escape(value)}</span>' for value in values)


def render_relation_table(rows: list[dict[str, str | int]]) -> str:
    if not rows:
        return "<p>No hay relaciones detectadas.</p>"
    body = "".join(
        "<tr>"
        f"<td>{html.escape(str(row['source']))}</td>"
        f"<td>{html.escape(str(row['target']))}</td>"
        f"<td>{html.escape(str(row['type']))}</td>"
        f"<td>{html.escape(str(row['article_count']))}</td>"
        f"<td>{html.escape(str(row['pmids']))}</td>"
        "</tr>"
        for row in rows
    )
    return f"<table><thead><tr><th>Origen</th><th>Destino</th><th>Tipo</th><th>Articulos</th><th>PMID</th></tr></thead><tbody>{body}</tbody></table>"


def render_article_table(analyses) -> str:
    body = ""
    for analysis in analyses:
        article = analysis.article
        title = html.escape(article.title)
        link = f'<a href="{html.escape(article.url)}" target="_blank" rel="noreferrer">{title}</a>' if article.url else title
        body += (
            "<tr>"
            f"<td>{html.escape(article.pmid)}</td>"
            f"<td>{html.escape(article.year)}</td>"
            f"<td>{link}</td>"
            f"<td>{html.escape(', '.join(analysis.genes))}</td>"
            f"<td>{html.escape(' | '.join(analysis.outcomes[:2]))}</td>"
            "</tr>"
        )
    return f"<table><thead><tr><th>PMID</th><th>Ano</th><th>Titulo</th><th>Genes</th><th>Resultados</th></tr></thead><tbody>{body}</tbody></table>"


def render_svg(rows: list[dict[str, str | int]]) -> str:
    nodes = []
    for row in rows:
        for key in ("source", "target"):
            value = str(row[key])
            if value not in nodes:
                nodes.append(value)
    if not nodes:
        return "<p style='padding:16px'>No hay suficientes relaciones para el grafo.</p>"

    width = 980
    row_gap = 74
    height = max(260, 80 + len(nodes) * row_gap)
    positions = {node: (80 if index % 2 == 0 else 570, 50 + index * row_gap) for index, node in enumerate(nodes)}
    edge_markup = ""
    for row in rows:
        x1, y1 = positions[str(row["source"])]
        x2, y2 = positions[str(row["target"])]
        edge_markup += f'<line x1="{x1 + 210}" y1="{y1 + 22}" x2="{x2}" y2="{y2 + 22}" stroke="#8a958d" stroke-width="1.4"/>'

    node_markup = ""
    for node, (x, y) in positions.items():
        label = html.escape(shorten(node, 36))
        node_markup += (
            f'<rect x="{x}" y="{y}" width="210" height="44" rx="7" fill="#ffffff" stroke="#c9d2cb"/>'
            f'<text x="{x + 12}" y="{y + 27}" font-size="12" font-family="Arial" fill="#17201c">{label}</text>'
        )

    return f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Mapa de relaciones">{edge_markup}{node_markup}</svg>'


def shorten(value: str, size: int) -> str:
    return value if len(value) <= size else value[: size - 3] + "..."


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), AppHandler)
    print(json.dumps({"url": f"http://{HOST}:{PORT}", "status": "running"}))
    server.serve_forever()


if __name__ == "__main__":
    main()
