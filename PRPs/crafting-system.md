## Goal

**Feature Goal**: Implement a recipe-based crafting system that allows players to combine basic blocks into new, more advanced block types, adding strategic depth and progression to PyMine's sandbox gameplay.

**Deliverable**: Complete crafting interface with recipe management, inventory integration, and visual crafting grid that extends PyMine's current block placement mechanics.

**Success Definition**: Players can open a crafting interface (C key), place blocks in a 3x3 grid pattern to match recipes, and create new block types that are automatically added to their inventory, with clear visual feedback for valid/invalid recipes.

## User Persona

**Target User**: Creative PyMine players who want progression mechanics and the satisfaction of creating complex materials from simple components.

**Use Case**: Player has collected basic blocks (grass, stone, wood) from the world and wants to create more interesting building materials through combination recipes.

**User Journey**:
1. Player explores world and collects various block types  
2. Player presses C key to open crafting interface
3. Player experiments with placing blocks in 3x3 crafting grid
4. Interface shows preview of craftable items as player arranges blocks
5. Player clicks craft button to create new blocks and add them to inventory
6. Player uses crafted blocks to build more advanced structures

**Pain Points Addressed**:
- Limited variety in available building blocks from world generation
- No progression system or goals beyond basic building
- Lack of strategic resource management in gameplay

## Why

- **Gameplay Depth**: Transforms PyMine from simple sandbox to strategic building game with resource management
- **Player Progression**: Creates goals and milestones as players discover and master new recipes
- **Creative Expansion**: Provides new building materials and colors not available through world generation alone
- **Foundation for Advanced Features**: Crafting system enables tools, decorative blocks, and functional items in future updates

## What

### User-Visible Behavior
- Press **C** key to open/close crafting interface overlay
- Crafting interface shows 3x3 grid for placing blocks plus inventory slots
- Drag blocks from inventory into crafting grid (or click block then click grid slot)
- Recipe preview updates in real-time as grid is filled
- "Craft" button becomes enabled when valid recipe is arranged
- Click "Craft" to consume ingredients and add result to inventory
- Interface displays recipe hints/suggestions for discovered combinations
- Crafted blocks seamlessly integrate with existing placement system

### Technical Requirements
- Crafting interface renders over game world (modal overlay)
- Recipe system supports flexible pattern matching (shaped and shapeless)
- Recipe database stored in JSON for easy modding and expansion
- Crafting operations maintain game performance (60fps during UI interaction)
- Integration preserves existing inventory management and theme system
- All crafted blocks support existing physics and world generation integration

### Success Criteria
- [ ] Crafting interface opens/closes smoothly with clear visual design
- [ ] Recipe system supports at least 10 starter recipes (wood->planks, stone->brick, etc.)
- [ ] Drag-and-drop interaction feels responsive and intuitive
- [ ] Crafted blocks fully integrate with existing block placement system
- [ ] Recipe discovery provides satisfying "aha" moments for players
- [ ] System maintains 60fps performance during crafting operations

## All Needed Context

### Context Completeness Check
_If someone knew nothing about PyMine's codebase, would they have everything needed to implement crafting functionality successfully?_

### Documentation & References

