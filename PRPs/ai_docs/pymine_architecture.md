# PyMine Architecture Overview

## Core Design Principles

### 1. Clean Layer Separation
PyMine follows a strict 3-layer architecture:
```
game.py (pygame frontend) 
    ↓ depends on
physics.py (game mechanics)
    ↓ depends on  
world.py (pure logic, no pygame)
```

**Critical Rule**: The world layer must remain pygame-independent for testability.

### 2. Dataclass-Based State Management
All major game state is managed through dataclasses:

```python
# Immutable Configuration (frozen=True)
@dataclass(frozen=True)
class BlockType:
    name: str
    color: Tuple[int, int, int]
    solid: bool = True

# Mutable Game State
@dataclass
class PlayerState:
    position: List[float]
    velocity: List[float]
    width: float
    height: float
    on_ground: bool = False
```

## Module Responsibilities

### world.py - Pure Game Logic
**No pygame imports allowed**

- `BlockType`: Immutable block definitions
- `BlockPalette`: Dictionary-style block access with ordering
- `Inventory`: Simple slot-based item management
- `PlayerState`: Complete player physics state
- `InfiniteWorld`: On-demand procedural world generation
- `WorldGrid`: Fixed-size tile storage (legacy, use InfiniteWorld)

**Key Patterns**:
- Factory functions: `build_palette()`, `create_prebuilt_world()`
- Pure functions: `within_build_radius()`, `place_player_on_surface()`
- Deterministic generation with seeded Random

### physics.py - Game Mechanics Bridge
**Minimal pygame, focus on calculations**

- `InputState`: Frame-based input capture
- `update_player_physics()`: Pure function for player movement
- Physics constants: `GRAVITY`, `MOVE_SPEED`, `JUMP_SPEED`, etc.

**Integration Pattern**:
```python
# Takes pygame-agnostic input, updates pygame-agnostic state
def update_player_physics(player: PlayerState, inputs: InputState, dt: float) -> None:
    # All physics logic here
    player.velocity[0] = move_dir * speed
    player.velocity[1] = min(player.velocity[1] + GRAVITY * dt, MAX_FALL_SPEED)
```

### game.py - Pygame Frontend
**All pygame integration happens here**

- Event handling and input translation
- Rendering pipeline with camera system
- Theme system with color generation
- Asset loading and management
- Game loop with frame timing

**Key Rendering Pattern**:
```python
# Layer-based rendering order
gradient_background(screen, theme)           # Background
draw_world(screen, world, camera_x, camera_y)  # World tiles
draw_player(screen, player, theme, camera_x, camera_y)  # Player
draw_crosshair(screen, crosshair_block, theme, camera_x, camera_y)  # UI overlay
draw_inventory(screen, fonts["inventory"], inventory, theme)  # HUD
pygame.display.flip()  # Present frame
```

## Data Flow Patterns

### Event Processing
```
pygame.event.get() → handle input → update InputState → 
update_player_physics() → move_player() → render frame
```

### World Generation
```
InfiniteWorld.get(x, y) → _ensure_column(x) → _generate_column() → 
_base_block_for(x, y) → deterministic placement logic
```

### Theme System
```
base_hue → _theme_colour() → Theme dataclass → 
build_palette() → world.retheme() → visual update
```

## Critical Integration Points

### Adding New Block Types
1. Extend `build_palette()` in world.py
2. Add generation logic in `InfiniteWorld._base_block_for()`  
3. Update theme color generation if needed

```python
# In build_palette()
palette_data = [
    # ... existing blocks ...
    ("new_block", BlockType("New Block", _soft_colour(base_hue + 0.20, 0.65, 0.25))),
]
```

### Adding New Controls
1. Extend `InputState` dataclass in physics.py
2. Update `handle_input()` in game.py
3. Modify `update_player_physics()` for new behaviors

```python
# In physics.py
@dataclass
class InputState:
    # ... existing fields ...
    new_action: bool = False

# In game.py handle_input()
state.new_action = keys.get(pygame.K_x, False)
```

### Adding New Rendering
1. Create `draw_new_feature()` function following existing patterns
2. Add to main rendering sequence in game loop
3. Extend Theme dataclass if new colors needed

