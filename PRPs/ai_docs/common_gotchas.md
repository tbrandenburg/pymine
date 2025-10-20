# Common Gotchas & Pitfalls

## Architecture Violations

### 1. Breaking Layer Separation
**❌ NEVER DO THIS**:
```python
# In world.py - NO pygame imports allowed!
import pygame  # BREAKS ARCHITECTURE

class WorldGrid:
    def draw(self, screen):  # Rendering logic doesn't belong here
        pygame.draw.rect(screen, color, rect)
```

**✅ CORRECT APPROACH**:
```python
# world.py stays pure
class WorldGrid:
    def get_visible_blocks(self, camera_x, camera_y, view_width, view_height):
        # Return data only, no rendering
        return block_data

# game.py handles all rendering
def draw_world(screen, world, camera_x, camera_y):
    blocks = world.get_visible_blocks(camera_x, camera_y, SCREEN_WIDTH, SCREEN_HEIGHT)
    for block in blocks:
        pygame.draw.rect(screen, block.color, block.rect)
```

### 2. State Management Confusion
**❌ COMMON MISTAKE**:
```python
# Creating new state objects instead of mutating
def update_player_physics(player):
    return PlayerState(  # EXPENSIVE! Creates new object every frame
        position=[player.position[0] + velocity, player.position[1]],
        velocity=[new_vx, new_vy]
    )

# Mixing immutable and mutable state
@dataclass(frozen=True)  # frozen=True means immutable
class PlayerState:
    position: List[float]  # But List is mutable! INCONSISTENT
```

**✅ CORRECT APPROACH**:
```python
# Mutate existing state objects
def update_player_physics(player: PlayerState, inputs: InputState, dt: float) -> None:
    player.velocity[0] = new_vx  # Direct mutation
    player.velocity[1] = new_vy
    player.position[0] += player.velocity[0] * dt
    player.position[1] += player.velocity[1] * dt

# Be consistent: frozen for config, mutable for state
@dataclass(frozen=True)
class BlockType:  # Configuration - immutable
    name: str
    color: Tuple[int, int, int]

@dataclass  
class PlayerState:  # Game state - mutable
    position: List[float]
    velocity: List[float]
```

## Coordinate System Pitfalls

### 3. Coordinate Conversion Errors
**❌ COMMON MISTAKES**:
```python
# Forgetting pygame's Y-axis goes DOWN
jump_velocity = +JUMP_SPEED  # WRONG! Should be negative

# Not converting between coordinate systems
tile_x = mouse_x  # WRONG! Mouse is screen coords, need world coords
tile_y = mouse_y

# Inconsistent coordinate types
def get_block(x: float, y: float):  # WRONG! Tiles are integers
    return self.blocks[x][y]  # Will crash with float indices
```

**✅ CORRECT APPROACH**:
```python
# Remember pygame coordinate system
jump_velocity = -JUMP_SPEED  # Negative Y = upward in pygame

# Always convert coordinate systems explicitly
mouse_world_x = mouse_screen_x + camera_x
mouse_world_y = mouse_screen_y + camera_y
tile_x = int(mouse_world_x // BLOCK_SIZE)
tile_y = int(mouse_world_y // BLOCK_SIZE)

# Use correct coordinate types
def get_block(self, x: int, y: int) -> Optional[BlockType]:
    # Tile coordinates are always integers
    return self.tiles.get((x, y))
```

### 4. Camera Math Errors
**❌ COMMON MISTAKES**:
```python
# Not centering camera correctly
camera_x = player.position[0]  # WRONG! Player appears at left edge

# Forgetting camera offset in rendering
screen_x = block.world_x  # WRONG! Need to subtract camera position
screen_y = block.world_y

# Inconsistent camera bounds
camera_x = max(0, player.x)  # May allow viewing beyond world edge
```

**✅ CORRECT APPROACH**:
```python
# Center camera on player
camera_x = player.position[0] + player.width/2 - SCREEN_WIDTH/2
camera_y = player.position[1] + player.height/2 - SCREEN_HEIGHT/2

# Always apply camera offset for world objects
screen_x = world_x - camera_x
screen_y = world_y - camera_y

# Clamp camera to world bounds
min_camera_x = 0
max_camera_x = world.width * BLOCK_SIZE - SCREEN_WIDTH
camera_x = max(min_camera_x, min(camera_x, max_camera_x))
```

