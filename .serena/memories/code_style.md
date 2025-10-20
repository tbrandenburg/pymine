# Code Style and Conventions

## General Style
- **PEP 8** compliant Python code
- Extensive docstrings explaining functionality and purpose
- Type hints used throughout (`from __future__ import annotations`)
- Clear, descriptive variable and function names
- Educational comments explaining game development concepts

## Naming Conventions
- **Classes**: PascalCase (e.g., `BlockType`, `PlayerState`, `InfiniteWorld`)
- **Functions**: snake_case (e.g., `create_themes`, `draw_world`, `update_player_physics`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `BLOCK_SIZE`, `GRAVITY`, `JUMP_SPEED`)
- **Private functions**: Leading underscore (e.g., `_theme_colour`, `_update_player_stance`)

## Documentation Style
- Comprehensive module docstrings explaining purpose and design
- Function docstrings with parameter descriptions
- Inline comments for complex logic
- Educational focus - explaining WHY not just WHAT

## Type Hints
- Consistent use of type annotations
- `dataclass` for structured data
- Generic types imported from `typing`
- Optional types properly specified

## Code Organization
- Clear separation of concerns between modules
- pygame-independent logic in core modules
- Constants defined at module level
- `__all__` exports for clean public APIs

## File Structure
- Imports at top, grouped logically
- Constants after imports
- Classes and functions in logical order
- Main execution guarded with `if __name__ == "__main__"`

## Error Handling
- Meaningful exception messages
- Proper bounds checking
- Defensive programming practices
- Clear error conditions in docstrings