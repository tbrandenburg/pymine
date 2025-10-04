"""Pygame front end for the colourful sandbox world.

The game is intentionally small so that new Python programmers can read
through the code and experiment with their own features.  The logic is
split into two layers: :mod:`pymine.world` contains the testable data
structures while this module deals with drawing, controls and physics.
"""
from __future__ import annotations

import math
import time
import colorsys
from dataclasses import dataclass
from typing import Dict, List, Tuple

import pygame

from .physics import InputState, update_player_physics
from .world import (
    Inventory,
    PlayerState,
    build_palette,
    create_prebuilt_world,
    within_build_radius,
)

# --- Configuration -------------------------------------------------------

BLOCK_SIZE = 24
WORLD_WIDTH = 40
WORLD_HEIGHT = 30
SCREEN_SIZE = (WORLD_WIDTH * BLOCK_SIZE, WORLD_HEIGHT * BLOCK_SIZE)
DOUBLE_TAP_WINDOW = 0.3
BUILD_RADIUS = 2

@dataclass(frozen=True)
class Theme:
    """Colour theme applied to the entire front end."""

    name: str
    base_hue: float
    background_top: Tuple[int, int, int]
    background_bottom: Tuple[int, int, int]
    crosshair_color: Tuple[int, int, int]
    crosshair_outline: Tuple[int, int, int]
    player_color: Tuple[int, int, int]
    hud_shadow: Tuple[int, int, int]
    hud_text: Tuple[int, int, int]
    hud_panel: Tuple[int, int, int, int]
    selection_glow: Tuple[int, int, int]
def _theme_colour(base_hue: float, *, offset: float, lightness: float, saturation: float) -> Tuple[int, int, int]:
    r, g, b = colorsys.hls_to_rgb((base_hue + offset) % 1.0, lightness, saturation)
    return (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))


def create_themes() -> List[Theme]:
    """Generate soft themes spanning the rainbow of base hues."""

    def theme(name: str, base_hue: float) -> Theme:
        background_top = _theme_colour(base_hue, offset=-0.03, lightness=0.92, saturation=0.18)
        background_bottom = _theme_colour(base_hue, offset=0.05, lightness=0.68, saturation=0.22)
        crosshair_color = _theme_colour(base_hue, offset=0.07, lightness=0.86, saturation=0.24)
        crosshair_outline = _theme_colour(base_hue, offset=0.07, lightness=0.6, saturation=0.32)
        player_color = _theme_colour(base_hue, offset=-0.02, lightness=0.35, saturation=0.38)
        hud_shadow = _theme_colour(base_hue, offset=-0.01, lightness=0.28, saturation=0.34)
        hud_text = _theme_colour(base_hue, offset=0.12, lightness=0.93, saturation=0.16)
        hud_panel_rgb = _theme_colour(base_hue, offset=-0.02, lightness=0.23, saturation=0.4)
        selection_glow = _theme_colour(base_hue, offset=0.18, lightness=0.78, saturation=0.25)
        return Theme(
            name=name,
            base_hue=base_hue,
            background_top=background_top,
            background_bottom=background_bottom,
            crosshair_color=crosshair_color,
            crosshair_outline=crosshair_outline,
            player_color=player_color,
            hud_shadow=hud_shadow,
            hud_text=hud_text,
            hud_panel=(*hud_panel_rgb, 200),
            selection_glow=selection_glow,
        )

    return [
        theme("Azure Coast", 0.58),
        theme("Rose Dawn", 0.01),
        theme("Amber Drift", 0.09),
        theme("Sunlit Meadow", 0.16),
        theme("Verdant Mist", 0.28),
        theme("Indigo Veil", 0.67),
        theme("Violet Bloom", 0.78),
    ]


def gradient_background(surface: pygame.Surface, theme: Theme) -> None:
    """Draw a subtle vertical gradient sky."""

    top = pygame.Color(*theme.background_top)
    bottom = pygame.Color(*theme.background_bottom)
    height = surface.get_height()
    for y in range(height):
        blend = y / max(1, height - 1)
        color = pygame.Color(
            int(top.r + (bottom.r - top.r) * blend),
            int(top.g + (bottom.g - top.g) * blend),
            int(top.b + (bottom.b - top.b) * blend),
        )
        pygame.draw.line(surface, color, (0, y), (surface.get_width(), y))


