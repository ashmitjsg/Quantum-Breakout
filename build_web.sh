#!/usr/bin/env bash
# Build the browser (pygbag/WebAssembly) bundle for Quantum Breakout.
#
# One command, fully reproducible: it generates an ephemeral, gitignored staging
# dir (webbuild/) from the repo source, vendoring qcge FROM THE INSTALLED PACKAGE
# so the browser runs the exact same qcge version as the desktop. No hand-copying,
# so the vendored copy can't drift from source.
#
# Why vendor at all: pygbag bundles local files into the page; it does not
# pip-install at runtime. qcge is pure-Python, so the bundled copy works in the
# browser, where backend="auto" selects qcge's pure-Python simulator (importing
# numpy inside pygbag breaks the SDL display, so the bundle stays numpy-free).
#
# Usage:  bash build_web.sh
# Output: webbuild/build/web/  -> upload its contents to itch.io
set -euo pipefail
cd "$(dirname "$0")"                       # repo root
export PYGAME_HIDE_SUPPORT_PROMPT=1        # keep the pygame banner out of captured output

REPO="$(pwd)"
PY="${PYTHON:-$REPO/.venv/Scripts/python.exe}"   # venv python (has qcge + pygbag)
STAGING="web-build"

command -v "$PY" >/dev/null 2>&1 || { echo "python not found at $PY (set PYTHON=...)"; exit 1; }

echo ">> clean staging dir: $STAGING"
rm -rf "$STAGING"
mkdir -p "$STAGING/assets" "$STAGING/qcge"

echo ">> copy game source (main.py + assets, minus dev/demo files)"
cp main.py "$STAGING/main.py"
cp -r assets/. "$STAGING/assets/"
# drop heavy demo videos + bytecode from the bundle (keep the .ogg music + images)
find "$STAGING/assets" \( -name '*.mp4' -o -name '*.pyc' \) -delete 2>/dev/null || true
find "$STAGING/assets" -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true

echo ">> vendor qcge from the installed package (matches desktop)"
QCGE_DIR="$("$PY" -c 'import qcge,os;print(os.path.dirname(qcge.__file__))' | tr -d '\r')"
QCGE_VER="$("$PY" -c 'import qcge;print(qcge.__version__)' | tr -d '\r')"
echo "   qcge $QCGE_VER  <-  $QCGE_DIR"
cp -r "$QCGE_DIR/." "$STAGING/qcge/"
find "$STAGING/qcge" -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true

echo ">> pygbag build"
( cd "$STAGING" && "$PY" -m pygbag --build main.py )

echo ">> apply Quantum-Breakout theme to index.html"
bash patch_index.sh "$STAGING/build/web/index.html"

echo
echo "Done. Browser bundle (qcge $QCGE_VER): $STAGING/build/web/"
echo "Upload the *contents* of that folder to itch.io (index.html at the zip root)."
