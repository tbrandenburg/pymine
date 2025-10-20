## Goal

**Feature Goal**: Implement a robust save/load system that persists PyMine world state and player progress, enabling players to continue their game sessions across application restarts.

**Deliverable**: Complete world persistence system with JSON-based save files, player state serialization, and automatic world generation restoration.

**Success Definition**: Players can save their current world state (including placed/removed blocks, player position, inventory) and load it back perfectly, maintaining infinite world generation consistency and theme preferences.

## User Persona

**Target User**: PyMine players who want to build persistent worlds and continue their creative projects across multiple gaming sessions.

**Use Case**: Player spends time exploring the infinite world, placing blocks to create structures, collecting different block types in inventory, and wants to return to the same world state later.

**User Journey**: 
1. Player builds structures and explores the world
2. Player presses S key or selects "Save Game" to save progress
3. Player exits PyMine
4. Player later restarts PyMine and presses L key or selects "Load Game"
5. Player continues exactly where they left off with all progress intact

**Pain Points Addressed**: 
- Losing creative work when game closes
- Unable to build complex structures over multiple sessions
- No way to preserve world exploration progress

## Why

- **Essential Foundation**: Save/load is prerequisite for meaningful gameplay - without it, PyMine is just a temporary sandbox
- **Player Retention**: Players invest more time when progress persists, leading to larger, more complex creations
- **Future Feature Enabler**: Many advanced features (multiplayer, achievements, advanced world generation) depend on world persistence
- **Minimal UI Impact**: Can be implemented with simple keyboard shortcuts initially, allowing focus on core persistence logic

## What

### User-Visible Behavior
- Press **S** key to save current game state to `saves/world_TIMESTAMP.json`
- Press **L** key to load most recent save file (or show file picker for multiple saves)
- Game displays "Game Saved" / "Game Loaded" messages briefly
- All placed/removed blocks persist exactly as left
- Player position, velocity, and flight mode restore correctly
- Inventory contents and selected slot maintain state
- Current theme preference preserved
- Infinite world continues generating consistently with same seed

### Technical Requirements
- Save files are human-readable JSON format for debugging and potential modding
- Save/load operations complete in <100ms for responsive feel
- Corrupted save files handled gracefully with error messages
- Multiple save slots supported (filename includes timestamp)
- Save file size optimized (only store player modifications, not generated world)

### Success Criteria
- [ ] Can save and load world state with 100% fidelity
- [ ] Save files are <1MB for typical gameplay sessions
- [ ] Load operation restores infinite world generation deterministically
- [ ] Player state (position, velocity, flight mode, inventory) fully preserved
- [ ] Save/load operations provide clear user feedback
- [ ] System handles file I/O errors gracefully

## All Needed Context

### Context Completeness Check
_If someone knew nothing about PyMine's codebase, would they have everything needed to implement save/load functionality successfully?_

### Documentation & References

```yaml
# MUST READ - Include these in your context window
- docfile: PRPs/ai_docs/pymine_architecture.md
  why: Complete understanding of PyMine's 3-layer architecture and data flow patterns
  critical: Must maintain pygame independence in world.py, understand dataclass state management

- docfile: PRPs/ai_docs/common_gotchas.md
  why: Avoid state management and coordinate system pitfalls during serialization
  section: State Management Confusion, Coordinate System Pitfalls
  
- file: src/pymine/world.py
  why: Core data structures that need serialization (PlayerState, InfiniteWorld, Inventory)
  pattern: Dataclass definitions, InfiniteWorld._columns storage, deterministic generation
  gotcha: InfiniteWorld only stores modified blocks in practice, not entire world

- file: src/pymine/game.py 
  why: Game loop integration points and state access patterns
  pattern: Theme system integration, main game state variables
  gotcha: Theme selection and camera state need persistence

- file: tests/test_world.py
  why: Testing patterns for world state validation and player state management
  pattern: make_player() factory functions, state assertion patterns

- url: https://docs.python.org/3/library/json.html
  why: JSON serialization for human-readable save files
  critical: Custom encoders needed for PyMine's dataclass types and tuples

- url: https://docs.python.org/3/library/pathlib.html#pathlib.Path
  why: Cross-platform file path handling for save directory management
  critical: Windows vs Unix path compatibility for save file locations
```