def draw_world(surface: pygame.Surface, world, camera_x: float, camera_y: float) -> None:
    """Render the visible slice of the endless map."""

    screen_width = surface.get_width()
    start_column = int(math.floor(camera_x / BLOCK_SIZE))
    column_offset = -(camera_x - start_column * BLOCK_SIZE)
    first_column = start_column - 1
    columns_to_draw = WORLD_WIDTH + 3
    world.ensure_range(first_column, columns_to_draw)

    screen_height = surface.get_height()
    start_row = int(math.floor(camera_y / BLOCK_SIZE))
    row_offset = -(camera_y - start_row * BLOCK_SIZE)
    first_row = start_row - 1
    rows_to_draw = WORLD_HEIGHT + 3
    world.ensure_vertical_range(first_row, rows_to_draw)

    for index in range(columns_to_draw):
        world_x = first_column + index
        screen_x = column_offset + (index - 1) * BLOCK_SIZE
        if screen_x <= -BLOCK_SIZE or screen_x >= screen_width:
            continue
        for row in range(rows_to_draw):
            world_y = first_row + row
            screen_y = row_offset + (row - 1) * BLOCK_SIZE
            if screen_y <= -BLOCK_SIZE or screen_y >= screen_height:
                continue
            block = world.get(world_x, world_y)
            if block is None:
                continue
            rect = pygame.Rect(int(screen_x), int(screen_y), BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(surface, block.color, rect)
            pygame.draw.rect(surface, (0, 0, 0), rect, 1)


def draw_player(
    surface: pygame.Surface, player: PlayerState, theme: Theme, camera_x: float, camera_y: float
) -> None:
    rect = pygame.Rect(
        int(player.position[0] - camera_x),
        int(player.position[1] - camera_y),
        int(player.width),
        int(player.height),
    )
    pygame.draw.rect(surface, theme.player_color, rect, border_radius=4)


def draw_crosshair(
    surface: pygame.Surface,
    block_pos: Tuple[int, int],
    theme: Theme,
    camera_x: float,
    camera_y: float,
) -> None:
    rect = pygame.Rect(
        int(block_pos[0] * BLOCK_SIZE - camera_x),
        int(block_pos[1] * BLOCK_SIZE - camera_y),
        BLOCK_SIZE,
        BLOCK_SIZE,
    )
    pygame.draw.rect(surface, theme.crosshair_color, rect, width=2)
    pygame.draw.rect(surface, theme.crosshair_outline, rect.inflate(-4, -4), width=2)


def draw_inventory(
    surface: pygame.Surface,
    font: pygame.font.Font,
    inventory: Inventory,
    theme: Theme,
) -> None:
    margin = 10
    slot_size = 48
    total_width = len(inventory.slots) * slot_size + (len(inventory.slots) - 1) * 8
    x = (surface.get_width() - total_width) // 2
    y = surface.get_height() - slot_size - margin

    overlay = pygame.Surface((total_width + 20, slot_size + 20), pygame.SRCALPHA)
    overlay.fill(theme.hud_panel)
    surface.blit(overlay, (x - 10, y - 10))

    for index, block in enumerate(inventory.slots):
        slot_rect = pygame.Rect(x + index * (slot_size + 8), y, slot_size, slot_size)
        pygame.draw.rect(surface, block.color, slot_rect.inflate(-10, -10), border_radius=8)
        pygame.draw.rect(surface, theme.hud_shadow, slot_rect, 2, border_radius=8)
        number = font.render(str(index + 1), True, theme.hud_shadow)
        surface.blit(number, (slot_rect.x + 4, slot_rect.y + 4))
        if index == inventory.selected_index:
            pygame.draw.rect(surface, theme.selection_glow, slot_rect, 3, border_radius=8)

        name_label = font.render(block.name, True, theme.hud_text)
        label_pos = (slot_rect.centerx - name_label.get_width() // 2, slot_rect.bottom + 2)
        surface.blit(name_label, label_pos)


def draw_status(
    surface: pygame.Surface,
    font: pygame.font.Font,
    player: PlayerState,
    theme: Theme,
    theme_name: str,
) -> None:
    messages = [
        "Space: jump  |  Double space: toggle flight",
        "Shift: crouch  |  1-5: choose block  |  Left click: place  |  Right click: remove",
        "Press T to relax with a new colour theme",
        f"Flight mode: {'ON' if player.flight_mode else 'OFF'}  |  Theme: {theme_name}",
    ]
    for i, text in enumerate(messages):
        label = font.render(text, True, theme.hud_shadow)
        surface.blit(label, (10, 10 + i * (label.get_height() + 4)))


def handle_input(keys: Dict[int, bool]) -> InputState:
    """Translate pygame's key state into our simpler structure."""

    state = InputState()
    state.left = keys.get(pygame.K_a, False) or keys.get(pygame.K_LEFT, False)
    state.right = keys.get(pygame.K_d, False) or keys.get(pygame.K_RIGHT, False)
    state.up = keys.get(pygame.K_w, False) or keys.get(pygame.K_UP, False)
    state.down = keys.get(pygame.K_s, False) or keys.get(pygame.K_DOWN, False)
    state.jump = keys.get(pygame.K_SPACE, False)
    state.crouch = keys.get(pygame.K_LSHIFT, False) or keys.get(pygame.K_RSHIFT, False)
    return state


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


def move_player(world, player: PlayerState, dt: float) -> None:
    """Move the player while preventing them from entering solid tiles."""

    _update_player_stance(world, player)

    # Horizontal movement
    player.position[0] += player.velocity[0] * dt
    if player.velocity[0] > 0:
        right = player.position[0] + player.width
        tile_x = int(right // BLOCK_SIZE)
        y_start = int(player.position[1] // BLOCK_SIZE)
        y_end = int((player.position[1] + player.height - 1) // BLOCK_SIZE)
        for tile_y in range(y_start, y_end + 1):
            if world.is_solid(tile_x, tile_y):
                player.position[0] = tile_x * BLOCK_SIZE - player.width
                player.velocity[0] = 0
                break
    elif player.velocity[0] < 0:
        left = player.position[0]
        tile_x = int(math.floor(left / BLOCK_SIZE))
        y_start = int(player.position[1] // BLOCK_SIZE)
        y_end = int((player.position[1] + player.height - 1) // BLOCK_SIZE)
        for tile_y in range(y_start, y_end + 1):
            if world.is_solid(tile_x, tile_y):
                player.position[0] = (tile_x + 1) * BLOCK_SIZE
                player.velocity[0] = 0
                break

    # Vertical movement
    player.position[1] += player.velocity[1] * dt
    player.on_ground = False
    if player.velocity[1] > 0:
        bottom = player.position[1] + player.height
        tile_y = int(bottom // BLOCK_SIZE)
        x_start = int(player.position[0] // BLOCK_SIZE)
        x_end = int((player.position[0] + player.width - 1) // BLOCK_SIZE)
        for tile_x in range(x_start, x_end + 1):
            if world.is_solid(tile_x, tile_y):
                player.position[1] = tile_y * BLOCK_SIZE - player.height
                player.velocity[1] = 0
                player.on_ground = True
                break
    elif player.velocity[1] < 0:
        top = player.position[1]
        tile_y = int(math.floor(top / BLOCK_SIZE))
        x_start = int(player.position[0] // BLOCK_SIZE)
        x_end = int((player.position[0] + player.width - 1) // BLOCK_SIZE)
        for tile_x in range(x_start, x_end + 1):
            if world.is_solid(tile_x, tile_y):
                player.position[1] = (tile_y + 1) * BLOCK_SIZE
                player.velocity[1] = 0
                break


def build_crosshair(
    player: PlayerState, mouse_pos: Tuple[int, int], camera_x: float, camera_y: float
) -> Tuple[int, int]:
    """Snap the mouse position to the grid and clamp to the build radius."""

    mouse_block = (
        int((mouse_pos[0] + camera_x) // BLOCK_SIZE),
        int((mouse_pos[1] + camera_y) // BLOCK_SIZE),
    )
    player_block = (
        int((player.position[0] + player.width / 2) // BLOCK_SIZE),
        int((player.position[1] + player.height / 2) // BLOCK_SIZE),
    )
    dx = int(clamp(mouse_block[0] - player_block[0], -BUILD_RADIUS, BUILD_RADIUS))
    dy = int(clamp(mouse_block[1] - player_block[1], -BUILD_RADIUS, BUILD_RADIUS))
    target_x = player_block[0] + dx
    target_y = player_block[1] + dy
    return target_x, target_y


def _area_intersects_solid(world, left: float, top: float, width: float, height: float) -> bool:
    x_start = int(math.floor(left / BLOCK_SIZE))
    x_end = int((left + width - 1) // BLOCK_SIZE)
    y_start = int(math.floor(top / BLOCK_SIZE))
    y_end = int((top + height - 1) // BLOCK_SIZE)
    for tile_x in range(x_start, x_end + 1):
        for tile_y in range(y_start, y_end + 1):
            if world.is_solid(tile_x, tile_y):
                return True
    return False


def _update_player_stance(world, player: PlayerState) -> None:
    """Ensure the player's collision box matches their crouch state."""

    target_height = (
        player.crouching_height if player.crouching else player.standing_height
    )
    assert target_height is not None

    # Nothing to do if already using the desired hitbox size.
    if abs(player.height - target_height) < 1e-5:
        return

    bottom = player.position[1] + player.height

    if target_height < player.height:
        # Shrinking simply lowers the top edge while keeping the feet planted.
        player.height = target_height
        player.position[1] = bottom - player.height
        return

    # Standing back up requires checking that the taller hitbox has clearance.
    new_top = bottom - target_height
    if _area_intersects_solid(world, player.position[0], new_top, player.width, target_height):
        # Not enough headroom—force the crouch state to persist.
        player.crouching = True
        return

    player.height = target_height
    player.position[1] = new_top


def block_rect(block_pos: Tuple[int, int]) -> pygame.Rect:
    return pygame.Rect(block_pos[0] * BLOCK_SIZE, block_pos[1] * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)


def player_intersects_block(player: PlayerState, block_pos: Tuple[int, int]) -> bool:
    rect = block_rect(block_pos)
    player_rect = pygame.Rect(
        player.position[0],
        player.position[1],
        player.width,
        player.height,
    )
    return player_rect.colliderect(rect)


def apply_palette_to_world(world, palette) -> None:
    """Replace themeable blocks in the world with the active palette."""

    if hasattr(world, "retheme"):
        world.retheme(palette)
        return

    replacements = {block.name: block for block in palette}
    for y, row in enumerate(world.tiles):
        for x, block in enumerate(row):
            if block is None:
                continue
            if block.name in replacements:
                world.tiles[y][x] = replacements[block.name]


def main() -> None:
    pygame.init()
    pygame.display.set_caption("PyMine - Colourful Sandbox")
    screen = pygame.display.set_mode(SCREEN_SIZE)
    clock = pygame.time.Clock()

    themes = create_themes()
    theme_index = 0
    theme = themes[theme_index]
    pygame.display.set_caption(f"PyMine - {theme.name}")

    palette = build_palette(theme.base_hue)
    inventory = Inventory(slots=list(palette))
    world = create_prebuilt_world(WORLD_WIDTH, WORLD_HEIGHT, palette)

    player = PlayerState(position=[BLOCK_SIZE * 3.0, BLOCK_SIZE * 10.0], velocity=[0.0, 0.0], width=BLOCK_SIZE * 0.6, height=BLOCK_SIZE * 0.9)

    fonts = {
        "hud": pygame.font.SysFont("arial", 18),
        "inventory": pygame.font.SysFont("arial", 16),
    }

    running = True
    last_space_time = 0.0
    camera_x = 0.0
    camera_y = 0.0

    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type in {pygame.QUIT, pygame.WINDOWCLOSE}:
                running = False
            elif event.type == pygame.KEYDOWN:
                if pygame.K_1 <= event.key <= pygame.K_5:
                    slot = event.key - pygame.K_1
                    if slot < len(inventory.slots):
                        inventory.select(slot)
                if event.key == pygame.K_SPACE:
                    now = time.time()
                    if now - last_space_time < DOUBLE_TAP_WINDOW:
                        player.toggle_flight()
                        last_space_time = 0.0
                    else:
                        last_space_time = now
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_t:
                    theme_index = (theme_index + 1) % len(themes)
                    theme = themes[theme_index]
                    pygame.display.set_caption(f"PyMine - {theme.name}")
                    palette = build_palette(theme.base_hue)
                    selected_slot = inventory.selected_index
                    inventory.slots = list(palette)
                    inventory.selected_index = min(selected_slot, len(inventory.slots) - 1)
                    apply_palette_to_world(world, palette)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                target_block = build_crosshair(
                    player, pygame.mouse.get_pos(), camera_x, camera_y
                )
                player_block = (
                    int((player.position[0] + player.width / 2) // BLOCK_SIZE),
                    int((player.position[1] + player.height / 2) // BLOCK_SIZE),
                )
                if not within_build_radius(player_block, target_block, BUILD_RADIUS):
                    continue
                if player_intersects_block(player, target_block):
                    continue

                if event.button == 1:
                    if world.get(*target_block) is None:
                        world.set(*target_block, inventory.selected)
                elif event.button == 3:
                    if world.get(*target_block) is not None:
                        world.set(*target_block, None)

        pressed = pygame.key.get_pressed()
        key_state = {key: pressed[key] for key in range(len(pressed))}
        inputs = handle_input(key_state)

        update_player_physics(player, inputs, dt)

        move_player(world, player, dt)

        # Keep the camera centred around the player as the world scrolls.
        camera_x = player.position[0] + player.width / 2 - SCREEN_SIZE[0] / 2
        camera_y = player.position[1] + player.height / 2 - SCREEN_SIZE[1] / 2

        min_camera_y = world.top * BLOCK_SIZE
        max_camera_y = world.bottom * BLOCK_SIZE + BLOCK_SIZE - SCREEN_SIZE[1]
        if max_camera_y < min_camera_y:
            max_camera_y = min_camera_y
        camera_y = clamp(camera_y, min_camera_y, max_camera_y)

        gradient_background(screen, theme)
        draw_world(screen, world, camera_x, camera_y)
        draw_player(screen, player, theme, camera_x, camera_y)
        crosshair_block = build_crosshair(
            player, pygame.mouse.get_pos(), camera_x, camera_y
        )
        draw_crosshair(screen, crosshair_block, theme, camera_x, camera_y)
        draw_inventory(screen, fonts["inventory"], inventory, theme)
        draw_status(screen, fonts["hud"], player, theme, theme.name)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