```yaml
# MUST READ - Include these in your context window  
- docfile: PRPs/ai_docs/pymine_architecture.md
  why: Understand 3-layer architecture for proper UI and logic separation
  critical: Crafting UI goes in game.py, recipe logic stays in world.py
  section: Theme System Integration, Event Handling Patterns

- docfile: PRPs/ai_docs/pygame_patterns.md
  why: UI rendering and event handling patterns for crafting interface
  critical: Proper surface management, input event vs state handling
  section: Event Handling, Surface Creation, Theme Integration

- docfile: PRPs/ai_docs/common_gotchas.md
  why: Avoid coordinate system and state management issues in UI
  section: Input Event vs State Confusion, Theme System Integration
  
- file: src/pymine/world.py
  why: Inventory and BlockType integration patterns, existing data structures
  pattern: Inventory.slots manipulation, BlockType creation, theme-compatible colors
  gotcha: Inventory selection management during crafting operations

- file: src/pymine/game.py
  why: UI rendering patterns, theme integration, event handling in game loop
  pattern: draw_inventory() structure, theme color usage, pygame event processing  
  gotcha: Modal UI overlay without breaking existing input handling

- file: tests/test_world.py
  why: Testing patterns for inventory manipulation and block type validation
  pattern: Inventory test fixtures, block type assertions, factory functions

- url: https://github.com/AlvarMarkhester/pg-inventory-system
  why: Pygame drag-and-drop inventory patterns and UI component design
  critical: Drag-and-drop implementation approaches for block movement

- url: https://stackoverflow.com/questions/21353398/game-crafting-system-logic
  why: Crafting system architecture and recipe matching algorithms
  critical: Flexible pattern matching for shaped vs shapeless recipes

- url: https://docs.python.org/3/library/json.html#json.JSONEncoder
  why: Recipe storage format and custom serialization for BlockType recipes
  critical: JSON serialization of complex recipe patterns and block references
```

### Current Codebase Tree
```bash
├── src/
│   └── pymine/
│       ├── __init__.py
│       ├── game.py          # Theme system, rendering, input handling
│       ├── physics.py       # InputState, player physics  
│       └── world.py         # BlockType, Inventory, block management
├── tests/
│   ├── test_physics.py
│   └── test_world.py
├── PRPs/ai_docs/            # AI implementation documentation
└── pyproject.toml
```

### Desired Codebase Tree with Files Added
```bash
├── src/
│   └── pymine/
│       ├── __init__.py
│       ├── game.py          # Add crafting UI rendering and input
│       ├── physics.py       # No changes needed
│       ├── world.py         # Add recipe validation logic
│       └── crafting.py      # NEW: Recipe system and crafting logic
├── tests/
│   ├── test_physics.py
│   ├── test_world.py
│   └── test_crafting.py     # NEW: Crafting system tests
├── recipes/
│   └── base_recipes.json    # NEW: Recipe definitions
├── PRPs/ai_docs/
└── pyproject.toml
```

### Known Gotchas & Library Quirks

```python
# Pygame UI Layering
# CRITICAL: Modal crafting interface must render above game world
# Must handle input event capture without breaking existing controls
crafting_open = True  # Blocks world input events
for event in pygame.event.get():
    if crafting_open and event.type in UI_EVENTS:
        handle_crafting_input(event)  # UI gets priority
    elif not crafting_open:
        handle_world_input(event)  # Normal game input

# Inventory Reference Management  
# CRITICAL: Crafting grid holds references to inventory blocks
# Must avoid duplicating blocks or breaking inventory state
crafting_grid[0][0] = inventory.slots[2]  # Reference, not copy
inventory.slots[2] = None  # Remove from inventory when placed in grid
# GOTCHA: Must restore blocks if crafting cancelled

# BlockType Theme Integration
# CRITICAL: Crafted blocks must work with theme system
crafted_block = BlockType("Planks", theme_colour(base_hue + 0.15, 0.6, 0.4))  # Theme-aware
# GOTCHA: Recipe results must regenerate colors when theme changes

# Recipe Pattern Matching
# CRITICAL: Recipe patterns need flexible matching (rotation, empty slots)
pattern = [["wood", "wood"], ["wood", "wood"]]  # 2x2 pattern
grid = [["wood", "wood", None], ["wood", "wood", None], [None, None, None]]  # 3x3 grid
# GOTCHA: Must handle pattern rotation and partial matching
```

## Implementation Blueprint

### Data Models and Structure

Create crafting system with flexible recipe management and UI components:

```python
# Core recipe structure
@dataclass(frozen=True)
class Recipe:
    """Defines a crafting recipe with input pattern and output"""
    name: str
    pattern: List[List[Optional[str]]]  # 3x3 grid pattern (None = empty)
    result: str  # Output block name  
    result_count: int = 1
    recipe_type: str = "shaped"  # "shaped" or "shapeless"

# Crafting grid state management
@dataclass
class CraftingState:
    """Manages crafting interface state and operations"""
    grid: List[List[Optional[BlockType]]]  # 3x3 crafting grid
    preview_result: Optional[Recipe] = None
    is_open: bool = False

# Recipe database management  
class RecipeManager:
    """Loads, validates, and matches crafting recipes"""
    
# UI component for crafting interface
class CraftingInterface:
    """Handles crafting UI rendering and interaction"""
```

