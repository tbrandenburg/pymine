# PyMine Project Overview

## Project Purpose
PyMine is a colorful 2D sandbox game inspired by Minecraft and Super Mario. It's designed as an educational tool for Python beginners to learn game development with pygame. The codebase is intentionally compact, extensively commented, and split into pygame-free logic layers so Python beginners can experiment without digging through framework specifics.

## Key Features
- Endless, pastel landscape with horizontal and vertical world generation
- 5-block inventory system (keys 1-5) with block placement/destruction
- Player movement with jumping, crouching, and flight mode
- Grid-snapped crosshair with 5x5 build radius
- Responsive physics and collision detection
- Multiple relaxing color themes (cycle with T key)
- Handcrafted spawn area with procedural expansion

## Target Users
- Python beginners learning game development
- Educators teaching programming concepts
- Hobbyist game developers
- Anyone interested in accessible game development

## Architecture
The project uses a clean 3-layer architecture:
1. **Game Layer** (`game.py`) - pygame rendering, input handling, main loop
2. **Physics Layer** (`physics.py`) - movement, gravity, collision logic
3. **World Layer** (`world.py`) - block types, world generation, player state

This separation allows for easy testing and modification of game logic without pygame dependencies.

## Development Philosophy
- Readable code over clever optimizations
- Extensive comments explaining game development concepts
- Beginner-friendly structure and naming
- Testable, modular design
- Educational value prioritized