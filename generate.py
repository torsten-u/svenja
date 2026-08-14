#!/usr/bin/env python3

from datetime import timezone
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree

from sources import fgs
from sources import finanzverwaltung_nrw

OUTPUT_DIR = Path(__file__).parent / "docs"

SOURCES = [
    fgs,
    finanzverwaltung_nrw,
]


def make_feed(source, articles):
    rss = Element("rss", version="2.0")
    channel = SubElement(rss, "channel")

    SubElement(channel, "title").text = source.FEED_TITLE
    SubElement(channel, "link").text = source.URL
    SubElement(channel, "description").text = source.FEED_DESCRIPTION
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

    output = OUTPUT_DIR / source.FEED_NAME
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    ElementTree(rss).write(
        output,
        encoding="utf-8",
        xml_declaration=True
    )

    print(f"  RSS erzeugt: {output}")


def main():
    for source in SOURCES:
        print(f"{source.FEED_TITLE} wird abgerufen …")

        articles = source.get_articles()
        print(f"  Gefundene Beiträge: {len(articles)}")

        if not articles:
            raise RuntimeError(
                f"Keine Beiträge für {source.FEED_TITLE} gefunden."
            )

        make_feed(source, articles)


if __name__ == "__main__":
    main()