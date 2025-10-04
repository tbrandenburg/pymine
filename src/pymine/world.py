"""Core game logic for the colourful sandbox world.

This module purposely keeps pygame specific code out so that the
behaviour can be unit tested.  The :mod:`pymine.game` module provides the
interactive pygame front end.  Colour palettes can be generated from a
base hue so that the front end can present multiple relaxing themes
without changing the underlying mechanics.
"""
from __future__ import annotations

import colorsys
import random
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple


@dataclass(frozen=True)
class BlockType:
    """Represents a single type of block.

    Attributes
    ----------
    name:
        Human readable name displayed in the HUD.
    color:
        RGB tuple used for drawing the block.
    solid:
        Whether the block obstructs the player.
    """

    name: str
    color: Tuple[int, int, int]
    solid: bool = True


class BlockPalette:
    """Palette containing every buildable block type.

    The palette exposes dictionary style access by name and keeps the
    insertion order to allow predictable inventory listings.
    """

    def __init__(self, blocks: Iterable[Tuple[str, BlockType]]):
        self._blocks: Dict[str, BlockType] = dict(blocks)

    def __getitem__(self, key: str) -> BlockType:
        return self._blocks[key]

    def __iter__(self) -> Iterable[BlockType]:
        return iter(self._blocks.values())

    def names(self) -> List[str]:
        return list(self._blocks.keys())

    def __len__(self) -> int:
        return len(self._blocks)


@dataclass
class Inventory:
    """A small, beginner friendly inventory implementation."""

    slots: List[BlockType]
    selected_index: int = 0

    def select(self, index: int) -> None:
        if not 0 <= index < len(self.slots):
            raise IndexError("Inventory slot out of range")
        self.selected_index = index

    @property
    def selected(self) -> BlockType:
        return self.slots[self.selected_index]


@dataclass
class WorldGrid:
    """Stores the tile based world layout."""

    width: int
    height: int
    default_block: Optional[BlockType]
    tiles: List[List[Optional[BlockType]]] = field(init=False)

    def __post_init__(self) -> None:
        self.tiles = [
            [self.default_block for _ in range(self.width)]
            for _ in range(self.height)
        ]

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def get(self, x: int, y: int) -> Optional[BlockType]:
        if not self.in_bounds(x, y):
            raise IndexError("Coordinate outside of world")
        return self.tiles[y][x]

    def set(self, x: int, y: int, block: Optional[BlockType]) -> None:
        if not self.in_bounds(x, y):
            raise IndexError("Coordinate outside of world")
        self.tiles[y][x] = block

    def is_solid(self, x: int, y: int) -> bool:
        if not self.in_bounds(x, y):
            return True
        block = self.tiles[y][x]
        return bool(block and block.solid)


class InfiniteWorld:
    """Procedurally extends the horizontal world as the player explores."""

    def __init__(
        self,
        *,
        height: int,
        palette: BlockPalette,
        default_block: Optional[BlockType] = None,
    ) -> None:
        self._top = 0
        self._bottom = height - 1
        self.default_block = default_block
        self._columns: Dict[int, List[Optional[BlockType]]] = {}
        self._palette_blocks: List[BlockType] = []
        self.horizon = height // 2 + 4
        self.ground_block = BlockType("Soil", (124, 98, 76))
        self.grass_block = BlockType("Grass", (118, 158, 108))
        self.stone_block = BlockType("Stone", (105, 110, 125))
        self.retheme(palette)

    @property
    def top(self) -> int:
        return self._top

    @property
    def bottom(self) -> int:
        return self._bottom

    @property
    def height(self) -> int:
        return self._bottom - self._top + 1

    def _base_block_for(self, x: int, y: int) -> Optional[BlockType]:
        """Return the default block generated for ``(x, y)``."""

        block: Optional[BlockType]
        if y < self.horizon:
            block = self.default_block
        else:
            depth = y - self.horizon
            if depth == 0:
                block = self.grass_block
            elif depth < 6:
                block = self.ground_block
            else:
                block = self.stone_block

        # Decorative floating platforms with palette colours.
        pattern_index = x // 9
        platform_phase = x % 9
        if platform_phase in {0, 1, 2}:
            height_offset = pattern_index % 3
            platform_y = self.horizon - 4 - height_offset * 2
            if y == platform_y:
                platform_block = self._palette_choice(pattern_index)
                if platform_block is not None:
                    return platform_block

        # Gentle crystal outcrops just above the grass.
        rng = random.Random((x + 3000) * 92821)
        spawn_crystal = rng.random() < 0.1
        spawn_stack = rng.random() < 0.5 if spawn_crystal else False
        if spawn_crystal:
            if y == self.horizon - 1:
                crystal = self._palette_choice(x)
                if crystal is not None:
                    return crystal
            if spawn_stack and y == self.horizon - 2:
                topper = self._palette_choice(x + 1)
                if topper is not None:
                    return topper

        # Mario-like staircase near the origin to keep the tutorial feel.
        if -2 <= x <= 8:
            step = max(0, 8 - x)
            stair_y = self.horizon - 1 - step
            if y == stair_y:
                return self.stone_block

        return block

    def _generate_column(self, x: int, top: int, bottom: int) -> List[Optional[BlockType]]:
        return [self._base_block_for(x, y) for y in range(top, bottom + 1)]

    def _expand_columns_to(self, new_top: int, new_bottom: int) -> None:
        for x, column in self._columns.items():
            if new_top < self._top:
                prepend = [self._base_block_for(x, y) for y in range(new_top, self._top)]
                column[0:0] = prepend
            if new_bottom > self._bottom:
                column.extend(
                    self._base_block_for(x, y)
                    for y in range(self._bottom + 1, new_bottom + 1)
                )
        self._top = min(self._top, new_top)
        self._bottom = max(self._bottom, new_bottom)

    def _ensure_vertical_bounds(self, y: int) -> None:
        if y < self._top or y > self._bottom:
            new_top = min(self._top, y)
            new_bottom = max(self._bottom, y)
            self._expand_columns_to(new_top, new_bottom)

    def _palette_choice(self, index: int) -> Optional[BlockType]:
        if not self._palette_blocks:
            return None
        return self._palette_blocks[index % len(self._palette_blocks)]

    def _ensure_column(self, x: int) -> None:
        if x in self._columns:
            return
        self._columns[x] = self._generate_column(x, self._top, self._bottom)

    def ensure_range(self, start_x: int, width: int) -> None:
        for x in range(start_x, start_x + width):
            self._ensure_column(x)

    def column(self, x: int) -> List[Optional[BlockType]]:
        """Return a full column, generating it when necessary."""

        self._ensure_column(x)
        return self._columns[x]

    def get(self, x: int, y: int) -> Optional[BlockType]:
        self._ensure_vertical_bounds(y)
        self._ensure_column(x)
        return self._columns[x][y - self._top]

    def set(self, x: int, y: int, block: Optional[BlockType]) -> None:
        self._ensure_vertical_bounds(y)
        self._ensure_column(x)
        self._columns[x][y - self._top] = block

    def is_solid(self, x: int, y: int) -> bool:
        self._ensure_vertical_bounds(y)
        self._ensure_column(x)
        index = y - self._top
        block = self._columns[x][index]
        return bool(block and block.solid)

    def iter_window(self, start_x: int, width: int) -> Iterable[List[Optional[BlockType]]]:
        self.ensure_range(start_x, width)
        for y in range(self._top, self._bottom + 1):
            yield [self.get(x, y) for x in range(start_x, start_x + width)]

    def ensure_vertical_range(self, start_y: int, height: int) -> None:
        end_y = start_y + height - 1
        self._ensure_vertical_bounds(start_y)
        self._ensure_vertical_bounds(end_y)

    def retheme(self, palette: BlockPalette) -> None:
        self.palette = palette
        self._palette_blocks = list(palette)
        replacements = {block.name: block for block in self._palette_blocks}
        for column in self._columns.values():
            for index, block in enumerate(column):
                if block is not None and block.name in replacements:
                    column[index] = replacements[block.name]


