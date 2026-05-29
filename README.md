# The Club Moms FAQ

Base de conocimiento tipo FAQ para organizar preguntas frecuentes de un grupo de mamás, a partir de información previamente revisada, depurada y categorizada.

El sitio está construido con **MkDocs** y **Material for MkDocs**, se publica con **GitHub Pages** y se actualiza a partir de un archivo CSV.

## Objetivo

Permitir que las mamás puedan consultar preguntas frecuentes de forma rápida, organizada y desde un enlace web, sin tener que buscar manualmente entre muchos mensajes del grupo de WhatsApp.

El contenido está organizado por categorías como:

- Lactancia
- Fórmula y teteros
- Sueño del bebé
- Pañales y popó
- Cólicos y reflujo
- Vacunas y controles
- Desarrollo
- Productos útiles
- Cuándo consultar
- Otras categorías que se agreguen al CSV

## Importante

Esta base de conocimiento tiene fines informativos y no reemplaza la valoración médica.

Ante fiebre, dificultad para respirar, rechazo persistente del alimento, vómito frecuente, sangre en las deposiciones, signos de deshidratación, decaimiento marcado o cualquier síntoma que preocupe, se debe consultar con el pediatra o acudir a urgencias.

## Tecnologías utilizadas

- Python
- MkDocs
- Material for MkDocs
- Pandas
- Git
- GitHub Pages

## Estructura del proyecto

```text
faq-mamas/
│
├── data/
│   └── preguntas_respuestas.csv
│
├── docs/
│   ├── index.md
│   ├── lactancia.md
│   ├── formula.md
│   ├── sueno.md
│   ├── panales.md
│   ├── colicos-reflujo.md
│   ├── vacunas.md
│   ├── desarrollo.md
│   ├── productos.md
│   ├── salud-alertas.md
│   └── stylesheets/
│       └── extra.css
│
├── scripts/
│   └── generar_faq.py
│
├── mkdocs.yml
├── requirements.txt
├── README.md
└── .gitignore
