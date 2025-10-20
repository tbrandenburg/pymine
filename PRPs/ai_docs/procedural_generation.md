# Procedural Generation Patterns

## Core Noise Concepts

### Frequency vs Amplitude
- **Frequency**: Horizontal size of features (higher frequency = smaller features)
- **Amplitude**: Vertical size of features (higher amplitude = taller mountains)
- **Octaves**: Frequency layers combined together (powers of 2: 1, 2, 4, 8, 16...)

### Colors of Noise
Based on frequency distribution:
- **White Noise**: All frequencies equal (completely random)
- **Pink Noise**: Low frequencies stronger (natural looking terrain)  
- **Red Noise**: Very low frequencies dominant (smooth, rolling hills)
- **Blue Noise**: High frequencies stronger (rough, jagged terrain)

```python
# Generate colored noise by combining frequencies
def pink_noise(x, frequencies=[1, 2, 4, 8, 16]):
    amplitudes = [1/math.sqrt(f) for f in frequencies]  # Pink noise spectrum
    result = 0
    for freq, amp in zip(frequencies, amplitudes):
        phase = random.uniform(0, 2*math.pi)
        result += amp * math.sin(2*math.pi * freq * x + phase)
    return result
```

## 2D World Generation Patterns

### Height Map Generation
```python
def generate_heightmap(width, height, octaves=6, persistence=0.5):
    """Generate 2D heightmap using multiple noise octaves"""
    heightmap = [[0 for _ in range(width)] for _ in range(height)]
    
    max_amplitude = 0
    amplitude = 1.0
    frequency = 1.0
    
    # Calculate normalization factor
    for i in range(octaves):
        max_amplitude += amplitude
        amplitude *= persistence
    
    # Generate each octave
    for y in range(height):
        for x in range(width):
            noise_value = 0
            amplitude = 1.0
            frequency = 1.0
            
            for octave in range(octaves):
                sample_x = x * frequency / width
                sample_y = y * frequency / height
                
                # Use your preferred 2D noise function here
                noise = perlin_2d(sample_x, sample_y) 
                noise_value += noise * amplitude
                
                amplitude *= persistence
                frequency *= 2
            
            heightmap[y][x] = noise_value / max_amplitude
    
    return heightmap
```

### Deterministic Generation
```python
class DeterministicGenerator:
    """Generate content deterministically based on coordinates"""
    
    def __init__(self, seed=12345):
        self.base_seed = seed
    
    def get_biome(self, x, y):
        # Use coordinate-specific seed for consistent results
        rng = random.Random(self.base_seed + x * 92821 + y * 47837)
        
        # Temperature and moisture maps
        temp = self.get_temperature(x, y)
        moisture = self.get_moisture(x, y) 
        
        if temp > 0.7 and moisture < 0.3:
            return "desert"
        elif temp < 0.3:
            return "tundra"  
        elif moisture > 0.7:
            return "swamp"
        else:
            return "grassland"
    
    def should_spawn_tree(self, x, y):
        rng = random.Random(self.base_seed + x * 73856 + y * 19373)
        biome = self.get_biome(x, y)
        
        tree_chance = {
            "desert": 0.01,
            "tundra": 0.1, 
            "swamp": 0.8,
            "grassland": 0.3
        }
        
        return rng.random() < tree_chance.get(biome, 0.1)
```

## PyMine's Generation Approach

### Infinite Column-Based Generation
```python
class InfiniteWorld:
    def _base_block_for(self, x: int, y: int) -> Optional[BlockType]:
        """PyMine's deterministic block placement"""
        
        # Base terrain layers
        if y < self.horizon:
            return None  # Air above horizon
        elif y == self.horizon:
            return self.grass_block  # Surface layer
        elif y < self.horizon + 6:
            return self.ground_block  # Soil layers  
        else:
            return self.stone_block  # Deep stone
    
    def _add_decorations(self, x: int, y: int) -> Optional[BlockType]:
        """Add decorative features deterministically"""
        
        # Floating platforms pattern
        pattern_index = x // 9
        platform_phase = x % 9
        if platform_phase in {0, 1, 2}:  # 3-block platforms
            height_offset = pattern_index % 3
            platform_y = self.horizon - 4 - height_offset * 2
            if y == platform_y:
                return self._palette_choice(pattern_index)
        
        # Crystal outcrops
        rng = random.Random((x + 3000) * 92821)  # Unique per x-coordinate
        if rng.random() < 0.1:  # 10% chance
            if y == self.horizon - 1:  # On surface
                return self._palette_choice(x)
```

