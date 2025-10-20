# Task Completion Checklist

After completing any development task, follow these steps:

## 1. Run Tests
```bash
# Always run the full test suite
uv run pytest

# Check for any failing tests
# All tests must pass before considering work complete
```

## 2. Code Quality (if tools available)
```bash
# Format code
black src/ tests/

# Check style
flake8 src/ tests/

# Type checking
mypy src/
```

## 3. Verify Game Functionality
```bash
# Run the game to ensure it starts and works
uv run pymine

# Test basic functionality:
# - Player movement (WASD/arrows)
# - Block placement (left click)
# - Block removal (right click)
# - Flight mode toggle (double space)
# - Theme cycling (T key)
# - Inventory selection (1-5 keys)
```

## 4. Documentation Updates
- Update README.md if new features added
- Update docstrings for any modified functions
- Add comments for complex new logic

## 5. Git Workflow
```bash
# Stage changes
git add .

# Commit with clear message
git commit -m "Descriptive commit message"

# Push to repository
git push
```

## 6. Performance Check
- Game should run at 60 FPS
- No noticeable lag during world generation
- Smooth player movement and block placement

## Quality Standards
- All tests must pass (100% success rate)
- No regression in existing functionality
- Code follows project style guidelines
- Educational value maintained (clear, readable code)
- No introduction of external dependencies without justification