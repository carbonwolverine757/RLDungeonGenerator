# RLDungeonGenerator - BearLibTerminal Edition

A roguelike dungeon generator with support for multiple rendering backends, including **native layer support** via BearLibTerminal.

## Features

- **Binary Space Partitioning (BSP)** dungeon generation
- **Multiple rendering backends**:
  - **BearLibTerminal** (Recommended) - Native layer support for clean tile compositing
  - **tcod** (Classic) - Traditional roguelike terminal rendering
  - **ASCII** (Fallback) - Plain text output
- **Multi-layer rendering** for objects and effects
- **Inventory system** with hotbar
- **Monster AI** with line-of-sight and alert states
- **Health and stamina** bars
- **Level progression** with themed dungeon levels

## Installation

### Windows / macOS / Linux

1. **Clone the repository**:
   ```bash
   git clone https://github.com/carbonwolverine757/RLDungeonGenerator.git
   cd RLDungeonGenerator
   ```

2. **Create a Python virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install BearLibTerminal** (optional, for best experience):
   ```bash
   pip install bearlib-terminal
   ```

## Usage

### Run with automatic renderer selection (tries tcod, then bearlib, then ASCII):
```bash
python RLDungeonGenerator.py
```

### Force a specific renderer:
```bash
# Use BearLibTerminal (recommended for layer support)
python RLDungeonGenerator.py --renderer bearlib

# Use tcod
python RLDungeonGenerator.py --renderer tcod

# ASCII mode
python RLDungeonGenerator.py --renderer ascii --level 0

# Force ASCII fallback
python RLDungeonGenerator.py --ascii
```

### Start at a specific level:
```bash
python RLDungeonGenerator.py --level 2
```

## Controls

| Key | Action |
|-----|--------|
| **Arrow Keys** / **WASD** | Move |
| **1-8** | Equip hotbar item |
| **I** | Toggle inventory |
| **Spacebar** | Attack / Swing weapon |
| **ESC** / **Close Window** | Exit game |

## Why BearLibTerminal?

BearLibTerminal provides **native support for rendering layers** — something that tcod handles through manual compositing. This means:

? **Cleaner code** — No manual layering logic needed  
? **Better performance** — GPU-accelerated rendering  
? **True transparency** — Alpha blending for effects  
? **Easier to extend** — Add new visual effects without touching base rendering  

### Example: Rendering with layers in BearLibTerminal

```python
# Layer 0: Terrain (floor/wall)
terminal.put(x, y, '·')  # Floor

# Layer 1: Objects (coins, items)
terminal.put(x, y, '¤')  # Coin

# Layer 2: Entities (monsters, player)
terminal.put(x, y, 'G')  # Monster

# Layer 3: Effects (attacks, spells)
terminal.put(x, y, '*')  # Attack effect
```

Each `put()` call is on a separate layer — no overwrites needed!

## Architecture

```
RLDungeonGenerator.py      # Main game logic and dungeon generation
??? render_with_tcod()    # tcod renderer (traditional)
??? render_bearlib.py     # BearLibTerminal renderer (layered)
    ??? Native layers: terrain ? objects ? entities ? effects
```

## Dungeon Generation

Dungeons are generated using **Binary Space Partitioning (BSP)**:

1. Recursively split the map into sections
2. Carve rooms within leaf sections
3. Connect adjacent rooms with corridors
4. Spawn monsters, coins, and level exits

Each level has unique parameters for room size, difficulty, and visuals.

## Level Templates

The game includes 5 difficulty tiers:

| Level | Name | Difficulty | Features |
|-------|------|-----------|----------|
| 0 | Caverns | Easy | Larger rooms, fewer monsters |
| 1 | Underground Halls | Medium | Standard layout |
| 2 | Dark Dungeons | Hard | Smaller rooms, more monsters |
| 3 | Obsidian Depths | Very Hard | Maze-like, dangerous |
| 4 | Abyss | Extreme | Open space with many enemies |

## Extending the Renderer

To add support for a new rendering backend:

1. Create a new file: `render_mybackend.py`
2. Implement `render_with_mybackend(dg)` function
3. Update `main()` in `RLDungeonGenerator.py` to include your renderer
4. Add renderer choice to `--renderer` argument

## Troubleshooting

**"BearLibTerminal is not installed"**
```bash
pip install bearlib-terminal
```

**"tcod is not installed"**
```bash
pip install tcod
```

**Can't load tileset**
- Ensure `assets/tilesets/unicode_tileset.png` exists
- Renderer will fallback to default font if tileset missing

**Performance issues with BearLibTerminal**
- Reduce view size (change `view_w` and `view_h` in renderer)
- Disable effects layer temporarily
- Ensure GPU drivers are up to date

## License

This code is released into the **Public Domain**. Use it freely in any project.

## Credits

- **Dungeon generation**: Binary Space Partitioning algorithm
- **Rendering**: BearLibTerminal, tcod-py
- **Unicode glyphs**: CP437 extended character set
