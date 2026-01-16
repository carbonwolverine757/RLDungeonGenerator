# Quick Start Guide - BearLibTerminal Edition

## Installation (3 Steps)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: (Optional) Verify Installation
```bash
python check_deps.py
```

You should see checkmarks for at least one renderer (BearLibTerminal or tcod).

### Step 3: Run the Game!
```bash
# Recommended: Use BearLibTerminal for native layer support
python RLDungeonGenerator.py --renderer bearlib

# Or let it auto-detect the best renderer
python RLDungeonGenerator.py
```

---

## Game Controls

| Control | Action |
|---------|--------|
| **Arrow Keys** or **WASD** | Move around dungeon |
| **Spacebar** | Attack monsters |
| **1-8 Keys** | Equip hotbar item |
| **I Key** | Toggle inventory |
| **ESC** | Exit game |

---

## Renderers Explained

### ?? **BearLibTerminal** (Recommended)
**Best for**: Multi-layer rendering, modern graphics, performance
```bash
python RLDungeonGenerator.py --renderer bearlib
```

**Advantages:**
- Native layer support (terrain ? objects ? entities ? effects)
- GPU-accelerated rendering
- Cleaner visual effects
- Best performance

**Requires:** `pip install bearlib-terminal`

---

### ??? **tcod** (Traditional Roguelike)
**Best for**: Classic roguelike feel, compatibility
```bash
python RLDungeonGenerator.py --renderer tcod
```

**Advantages:**
- Traditional roguelike rendering
- Wide library support
- Well-documented

**Requires:** `pip install tcod` (usually installed with requirements.txt)

---

### ?? **ASCII** (Fallback)
**Best for**: Testing, headless systems, accessibility
```bash
python RLDungeonGenerator.py --renderer ascii
```

**Advantages:**
- No graphics library needed
- Works everywhere
- Lightweight

**No dependencies required!**

---

## What is "Layering"?

Traditional terminal rendering can only display **one character per cell**. This means you can't easily show both a floor tile AND a coin on the same spot.

**BearLibTerminal fixes this** with native layer support:

```
Layer 0: ·  (floor)
Layer 1: ¤  (coin)    ? Visible on top!
Layer 2:    (empty)
Layer 3:    (empty)
```

The layers are composited automatically, making it easy to:
- Show items on floors
- Display visual effects over entities
- Create better-looking UIs
- Reduce rendering complexity

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'bearlib'"
```bash
pip install bearlib-terminal
```

### "ModuleNotFoundError: No module named 'tcod'"
```bash
pip install tcod
```

### Game runs but renders nothing
Try forcing ASCII mode:
```bash
python RLDungeonGenerator.py --renderer ascii
```

### Performance is slow in BearLibTerminal
- Reduce view size in `render_bearlib.py` (change `view_w` and `view_h`)
- Check GPU drivers are up to date
- Try tcod renderer instead: `--renderer tcod`

### Tileset not loading
- Verify `assets/tilesets/unicode_tileset.png` exists
- Renderers will fallback to default font if missing
- No error = game will still work, just with default characters

---

## Extending the Game

See `ARCHITECTURE.md` for details on:
- Adding new dungeon levels
- Creating custom renderers
- Extending the inventory system
- Modifying monster AI

---

## Tips for Gameplay

1. **Equip weapons** with number keys (1-8) before attacking
2. **Stamina regenerates slowly** — pace your attacks
3. **Explore fully** to reveal all coins and monsters
4. **Advance to harder levels** via the exit `>`
5. **Check inventory** with I key to see your loot

Enjoy exploring the dungeons! ??

---

## Next Steps

- Read `README_BEARLIB.md` for full feature list
- Check `RLDungeonGenerator.py` for game logic
- Explore `render_bearlib.py` to understand layering
- Run `python check_deps.py` to verify setup