### Biome System Architecture
```python
class BiomeManager:
    """Manage different biome types and their properties"""
    
    def __init__(self, world_seed=0):
        self.seed = world_seed
        self.biomes = {
            "plains": BiomeConfig(
                surface_block="grass",
                sub_blocks=["dirt", "stone"],
                tree_chance=0.1,
                ore_veins={"iron": 0.05, "coal": 0.08}
            ),
            "desert": BiomeConfig(
                surface_block="sand", 
                sub_blocks=["sand", "sandstone", "stone"],
                tree_chance=0.001,
                ore_veins={"gold": 0.02}
            )
        }
    
    def get_biome_at(self, x: int, y: int) -> str:
        """Determine biome using multiple noise layers"""
        
        # Temperature noise (large scale)
        temp_noise = self.fractal_noise(x/200.0, y/200.0, octaves=3)
        
        # Rainfall noise (different frequency)
        rain_noise = self.fractal_noise(x/150.0, y/150.0, octaves=4, seed_offset=1000)
        
        # Elevation influence
        elevation = self.get_elevation(x, y)
        
        if temp_noise > 0.4 and rain_noise < -0.2:
            return "desert"
        elif elevation > 0.6:
            return "mountains"  
        else:
            return "plains"
```

## Cave Generation Techniques

### 3D Density-Based Caves
```python
def generate_caves_3d(world, cave_threshold=0.4):
    """Generate caves using 3D noise density"""
    
    for x in range(world.width):
        for y in range(world.height):
            for z in range(world.depth):
                # 3D noise value
                density = perlin_3d(x * 0.1, y * 0.1, z * 0.1)
                
                # Only carve caves below surface
                if y > world.surface_level:
                    if density > cave_threshold:
                        world.set_block(x, y, z, None)  # Air pocket
```

### 2D Worm-Based Caves  
```python
def generate_cave_worms(world, num_worms=5):
    """Generate caves using random walk 'worms'"""
    
    for _ in range(num_worms):
        # Start below surface
        x = random.randint(0, world.width)
        y = random.randint(world.surface_level + 10, world.height - 10)
        
        length = random.randint(50, 200)
        radius = random.randint(1, 3)
        
        # Direction bias (slightly downward)
        dx, dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        
        for step in range(length):
            # Carve circular area
            for r in range(radius):
                for angle in range(0, 360, 45):
                    ox = int(x + r * math.cos(math.radians(angle)))
                    oy = int(y + r * math.sin(math.radians(angle)))
                    
                    if world.in_bounds(ox, oy):
                        world.set_block(ox, oy, None)
            
            # Random walk with momentum
            if random.random() < 0.1:  # 10% chance to change direction
                dx, dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            
            x += dx
            y += dy
            
            # Keep in bounds
            x = max(1, min(world.width - 1, x))
            y = max(world.surface_level + 5, min(world.height - 1, y))
```

## Structure Generation

### Template-Based Structures
```python
class StructureTemplate:
    def __init__(self, pattern, blocks):
        self.pattern = pattern  # 2D array of symbols
        self.blocks = blocks    # symbol -> BlockType mapping
        self.width = len(pattern[0])
        self.height = len(pattern)
    
    def can_place(self, world, x, y):
        """Check if structure can be placed at location"""
        for dy in range(self.height):
            for dx in range(self.width):
                if not world.in_bounds(x + dx, y + dy):
                    return False
                    
                # Check for conflicts with existing blocks
                symbol = self.pattern[dy][dx]
                if symbol != ' ' and world.get_block(x + dx, y + dy) is not None:
                    return False
        return True
    
    def place(self, world, x, y):
        """Place structure at location"""
        for dy in range(self.height):
            for dx in range(self.width):
                symbol = self.pattern[dy][dx]
                if symbol in self.blocks:
                    world.set_block(x + dx, y + dy, self.blocks[symbol])

# Define a simple house template
HOUSE_TEMPLATE = StructureTemplate(
    pattern=[
        "wwwww",
        "w   w", 
        "w   w",
        "wwdww"
    ],
    blocks={
        'w': BlockType("Wood", (139, 69, 19)),
        'd': BlockType("Door", (160, 82, 45))
    }
)
```

