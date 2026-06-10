#!/usr/bin/env bash
# Apply the Quantum-Breakout theme to pygbag's generated index.html.
# `pygbag --build` regenerates index.html each time, so build_web.sh calls this
# after every build. Usage: bash patch_index.sh <path/to/index.html>
# Run from the repo root (it copies the game font from assets/font/).
set -euo pipefail
f="${1:-webbuild/build/web/index.html}"
webdir="$(dirname "$f")"

# allow a clean tab close (drop pygbag's "Leave site?" guard, which also freezes
# the loop and leaves audio looping while it is shown)
sed -i 's/can_close : 0/can_close : 1/' "$f"

# page / loader background -> black
sed -i 's/style.background = "#7f7f7f"/style.background = "#000000"/' "$f"
sed -i 's/background-color:powderblue;/background-color:#000000;/'    "$f"
sed -i 's/background: green;/background: #000000;/'                   "$f"

# loader strings
sed -i 's/Loading, please wait \.\.\./loading.../'                      "$f"
sed -i 's/Ready to start ! Please click\/touch page/click to start/'    "$f"

# style overrides: white centred loader text; centre the two pre-load overlays
# (Downloading bar + loading infobox) without overlap; no canvas outline.
# NB: the in-game 8-bit font (bit5x3.ttf) is loaded by pygame for canvas text; it is
# NOT usable as a web @font-face (browsers' OpenType Sanitizer rejects it), so the
# brief HTML loader text just uses monospace.
read -r -d '' CSS <<'EOF' || true
        #infobox, #status { color: #ffffff !important; text-align: center; font-family: monospace !important; background: transparent !important; }
        #transfer { position: fixed !important; left: 0 !important; right: 0 !important; top: 44% !important; transform: translateY(-50%) !important; text-align: center !important; }
        #status { margin: 0 !important; display: block !important; }
        #infobox { left: 50% !important; top: 56% !important; transform: translate(-50%, -50%) !important; }
        canvas, #canvas, .emscripten { outline: none !important; border: none !important; }
    </style>
EOF
awk -v css="$CSS" '{ if ($0 ~ /<\/style>/ && !done) { print css; done=1 } else print }' "$f" > "$f.tmp" && mv "$f.tmp" "$f"

echo "themed $f"
