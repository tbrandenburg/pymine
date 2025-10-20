# PyMine Product Requirement Prompts (PRPs)

## Overview

This directory contains Product Requirement Prompts (PRPs) for extending PyMine, a colorful 2D Minecraft/Super Mario inspired sandbox built with pygame. Each PRP provides comprehensive implementation guidance designed for AI-driven development, including complete context, specific patterns, and thorough validation procedures.

## What are PRPs?

Product Requirement Prompts (PRPs) combine the disciplined scope of traditional Product Requirements Documents (PRDs) with the "context-is-king" mindset of modern prompt engineering. Each PRP provides:

- **Complete Context**: All necessary codebase patterns, architectural constraints, and external references
- **Implementation Strategy**: Step-by-step tasks with dependency ordering and specific naming conventions  
- **Validation Gates**: Multi-level testing from syntax to system integration to creative validation
- **Quality Assurance**: Comprehensive checklists ensuring production-ready implementation

## Architecture Foundation

### Core PyMine Architecture

PyMine follows a strict 3-layer architecture that all PRPs must respect:

```
game.py (pygame frontend) 
    ↓ depends on
physics.py (game mechanics)
    ↓ depends on  
world.py (pure logic, no pygame)
```

**Critical Rules**:
- `world.py` must remain pygame-independent for testability
- All pygame integration happens in `game.py`
- State management uses dataclasses with clear mutability patterns
- Theme system integration required for all visual elements

### Essential Documentation

Before implementing any PRP, thoroughly understand:

1. **[PyMine Architecture](ai_docs/pymine_architecture.md)** - Complete architectural overview and integration patterns
2. **[Pygame Patterns](ai_docs/pygame_patterns.md)** - Performance optimization and rendering techniques  
3. **[Procedural Generation](ai_docs/procedural_generation.md)** - World generation techniques and noise algorithms
4. **[Common Gotchas](ai_docs/common_gotchas.md)** - Critical pitfalls to avoid during implementation

## Available PRPs

### Tier 1: Foundation Features (High Impact, Low Risk)

#### 1. Save/Load System
**File**: `save-load-system.md` | **Confidence**: 9/10 | **Status**: Ready

**Purpose**: Implement world persistence with JSON-based save files, enabling players to continue their game sessions across application restarts.

**Key Features**:
- Player state and inventory serialization
- Modified block persistence (infinite world optimization)
- Deterministic world generation restoration
- Error handling for corrupted save files

**Dependencies**: None (builds on existing architecture)
**Implementation Time**: 2-3 days
**Integration Points**: Theme system, infinite world generation, player physics

#### 2. Crafting System  
**File**: `crafting-system.md` | **Confidence**: 8/10 | **Status**: Ready

**Purpose**: Recipe-based crafting system allowing players to combine basic blocks into new, advanced block types.

**Key Features**:
- 3x3 crafting grid with drag-and-drop interaction
- Recipe pattern matching (shaped and shapeless)
- Theme-integrated crafted blocks
- JSON-based recipe definitions for easy modding

**Dependencies**: Save/Load System (for recipe result persistence)
**Implementation Time**: 3-4 days  
**Integration Points**: Inventory system, theme system, block placement mechanics

### Tier 2: Gameplay Enhancement Features (Medium Complexity)

#### 3. Mob/Entity System
**File**: `mob-system.md` | **Confidence**: 7/10 | **Status**: Planned

**Purpose**: Add life to PyMine world with moving entities, basic AI, and physics integration.

**Key Features**:
- Entity-component system compatible with existing physics
- Basic AI behaviors (wandering, player following/avoidance)
- Spawning system with biome-appropriate mob types
- Collision and rendering integration

**Dependencies**: Save/Load System (for entity persistence)
**Implementation Time**: 5-6 days
**Integration Points**: Physics system, world generation, theme system

### Tier 3: Advanced Features (High Complexity)

#### 4. Advanced World Generation
**Purpose**: Enhanced procedural generation with biomes, structures, and caves.

**Key Features**:
- Multiple biome types with distinct characteristics
- Structure generation (villages, dungeons, temples)  
- Cave system using density-based or worm-based algorithms
- Ore vein generation with rarity systems

**Dependencies**: Save/Load System, potentially Mob System
**Implementation Time**: 7-10 days

#### 5. Multiplayer Support
**Purpose**: Network-based multiplayer with state synchronization.

**Key Features**:
- Client-server architecture
- Player state synchronization  
- World modification broadcasting
- Conflict resolution for simultaneous edits

**Dependencies**: Save/Load System (for server world persistence)
**Implementation Time**: 10-15 days

## Implementation Ordering

### Recommended Sequence

1. **Start with Save/Load System** - Essential foundation that all other features depend on
2. **Implement Crafting System** - Adds gameplay depth while being relatively self-contained
3. **Add Mob/Entity System** - Brings world to life, requires careful physics integration
4. **Expand World Generation** - Adds exploration value, builds on existing generation
5. **Consider Multiplayer** - Most complex, requires all previous systems working well

### Dependency Graph