### Current Codebase Tree
```bash
├── src/
│   └── pymine/
│       ├── __init__.py
│       ├── game.py          # Game loop, themes, rendering
│       ├── physics.py       # InputState, player physics  
│       └── world.py         # PlayerState, InfiniteWorld, Inventory
├── tests/
│   ├── test_physics.py
│   └── test_world.py
├── saves/                   # Will be created
└── pyproject.toml
```

### Desired Codebase Tree with Files Added
```bash
├── src/
│   └── pymine/
│       ├── __init__.py
│       ├── game.py          # Add save/load key handling
│       ├── physics.py       # No changes needed
│       ├── world.py         # No changes needed  
│       └── persistence.py   # NEW: Save/load logic
├── tests/
│   ├── test_physics.py
│   ├── test_world.py
│   └── test_persistence.py  # NEW: Save/load tests
├── saves/                   # NEW: Save file directory
│   └── .gitkeep            # NEW: Ensure directory exists
└── pyproject.toml
```

### Known Gotchas & Library Quirks

```python
# JSON Limitations with PyMine Types
# CRITICAL: JSON can't serialize tuples, dataclasses, or custom types directly
tuple_color = (255, 128, 0)  # Becomes [255, 128, 0] in JSON
player_state = PlayerState(...)  # Needs custom encoder

# InfiniteWorld Memory Management  
# CRITICAL: InfiniteWorld stores only modified blocks, not entire world
# Save system must distinguish between generated vs modified blocks
world._columns  # Contains ALL accessed columns (generated + modified)
world._modified_blocks  # Should only contain player changes

# Coordinate Precision
# CRITICAL: Player position uses floats but must survive JSON roundtrip
player.position = [123.456789, 67.891234]  # May lose precision

# Theme System Integration
# CRITICAL: Theme index must be saved separately from base_hue
current_theme_index = 3  # Needed to restore theme selection
current_theme.base_hue = 0.67  # Needed for palette regeneration
```

## Implementation Blueprint

### Data Models and Structure

Create the persistence layer with comprehensive save state representation:

```python
# Core save state structure
@dataclass
class SaveState:
    """Complete game state for persistence"""
    version: str  # Save format version for future compatibility
    timestamp: float  # When save was created
    world_seed: int  # For deterministic world generation
    player: dict  # Serialized PlayerState
    inventory: dict  # Serialized Inventory
    modified_blocks: dict  # Only player-placed/removed blocks
    theme_index: int  # Current theme selection
    camera_position: tuple  # Camera x, y for seamless restoration
    
# Custom JSON encoder for PyMine types
class PyMineEncoder(json.JSONEncoder):
    """Handle PyMine-specific types in JSON serialization"""
    
# Save file format validation
class SaveFormatValidator:
    """Validate save file structure and migrate old formats"""
```

### Implementation Tasks (ordered by dependencies)

