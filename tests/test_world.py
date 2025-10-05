"""Tests for the pygame independent mechanics."""

import math

import pytest

from pymine import world


BLOCK_SIZE = 24


def test_inventory_selection():
    palette = world.build_palette()
    inventory = world.Inventory(slots=list(palette))
    inventory.select(2)
    assert inventory.selected == list(palette)[2]


def test_inventory_out_of_range():
    palette = world.build_palette()
    inventory = world.Inventory(slots=list(palette))
    try:
        inventory.select(10)
    except IndexError:
        pass
    else:
        raise AssertionError("Selecting an invalid slot should raise IndexError")


def test_world_generation_layout():
    palette = world.build_palette()
    infinite = world.create_prebuilt_world(40, 30, palette)
    horizon = infinite.horizon

    # Grass layer should exist across a generous span both directions.
    for x in range(-20, 20):
        assert infinite.get(x, horizon) is not None

    # Air above the horizon should contain some floating palette blocks without filling the sky.
    sky_blocks = 0
    for y in range(horizon):
        for x in range(-20, 20):
            block = infinite.get(x, y)
            if block is not None:
                sky_blocks += 1
    assert sky_blocks > 0
    assert sky_blocks < horizon * 40


def test_infinite_world_expands_both_directions():
    palette = world.build_palette()
    infinite = world.create_prebuilt_world(40, 30, palette)
    horizon = infinite.horizon

    assert infinite.get(250, horizon) is not None
    assert infinite.get(-250, horizon) is not None


def test_retheme_updates_existing_columns():
    first_palette = world.build_palette(0.1)
    second_palette = world.build_palette(0.6)
    infinite = world.create_prebuilt_world(40, 30, first_palette)

    palette_names = {block.name for block in first_palette}
    target = None
    for x in range(-40, 40):
        column = infinite.column(x)
        for offset, block in enumerate(column):
            y = infinite.top + offset
            if block and block.name in palette_names:
                target = (x, y, block.color)
                break
        if target:
            break

    assert target is not None
    x, y, original_color = target

    infinite.retheme(second_palette)
    updated_block = infinite.get(x, y)
    assert updated_block is not None
    assert updated_block.color != original_color
    assert updated_block.name in {block.name for block in second_palette}


def test_build_radius_check():
    assert world.within_build_radius((5, 5), (7, 7), radius=2)
    assert not world.within_build_radius((5, 5), (9, 9), radius=2)


def test_world_grid_bounds_and_solidity():
    empty = world.WorldGrid(width=4, height=3, default_block=None)
    rock = world.BlockType("Rock", (10, 10, 10))

    empty.set(1, 2, rock)
    assert empty.get(1, 2) is rock
    assert empty.is_solid(1, 2)
    assert not empty.is_solid(3, 0)

    with pytest.raises(IndexError):
        empty.get(6, 0)

    # Out-of-bounds should be treated as solid so the player cannot leave.
    assert empty.is_solid(-1, 0)


def test_infinite_world_set_and_solidity_updates():
    palette = world.build_palette()
    infinite = world.create_prebuilt_world(40, 30, palette)
    target_y = infinite.horizon - 3

    assert not infinite.is_solid(0, target_y)

    block = list(palette)[0]
    infinite.set(0, target_y, block)
    assert infinite.get(0, target_y) is block
    assert infinite.is_solid(0, target_y)

    infinite.set(0, target_y, None)
    assert infinite.get(0, target_y) is None
    assert not infinite.is_solid(0, target_y)


def test_infinite_world_extends_vertically_on_demand():
    palette = world.build_palette()
    infinite = world.create_prebuilt_world(40, 30, palette)

    original_top = infinite.top
    original_bottom = infinite.bottom

    above_block = list(palette)[0]
    below_block = list(palette)[1]

    # Extending above the current ceiling should shift the tracked top.
    new_top_y = original_top - 5
    infinite.set(2, new_top_y, above_block)
    assert infinite.top == new_top_y
    assert infinite.get(2, new_top_y) is above_block
    assert not infinite.is_solid(2, new_top_y - 1)

    # Extending below the ground should grow the world downward as well.
    new_bottom_y = original_bottom + 10
    infinite.set(-3, new_bottom_y, below_block)
    assert infinite.bottom >= new_bottom_y
    assert infinite.get(-3, new_bottom_y) is below_block
    assert infinite.is_solid(-3, new_bottom_y)


