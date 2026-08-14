#!/bin/bash

PLIST="$HOME/Library/LaunchAgents/de.torsten.fgs-rss.plist"

cat > "$PLIST" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>de.torsten.fgs-rss</string>

    <key>ProgramArguments</key>
    <array>
        <string>/Users/torsten/GitHub/fgs-steuerrecht-rss/FGS RSS aktualisieren.command</string>
    </array>

    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>8</integer>
        <key>Minute</key>
        <integer>15</integer>
    </dict>

    <key>RunAtLoad</key>
    <false/>

    <key>StandardOutPath</key>
    <string>/tmp/fgs-rss.log</string>

    <key>StandardErrorPath</key>
    <string>/tmp/fgs-rss-error.log</string>
</dict>
</plist>
EOF

launchctl bootout gui/$(id -u) "$PLIST" 2>/dev/null
launchctl bootstrap gui/$(id -u) "$PLIST"

echo "FGS-RSS-Automation installiert."