```yaml
Task 1: CREATE src/pymine/persistence.py
  - IMPLEMENT: SaveState dataclass, PyMineEncoder, SaveFormatValidator classes
  - IMPLEMENT: save_game(), load_game(), list_saves() functions
  - FOLLOW pattern: src/pymine/world.py (dataclass usage, type hints, __all__ exports)
  - NAMING: snake_case functions, CamelCase classes, descriptive method names
  - PLACEMENT: New module in src/pymine/ following existing structure
  - DEPENDENCIES: None (pure Python stdlib)

Task 2: CREATE saves directory structure
  - CREATE: saves/ directory in project root
  - CREATE: saves/.gitkeep file to ensure directory exists in version control
  - IMPLEMENT: Directory creation logic in persistence.py if missing
  - FOLLOW pattern: Existing project structure (tests/, src/ directories)
  - NAMING: saves/ directory for clarity, timestamp-based filenames
  - PLACEMENT: Project root level alongside src/, tests/

Task 3: EXTEND src/pymine/world.py with serialization support
  - IMPLEMENT: to_dict() and from_dict() methods for PlayerState, Inventory
  - IMPLEMENT: get_modified_blocks() method for InfiniteWorld
  - FOLLOW pattern: Existing world.py dataclass methods and factory functions
  - NAMING: to_dict/from_dict for consistency with JSON serialization patterns
  - DEPENDENCIES: Task 1 (SaveState structure defined)
  - PRESERVE: Existing functionality, no breaking changes to public API

Task 4: MODIFY src/pymine/game.py for save/load integration
  - IMPLEMENT: Save key handling (S key press) in pygame event loop
  - IMPLEMENT: Load key handling (L key press) in pygame event loop  
  - IMPLEMENT: restore_game_state() function to apply loaded data
  - IMPLEMENT: Status message display for save/load feedback
  - FOLLOW pattern: Existing event handling in main game loop
  - NAMING: save_current_game(), load_latest_game() function names
  - DEPENDENCIES: Task 1, 3 (persistence module and serialization support)

Task 5: CREATE tests/test_persistence.py
  - IMPLEMENT: Test save/load roundtrip with all data types
  - IMPLEMENT: Test save file format validation and error handling
  - IMPLEMENT: Test multiple save slots and file management
  - FOLLOW pattern: tests/test_world.py (helper functions, pytest fixtures)
  - NAMING: test_save_load_roundtrip(), test_invalid_save_file() patterns
  - COVERAGE: All public functions with success and error cases
  - DEPENDENCIES: Task 1, 3 (implementation complete)

Task 6: EXTEND existing tests with persistence verification
  - MODIFY: tests/test_world.py to include serialization method tests
  - ADD: Helper functions for creating test save states
  - IMPLEMENT: Test deterministic world generation with saved seeds
  - FOLLOW pattern: Existing test helper patterns and assertion styles
  - COVERAGE: Ensure dataclass serialization methods work correctly
  - DEPENDENCIES: Task 3, 5 (serialization methods and persistence tests)
```

### Implementation Patterns & Key Details

```python
# Save State Serialization Pattern
@dataclass 
class SaveState:
    version: str = "1.0"
    timestamp: float = 0.0
    world_seed: int = 0
    player: dict = field(default_factory=dict)
    inventory: dict = field(default_factory=dict)
    modified_blocks: dict = field(default_factory=dict)
    theme_index: int = 0
    camera_position: tuple = (0.0, 0.0)
    
    def to_json(self) -> str:
        """Serialize to JSON string with custom encoder"""
        return json.dumps(asdict(self), cls=PyMineEncoder, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'SaveState':
        """Deserialize from JSON string with validation"""
        # PATTERN: Validate before constructing, handle errors gracefully
        # GOTCHA: Must restore tuples from lists, validate all required fields

# World State Extraction Pattern  
class InfiniteWorld:
    def get_modified_blocks(self) -> dict:
        """Return only player-modified blocks for save file"""
        # PATTERN: Only serialize changes, not generated content
        # CRITICAL: Generated blocks can be recreated from seed
        modified = {}
        for (x, y), block in self.player_modifications.items():
            modified[f"{x},{y}"] = block.name if block else None
        return modified
    
    def apply_modified_blocks(self, modified_blocks: dict):
        """Restore player modifications from save file"""
        # PATTERN: Apply changes after world generation initialized
        # GOTCHA: Must convert string keys back to int tuples

# Error Handling Pattern
def load_game(save_path: str) -> SaveState:
    """Load game state with comprehensive error handling"""
    try:
        with open(save_path, 'r') as f:
            data = json.load(f)
        
        # PATTERN: Validate save format version first
        if data.get('version') != CURRENT_VERSION:
            raise SaveFormatError(f"Unsupported save format: {data.get('version')}")
        
        return SaveState.from_dict(data)
        
    except FileNotFoundError:
        raise SaveError(f"Save file not found: {save_path}")
    except json.JSONDecodeError as e:
        raise SaveError(f"Corrupted save file: {e}")
    except KeyError as e:
        raise SaveError(f"Invalid save file format: missing {e}")
```

