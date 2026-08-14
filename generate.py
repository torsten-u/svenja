#!/usr/bin/env python3

import html
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin
from xml.etree.ElementTree import Element, SubElement, ElementTree

URL = "https://www.fgs.de/news-and-insights/blog/steuerrecht"
BASE = "https://www.fgs.de"
OUTPUT = Path(__file__).parent / "docs" / "feed.xml"


def get_page():
    request = urllib.request.Request(
        URL,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def clean(text):
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text).strip()


def parse_articles(page):
    articles = []

    date_pattern = re.compile(r"\d{2}\.\d{2}\.\d{4}")

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

        date_text = dates[-1]
        date = datetime.strptime(date_text, "%d.%m.%Y")

        link = urljoin(BASE, href)

        articles.append({
            "title": title,
            "link": link,
            "date": date,
        })

    # Doppelte Links entfernen
    unique = {}
    for article in articles:
        unique[article["link"]] = article

    return sorted(
        unique.values(),
        key=lambda x: x["date"],
        reverse=True
    )


def make_feed(articles):
    rss = Element("rss", version="2.0")
    channel = SubElement(rss, "channel")

    SubElement(channel, "title").text = "FGS – Steuerrecht"
    SubElement(channel, "link").text = URL
    SubElement(channel, "description").text = (
        "Aktuelle Beiträge zum Steuerrecht von Flick Gocke Schaumburg"
    )
    SubElement(channel, "language").text = "de"

    for article in articles:
        item = SubElement(channel, "item")

        SubElement(item, "title").text = article["title"]
        SubElement(item, "link").text = article["link"]
        SubElement(item, "guid").text = article["link"]

        pubdate = article["date"].replace(tzinfo=timezone.utc)

        SubElement(item, "pubDate").text = pubdate.strftime(
            "%a, %d %b %Y 00:00:00 +0000"
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    ElementTree(rss).write(
        OUTPUT,
        encoding="utf-8",
        xml_declaration=True
    )


def main():
    print("FGS-Seite wird abgerufen …")

    page = get_page()
    articles = parse_articles(page)

    print(f"Gefundene Beiträge: {len(articles)}")

    if not articles:
        raise RuntimeError("Keine FGS-Beiträge gefunden.")

    make_feed(articles)

    print(f"RSS erzeugt: {OUTPUT}")


if __name__ == "__main__":
    main()