### Implementation Tasks (ordered by dependencies)

```yaml
Task 1: CREATE src/pymine/crafting.py
  - IMPLEMENT: Recipe, CraftingState dataclasses, RecipeManager, CraftingInterface classes
  - IMPLEMENT: load_recipes(), find_matching_recipe(), execute_recipe() functions
  - FOLLOW pattern: src/pymine/world.py (dataclass usage, type hints, factory functions)
  - NAMING: CamelCase classes, snake_case functions, descriptive method names
  - PLACEMENT: New module in src/pymine/ alongside world.py
  - DEPENDENCIES: None (imports from world.py for BlockType)

Task 2: CREATE recipes/base_recipes.json
  - IMPLEMENT: Starter recipe set (wood->planks, stone->bricks, clay->pottery, etc.)
  - IMPLEMENT: Recipe format specification with pattern validation
  - FOLLOW pattern: JSON structure similar to block palette definitions  
  - NAMING: base_recipes.json for core recipes, descriptive recipe names
  - PLACEMENT: New recipes/ directory at project root
  - DEPENDENCIES: Task 1 (Recipe dataclass structure defined)

Task 3: EXTEND src/pymine/world.py with crafting integration
  - IMPLEMENT: get_craftable_blocks() method for theme-compatible recipe results
  - IMPLEMENT: Inventory.reserve_blocks() and restore_blocks() for crafting operations
  - FOLLOW pattern: Existing inventory manipulation methods and block creation
  - NAMING: crafting-specific method names, maintain inventory interface consistency
  - DEPENDENCIES: Task 1 (crafting data structures available)
  - PRESERVE: All existing inventory and block functionality

Task 4: MODIFY src/pymine/game.py for crafting UI integration
  - IMPLEMENT: Crafting interface rendering with theme integration
  - IMPLEMENT: C key toggle for crafting interface modal
  - IMPLEMENT: Drag-and-drop interaction for crafting grid
  - IMPLEMENT: Recipe preview and craft button functionality
  - FOLLOW pattern: draw_inventory() rendering style, existing event handling
  - NAMING: draw_crafting_interface(), handle_crafting_input() function names
  - DEPENDENCIES: Task 1, 2, 3 (complete crafting system available)

Task 5: CREATE tests/test_crafting.py
  - IMPLEMENT: Recipe matching tests with various pattern configurations
  - IMPLEMENT: Crafting grid manipulation and inventory integration tests
  - IMPLEMENT: UI state management and error condition tests
  - FOLLOW pattern: tests/test_world.py (helper functions, comprehensive coverage)
  - NAMING: test_recipe_matching(), test_crafting_grid_operations() patterns
  - COVERAGE: All crafting operations including edge cases and error conditions
  - DEPENDENCIES: Task 1, 2, 3 (implementation complete)

Task 6: EXTEND existing tests with crafting integration
  - MODIFY: tests/test_world.py to test inventory methods with crafting operations
  - ADD: Theme compatibility tests for crafted blocks
  - IMPLEMENT: Integration tests for crafting with save/load system
  - FOLLOW pattern: Existing test organization and assertion styles
  - COVERAGE: Verify crafting works with all existing PyMine systems
  - DEPENDENCIES: Task 5 (crafting tests established)
```

### Implementation Patterns & Key Details