### Integration Points

```yaml
GAME_LOOP:
  - event handling: "Add S/L key detection in pygame.event.get() loop"
  - state access: "Capture current player, inventory, world, theme states"
  - feedback: "Display save/load status messages in HUD area"

WORLD_GENERATION:  
  - seed preservation: "Store and restore world seed for deterministic generation"
  - modification tracking: "Distinguish generated vs player-placed blocks"
  - infinite expansion: "Ensure saved world continues expanding correctly"

PLAYER_STATE:
  - position precision: "Maintain exact player coordinates through JSON"
  - physics state: "Preserve velocity, on_ground, flight_mode, crouching"
  - inventory sync: "Keep selected slot and block types consistent"

THEME_SYSTEM:
  - index tracking: "Save current theme selection index"
  - palette regeneration: "Restore theme and regenerate block palettes"
  - visual consistency: "Ensure UI colors match restored theme"
```

## Validation Loop

### Level 1: Syntax & Style (Immediate Feedback)

```bash
# Run after each file creation - fix before proceeding
uv run ruff check src/pymine/persistence.py --fix
uv run mypy src/pymine/persistence.py
uv run ruff format src/pymine/persistence.py

# Project-wide validation  
uv run ruff check src/ --fix
uv run mypy src/
uv run ruff format src/

# Expected: Zero errors. If errors exist, READ output and fix before proceeding.
```

### Level 2: Unit Tests (Component Validation)

```bash
# Test persistence module as it's created
uv run pytest tests/test_persistence.py -v

# Test integration with existing world module
uv run pytest tests/test_world.py::test_player_serialization -v
uv run pytest tests/test_world.py::test_inventory_serialization -v

# Full persistence-related test suite
uv run pytest tests/ -k "persistence or serializ" -v

# Coverage validation
uv run pytest tests/test_persistence.py --cov=src/pymine/persistence --cov-report=term-missing

# Expected: All tests pass. Coverage >90% for new persistence code.
```

### Level 3: Integration Testing (System Validation)

```bash
# Test complete save/load workflow
uv run python -c "
import json
from src.pymine.persistence import save_game, load_game
from src.pymine.world import PlayerState, Inventory, build_palette

# Create test game state
player = PlayerState(position=[100.5, 200.75], velocity=[1.2, -0.5], width=14.4, height=21.6, flight_mode=True)
inventory = Inventory(slots=list(build_palette(0.3)))
inventory.select(2)

# Test save
save_path = save_game(player, inventory, {}, 12345, 1, (50.0, 75.0))
print(f'Saved to: {save_path}')

# Test load  
loaded_state = load_game(save_path)
print(f'Loaded state version: {loaded_state.version}')
print(f'Player position: {loaded_state.player[\"position\"]}')
print(f'Theme index: {loaded_state.theme_index}')
"

# Test save file format
ls -la saves/
head -20 saves/world_*.json  # Inspect JSON structure

# Test error handling
uv run python -c "
from src.pymine.persistence import load_game, SaveError
try:
    load_game('nonexistent.json')
except SaveError as e:
    print(f'Handled error correctly: {e}')
"

# Expected: Save files created, JSON format readable, errors handled gracefully
```

### Level 4: Creative & Domain-Specific Validation