## Performance Gotchas

### 5. Unnecessary Surface Creation
**❌ PERFORMANCE KILLER**:
```python
def draw_text(text, font, color):
    return font.render(text, True, color)  # Creates new surface every call!

def game_loop():
    while running:
        score_text = draw_text(f"Score: {score}", font, white)  # EXPENSIVE
        screen.blit(score_text, (10, 10))
```

**✅ OPTIMIZED APPROACH**:
```python
class TextCache:
    def __init__(self):
        self.cache = {}
    
    def get_text(self, text, font, color):
        key = (text, font, color)
        if key not in self.cache:
            self.cache[key] = font.render(text, True, color)
        return self.cache[key]

# Or update only when score changes
class GameUI:
    def __init__(self):
        self.score = 0
        self.score_surface = None
    
    def update_score(self, new_score):
        if new_score != self.score:
            self.score = new_score
            self.score_surface = font.render(f"Score: {score}", True, white)
```

### 6. Inefficient Collision Detection
**❌ PERFORMANCE KILLER**:
```python
def check_collisions(player, all_blocks):
    for block in all_blocks:  # Checking ALL blocks every frame!
        if player.rect.colliderect(block.rect):
            return block
    return None

def move_player(world, player, dt):
    # Moving first, then checking - may clip through blocks
    player.x += player.velocity_x * dt
    player.y += player.velocity_y * dt
    if check_collision(player, world.all_blocks):
        # Too late! Already moved into block
        player.x -= player.velocity_x * dt
        player.y -= player.velocity_y * dt
```

**✅ OPTIMIZED APPROACH**:
```python
def check_block_collision(world, left, top, width, height):
    # Only check tiles in the area we care about
    x_start = int(left // BLOCK_SIZE)
    x_end = int((left + width - 1) // BLOCK_SIZE)
    y_start = int(top // BLOCK_SIZE) 
    y_end = int((top + height - 1) // BLOCK_SIZE)
    
    for tile_x in range(x_start, x_end + 1):
        for tile_y in range(y_start, y_end + 1):
            if world.is_solid(tile_x, tile_y):
                return True
    return False

def move_player(world, player, dt):
    # Test movement before committing
    new_x = player.x + player.velocity_x * dt
    if not check_block_collision(world, new_x, player.y, player.width, player.height):
        player.x = new_x  # Safe to move horizontally
    
    new_y = player.y + player.velocity_y * dt  
    if not check_block_collision(world, player.x, new_y, player.width, player.height):
        player.y = new_y  # Safe to move vertically
```

## World Generation Pitfalls

### 7. Non-Deterministic Generation
**❌ MAJOR PROBLEM**:
```python
# Using global random state
def generate_block(x, y):
    if random.random() < 0.1:  # Different result each time!
        return special_block
    return normal_block

# Time-based seeds
def create_world():
    random.seed(time.time())  # Different world every time
    return generate_terrain()
```

**✅ DETERMINISTIC APPROACH**:
```python
# Coordinate-based seeding
def generate_block(x, y, world_seed=12345):
    # Same input always gives same output
    rng = random.Random(world_seed + x * 92821 + y * 47837)
    if rng.random() < 0.1:
        return special_block
    return normal_block

# Save/load the world seed
class World:
    def __init__(self, seed=None):
        self.seed = seed if seed is not None else random.randint(0, 2**32-1)
    
    def save_state(self):
        return {"seed": self.seed, "blocks": self.modified_blocks}
```

### 8. Infinite World Memory Issues
**❌ MEMORY EXPLOSION**:
```python
class InfiniteWorld:
    def __init__(self):
        self.blocks = {}  # Stores EVERY block ever accessed
    
    def get_block(self, x, y):
        if (x, y) not in self.blocks:
            self.blocks[(x, y)] = self.generate_block(x, y)  # Never cleaned up!
        return self.blocks[(x, y)]
```