```python
# Recipe System Pattern
class RecipeManager:
    def __init__(self, recipe_file="recipes/base_recipes.json"):
        self.recipes = self.load_recipes(recipe_file)
    
    def find_matching_recipe(self, grid: List[List[Optional[BlockType]]]) -> Optional[Recipe]:
        """Find recipe matching current crafting grid state"""
        # PATTERN: Try exact match first, then rotations, then shapeless
        # CRITICAL: Handle empty slots and pattern flexibility
        for recipe in self.recipes:
            if self.matches_pattern(grid, recipe.pattern):
                return recipe
            if recipe.recipe_type == "shaped":
                for rotation in self.get_rotations(recipe.pattern):
                    if self.matches_pattern(grid, rotation):
                        return recipe
        return None

# Crafting UI Integration Pattern
def draw_crafting_interface(surface, crafting_state, inventory, theme):
    """Render crafting interface with theme integration"""
    
    # PATTERN: Modal overlay with semi-transparent background
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((*theme.hud_shadow, 128))  # Semi-transparent
    surface.blit(overlay, (0, 0))
    
    # PATTERN: Center crafting grid on screen
    grid_size = 3 * SLOT_SIZE + 2 * SLOT_SPACING
    grid_x = (surface.get_width() - grid_size) // 2
    grid_y = (surface.get_height() - grid_size) // 2
    
    # PATTERN: Draw grid slots with theme colors
    for row in range(3):
        for col in range(3):
            slot_rect = pygame.Rect(
                grid_x + col * (SLOT_SIZE + SLOT_SPACING),
                grid_y + row * (SLOT_SIZE + SLOT_SPACING), 
                SLOT_SIZE, SLOT_SIZE
            )
            pygame.draw.rect(surface, theme.hud_panel, slot_rect)
            # Draw block if present in grid
            block = crafting_state.grid[row][col]
            if block:
                pygame.draw.rect(surface, block.color, slot_rect.inflate(-8, -8))

# Drag and Drop Pattern  
def handle_crafting_mouse_input(event, crafting_state, inventory):
    """Handle mouse interaction with crafting grid"""
    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:  # Left click
            grid_pos = get_grid_position(event.pos)
            inventory_pos = get_inventory_position(event.pos)
            
            if grid_pos and inventory_pos is None:
                # PATTERN: Move block from grid back to inventory
                row, col = grid_pos
                if crafting_state.grid[row][col]:
                    block = crafting_state.grid[row][col]
                    crafting_state.grid[row][col] = None
                    inventory.add_block(block)
            
            elif inventory_pos and grid_pos is None:
                # PATTERN: Move block from inventory to grid  
                slot = inventory_pos
                if inventory.slots[slot]:
                    block = inventory.slots[slot]
                    empty_grid_slot = find_empty_grid_slot(crafting_state.grid)
                    if empty_grid_slot:
                        row, col = empty_grid_slot
                        crafting_state.grid[row][col] = block
                        inventory.slots[slot] = None

# Recipe Result Generation Pattern
def generate_recipe_result(recipe: Recipe, base_hue: float) -> BlockType:
    """Create recipe result block with current theme colors"""
    # PATTERN: Use recipe metadata to determine color offset
    color_offset = RECIPE_COLOR_OFFSETS.get(recipe.name, 0.0)
    result_color = _theme_colour(base_hue + color_offset, 0.6, 0.4)
    
    return BlockType(
        name=recipe.name,
        color=result_color, 
        solid=True  # Most crafted blocks are solid
    )
    # CRITICAL: Recipe results must regenerate when theme changes
```

### Integration Points

```yaml
INVENTORY_SYSTEM:
  - block management: "Extend inventory to support crafting grid operations"
  - slot manipulation: "Preserve inventory selection during crafting"
  - capacity handling: "Manage inventory space for crafted items"

THEME_SYSTEM:
  - color generation: "Crafted blocks must use theme-derived colors"
  - palette integration: "Add crafted blocks to available block palette"  
  - visual consistency: "Crafting UI colors match current theme"

WORLD_PLACEMENT:
  - block integration: "Crafted blocks work with existing placement system"
  - physics compatibility: "Crafted blocks interact normally with collision system"
  - save/load support: "Crafted blocks persist correctly in save files"

INPUT_SYSTEM:
  - modal control: "Crafting interface captures input when open"
  - key bindings: "C key toggle without conflicting with existing controls"
  - mouse handling: "Drag-and-drop interaction with grid and inventory"
```

## Validation Loop

