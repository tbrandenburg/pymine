"""Regression tests for the pygame facing physics helpers."""

from __future__ import annotations

import pytest

from pymine.physics import (
    FLIGHT_SPEED,
    GRAVITY,
    JUMP_SPEED,
    MAX_FALL_SPEED,
    InputState,
    update_player_physics,
)
from pymine.world import PlayerState


def make_player(*, on_ground: bool = True, flight_mode: bool = False) -> PlayerState:
    return PlayerState(
        position=[0.0, 0.0],
        velocity=[0.0, 0.0],
        width=12.0,
        height=20.0,
        on_ground=on_ground,
        flight_mode=flight_mode,
    )


def test_left_and_right_inputs_apply_expected_signs() -> None:
    player = make_player()
    update_player_physics(player, InputState(left=True), 1 / 60)
    assert player.velocity[0] < 0

    update_player_physics(player, InputState(right=True), 1 / 60)
    assert player.velocity[0] > 0


def test_jump_initialises_negative_vertical_velocity() -> None:
    player = make_player(on_ground=True)
    update_player_physics(player, InputState(jump=True), 1 / 60)
    assert player.velocity[1] == pytest.approx(-JUMP_SPEED)
    assert not player.on_ground


def test_gravity_accumulates_positive_velocity_until_terminal() -> None:
    player = make_player(on_ground=False)
    dt = 1 / 30
    update_player_physics(player, InputState(), dt)
    assert player.velocity[1] == pytest.approx(min(GRAVITY * dt, MAX_FALL_SPEED))

    # Apply a large delta time to force the clamp.
    update_player_physics(player, InputState(), 5.0)
    assert player.velocity[1] == MAX_FALL_SPEED


def test_flight_controls_use_correct_signs() -> None:
    player = make_player(on_ground=False, flight_mode=True)
    update_player_physics(player, InputState(up=True), 1 / 60)
    assert player.velocity[1] == -FLIGHT_SPEED

    update_player_physics(player, InputState(down=True), 1 / 60)
    assert player.velocity[1] == FLIGHT_SPEED

