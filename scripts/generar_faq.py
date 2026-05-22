import pandas as pd
from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = BASE_DIR / "data" / "preguntas_respuestas.csv"
DOCS_DIR = BASE_DIR / "docs"

CATEGORY_FILES = {
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

def clean_text(value):
    if pd.isna(value):
        return ""
    value = str(value).strip()
    value = re.sub(r"\s+", " ", value)
    return value

def build_page(category, rows):
    content = [f"# {category}", ""]
    content.append(
        "!!! info \"Nota\"\n"
        "    Esta información es de carácter general y no reemplaza la valoración médica."
    )
    content.append("")

    for _, row in rows.iterrows():
        pregunta = clean_text(row["pregunta"])
        respuesta = clean_text(row["respuesta"])
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

def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {DATA_FILE}")

    df = pd.read_csv(DATA_FILE)

    required_columns = {"categoria", "pregunta", "respuesta"}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Faltan columnas obligatorias: {missing}")

    if "revisado" in df.columns:
        df = df[df["revisado"].astype(str).str.lower().str.strip().isin(["sí", "si", "yes", "true", "1"])]

    for category, file_name in CATEGORY_FILES.items():
        rows = df[df["categoria"].astype(str).str.strip() == category]

        if rows.empty:
            continue

        page_content = build_page(category, rows)
        output_file = DOCS_DIR / file_name
        output_file.write_text(page_content, encoding="utf-8")
        print(f"Página generada: {output_file}")

if __name__ == "__main__":
    main()