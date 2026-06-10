# Browser build (pygbag → itch.io)

Quantum-Breakout runs in the browser via [pygbag](https://github.com/pygame-web/pygbag),
which compiles the pygame game to WebAssembly (Pyodide). In the browser, qcge's
`backend="auto"` automatically uses the dependency-free **pure-Python** statevector
simulator (`backend="python"`), since Qiskit cannot run under Pyodide.

## CRITICAL: the browser build must stay numpy-free

Importing **numpy** inside pygbag breaks the SDL display: `pygame.display.set_mode()`
hangs / raises *"The video driver did not add any displays"*, and you get a grey
screen that never starts. This is independent of import order - pygbag preloads the
numpy wheel at boot from a scan of `main.py`, and merely loading it poisons the
canvas/display init. (Diagnosed by A/B: a minimal pygame app renders; the same app
`+ import numpy` hangs at `set_mode`.)

Therefore:
- **`main.py` must not import numpy**, and nothing it imports on the startup path may
  either. qcge is structured so `import qcge` is numpy-free (the numpy/qiskit backends
  are lazy; the core, IR, result and registry use only the standard library).
- The browser path uses qcge's **pure-Python** backend (identical results to numpy and
  qiskit - verified to 0.0 amplitude difference).
- Desktop is unaffected: there `backend="auto"` picks real Qiskit.

## Why a clean staging directory

pygbag bundles the *entire* working directory. If you build from the repo root it
will try to package `.venv/` (hundreds of MB, including Qiskit/SciPy) and fail on
stray asset formats. Build from a clean staging dir (`qbreakout-web/`) that contains
only what the browser needs: `main.py`, the vendored `qcge/`, and `assets/`.

## Build steps

```bash
# from quantum-games/, into the existing clean staging dir qbreakout-web/
cp Quantum-Breakout/main.py qbreakout-web/main.py
# re-vendor qcge (until qcge 2.x is on PyPI)
cp -r Quantum-Circuit-Game-Engine/qcge/* qbreakout-web/qcge/

cd qbreakout-web
python -m pygbag --build main.py        # produces build/web/{index.html, *.apk, favicon.png}
bash patch_index.sh                      # re-apply the black/magenta theme (see below)
# or, to playtest locally:
python -m pygbag main.py                 # serves at http://localhost:8000
```

Result: `qbreakout-web/build/web/` - `index.html` + `*.apk` (~5 MB). No `numpy-*.whl`
is fetched at runtime (check the Network tab; only `pygame_ce-*.whl` should load).

## Theme patch (`patch_index.sh`)

`pygbag --build` regenerates `index.html` with a grey page background, a
green/powderblue loader splash, and a focus outline on the canvas (thin white
border). Re-apply the Quantum-Breakout theme after every build:

```bash
# from qbreakout-web/, against build/web/index.html
f=build/web/index.html
sed -i 's/style.background = "#7f7f7f"/style.background = "#000000"/' "$f"   # page bg -> black
sed -i 's/background-color:powderblue;/background-color:#000000;/'    "$f"   # body bg -> black
sed -i 's/background: green;/background: #000000;/'                   "$f"   # loader box -> black
sed -i 's/color: blue;/color: #ff00ff;/'                             "$f"   # loader text -> magenta
# kill the canvas focus outline (thin white border, top/bottom)
sed -i 's#</style>#        canvas, #canvas, .emscripten { outline: none !important; border: none !important; }\n    </style>#' "$f"
```

(The repo keeps these as `qbreakout-web/patch_index.sh` so it is one command.)

## Audio

`start_music()` runs on web too. Browsers block autoplay until the player's first
gesture (click/keypress); pygbag resumes the queued stream automatically on that
gesture, so background music starts after the first interaction. The track
(`assets/8BitAdventure.ogg`) is bundled.

## Upload to itch.io

1. Zip the **contents** of `build/web/` (so `index.html` is at the zip root).
2. itch.io → your project (https://ashmitjsg.itch.io/quantum-breakout) → Edit →
   Kind of project: **HTML**, upload the zip, tick **"This file will be played in
   the browser"**.
3. Set viewport to the game size (1200×750) and enable fullscreen.
