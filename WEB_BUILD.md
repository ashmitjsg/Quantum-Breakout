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

## Build steps - one command

The browser bundle is a **generated artifact**, not source. `build_web.sh` produces
it reproducibly: it makes an ephemeral, gitignored staging dir (`web-build/`), copies
`main.py` + `assets/`, **vendors qcge from the installed package** (so the browser
runs the *exact same* qcge version as the desktop), runs pygbag, and applies the
theme. No hand-copying, so the vendored copy can't drift from source.

```bash
# from Quantum-Breakout/  (qcge must be installed in .venv: pip install -r requirements-dev.txt)
bash build_web.sh
```

Result: `web-build/build/web/` - `index.html` + `*.apk` (~5 MB). No `numpy-*.whl` is
fetched at runtime (check the Network tab; only `pygame_ce-*.whl` should load).

> Why vendor at all: pygbag bundles local files into the page; it does **not**
> pip-install at runtime. qcge is pure-Python, so the bundled copy runs in the
> browser. `web-build/` is throwaway (gitignored) - never edit it by hand; change the
> source (`main.py`, `assets/`, or qcge) and rebuild.

To playtest locally, serve the built folder statically (the bundle uses an absolute
CDN, so no proxy is needed):

```bash
python -m http.server 8000 -d web-build/build/web    # then open http://localhost:8000
```

## Theme patch (`patch_index.sh`)

`pygbag --build` regenerates `index.html` with a grey page background, a
green/powderblue loader splash, and a focus outline on the canvas (thin white
border). `build_web.sh` calls `patch_index.sh` to re-apply the Quantum-Breakout
theme (black background, white centred 8-bit loader text, no canvas outline, clean
tab-close). To re-theme an existing build by hand:

```bash
bash patch_index.sh web-build/build/web/index.html
```

## Audio

`start_music()` runs on web too. Browsers block autoplay until the player's first
gesture (click/keypress); pygbag resumes the queued stream automatically on that
gesture, so background music starts after the first interaction. The track
(`assets/8BitAdventure.ogg`) is bundled.

## Upload to itch.io

1. Zip the **contents** of `web-build/build/web/` (so `index.html` is at the zip root).
2. itch.io → your project (https://ashmitjsg.itch.io/quantum-breakout) → Edit →
   Kind of project: **HTML**, upload the zip, tick **"This file will be played in
   the browser"**.
3. Set viewport to the game size (1200×750) and enable fullscreen.