```python
def draw_new_feature(surface: pygame.Surface, feature_data, theme: Theme, camera_x: float, camera_y: float) -> None:
    # Follow existing draw function patterns
    # Use theme colors for consistency
    # Apply camera offset for world-space objects
```

## Advanced Patterns

### Procedural Generation Architecture
```python
# Pattern: Deterministic generation with coordinate-based seeds
rng = random.Random((x + 3000) * 92821)  # Unique per coordinate
if rng.random() < 0.1:  # Probability-based placement
    return special_block
```

### Theme Integration
```python
# Pattern: All visual elements derive from base_hue
def _theme_colour(base_hue: float, *, offset: float, lightness: float, saturation: float) -> Tuple[int, int, int]:
    r, g, b = colorsys.hls_to_rgb((base_hue + offset) % 1.0, lightness, saturation)
    return (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))
```

### Collision System
```python
# Pattern: Axis-separated collision with pixel-to-tile conversion
def move_player(world, player: PlayerState, dt: float) -> None:
    # Horizontal movement first
    player.position[0] += player.velocity[0] * dt
    # Check horizontal collisions, resolve
    
    # Vertical movement second  
    player.position[1] += player.velocity[1] * dt
    # Check vertical collisions, resolve
```

## Testing Architecture

### Test Organization
- Mirror source structure: `tests/test_physics.py`, `tests/test_world.py`
- Helper functions: `make_player()`, `_player_intersects_solid()`
- Realistic test data: Use actual block sizes and physics constants

### Test Patterns
```python
# Factory functions for test data
def make_player(*, on_ground: bool = True, flight_mode: bool = False) -> PlayerState:
    return PlayerState(
        position=[0.0, 0.0], velocity=[0.0, 0.0],
        width=12.0, height=20.0,
        on_ground=on_ground, flight_mode=flight_mode
    )

# Physics testing with realistic timing
def test_gravity():
    player = make_player(on_ground=False)
    dt = 1 / 60  # Real frame time
    update_player_physics(player, InputState(), dt)
    assert player.velocity[1] == pytest.approx(GRAVITY * dt)
```

## Common Implementation Gotchas

### Coordinate Systems
- World coordinates: Continuous float values
- Tile coordinates: Integer grid positions  
- Screen coordinates: Pixel positions with camera offset
- **Always convert explicitly**: `int(world_pos // BLOCK_SIZE)`

### Camera Calculations
```python
# Pattern: Convert mouse to world coordinates
mouse_world_x = mouse_screen_x + camera_x
mouse_world_y = mouse_screen_y + camera_y
tile_x = int(mouse_world_x // BLOCK_SIZE)
tile_y = int(mouse_world_y // BLOCK_SIZE)
```

### Infinite World Bounds
```python
# Pattern: Always ensure vertical bounds before access
def get(self, x: int, y: int) -> Optional[BlockType]:
    self._ensure_vertical_bounds(y)  # Expand world if needed
    self._ensure_column(x)           # Generate column if needed
    return self._columns[x][y - self._top]
```

### State Mutation
```python
# GOOD: Direct state modification in physics
def update_player_physics(player: PlayerState, inputs: InputState, dt: float) -> None:
    player.velocity[0] = move_dir * speed  # Mutate in place

# BAD: Creating new state objects
def update_player_physics(player: PlayerState, inputs: InputState, dt: float) -> PlayerState:
    return PlayerState(...)  # Expensive and unnecessary
```

## File Organization Rules

### Imports
```python
# Standard order
from __future__ import annotations  # Always first

import math                          # Standard library
import colorsys
from dataclasses import dataclass
from typing import Dict, List, Tuple

import pygame                        # Third party

from .physics import InputState      # Local relative imports
from .world import PlayerState
```

### Naming Conventions
- **snake_case**: Functions, variables, modules (`update_player_physics`)
- **CamelCase**: Classes (`PlayerState`, `BlockType`)  
- **UPPER_CASE**: Constants (`GRAVITY`, `BLOCK_SIZE`)
- **Descriptive names**: `place_player_on_surface` not `place_player`

### Documentation
- Module docstrings explain purpose and pygame boundaries
- Function docstrings for public API
- Type hints on all functions
- `__all__` exports for public interface

This architecture has proven robust for PyMine's current feature set and provides clean extension points for new features like crafting, mobs, and save/load systems.