def test_iter_window_prefills_columns():
    palette = world.build_palette()
    infinite = world.create_prebuilt_world(40, 30, palette)

    start_x, width = -5, 11
    rows = list(infinite.iter_window(start_x, width))

    assert len(rows) == infinite.height
    assert all(len(row) == width for row in rows)


def test_player_state_toggle_flight_resets_velocity():
    state = world.PlayerState(position=[0.0, 0.0], velocity=[1.0, 5.5], width=1.0, height=2.0)

    assert state.toggle_flight() is True
    assert state.flight_mode is True
    assert state.velocity[1] == 0.0

    # Toggling again should disable flight without altering velocity.
    state.velocity[1] = -3.0
    assert state.toggle_flight() is False
    assert state.flight_mode is False
    assert state.velocity[1] == -3.0


def test_build_palette_hues_are_distinct():
    default_palette = list(world.build_palette())
    warm_palette = list(world.build_palette(0.1))

    assert len(default_palette) == len(warm_palette)
    assert [block.color for block in default_palette] != [block.color for block in warm_palette]

    for block in default_palette + warm_palette:
        for channel in block.color:
            assert 0 <= channel <= 255


def _player_intersects_solid(test_world, player) -> bool:
    x_start = int(math.floor(player.position[0] / BLOCK_SIZE))
    x_end = int(math.floor((player.position[0] + player.width - 1) / BLOCK_SIZE))
    y_start = int(math.floor(player.position[1] / BLOCK_SIZE))
    y_end = int(math.floor((player.position[1] + player.height - 1) / BLOCK_SIZE))
    for tile_x in range(x_start, x_end + 1):
        for tile_y in range(y_start, y_end + 1):
            if test_world.is_solid(tile_x, tile_y):
                return True
    return False


def test_place_player_on_surface_drops_to_ground():
    palette = world.build_palette()
    terrain = world.create_prebuilt_world(40, 30, palette)
    spawn_column = 15
    player = world.PlayerState(
        position=[BLOCK_SIZE * spawn_column, BLOCK_SIZE * 3.0],
        velocity=[0.0, 0.0],
        width=BLOCK_SIZE * 0.6,
        height=BLOCK_SIZE * 0.9,
    )

    world.place_player_on_surface(terrain, player, block_size=BLOCK_SIZE)

    assert player.on_ground is True
    assert not _player_intersects_solid(terrain, player)
    support_tile = int((player.position[1] + player.height) // BLOCK_SIZE)
    x_start = int(math.floor(player.position[0] / BLOCK_SIZE))
    x_end = int(math.floor((player.position[0] + player.width - 1) / BLOCK_SIZE))
    assert all(terrain.is_solid(tile_x, support_tile) for tile_x in range(x_start, x_end + 1))


def test_place_player_on_surface_clears_embedded_spawn():
    palette = world.build_palette()
    terrain = world.create_prebuilt_world(40, 30, palette)
    player_height = BLOCK_SIZE * 0.9
    spawn_y = terrain.horizon * BLOCK_SIZE - player_height
    player = world.PlayerState(
        position=[BLOCK_SIZE * 6.0, spawn_y - BLOCK_SIZE * 0.25],
        velocity=[0.0, 0.0],
        width=BLOCK_SIZE * 0.6,
        height=player_height,
    )

    player.position[1] += BLOCK_SIZE * 0.5
    assert _player_intersects_solid(terrain, player)

    world.place_player_on_surface(terrain, player, block_size=BLOCK_SIZE)

    assert player.on_ground is True
    assert not _player_intersects_solid(terrain, player)


def test_place_player_on_surface_handles_missing_support():
    palette = world.build_palette()
    terrain = world.create_prebuilt_world(40, 30, palette)
    column_x = 25
    for depth in range(terrain.top, terrain.bottom + 1):
        terrain.set(column_x, depth, None)

    player = world.PlayerState(
        position=[BLOCK_SIZE * column_x, BLOCK_SIZE * 4.0],
        velocity=[0.0, 0.0],
        width=BLOCK_SIZE * 0.6,
        height=BLOCK_SIZE * 0.9,
    )

    world.place_player_on_surface(terrain, player, block_size=BLOCK_SIZE)

    assert player.on_ground is False
    assert not _player_intersects_solid(terrain, player)
