import pandas as pd
from pathlib import Path
import re
import unicodedata


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = BASE_DIR / "data" / "preguntas_respuestas.csv"
DOCS_DIR = BASE_DIR / "docs"
MKDOCS_FILE = BASE_DIR / "mkdocs.yml"


FIXED_CATEGORY_FILES = {
    "Primeros auxilios de mamá": "primeros-auxilios.md",
    "Lactancia": "lactancia.md",
    "Fórmula y teteros": "formula.md",
    "Sueño del bebé": "sueno.md",
    "Pañales y popó": "panales.md",
    "Cólicos y reflujo": "colicos-reflujo.md",
    "Vacunas y controles": "vacunas.md",
    "Desarrollo": "desarrollo.md",
    "Productos útiles": "productos.md",
    "Cuándo consultar": "salud-alertas.md",
}


CONSULTA_RAPIDA = {
    "Primeros auxilios de mamá",
    "Cuándo consultar",
}


def clean_text(value):
    if pd.isna(value):
        return ""
    value = str(value).strip()
    value = re.sub(r"\s+", " ", value)
    return value


def slugify(value):
    value = str(value).strip().lower()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(c for c in value if not unicodedata.combining(c))
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value or "categoria"


def get_file_name(category):
    category = clean_text(category)
    if category in FIXED_CATEGORY_FILES:
        return FIXED_CATEGORY_FILES[category]
    return f"{slugify(category)}.md"


def normalize_review(value):
    value = clean_text(value).lower()
    return value in ["sí", "si", "yes", "true", "1", "x", "ok", "aprobado"]


def read_csv_data():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {DATA_FILE}")

    try:
        df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(DATA_FILE, encoding="latin-1")

    df.columns = [clean_text(col).lower() for col in df.columns]

    required_columns = {"categoria", "pregunta", "respuesta"}
    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"Faltan columnas obligatorias en el CSV: {missing}. "
            f"Columnas encontradas: {list(df.columns)}"
        )

    if "tags" not in df.columns:
        df["tags"] = ""

    if "revisado" not in df.columns:
        df["revisado"] = "sí"

    df["categoria"] = df["categoria"].apply(clean_text)
    df["pregunta"] = df["pregunta"].apply(clean_text)
    df["respuesta"] = df["respuesta"].apply(clean_text)
    df["tags"] = df["tags"].apply(clean_text)

    df = df[df["categoria"] != ""]
    df = df[df["pregunta"] != ""]
    df = df[df["respuesta"] != ""]
    df = df[df["revisado"].apply(normalize_review)]

    if df.empty:
        raise ValueError("No hay preguntas revisadas para publicar. Revisa la columna 'revisado'.")

    return df


def build_page(category, rows):
    content = [f"# {category}", ""]

    content.append(
        "!!! info \"Nota importante\"\n"
        "    Esta información tiene fines informativos y no reemplaza la valoración médica. "
        "Ante síntomas de alarma o dudas sobre el estado del bebé, se debe consultar con el pediatra."
    )
    content.append("")

    for _, row in rows.iterrows():
        pregunta = clean_text(row.get("pregunta", ""))
        respuesta = clean_text(row.get("respuesta", ""))
        tags = clean_text(row.get("tags", ""))

        if not pregunta or not respuesta:
            continue

        content.append(f"## {pregunta}")
        content.append("")
        content.append(respuesta)
        content.append("")

        if tags:
            content.append(f"**Temas relacionados:** {tags}")
            content.append("")

        content.append("---")
        content.append("")

    return "\n".join(content)


def generate_markdown_pages(df):
    categories = sorted(df["categoria"].unique())

    print("Categorías encontradas en el CSV:")
    for category in categories:
        print(f"- {category}")

    for category in categories:
        rows = df[df["categoria"] == category]
        file_name = get_file_name(category)
        output_file = DOCS_DIR / file_name

        page_content = build_page(category, rows)
        output_file.write_text(page_content, encoding="utf-8")

        print(f"Página generada: {output_file} ({len(rows)} preguntas)")

    return categories


def build_mkdocs_yaml(categories):
    consulta_rapida = []
    temas_frecuentes = []

    for category in categories:
        item = f"      - {category}: {get_file_name(category)}"
        if category in CONSULTA_RAPIDA:
            consulta_rapida.append(item)
        else:
            temas_frecuentes.append(item)

    consulta_rapida_block = "\n".join(consulta_rapida)
    temas_frecuentes_block = "\n".join(temas_frecuentes)

    if not consulta_rapida_block:
        consulta_rapida_block = "      - Cuándo consultar: salud-alertas.md"

    mkdocs_content = f"""site_name: The Club Moms FAQ
site_description: Preguntas frecuentes para mamás
site_url: http://127.0.0.1:8000/

theme:
  name: material
  language: es
  favicon: assets/favicon.png
  features:
    - navigation.sections
    - navigation.expand
    - navigation.top
    - search.suggest
    - search.highlight
    - content.code.copy
  palette:
    - scheme: default
      primary: pink
      accent: deep orange
      toggle:
        icon: material/weather-night
        name: Cambiar a modo oscuro
    - scheme: slate
      primary: pink
      accent: deep orange
      toggle:
        icon: material/weather-sunny
        name: Cambiar a modo claro

nav:
  - Inicio: index.md
  - Consulta rápida:
{consulta_rapida_block}
  - Temas frecuentes:
{temas_frecuentes_block}

markdown_extensions:
  - admonition
  - attr_list
  - md_in_html
  - tables
  - pymdownx.details
  - pymdownx.superfences
  - toc:
      permalink: true

extra_css:
  - stylesheets/extra.css

copyright: "Contenido informativo. No reemplaza valoración médica."
"""

    return mkdocs_content


def update_mkdocs_file(categories):
    mkdocs_content = build_mkdocs_yaml(categories)
    MKDOCS_FILE.write_text(mkdocs_content, encoding="utf-8")
    print(f"Archivo actualizado: {MKDOCS_FILE}")


def main():
    df = read_csv_data()
    categories = generate_markdown_pages(df)
    update_mkdocs_file(categories)

    print("")
    print("Proceso finalizado correctamente.")
    print("Se generaron las páginas .md y se actualizó mkdocs.yml con las categorías del CSV.")


if __name__ == "__main__":
    main()