### Recursive Structure Generation
```python
def generate_dungeon_rooms(world, start_x, start_y, depth=0, max_depth=3):
    """Recursively generate connected dungeon rooms"""
    
    if depth >= max_depth:
        return
    
    # Room size
    room_w = random.randint(5, 12)
    room_h = random.randint(5, 8)
    
    # Carve out room
    for x in range(start_x, start_x + room_w):
        for y in range(start_y, start_y + room_h):
            if world.in_bounds(x, y):
                world.set_block(x, y, None)  # Air
    
    # Generate connected rooms
    num_connections = random.randint(1, 3)
    for _ in range(num_connections):
        # Pick random wall for connection
        side = random.choice(['north', 'south', 'east', 'west'])
        
        if side == 'east':
            new_x = start_x + room_w + 1
            new_y = start_y + random.randint(1, room_h - 2)
            # Carve tunnel
            for tx in range(start_x + room_w, new_x):
                world.set_block(tx, new_y, None)
        # ... similar for other sides
        
        generate_dungeon_rooms(world, new_x, new_y, depth + 1, max_depth)
```

## Performance Optimization

### Chunk-Based Generation
```python
class ChunkedWorld:
    CHUNK_SIZE = 16
    
    def __init__(self):
        self.chunks = {}  # (chunk_x, chunk_y) -> Chunk
        self.loaded_chunks = set()
    
    def get_chunk_coords(self, x, y):
        return x // self.CHUNK_SIZE, y // self.CHUNK_SIZE
    
    def ensure_chunk_loaded(self, chunk_x, chunk_y):
        chunk_key = (chunk_x, chunk_y)
        
        if chunk_key not in self.chunks:
            # Generate chunk on-demand
            chunk = self.generate_chunk(chunk_x, chunk_y)
            self.chunks[chunk_key] = chunk
            self.loaded_chunks.add(chunk_key)
    
    def get_block(self, x, y):
        chunk_x, chunk_y = self.get_chunk_coords(x, y)
        self.ensure_chunk_loaded(chunk_x, chunk_y)
        
        chunk = self.chunks[(chunk_x, chunk_y)]
        local_x = x % self.CHUNK_SIZE
        local_y = y % self.CHUNK_SIZE
        return chunk.get_block(local_x, local_y)
```

### Caching Expensive Calculations
```python
class CachedNoiseGenerator:
    def __init__(self):
        self.cache = {}
        self.cache_size_limit = 10000
    
    def get_noise(self, x, y, frequency=1.0):
        key = (x, y, frequency)
        
        if key in self.cache:
            return self.cache[key]
        
        # Generate expensive noise
        value = self.calculate_fractal_noise(x, y, frequency)
        
        # Cache management
        if len(self.cache) >= self.cache_size_limit:
            # Remove oldest entries (simple FIFO)
            old_key = next(iter(self.cache))
            del self.cache[old_key]
        
        self.cache[key] = value
        return value
```

## Common Pitfalls

### 1. Non-Deterministic Generation
```python
# BAD: Different results each run
def generate_block(x, y):
    if random.random() < 0.1:  # Uses global random state
        return special_block

# GOOD: Deterministic based on coordinates  
def generate_block(x, y):
    rng = random.Random(x * 92821 + y * 47837)  # Coordinate-specific seed
    if rng.random() < 0.1:
        return special_block
```

### 2. Unnatural Patterns
```python
# BAD: Obvious mathematical patterns
height = math.sin(x * 0.1) * 10

# GOOD: Multiple noise layers with natural variation
base_height = perlin_noise(x * 0.01) * 50
detail = perlin_noise(x * 0.1) * 5  
height = base_height + detail
```

### 3. Performance Issues
```python
# BAD: Generating entire world at once
world = generate_full_world(10000, 10000)  # Memory explosion

# GOOD: On-demand generation
def get_block(x, y):
    if not self.is_generated(x, y):
        self.generate_local_area(x, y)
    return self.blocks.get((x, y))
```

## References

- [Red Blob Games - Noise Functions](https://www.redblobgames.com/articles/noise/introduction.html)
- [Minecraft Wiki - World Generation](https://minecraft.fandom.com/wiki/World_generation)
- [Perlin Noise Tutorial](http://eastfarthing.com/blog/2015-04-21-noise/)
- [Cave Generation Algorithms](https://www.reddit.com/r/proceduralgeneration/comments/12ybj4x/algorithm_suggestions_for_a_2d_cave_generation/)
- [Procedural World Generation Tutorial](https://www.gamedeveloper.com/programming/a-real-time-procedural-universe-part-one-generating-planetary-bodies)