from html import escape
from pathlib import Path, PurePosixPath
import re
import shutil
from urllib.parse import urlsplit

from openpyxl import load_workbook


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "_site"
FIELDS = (
    "ID", "Actividad", "Destino", "Descripción", "Fotos", "Instagram",
    "Teléfono", "Ubicación o punto de encuentro", "Precio por persona",
    "Horario", "Duración", "Reserva", "Qué llevar", "Requisitos y notas",
)
MAP = {
    "Ubicación o punto de encuentro": "Ubicación o punto de encuentro",
    "Precio por persona": "Precio por persona",
    "Horario": "Horario",
    "Duración": "Duración",
    "Reserva": "Reserva",
    "Qué llevar": "Qué llevar",
    "Requisitos y notas": "Requisitos y notas",
}


def clean(value):
    return "" if value is None else str(value).strip()


def safe_url(value):
    try:
        parts = urlsplit(value)
        return parts.scheme == "https" and bool(parts.hostname) and not parts.username
    except ValueError:
        return False


def photo_url(value):
    if safe_url(value):
        return value
    path = PurePosixPath(value)
    if (
        path.parts[:1] == ("fotos",)
        and ".." not in path.parts
        and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".avif"}
        and (ROOT / "recursos" / path).is_file()
    ):
        return path.as_posix()
    raise ValueError(f"Foto inválida o inexistente: {value}")


def read_activities():
    workbook = load_workbook(ROOT / "Catalogo.xlsx", read_only=True)
    try:
        rows = iter(workbook["Actividades"].values)
        headers = [clean(value) for value in next(rows, ())]
        for field in FIELDS:
            if headers.count(field) != 1:
                raise ValueError(f"La columna «{field}» debe aparecer una vez.")
        activities = []
        used_ids = set()
        for number, values in enumerate(rows, 2):
            if not any(clean(value) for value in values):
                continue
            item = {field: clean(value) for field, value in zip(headers, values)}
            try:
                key = item["ID"]
                if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", key) or key in used_ids:
                    raise ValueError("Usa un ID único en minúsculas, con números o guiones si hace falta.")
                if not all(item[field] for field in ("Actividad", "Destino", "Descripción")):
                    raise ValueError("Completa Actividad, Destino y Descripción.")
                instagram = item["Instagram"]
                if instagram and (not safe_url(instagram) or urlsplit(instagram).hostname not in {"instagram.com", "www.instagram.com"}):
                    raise ValueError("Instagram requiere un enlace HTTPS de instagram.com.")
                phone = item["Teléfono"]
                digits = re.sub(r"[\s().-]", "", phone)
                if phone and not re.fullmatch(r"\+?[0-9]{10,15}", digits):
                    raise ValueError("Escribe el teléfono con código de área o en formato internacional.")
                if len(digits) == 10 and digits.isdigit():
                    digits = "+1" + digits
                item["tel"] = digits
                item["photos"] = [photo_url(value.strip()) for value in item["Fotos"].splitlines() if value.strip()]
            except ValueError as error:
                raise ValueError(f"Actividades, fila {number}. {error}") from error
            used_ids.add(key)
            activities.append(item)
        return activities
    finally:
        workbook.close()


def page(title, content, prefix="", script=False):
    assets = f'<script src="{prefix}catalogo.js" defer></script>' if script else ""
    return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)} · Terreneitor</title>
  <link rel="stylesheet" href="{prefix}estilos.css">
  {assets}