@dataclass
class PlayerState:
    """Tracks the player's physical state independent of pygame."""

    position: List[float]
    velocity: List[float]
    width: float
    height: float
    standing_height: float | None = None
    crouching_height: float | None = None
    on_ground: bool = False
    crouching: bool = False
    flight_mode: bool = False

    def __post_init__(self) -> None:
        # Preserve the original constructor signature where ``height`` defined the
        # standing collision size.  The crouching height defaults to a gentle
        # squeeze so the player still feels responsive while ducking under
        # blocks.
        if self.standing_height is None:
            self.standing_height = self.height
        if self.crouching_height is None:
            self.crouching_height = self.standing_height * 0.6

    def rect(self) -> Tuple[float, float, float, float]:
        return (*self.position, self.width, self.height)

    def toggle_flight(self) -> bool:
        self.flight_mode = not self.flight_mode
        if self.flight_mode:
            self.velocity[1] = 0.0
        return self.flight_mode


def _soft_colour(hue: float, lightness: float, saturation: float) -> Tuple[int, int, int]:
    """Convert an HLS colour to an RGB tuple tuned for soft palettes."""

    r, g, b = colorsys.hls_to_rgb(hue % 1.0, lightness, saturation)
    return (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))


def build_palette(base_hue: Optional[float] = None) -> BlockPalette:
    """Create a harmonic block palette derived from a base hue.

    Parameters
    ----------
    base_hue:
        Hue value in the range ``0-1`` used to tint the palette.  When no
        value is provided a calming blue-green hue is used by default.
    """

    if base_hue is None:
        base_hue = 0.58  # Gentle teal by default

    palette_data = [
        (
            "cloudstone",
            BlockType("Cloudstone", _soft_colour(base_hue - 0.05, 0.74, 0.22)),
        ),
        (
            "petal_clay",
            BlockType("Petal Clay", _soft_colour(base_hue, 0.63, 0.28)),
        ),
        (
            "moss_brick",
            BlockType("Moss Brick", _soft_colour(base_hue + 0.07, 0.58, 0.26)),
        ),
        (
            "glass_tile",
            BlockType("Glass Tile", _soft_colour(base_hue + 0.14, 0.68, 0.18)),
        ),
        (
            "dune_sand",
            BlockType("Dune Sand", _soft_colour(base_hue - 0.12, 0.82, 0.18)),
        ),
    ]
    return BlockPalette(palette_data)


def create_prebuilt_world(width: int, height: int, palette: BlockPalette) -> InfiniteWorld:
    """Generate the endless colourful landscape."""

    world = InfiniteWorld(height=height, palette=palette, default_block=None)

    # Prepare enough columns so the opening view feels handcrafted.  The
    # generator will take over as soon as the player ventures farther afield.
    preload_start = -width
    world.ensure_range(preload_start, width * 3)
    return world


def within_build_radius(player_block: Tuple[int, int], target_block: Tuple[int, int], radius: int = 2) -> bool:
    """Check whether the target is within a square radius of the player."""

    dx = abs(player_block[0] - target_block[0])
    dy = abs(player_block[1] - target_block[1])
    return max(dx, dy) <= radius


__all__ = [
    "BlockPalette",
    "BlockType",
    "Inventory",
    "PlayerState",
    "WorldGrid",
    "InfiniteWorld",
    "build_palette",
    "create_prebuilt_world",
    "within_build_radius",
]