**✅ MEMORY CONSCIOUS**:
```python
class InfiniteWorld:
    def __init__(self):
        self.modified_blocks = {}  # Only store player changes
        self.loaded_chunks = {}
        self.max_loaded_chunks = 100
    
    def get_block(self, x, y):
        # Check for player modifications first
        if (x, y) in self.modified_blocks:
            return self.modified_blocks[(x, y)]
        
        # Generate on-demand (don't store unless modified)
        return self.generate_block(x, y)
    
    def set_block(self, x, y, block):
        # Only store modifications
        self.modified_blocks[(x, y)] = block
    
    def cleanup_distant_chunks(self, player_x, player_y):
        # Unload chunks far from player
        player_chunk = (player_x // 16, player_y // 16)
        for chunk_pos in list(self.loaded_chunks.keys()):
            distance = abs(chunk_pos[0] - player_chunk[0]) + abs(chunk_pos[1] - player_chunk[1])
            if distance > 10:  # Too far from player
                del self.loaded_chunks[chunk_pos]
```

## Input Handling Gotchas

### 9. Input Event vs State Confusion
**❌ COMMON MISTAKE**:
```python
# Using events for continuous actions
for event in pygame.event.get():
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_a:
            player.move_left()  # Only triggers once per press!

# Using state for discrete actions  
keys = pygame.key.get_pressed()
if keys[pygame.K_SPACE]:
    player.jump()  # Jumps every frame while held!
```

**✅ CORRECT APPROACH**:
```python
# Events for discrete actions (once per press)
for event in pygame.event.get():
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
            player.jump()  # Once per keypress
        elif event.key == pygame.K_e:
            inventory.toggle()  # Once per keypress

# State for continuous actions
keys = pygame.key.get_pressed()
input_state = InputState(
    left=keys[pygame.K_a],
    right=keys[pygame.K_d],  # Held down = continuous movement
    jump=False,  # Jump handled by events above
    crouch=keys[pygame.K_LSHIFT]
)
update_player_physics(player, input_state, dt)
```

### 10. Frame Rate Dependent Movement
**❌ INCONSISTENT MOVEMENT**:
```python
def update_player(player):
    if keys[pygame.K_a]:
        player.x -= 5  # 5 pixels per frame - speed depends on framerate!
    
    # Apply gravity
    player.velocity_y += 0.5  # Gravity depends on framerate too!
```

**✅ FRAME RATE INDEPENDENT**:
```python
def update_player(player, dt):
    speed = 200  # pixels per second
    if keys[pygame.K_a]:
        player.x -= speed * dt  # Same speed regardless of framerate
    
    # Apply gravity
    player.velocity_y += GRAVITY * dt  # Consistent physics
    
# In main loop
clock = pygame.time.Clock()
while running:
    dt = clock.tick(60) / 1000.0  # Delta time in seconds
    update_player(player, dt)
```

## Testing Pitfalls

### 11. Testing Pygame-Dependent Code
**❌ HARD TO TEST**:
```python
def test_player_movement():
    pygame.init()  # Requires pygame initialization
    screen = pygame.display.set_mode((800, 600))
    # Complex setup just to test movement logic
    
def update_player_and_render(screen, player, dt):
    # Logic mixed with rendering - can't test logic alone
    player.x += player.velocity * dt
    pygame.draw.rect(screen, player.color, player.rect)
```

**✅ TESTABLE DESIGN**:
```python
# Separate logic from rendering
def update_player_physics(player, inputs, dt):
    # Pure function - easy to test
    player.velocity[0] = inputs.left * -SPEED + inputs.right * SPEED
    player.position[0] += player.velocity[0] * dt

def test_player_movement():
    # No pygame required
    player = PlayerState(position=[0, 0], velocity=[0, 0], width=10, height=20)
    inputs = InputState(left=True, right=False)
    
    update_player_physics(player, inputs, 1/60)
    
    assert player.position[0] < 0  # Moved left
    assert player.velocity[0] == -SPEED
```

### 12. Forgetting Edge Cases in Tests
**❌ INCOMPLETE TESTING**:
```python
def test_world_bounds():
    world = WorldGrid(width=10, height=10)
    assert world.get_block(5, 5) is not None  # Only tests valid coordinates
```