```
Save/Load System (Foundation)
    ↓
Crafting System ←→ Mob System
    ↓               ↓
Advanced World Generation
    ↓
Multiplayer Support
```

## Usage Guidelines

### For AI Agents

1. **Read Architecture Documents First**: Always start with `ai_docs/` to understand constraints
2. **Follow PRP Structure Exactly**: Each PRP is designed for single-pass implementation success
3. **Execute All Validation Gates**: Don't skip testing levels - they catch critical issues
4. **Respect Dependencies**: Implement foundation features before dependent ones
5. **Maintain Test Coverage**: Aim for >80% coverage with simple, black-box tests

### For Human Developers

1. **Use PRPs as Detailed Specifications**: Each PRP contains complete implementation guidance
2. **Adapt Validation Commands**: Modify shell commands for your development environment
3. **Reference External URLs**: PRPs contain curated links to relevant documentation
4. **Follow Existing Patterns**: PRPs extract and document PyMine's proven patterns
5. **Contribute Improvements**: Submit feedback if PRPs need clarification or updates

## Quality Standards

### PRP Quality Metrics

Each PRP meets these standards:

- **Context Completeness**: Passes "No Prior Knowledge" test - contains everything needed for implementation
- **Specific References**: All file paths, URLs, and patterns are concrete and actionable
- **Dependency Ordering**: Implementation tasks are properly sequenced with clear dependencies
- **Validation Completeness**: 4-level testing approach from syntax to creative validation
- **Pattern Consistency**: Uses PyMine's established architectural and coding patterns

### Implementation Success Criteria

- **100% Test Suite Pass**: All existing tests continue passing after implementation
- **Architecture Compliance**: Maintains clean layer separation and existing patterns
- **Performance Standards**: Maintains 60fps gameplay during all operations
- **Theme Integration**: All visual elements work with PyMine's theme switching
- **Save/Load Compatibility**: New features persist correctly across game sessions

## File Organization

```
PRPs/
├── README.md                    # This master index
├── save-load-system.md         # Tier 1: World persistence
├── crafting-system.md           # Tier 1: Recipe-based crafting
├── mob-system.md               # Tier 2: Entity system (planned)
└── ai_docs/                    # Implementation documentation
    ├── pymine_architecture.md   # Complete architectural overview
    ├── pygame_patterns.md       # Performance and rendering patterns
    ├── procedural_generation.md # World generation techniques
    └── common_gotchas.md       # Critical pitfalls to avoid
```

## Validation Approach

### Multi-Level Validation Strategy

Each PRP includes comprehensive validation at 4 levels:

1. **Level 1 - Syntax & Style**: Immediate feedback via linting and type checking
2. **Level 2 - Unit Tests**: Component validation with comprehensive test coverage  
3. **Level 3 - Integration**: System-level testing with real data and workflows
4. **Level 4 - Creative**: Domain-specific validation including manual gameplay testing

### Testing Philosophy

- **Simple Over Complex**: Prefer black-box tests with minimal mocking
- **Comprehensive Coverage**: Aim for >80% code coverage overall
- **Performance Conscious**: Validate that features maintain 60fps gameplay
- **User Experience Focused**: Manual testing confirms features feel polished

## Contributing

### Improving Existing PRPs

If you find gaps, unclear instructions, or implementation issues:

1. Document the specific problem and context
2. Propose concrete improvements to PRP content
3. Test your improvements with actual implementation
4. Submit updates with rationale and validation results

### Adding New PRPs

When creating new PRPs:

1. Follow the established template structure from existing PRPs
2. Include complete context using the "No Prior Knowledge" test
3. Provide specific, actionable references (not generic ones)
4. Create comprehensive validation procedures at all 4 levels
5. Assign realistic confidence scores based on implementation complexity

## Success Metrics

### PRP Effectiveness

- **One-Pass Success Rate**: Percentage of PRPs that succeed on first implementation attempt
- **Context Completeness**: Whether implementers need to seek additional information
- **Validation Effectiveness**: Whether validation procedures catch real implementation issues
- **Pattern Consistency**: Whether implementations follow PyMine's established patterns

### Feature Quality

- **User Experience**: Do implemented features feel polished and integrated?
- **Performance Impact**: Do features maintain target framerate and responsiveness?
- **Architectural Integrity**: Do implementations respect PyMine's clean separation of concerns?
- **Test Coverage**: Do implementations include comprehensive, maintainable tests?

---

## Getting Started

1. **Choose a PRP**: Start with Tier 1 features (Save/Load or Crafting)
2. **Read Architecture Docs**: Understand PyMine's patterns in `ai_docs/`
3. **Follow PRP Exactly**: Execute all tasks in dependency order
4. **Validate Thoroughly**: Complete all 4 validation levels
5. **Submit Feedback**: Share results and suggest improvements

**Remember**: Each PRP is designed to provide everything needed for successful implementation. Trust the process, follow the validation gates, and contribute improvements based on your experience.

**Total Implementation Confidence**: Foundation PRPs provide 8-9/10 confidence for one-pass implementation success when followed exactly as specified.