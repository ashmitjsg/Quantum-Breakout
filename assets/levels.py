"""Data-driven level definitions.

Each :class:`Level` pairs a quantum concept with the in-game lesson shown on its
concept board before play. Levels are pure data, so the teaching content and
ordering can be changed or extended without touching scene/engine code
(open/closed: new levels = new data, not new code paths).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Level:
    number: int
    title: str          # short concept name, e.g. "Superposition"
    lines: tuple[str, ...]   # teaching board body, one entry per line
    goal: str           # one-line objective shown during play
    gate_hint: str      # which gate(s) this level is about
    allowed_gates: tuple[str, ...] | None = None  # restrict the palette (None = all)


LEVELS: tuple[Level, ...] = (
    Level(
        number=1,
        title="Superposition",
        lines=(
            "A qubit can be 0 AND 1 at once - a 'superposition'.",
            "The H (Hadamard) gate puts a qubit into an equal",
            "superposition, so your paddle exists over several",
            "positions at the same time.",
            "",
            "Press H on the top wire and watch the paddles glow",
            "with their probabilities.",
        ),
        goal="Use H to spread your paddle across positions.",
        gate_hint="H",
        allowed_gates=("H",),
    ),
    Level(
        number=2,
        title="Measurement & Collapse",
        lines=(
            "You never see a superposition directly. Looking at it",
            "- a 'measurement' - collapses it to ONE outcome,",
            "at random, weighted by the probabilities.",
            "",
            "When the ball comes close, the quantum paddle is",
            "measured and snaps to a single position.",
        ),
        goal="Watch the ball collapse your paddle to one state.",
        gate_hint="(measurement happens automatically)",
        allowed_gates=("H", "X"),
    ),
    Level(
        number=3,
        title="Pauli-X (bit flip)",
        lines=(
            "The X gate is the quantum NOT: it flips |0> to |1>",
            "and |1> to |0>, moving which basis state you occupy.",
            "",
            "Combine X with H to choose WHICH positions your",
            "superposition covers.",
        ),
        goal="Use X to flip qubits and steer your paddle.",
        gate_hint="X",
        allowed_gates=("H", "X"),
    ),
    Level(
        number=4,
        title="Phase: Z, S, T",
        lines=(
            "Beyond 0 and 1, a qubit carries a 'phase'. The Z, S",
            "and T gates rotate this phase. Phase is invisible to a",
            "single measurement, but it changes how amplitudes",
            "interfere when you apply more gates (e.g. H Z H).",
        ),
        goal="Add phase gates between H gates and watch interference.",
        gate_hint="Z / S / T",
        allowed_gates=("H", "Z", "S", "T"),
    ),
    Level(
        number=5,
        title="Entanglement (CX)",
        lines=(
            "The controlled-X (CX) gate links two qubits: the",
            "target flips only if the control is 1. Applied to a",
            "superposition it creates ENTANGLEMENT - measuring one",
            "qubit instantly determines the other.",
            "",
            "Press C on an X gate, then R/F to attach a control.",
        ),
        goal="Build a CX to entangle your qubits.",
        gate_hint="CX (C then R/F)",
        allowed_gates=("H", "X", "CTRL"),
    ),
)