</head>
<body>
{content}
<footer><div class="wrap"><strong>Terreneitor.</strong><span>República Dominicana</span></div></footer>
</body>
</html>"""


def photo(src, prefix="", lazy=True):
    url = src if safe_url(src) else prefix + src
    loading = ' loading="lazy"' if lazy else ""
    return f'<img src="{escape(url)}" alt=""{loading}>'


def catalog(activities):
    cards = []
    destinations = dict.fromkeys(item["Destino"] for item in activities)
    filters = ['<button type="button" data-destino="" aria-pressed="true">Todos</button>']
    for destination in destinations:
        label = escape(destination)
        filters.append(f'<button type="button" data-destino="{label}" aria-pressed="false">{label}</button>')
    for item in activities:
        name, destination = (escape(item[field]) for field in ("Actividad", "Destino"))
        image = photo(item["photos"][0]) if item["photos"] else '<div class="photo-placeholder">Foto pendiente</div>'
        cards.append(f"""<article class="card" data-destino="{destination}">
  {image}
  <div class="card-content">
    <p class="destination">{destination}</p>
    <h3>{name}</h3>
    <a href="actividades/{item['ID']}.html" aria-label="Ver plan de {name} en {destination}">Ver el plan →</a>
  </div>
</article>""")
    count = "1 actividad" if len(cards) == 1 else f"{len(cards)} actividades"
    return page("Planes de fin de semana", f"""
<header class="hero">
  <nav class="wrap"><a class="brand" href="index.html">Terreneitor<span>.</span></a><a class="navigation" href="#actividades">Ver planes</a></nav>
  <div class="wrap intro">
    <p class="place">Un regalo para ti</p>
    <h1>Fines de semana<br>por descubrir.</h1>
    <p>Te regalo una colección de lugares y aventuras para esos días en que quieras salir de la rutina.</p>
    <a class="cta" href="#actividades">Elige tu próxima salida ↓</a>
  </div>
</header>
<main id="actividades" class="wrap">
  <h2>Planes para el fin de semana</h2>
  <div class="filters" role="group" aria-label="Filtrar por destino" hidden>{''.join(filters)}</div>
  <p id="results" role="status">{count}</p>
  <div class="grid">{''.join(cards)}</div>
</main>""", script=True)


def detail(item):
    name, destination, description = (escape(item[field]) for field in ("Actividad", "Destino", "Descripción"))
    gallery = "".join(photo(src, "../", lazy=index > 0) for index, src in enumerate(item["photos"]))
    gallery_html = f'<div class="gallery">{gallery}</div>' if gallery else ""
    planning = []
    for field, label in MAP.items():
        value = item[field]
        rendered = escape(value) if value else '<span class="pending">Por confirmar</span>'
        if field in {"Ubicación o punto de encuentro", "Reserva"} and safe_url(value):
            rendered = f'<a href="{escape(value)}">{"Abrir mapa" if field.startswith("Ubicación") else "Abrir enlace de reserva"} ↗</a>'
        planning.append(f"<div><dt>{label}</dt><dd>{rendered}</dd></div>")
    contacts = []
    if item["Instagram"]:
        contacts.append(f'<a class="cta" href="{escape(item["Instagram"])}">Consultar por Instagram ↗</a>')
    if item["Teléfono"]:
        contacts.append(f'<a class="cta" href="tel:{item["tel"]}">Llamar · {escape(item["Teléfono"])}</a>')
    contact_html = "".join(contacts) or '<p class="pending">Contacto por confirmar.</p>'
    return page(item["Actividad"], f"""
<header class="detail-header">
  <nav class="wrap"><a class="brand" href="../index.html">Terreneitor<span>.</span></a><a class="navigation" href="../index.html#actividades">← Todos los planes</a></nav>
</header>
<main class="wrap detail">
  <p class="destination">{destination}</p>
  <h1>{name}</h1>
  <p class="description">{description}</p>
  {gallery_html}
  <div class="trip-grid">
    <section><h2>Planifica la salida</h2><dl>{''.join(planning)}</dl></section>
    <section class="contacts"><h2>Contacto</h2>{contact_html}</section>
  </div>
</main>""", prefix="../")


def main():
    activities = read_activities()
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    shutil.copytree(ROOT / "recursos", OUTPUT)
    (OUTPUT / "actividades").mkdir()
    (OUTPUT / "index.html").write_text(catalog(activities), encoding="utf-8")
    for item in activities:
        filename = OUTPUT / "actividades" / f"{item['ID']}.html"
        filename.write_text(detail(item), encoding="utf-8")
    print(f"Sitio generado con {len(activities)} actividades en {OUTPUT.name}.")


if __name__ == "__main__":
    main()
