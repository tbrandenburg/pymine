# Pygame Patterns & Optimizations

## Critical Performance Patterns

### Surface Conversion
**CRITICAL**: Always convert surfaces after loading for optimal blitting performance.
```python
# After loading any image
image = pygame.image.load("sprite.png")
image = image.convert()  # For opaque images
image = image.convert_alpha()  # For images with transparency
```

### Dirty Rectangle Updates
Use dirty rectangles to update only changed screen areas:
```python
# Use sprite.RenderUpdates group for automatic dirty rect tracking
all_sprites = pygame.sprite.RenderUpdates()
dirty_rects = all_sprites.draw(screen)
pygame.display.update(dirty_rects)  # Only update changed areas
```

### Block-Based Game Optimization
For infinite world games like PyMine:
```python
# Pre-calculate visible range
start_column = int(math.floor(camera_x / BLOCK_SIZE))
column_offset = -(camera_x - start_column * BLOCK_SIZE)
columns_to_draw = WORLD_WIDTH + 3

# Only render visible blocks
for index in range(columns_to_draw):
    screen_x = column_offset + (index - 1) * BLOCK_SIZE
    if screen_x <= -BLOCK_SIZE or screen_x >= screen_width:
        continue  # Skip off-screen blocks
```

## Memory Management

### Pre-load Assets
Load all assets at startup, not during gameplay:
```python
class AssetManager:
    def __init__(self):
        self.textures = {}
    
    def load_texture(self, name, path):
        texture = pygame.image.load(path).convert_alpha()
        self.textures[name] = texture
        return texture
```

### Avoid Frequent Surface Creation
```python
# BAD: Creating surfaces in game loop
def render_text(text):
    return font.render(text, True, color)  # Creates new surface each call

# GOOD: Cache rendered text surfaces
class TextCache:
    def __init__(self):
        self.cache = {}
    
    def get_text(self, text, font, color):
        key = (text, font, color)
        if key not in self.cache:
            self.cache[key] = font.render(text, True, color)
        return self.cache[key]
```

## Collision Detection

### Efficient Block-Based Collision
```python
def area_intersects_solid(world, left, top, width, height, block_size):
    x_start = int(math.floor(left / block_size))
    x_end = int((left + width - 1) // block_size)
    y_start = int(math.floor(top / block_size))
    y_end = int((top + height - 1) // block_size)
    
    for tile_x in range(x_start, x_end + 1):
        for tile_y in range(y_start, y_end + 1):
            if world.is_solid(tile_x, tile_y):
                return True
    return False
```

### Spatial Partitioning
For entities/mobs:
```python
class SpatialGrid:
    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.grid = defaultdict(list)
    
    def add(self, entity, x, y):
        cell = (int(x // self.cell_size), int(y // self.cell_size))
        self.grid[cell].append(entity)
    
    def get_nearby(self, x, y):
        cell = (int(x // self.cell_size), int(y // self.cell_size))
        nearby = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nearby.extend(self.grid.get((cell[0] + dx, cell[1] + dy), []))
        return nearby
```

## Camera & Viewport

### Smooth Camera Following
```python
def update_camera(camera, target, dt, follow_speed=5.0):
    target_x = target.x - SCREEN_WIDTH // 2
    target_y = target.y - SCREEN_HEIGHT // 2
    
    # Smooth interpolation
    camera.x += (target_x - camera.x) * follow_speed * dt
    camera.y += (target_y - camera.y) * follow_speed * dt
    
    # Clamp to world bounds
    camera.x = max(min_x, min(camera.x, max_x))
    camera.y = max(min_y, min(camera.y, max_y))
```

## Event Handling

### Efficient Input Management
```python
class InputManager:
    def __init__(self):
        self.keys = {}
        self.mouse_pos = (0, 0)
        self.mouse_buttons = {}
    
    def update(self):
        self.keys = pygame.key.get_pressed()
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_buttons = pygame.mouse.get_pressed()
    
    def is_key_held(self, key):
        return self.keys.get(key, False)
    
    def is_mouse_held(self, button):
        return self.mouse_buttons[button] if len(self.mouse_buttons) > button else False
```

### Frame-Independent Movement
```python
def update_entity(entity, dt):
    # Use delta time for consistent movement across different frame rates
    entity.x += entity.velocity_x * dt
    entity.y += entity.velocity_y * dt
    
    # Apply gravity
    entity.velocity_y += GRAVITY * dt
    entity.velocity_y = min(entity.velocity_y, MAX_FALL_SPEED)
```

## Common Gotchas

### Coordinate System
- Pygame uses (0,0) at top-left
- Y increases downward (opposite of math convention)
- Always use int() for pixel positions to avoid blurring

### Color Format
```python
# RGB tuples (0-255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# pygame.Color objects for more functionality
color = pygame.Color(255, 100, 50)
color.hsla = (180, 50, 75, 100)  # Can set HSL directly
```

### Surface Alpha
```python
# For per-pixel alpha (transparency)
surface = surface.convert_alpha()

# For surface-wide alpha
surface = surface.convert()
surface.set_alpha(128)  # 0-255, 0=transparent, 255=opaque
```

### Clock and Frame Rate
```python
clock = pygame.time.Clock()
while running:
    dt = clock.tick(60) / 1000.0  # 60 FPS, dt in seconds
    # Always use dt for time-based calculations
```

## Advanced Patterns

### State Machines
```python
class GameState:
    def enter(self): pass
    def exit(self): pass
    def update(self, dt): pass
    def render(self, screen): pass

class StateMachine:
    def __init__(self):
        self.current_state = None
    
    def change_state(self, new_state):
        if self.current_state:
            self.current_state.exit()
        self.current_state = new_state
        if new_state:
            new_state.enter()
```

### Object Pooling
```python
class ObjectPool:
    def __init__(self, create_func, max_size=100):
        self.create_func = create_func
        self.available = []
        self.max_size = max_size
    
    def get(self):
        if self.available:
            return self.available.pop()
        return self.create_func()
    
    def release(self, obj):
        if len(self.available) < self.max_size:
            obj.reset()  # Object should have reset method
            self.available.append(obj)
```

## Testing Patterns

### Mock Pygame for Unit Tests
```python
class MockSurface:
    def __init__(self, size):
        self.size = size
    def get_width(self): return self.size[0]
    def get_height(self): return self.size[1]
    def blit(self, *args): pass

# In tests, replace pygame surfaces with mocks
def test_rendering():
    screen = MockSurface((800, 600))
    render_function(screen)
    assert True  # Test rendering logic without pygame
```

## References

- [Pygame Optimization Wiki](http://www.pygame.org/wiki/Optimisations)
- [10 Pygame Performance Tips](https://dhirajkumarblog.medium.com/10-must-know-pygame-hacks-every-game-developer-should-master-342dd42b3ec7)
- [Dirty Rectangle Updates](https://www.pygame.org/docs/ref/display.html#pygame.display.update)
- [Surface Conversion](https://www.pygame.org/docs/ref/surface.html#pygame.Surface.convert)