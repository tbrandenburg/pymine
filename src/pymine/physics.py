"""Physics helpers shared between the core game and unit tests."""

from __future__ import annotations

from dataclasses import dataclass

from .world import PlayerState

GRAVITY = 1200.0
"""Downward acceleration applied when the player is not in flight."""

MOVE_SPEED = 180.0
FLIGHT_SPEED = 200.0
JUMP_SPEED = 480.0
"""Initial upward launch speed when jumping (roughly a four block leap)."""

MAX_FALL_SPEED = 900.0
"""Terminal velocity in pixels per second so falling feels responsive."""


@dataclass
class InputState:
    """Tracks pressed keys for a frame in a pygame agnostic way."""

    left: bool = False
    right: bool = False
    up: bool = False
    down: bool = False
    jump: bool = False
    crouch: bool = False


def update_player_physics(player: PlayerState, inputs: InputState, dt: float) -> None:
    """Update player velocity based on the controls and elapsed time.

    The function keeps the signs of the movement values intuitive for the
    coordinate system used by pygame (``y`` increases downward).  Jumping
    therefore sets a *negative* velocity and gravity adds a *positive*
    acceleration so that the player initially moves upward before being
    pulled back toward the terrain.  Flight mode overrides the gravitational
    integration and allows direct vertical steering.
    """

    # Horizontal behaviour is identical in both grounded and flight states.
    player.crouching = inputs.crouch and not player.flight_mode
    move_dir = 0
    if inputs.left:
        move_dir -= 1
    if inputs.right:
        move_dir += 1
    speed = MOVE_SPEED * (0.5 if player.crouching else 1.0)
    player.velocity[0] = move_dir * (FLIGHT_SPEED if player.flight_mode else speed)

    # Vertical behaviour switches between flight and gravity driven motion.
    if player.flight_mode:
        vertical_dir = 0
        if inputs.up:
            vertical_dir -= 1
        if inputs.down:
            vertical_dir += 1
        player.velocity[1] = vertical_dir * FLIGHT_SPEED
    else:
        if inputs.jump and player.on_ground:
            player.velocity[1] = -JUMP_SPEED
            player.on_ground = False
        else:
            player.velocity[1] = min(player.velocity[1] + GRAVITY * dt, MAX_FALL_SPEED)


__all__ = [
    "FLIGHT_SPEED",
    "GRAVITY",
    "InputState",
    "JUMP_SPEED",
    "MAX_FALL_SPEED",
    "MOVE_SPEED",
    "update_player_physics",
]