```bash
# Full game integration test
echo "Testing full save/load integration..."
uv run python -c "
# Simulate full game session with save/load
import sys
sys.path.append('src')

from pymine.game import main
# Note: This would require headless testing setup for full validation
print('Full integration test requires manual verification in game')
"

# Save file format validation
python -c "
import json
save_files = list(Path('saves').glob('*.json'))
for save_file in save_files:
    try:
        with open(save_file) as f:
            data = json.load(f)
        required_fields = ['version', 'world_seed', 'player', 'inventory']
        missing = [f for f in required_fields if f not in data]
        if missing:
            print(f'ERROR: {save_file} missing fields: {missing}')
        else:
            print(f'OK: {save_file} format valid')
    except Exception as e:
        print(f'ERROR: {save_file} corrupted: {e}')
"

# Performance validation
uv run python -c "
import time
from src.pymine.persistence import save_game, load_game
from src.pymine.world import *

# Create realistic game state
player = PlayerState(position=[500.0, 300.0], velocity=[0.0, 0.0], width=14.4, height=21.6)
inventory = Inventory(slots=list(build_palette()))
large_modifications = {f'{x},{y}': 'stone' for x in range(100) for y in range(100)}

# Test save performance
start = time.time()
save_path = save_game(player, inventory, large_modifications, 54321, 2, (250.0, 150.0))
save_time = time.time() - start
print(f'Save time: {save_time:.3f}s (should be <0.1s)')

# Test load performance  
start = time.time()
loaded_state = load_game(save_path)
load_time = time.time() - start
print(f'Load time: {load_time:.3f}s (should be <0.1s)')

# Check file size
import os
size_mb = os.path.getsize(save_path) / (1024 * 1024)
print(f'Save file size: {size_mb:.2f}MB (should be <1MB)')
"

# Manual game testing checklist
echo "MANUAL TESTING REQUIRED:"
echo "1. Start PyMine, build some structures"  
echo "2. Press S to save, verify 'Game Saved' message"
echo "3. Continue playing, modify inventory, change theme"
echo "4. Press S again to save updated state"
echo "5. Exit and restart PyMine"
echo "6. Press L to load, verify everything restored perfectly"
echo "7. Check that infinite world generation continues correctly"
echo "8. Verify theme and camera position maintained"

# Expected: All performance targets met, manual testing confirms perfect state restoration
```

## Final Validation Checklist

### Technical Validation
- [ ] All 4 validation levels completed successfully  
- [ ] All tests pass: `uv run pytest tests/ -v`
- [ ] No linting errors: `uv run ruff check src/`
- [ ] No type errors: `uv run mypy src/`
- [ ] No formatting issues: `uv run ruff format src/ --check`

### Feature Validation
- [ ] Save operation completes in <100ms with user feedback
- [ ] Load operation restores game state with 100% fidelity
- [ ] Save files are <1MB and human-readable JSON format
- [ ] Multiple save slots work (timestamp-based filenames)
- [ ] Error cases handled gracefully with clear messages
- [ ] Infinite world generation continues deterministically after load

### Code Quality Validation  
- [ ] Follows PyMine architecture: no pygame imports in world.py
- [ ] Uses existing dataclass patterns consistently
- [ ] File placement matches desired codebase tree structure
- [ ] Maintains clean dependency hierarchy (game -> persistence -> world)
- [ ] Public API clearly defined with __all__ exports

### User Experience Validation
- [ ] S key saves game with visible "Game Saved" confirmation
- [ ] L key loads most recent save with "Game Loaded" confirmation  
- [ ] Player returns to exact position and state after load
- [ ] All placed/removed blocks perfectly preserved
- [ ] Inventory contents and selection maintained
- [ ] Current theme and visual state preserved
- [ ] Camera position restored for seamless experience

---

## Anti-Patterns to Avoid

- ❌ Don't store generated world data - only save player modifications
- ❌ Don't break layer separation - keep persistence logic out of game.py rendering  
- ❌ Don't use pickle or binary formats - JSON is debuggable and portable
- ❌ Don't ignore save/load errors - always provide user feedback
- ❌ Don't lose precision on player coordinates through serialization  
- ❌ Don't forget to handle missing save directory or permission errors
- ❌ Don't create save files in source code directory - use dedicated saves/ folder
- ❌ Don't serialize theme colors directly - save theme index and regenerate
- ❌ Don't assume save files will always be valid - validate format and handle corruption
- ❌ Don't block the game loop during save/load - keep operations fast

**Confidence Score: 9/10** - This PRP provides comprehensive implementation guidance with complete context, specific patterns, and thorough validation. The save/load system is well-architected to integrate cleanly with PyMine's existing structure while providing essential persistence functionality.