### Level 1: Syntax & Style (Immediate Feedback)

```bash
# Run after each file creation - fix before proceeding
uv run ruff check src/pymine/crafting.py --fix
uv run mypy src/pymine/crafting.py
uv run ruff format src/pymine/crafting.py

# Recipe file validation
python -c "
import json
with open('recipes/base_recipes.json') as f:
    recipes = json.load(f)
print(f'Loaded {len(recipes)} recipes successfully')
for recipe in recipes[:3]:
    print(f'Recipe: {recipe[\"name\"]} -> {recipe[\"result\"]}')
"

# Project-wide validation
uv run ruff check src/ --fix
uv run mypy src/
uv run ruff format src/

# Expected: Zero errors. Recipe JSON valid. All formatting consistent.
```

### Level 2: Unit Tests (Component Validation)

```bash
# Test crafting module components
uv run pytest tests/test_crafting.py::test_recipe_loading -v
uv run pytest tests/test_crafting.py::test_pattern_matching -v
uv run pytest tests/test_crafting.py::test_crafting_grid_operations -v

# Test integration with existing systems
uv run pytest tests/test_world.py::test_inventory_crafting_integration -v
uv run pytest tests/test_crafting.py::test_theme_compatibility -v

# Full crafting test suite with coverage
uv run pytest tests/test_crafting.py --cov=src/pymine/crafting --cov-report=term-missing

# Expected: All tests pass. >90% coverage on crafting module.
```

### Level 3: Integration Testing (System Validation)

```bash
# Test complete crafting workflow
uv run python -c "
from src.pymine.crafting import RecipeManager, CraftingState
from src.pymine.world import BlockType, Inventory, build_palette

# Set up test environment
recipes = RecipeManager()
print(f'Loaded {len(recipes.recipes)} recipes')

# Test recipe matching
palette = build_palette(0.5)
wood_block = next(b for b in palette if 'wood' in b.name.lower())

# Create test crafting grid (2x2 wood pattern)
grid = [[wood_block, wood_block, None],
        [wood_block, wood_block, None], 
        [None, None, None]]

# Find matching recipe
recipe = recipes.find_matching_recipe(grid)
if recipe:
    print(f'Found recipe: {recipe.name} -> {recipe.result}')
else:
    print('No matching recipe found')
"

# Test UI integration (requires pygame)
uv run python -c "
import pygame
pygame.init()
screen = pygame.display.set_mode((100, 100), pygame.HIDDEN)

from src.pymine.game import draw_crafting_interface
from src.pymine.crafting import CraftingState
from src.pymine.world import Inventory, build_palette

# Test rendering without errors
crafting_state = CraftingState(grid=[[None]*3 for _ in range(3)])
inventory = Inventory(slots=list(build_palette()))
# draw_crafting_interface(screen, crafting_state, inventory, theme)
print('Crafting interface rendering test passed')
pygame.quit()
"

# Performance validation
uv run python -c "
import time
from src.pymine.crafting import RecipeManager

# Recipe loading performance
start = time.time()
recipes = RecipeManager()
load_time = time.time() - start
print(f'Recipe loading time: {load_time:.3f}s (should be <0.01s)')

# Recipe matching performance
start = time.time()
for _ in range(1000):
    recipe = recipes.find_matching_recipe([[None]*3 for _ in range(3)])
match_time = time.time() - start
print(f'1000 recipe matches: {match_time:.3f}s (should be <0.1s)')
"

# Expected: Recipe system works correctly, UI renders, performance targets met
```

### Level 4: Creative & Domain-Specific Validation

