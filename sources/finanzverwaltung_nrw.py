import html
import re
import urllib.request
from datetime import datetime
from urllib.parse import urljoin

URL = "https://www.finanzverwaltung.nrw.de/uebersicht-rubrik-aktuelles-und-presse/pressemitteilungen"
BASE = "https://www.finanzverwaltung.nrw.de"

FEED_NAME = "finanzverwaltung-nrw.xml"
FEED_TITLE = "Finanzverwaltung NRW – Steuerrelevantes"
FEED_DESCRIPTION = (
    "Ausgewählte steuerrelevante Pressemitteilungen der Finanzverwaltung NRW"
)

INCLUDE = [
    "steuer",
    "finanzamt",
    "finanzämter",
    "elster",
    "einkommensteuer",
    "lohnsteuer",
    "umsatzsteuer",
    "mehrwertsteuer",
    "körperschaftsteuer",
    "gewerbesteuer",
    "grundsteuer",
    "grunderwerbsteuer",
    "erbschaftsteuer",
    "schenkungsteuer",
    "steuererklärung",
    "betriebsprüfung",
    "steuerfahndung",
    "steuerbetrug",
    "steuerhinterziehung",
    "steuerbescheid",
    "abgabenordnung",
    "steuerveranlagung",
]


def clean(text):
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def relevant(text):
    text = text.lower()
    return any(term in text for term in INCLUDE)


def get_articles():
    request = urllib.request.Request(
        URL,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        page = response.read().decode("utf-8")

    articles = []

    link_pattern = re.compile(
        r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
        re.S | re.I
    )

    date_pattern = re.compile(r"\d{2}\.\d{2}\.\d{4}")

    for match in link_pattern.finditer(page):
        href, content = match.groups()

        if "pressemitteilung" not in href.lower():
            continue

        full_text = clean(content)

        if len(full_text) < 20:
            continue

        if not relevant(full_text):
            continue

        dates = date_pattern.findall(full_text)

        if not dates:
            continue

        date_text = dates[0]
        date = datetime.strptime(date_text, "%d.%m.%Y")

        # Auf der NRW-Seite folgen Datum und Teaser dem Titel.
        title = full_text.split(date_text, 1)[0].strip()

        if len(title) < 10:
            continue

        link = urljoin(BASE, href)

        articles.append({
            "title": title,
            "link": link,
            "date": date,
        })

    unique = {}

    for article in articles:
        unique[article["link"]] = article

    return sorted(
        unique.values(),
        key=lambda x: x["date"],
        reverse=True
    )