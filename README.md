# Busqueda Bioedica

MVP local para explorar literatura publica de PubMed sobre sindromes geneticos y cancer infantil. La app busca articulos, extrae entidades biomedicas basicas, construye relaciones y propone hipotesis revisables por investigadores.

## Que hace

- Busca articulos en PubMed con NCBI E-utilities.
- Extrae genes, enfermedades/sindromes, tratamientos y frases de resultado.
- Construye relaciones tipo `gen -> enfermedad`, `enfermedad -> tratamiento` y `tratamiento -> resultado`.
- Muestra tablas, un grafo Graphviz y posibles hipotesis de investigacion.
- Incluye datos de ejemplo para probar la app sin internet.

## Instalacion

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Uso

```powershell
python server.py
```

Abre `http://127.0.0.1:8501`.

Tambien existe `app.py` como UI Streamlit opcional, pero el servidor principal no depende de Streamlit. Para esa variante:

```powershell
python -m pip install -r requirements-streamlit.txt
streamlit run app.py
```

Busqueda sugerida:

```text
genetic syndromes childhood leukemia treatment outcomes
```

## Nota medica y legal

Esta herramienta no diagnostica, no recomienda tratamientos y no usa datos privados de pacientes. Solo organiza literatura publica para ayudar a formular preguntas de investigacion que deben ser revisadas por profesionales.

## Tests

```powershell
python -m pytest
```