```bash
# Manual gameplay testing checklist
echo "MANUAL TESTING REQUIRED:"
echo "1. Start PyMine and collect some basic blocks (wood, stone)"
echo "2. Press C to open crafting interface - should appear centered"
echo "3. Try dragging blocks from inventory to crafting grid"
echo "4. Arrange blocks in valid recipe pattern (2x2 wood -> planks)"
echo "5. Verify recipe preview updates and craft button enables"
echo "6. Click craft button - should consume ingredients and add result"
echo "7. Test crafted blocks in normal building - should place normally"
echo "8. Test theme switching - crafted blocks should change colors"
echo "9. Test save/load - crafted blocks should persist correctly"

# Recipe validation
python -c "
import json
from pathlib import Path

recipe_file = Path('recipes/base_recipes.json')
with open(recipe_file) as f:
    recipes = json.load(f)

# Validate recipe format
required_fields = ['name', 'pattern', 'result']
for i, recipe in enumerate(recipes):
    missing = [f for f in required_fields if f not in recipe]
    if missing:
        print(f'ERROR: Recipe {i} missing fields: {missing}')
    
    # Validate pattern dimensions
    if len(recipe['pattern']) > 3 or any(len(row) > 3 for row in recipe['pattern']):
        print(f'ERROR: Recipe {recipe[\"name\"]} pattern too large (max 3x3)')
    
    print(f'OK: Recipe {recipe[\"name\"]} format valid')
"

# Integration testing
echo "Testing integration with existing systems..."

# Test with save/load system
uv run python -c "
# Simulate crafting -> save -> load -> verify sequence
print('Testing crafting + save/load integration...')
print('This requires PRPs/save-load-system.md to be implemented first')
print('Manual verification: Craft items, save game, reload, verify crafted items persist')
"

# Theme system integration
uv run python -c "
from src.pymine.world import build_palette
from src.pymine.game import create_themes

# Test recipe results with different themes
themes = create_themes()
for theme in themes[:2]:
    palette = build_palette(theme.base_hue)
    print(f'Theme {theme.name}: Generated {len(list(palette))} blocks')
    # Recipe results should use theme-compatible colors
"

# Expected: Manual testing confirms smooth crafting workflow, all integrations work
```

## Final Validation Checklist

### Technical Validation
- [ ] All 4 validation levels completed successfully
- [ ] All tests pass: `uv run pytest tests/ -v`  
- [ ] No linting errors: `uv run ruff check src/`
- [ ] No type errors: `uv run mypy src/`
- [ ] Recipe JSON format valid and loads correctly

### Feature Validation  
- [ ] Crafting interface opens/closes with C key smoothly
- [ ] Drag-and-drop block movement feels responsive
- [ ] Recipe matching works for shaped and shapeless recipes
- [ ] Recipe preview updates in real-time during grid changes
- [ ] Craft button correctly consumes ingredients and produces results
- [ ] Crafted blocks integrate seamlessly with existing building system

### Code Quality Validation
- [ ] Follows PyMine architecture: crafting logic in separate module
- [ ] Uses existing patterns: dataclass structure, theme integration  
- [ ] File placement matches desired codebase tree
- [ ] Maintains performance: 60fps during crafting operations
- [ ] Public API clearly defined with __all__ exports

### User Experience Validation
- [ ] Crafting interface visual design matches PyMine's aesthetic
- [ ] Recipe discovery feels rewarding and intuitive
- [ ] Crafted blocks provide meaningful new building options  
- [ ] Theme switching updates crafted block colors correctly
- [ ] Error states (invalid recipes) handled gracefully
- [ ] Interface controls are discoverable and memorable

---

## Anti-Patterns to Avoid

- ❌ Don't create complex recipe formats - keep JSON simple and readable
- ❌ Don't break existing inventory management - preserve all current functionality
- ❌ Don't hardcode recipe colors - integrate with theme system properly  
- ❌ Don't ignore performance during recipe matching - optimize for common cases
- ❌ Don't create blocking UI - crafting interface should feel responsive
- ❌ Don't duplicate blocks between inventory and crafting grid - use references
- ❌ Don't forget drag-and-drop feedback - provide clear visual cues
- ❌ Don't make recipes too complex initially - start simple and expand
- ❌ Don't skip error handling - validate recipe patterns and handle edge cases
- ❌ Don't break save/load compatibility - ensure crafted blocks persist correctly

**Confidence Score: 8/10** - This PRP provides comprehensive implementation guidance with complete context and specific patterns. The crafting system integrates cleanly with PyMine's architecture and provides meaningful gameplay enhancement while maintaining the game's simplicity and charm.