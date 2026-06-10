"""Data-driven level definitions.

Each :class:`Level` pairs a quantum concept with the in-game lesson shown on its
concept board, the gate palette the player may use, and a concrete scoring aim
(bricks to break vs. balls you may drop). Levels are pure data, so the teaching
content, difficulty and ordering can be changed or extended without touching
scene/engine code (open/closed: new levels = new data, not new code paths).

Design rationale - the paddle is a 3-qubit state spread over 8 slots, and a slot is
caught only if the random measurement lands on the ball's lane:
  * Deterministic gates (X) let you put 100% of the probability on one slot, so the
    paddle is fully steerable and the level is reliably winnable.
  * Superposition (H) spreads probability across slots, so each catch is a gamble -
    great for *teaching* measurement, but a poor primary objective.
So the progression front-loads steerability (X first), then introduces probability,
interference and entanglement, and the per-level `win_score`/`lose_score` are tuned
so the objective stays achievable with the gates that level allows.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Level:
    number: int
    title: str               # short concept name, e.g. "Superposition"
    lines: tuple[str, ...]    # teaching board body, one entry per line
    goal: str                 # one-line objective shown during play
    gate_hint: str            # which gate(s) this level is about
    win_score: int            # bricks to break to clear the level
    lose_score: int           # balls you may drop before losing
    allowed_gates: tuple[str, ...] | None = None  # restrict the palette (None = all)


LEVELS: tuple[Level, ...] = (
    Level(
        number=1,
        title="Qubits & the X gate",
        lines=(
            "Your paddle is a 3-qubit register: 3 wires = 8 possible",
            "slots (000..111). The X gate is the quantum NOT - it",
            "flips a wire's 0 to 1, moving the paddle to a definite",
            "slot. No randomness here: you are in full control.",
            "",
            "Place X gates to put the paddle exactly under the ball.",
        ),
        goal="Steer with X and break 5 bricks (drop 5 and you lose).",
        gate_hint="X",
        win_score=5,
        lose_score=5,
        allowed_gates=("X",),
    ),
    Level(
        number=2,
        title="Superposition (H)",
        lines=(
            "The H (Hadamard) gate puts a wire into an equal",
            "superposition of 0 and 1 - so the paddle exists over",
            "TWO slots at once, each at 50% (shown as paddle opacity).",
            "",
            "One H doubles your coverage but halves each slot's",
            "chance. Use X to aim the pair near the ball.",
        ),
        goal="Cover the ball with one H (50/50). Break 3 bricks; you may drop 8.",
        gate_hint="H (+ X to aim)",
        win_score=3,
        lose_score=8,
        allowed_gates=("X", "H"),
    ),
    Level(
        number=3,
        title="Measurement & Collapse",
        lines=(
            "You never see a superposition directly. When the ball",
            "arrives the paddle is MEASURED and collapses to a single",
            "slot, at random, weighted by the probabilities you built.",
            "",
            "More H gates = wider spread but lower odds per slot.",
            "Keep probability concentrated where the ball will be.",
        ),
        goal="Balance spread vs. odds. Break 4 bricks; you may drop 7.",
        gate_hint="H + X (measurement is automatic)",
        win_score=4,
        lose_score=7,
        allowed_gates=("X", "H"),
    ),
    Level(
        number=4,
        title="Phase & interference (Z, S, T)",
        lines=(
            "Beyond 0 and 1 a qubit carries a phase. Z, S and T",
            "rotate it. Phase is invisible to one measurement, but",
            "it changes how amplitudes interfere under more gates:",
            "H - Z - H on a wire flips it, steering via interference.",
            "",
            "Use phase between H gates to redirect your paddle.",
        ),
        goal="Steer with interference (try H-Z-H). Break 4 bricks; you may drop 8.",
        gate_hint="Z / S / T between H gates",
        win_score=4,
        lose_score=8,
        allowed_gates=("H", "Z", "S", "T"),
    ),
    Level(
        number=5,
        title="Entanglement (CX)",
        lines=(
            "Press C on an X gate, then R/F to attach a control on",
            "another wire: a controlled-X (CX). The target flips only",
            "when the control is 1. Put H on the control first and",
            "you get a Bell state - two slots, perfectly correlated.",
            "",
            "Measuring one wire instantly decides the other.",
        ),
        goal="Build H then CX to entangle. Break 4 bricks; you may drop 8.",
        gate_hint="H, then CX (C then R/F)",
        win_score=4,
        lose_score=8,
        allowed_gates=("H", "X", "CTRL"),
    ),
)