**✅ COMPREHENSIVE TESTING**:
```python
def test_world_bounds():
    world = WorldGrid(width=10, height=10)
    
    # Test valid coordinates
    assert world.get_block(5, 5) is not None
    assert world.get_block(0, 0) is not None  # Corner case
    assert world.get_block(9, 9) is not None  # Other corner
    
    # Test invalid coordinates
    with pytest.raises(IndexError):
        world.get_block(-1, 5)  # Negative x
    with pytest.raises(IndexError):
        world.get_block(5, -1)  # Negative y  
    with pytest.raises(IndexError):
        world.get_block(10, 5)  # x too large
    with pytest.raises(IndexError):
        world.get_block(5, 10)  # y too large
```

## Theme System Gotchas

### 13. Inconsistent Color Usage
**❌ BREAKS THEME SYSTEM**:
```python
# Hardcoded colors bypass theme system
button_color = (255, 0, 0)  # Red - doesn't change with themes
background_color = (0, 255, 0)  # Green - doesn't change with themes

def draw_ui(screen):
    pygame.draw.rect(screen, button_color, button_rect)
    pygame.draw.rect(screen, background_color, bg_rect)
```

**✅ THEME INTEGRATED**:
```python
# Extend Theme dataclass for new UI elements
@dataclass(frozen=True)
class Theme:
    # ... existing theme colors ...
    button_color: Tuple[int, int, int]
    button_hover: Tuple[int, int, int]
    ui_background: Tuple[int, int, int]

def create_themes():
    def theme(name: str, base_hue: float) -> Theme:
        # Derive all colors from base_hue
        button_color = _theme_colour(base_hue + 0.1, 0.6, 0.3)
        button_hover = _theme_colour(base_hue + 0.1, 0.7, 0.4)
        ui_background = _theme_colour(base_hue - 0.05, 0.9, 0.1)
        
        return Theme(
            # ... existing fields ...
            button_color=button_color,
            button_hover=button_hover, 
            ui_background=ui_background
        )

def draw_ui(screen, theme):
    pygame.draw.rect(screen, theme.button_color, button_rect)
    pygame.draw.rect(screen, theme.ui_background, bg_rect)
```

## File Organization Anti-Patterns

### 14. Import Circular Dependencies  
**❌ CIRCULAR IMPORTS**:
```python
# game.py
from .world import World
from .inventory import Inventory

# world.py  
from .game import BLOCK_SIZE  # CIRCULAR! game -> world -> game

# inventory.py
from .world import BlockType
from .game import draw_inventory  # CIRCULAR! game -> inventory -> game
```

**✅ CLEAN DEPENDENCIES**:
```python
# Constants in separate module or pass as parameters
# constants.py
BLOCK_SIZE = 24

# world.py
from .constants import BLOCK_SIZE  # No circular dependency

# game.py
from .world import World
from .constants import BLOCK_SIZE

def draw_inventory(screen, inventory, theme):  # Pass theme, don't import
    # Rendering code here
```

### 15. Missing __all__ Exports
**❌ UNCLEAR PUBLIC API**:
```python
# world.py
class WorldGrid: pass
class InfiniteWorld: pass  
def _internal_helper(): pass  # Private but exposed
def build_palette(): pass

# Users don't know what's public vs private
from pymine.world import *  # Imports everything including _internal_helper
```

**✅ EXPLICIT PUBLIC API**:
```python
# world.py
class WorldGrid: pass
class InfiniteWorld: pass
def _internal_helper(): pass
def build_palette(): pass

__all__ = [
    "WorldGrid",
    "InfiniteWorld", 
    "build_palette"
]
# Now users know _internal_helper is private and not part of public API
```

## Summary Checklist

Before implementing any feature:

- [ ] Does this maintain clean layer separation? (No pygame in world.py)
- [ ] Am I mutating state efficiently vs creating new objects?
- [ ] Are coordinate conversions explicit and correct?
- [ ] Is the camera math properly centering and offsetting?
- [ ] Am I caching expensive operations like surface creation?
- [ ] Is collision detection optimized for the area of interest?
- [ ] Is world generation deterministic and memory conscious?
- [ ] Am I using events vs state appropriately for input?
- [ ] Is movement frame-rate independent using delta time?
- [ ] Can I test the logic without pygame dependencies?
- [ ] Are colors derived from the theme system?
- [ ] Do imports follow the dependency hierarchy?
- [ ] Is the public API clearly defined with __all__?

Following these patterns will help you avoid the most common pitfalls when extending PyMine.