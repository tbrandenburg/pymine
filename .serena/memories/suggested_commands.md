# Development Commands

## Installation and Setup
```bash
# Using uv (recommended)
uv pip install -r pyproject.toml

# Using pip (alternative)
pip install -e .
```

## Running the Game
```bash
# Using uv
uv run pymine

# Using pip installation
pymine

# Direct execution
python src/pymine/game.py
```

## Testing
```bash
# Run all tests
uv run pytest

# Run with coverage (if coverage installed)
uv run pytest --cov=pymine

# Run specific test file
uv run pytest tests/test_world.py
```

## Development Workflow
```bash
# Install in development mode
pip install -e .

# Run tests after changes
uv run pytest

# Check code style (if tools installed)
black src/ tests/
flake8 src/ tests/
mypy src/
```

## Windows-Specific Commands
```cmd
# Directory listing
dir

# Change directory
cd path\to\directory

# Find files
dir /s *.py

# Search in files
findstr "search_term" *.py
```

## Git Commands
```bash
git status
git add .
git commit -m "message"
git push
```

## Virtual Environment (if not using uv)
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Unix
deactivate
```