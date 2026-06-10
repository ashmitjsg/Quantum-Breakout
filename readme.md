# Quantum Breakout

**▶ Play in your browser:** [ashmitjsg.itch.io/quantum-breakout](https://ashmitjsg.itch.io/quantum-breakout)

A quantum version of the classic Breakout game. Your paddle is a **quantum state**:
you build a small quantum circuit to control *where the paddle can be*, then break the
bricks. The paddle's opacity over each position is the probability of measuring that
state; as the ball approaches, the state is **measured** and the paddle collapses to a
single position.

Built with **Pygame** on top of the reusable [**qcge**](https://pypi.org/project/qcge/)
(Quantum Circuit Game Engine). The circuit runs on real **Qiskit** on the desktop and on
a dependency-free **pure-Python statevector simulator** in the browser (pygbag/WebAssembly),
where Qiskit cannot run - so the exact same game plays both places.

## Learn by playing - in-game levels

There is no separate tutorial to read: the game teaches itself. Each level opens with a
short concept board, then restricts the gate palette so you practise that one idea:

1. **Superposition** - the H (Hadamard) gate spreads the paddle across positions.
2. **Measurement & Collapse** - the approaching ball measures the paddle to one position.
3. **Pauli-X (bit flip)** - X moves which basis state you occupy; combine with H.
4. **Phase: Z, S, T** - phase is invisible to a single measurement but changes interference.
5. **Entanglement (CX)** - a controlled-X links two qubits.

## Play instructions

- **Arrow keys** - move the circuit cursor.
- **X / Y / Z / H** - place an X / Y / Z / Hadamard gate.
- **S / T** - place S / T phase gates. *(This is why the cursor uses the arrow keys, not WASD - the S key is needed for the S gate.)*
- **C** - make a gate controlled, then **R / F** to attach the control above/below.
- **Q / E** - turn X/Y/Z into a rotation (RX/RY/RZ), decreasing/increasing the angle by π/8.
- **Backspace** - remove the gate under the cursor. **Delete** - clear the circuit.
- **Space** - advance the concept boards / start a level.

## Run on the desktop

```bash
python -m venv qenv
# Windows:  .\qenv\Scripts\Activate.ps1     Linux/macOS: source qenv/bin/activate
pip install -r requirements-dev.txt
python main.py
```

On the desktop `qcge` selects the real Qiskit backend automatically.

## Build for the browser (itch.io)

The browser build is produced with [pygbag](https://github.com/pygame-web/pygbag) and
must stay **numpy-free** (importing numpy inside pygbag breaks the SDL display); qcge's
`backend="auto"` handles this by using its pure-Python simulator in the browser. Full,
reproducible steps - including the post-build theming - are in
[**WEB_BUILD.md**](WEB_BUILD.md).

## Credits

A quantum re-imagining of the Atari *Breakout*, inspired by and indebted to **QPong** by
Junye Huang and the Qiskit *12 Days of Qiskit* series
([playlist](https://youtube.com/playlist?list=PLOFEBzvs-VvodTkP_rfrs3RWdeWE9aNRD)).
Originally built for Team Abraxas at Fest Nimbus (NIT Hamirpur), and rebuilt for v2 on the
standalone qcge engine with in-game teaching levels and a browser build.
