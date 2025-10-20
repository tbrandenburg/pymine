# PyMine Tech Stack and Dependencies

## Programming Language
- **Python 3.11+** (specified in pyproject.toml)

## Core Dependencies
- **pygame >= 2.5.0** - Main game framework for graphics, input, and sound
- No other external dependencies (intentionally minimal)

## Development Tools
- **uv** - Modern Python package manager (recommended)
- **pytest** - Testing framework
- Standard Python tools (pip as alternative)

## Project Structure
```
pymine/
├── src/pymine/           # Main package
│   ├── game.py          # pygame frontend and main loop
│   ├── physics.py       # Player movement and physics
│   ├── world.py         # World generation and game logic
│   └── __init__.py      # Package initialization
├── tests/               # Unit tests
│   ├── test_physics.py  # Physics system tests
│   └── test_world.py    # World logic tests
├── pyproject.toml       # Project configuration
├── README.md           # Documentation
└── uv.lock            # Dependency lock file
```

## Build System
- **setuptools** with **wheel** backend
- Entry point: `pymine = "pymine.game:main"`
- Editable installation support

## Platform Support
- Cross-platform (Windows, macOS, Linux)
- pygame handles platform-specific graphics/input
- Currently developed and tested on Windows