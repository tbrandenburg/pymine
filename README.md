# pymine

<img width="1038" height="820" alt="grafik" src="https://github.com/user-attachments/assets/4530e242-a8ce-41e1-a9aa-e2aecf11583f" />

A colourful 2D Minecraft / Super Mario inspired sandbox built with
pygame.  The codebase is intentionally compact, extensively commented and
split into a pygame free logic layer so Python beginners can experiment
without digging through framework specifics.

## Features

* Endless, pastel landscape that scrolls beneath the player while preserving a cosy handcrafted spawn area.
* Terrain now flows both horizontally and vertically – wander into new territory or build skyward/deep underground and fresh columns are generated on demand.
* Five block inventory (selectable with keys 1-5) with left click to place and right click to remove blocks.
* Rectangular crosshair that snaps to the grid and respects a 5x5 build radius around the player.
* Responsive controls with jumping, crouching and a double-space flight toggle.
* Relaxing rainbow of colour themes crafted with pastel harmony – cycle them with the ``T`` key.

## Getting started

This repository uses a standard [uv](https://github.com/astral-sh/uv)
layout.  Install dependencies and run the game with:

```bash
uv pip install -r pyproject.toml
uv run pymine
```

If you prefer using plain `pip`, install the project in editable mode and
run the script entry point:

```bash
pip install -e .
pymine
```

## Running the tests

Automated tests cover the pygame independent mechanics:

```bash
uv run pytest
```

## Controls

* **Arrow keys / WASD** – move left/right (and up/down when in flight mode)
* **Space** – jump
* **Double space** – toggle flight mode
* **Shift** – crouch for precise movement
* **Mouse** – position the crosshair, left click to place, right click to remove
* **1-5** – select blocks from the inventory bar
* **T** – cycle through the curated relaxing colour themes
* **Escape** – quit the game
