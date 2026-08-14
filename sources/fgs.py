import html
import re
import urllib.request
from datetime import datetime
from urllib.parse import urljoin

URL = "https://www.fgs.de/news-and-insights/blog/steuerrecht"
BASE = "https://www.fgs.de"

FEED_NAME = "fgs.xml"
FEED_TITLE = "FGS – Steuerrecht"
FEED_DESCRIPTION = (
    "Aktuelle Beiträge zum Steuerrecht von Flick Gocke Schaumburg"
)


def clean(text):
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text).strip()


def get_articles():
    request = urllib.request.Request(
        URL,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        page = response.read().decode("utf-8")

    articles = []

    date_pattern = re.compile(
        r"\d{2}\.\d{2}\.\d{4}"
    )

    link_pattern = re.compile(
        r'<a[^>]+href="(/news-and-insights/blog/detail/[^"]+)"[^>]*>(.*?)</a>',
        re.S | re.I
    )

    for match in link_pattern.finditer(page):
        href, content = match.groups()
        title = clean(content)

        if not title or len(title) < 15:
            continue

        start = max(0, match.start() - 1500)
        context = page[start:match.start()]
        dates = date_pattern.findall(context)

        if not dates:
            continue

        date = datetime.strptime(
            dates[-1],
            "%d.%m.%Y"
        )

        link = urljoin(BASE, href)

        articles.append({
            "title": title,
            "link": link,
            "date": date,
        })

    # FGS verlinkt denselben Artikel mehrfach:
    # zuerst mit der echten Überschrift, danach mit dem Teaser.
    # Deshalb beim gleichen Link immer den ERSTEN Treffer behalten.
    unique = {}

    for article in articles:
        unique.setdefault(
            article["link"],
            article
        )

    return sorted(
        unique.values(),
        key=lambda x: x["date"],
        reverse=True
    )