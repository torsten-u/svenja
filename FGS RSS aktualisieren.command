#!/bin/bash

cd /Users/torsten/GitHub/fgs-steuerrecht-rss || exit 1

/usr/bin/python3 generate.py || exit 1

git add docs/feed.xml

if git diff --cached --quiet; then
    echo "Keine neuen FGS-Beiträge."
    exit 0
fi

git commit -m "FGS RSS automatisch aktualisiert"
git push

echo "FGS RSS aktualisiert und zu GitHub übertragen."