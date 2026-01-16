# Architecture & Layer System

## Overview

The RLDungeonGenerator now supports **multiple rendering backends** with the BearLibTerminal backend providing native **multi-layer rendering**.

```
???????????????????????????????????????????????
?         RLDungeonGenerator (Main)           ?
?  - Dungeon generation (BSP algorithm)       ?
?  - Monster AI & pathfinding                 ?
?  - Inventory system                         ?
?  - Player state management                  ?
???????????????????????????????????????????????
         ?
         ???? render_with_tcod()        (tcod backend)
         ???? render_with_bearlib()     (BearLibTerminal backend)
         ???? dg.print_map()            (ASCII backend)
```

---

## Rendering Backends

### 1. BearLibTerminal (`render_bearlib.py`)

**Native Layer Architecture:**

```
Screen Output
    ?
???????????????????????????
?  Layer 3: Effects       ?  (attack flashes, spells)
?  Layer 2: Entities      ?  (player, monsters)
?  Layer 1: Objects       ?  (coins, items, doors)
?  Layer 0: Terrain       ?  (floors, walls)
???????????????????????????
    ?
Display Cell [x,y]
```

**Each layer uses `terminal.put()`:**
```python
# Render floor on layer 0
terminal.color((200, 210, 235))
terminal.put(x, y, '·')

# Render coin on layer 1 (automatically composited)
terminal.color((255, 215, 0))
terminal.put(x, y, '¤')

# Result: Coin is visible on top of floor
```

**Advantages:**
- ? Automatic compositing — no manual layer logic
- ? GPU-accelerated rendering
- ? True color support (16 million colors)
- ? Built-in input handling
- ? Native window management

### 2. tcod (`render_with_tcod()`)

**Manual Layer Architecture:**

```
tcod Console (single layer per console)
    ?? Main console (terrain + entities)
    ?? HUD console (hotbar + stats)
    ?? Blit operations (manual compositing)
```

**Simulated layers through manual rendering:**
```python
# Must render in order, each overwrites previous
console.print(x, y, floor_char)      # Layer 0
console.print(x, y, coin_char)       # Layer 1 (overwrites if present)
console.print(x, y, player_char)     # Layer 2 (overwrites if present)
```

**Advantages:**
- ? Mature and well-documented
- ? Cross-platform support
- ? Traditional roguelike rendering
- ? More complex for multi-layer effects

### 3. ASCII (`dg.print_map()`)

**Single-layer text output:**

```
Prints map as plain text to console.
No graphics, no colors, maximum compatibility.
```

---

## Layer Organization (BearLibTerminal)

### Layer 0: Terrain
- **Purpose**: Static dungeon features
- **Characters**: Floors (·), walls (?), doors (?)
- **Color**: Determined by level template

```python
terminal.color((200, 210, 235))  # Floor color
terminal.put(x, y, '·')
```

### Layer 1: Objects
- **Purpose**: Pickable items and interactive elements
- **Characters**: Coins (¤), treasure, chests
- **Color**: Yellow/gold for visibility

```python
terminal.color((255, 215, 0))
terminal.put(x, y, '¤')
```

### Layer 2: Entities
- **Purpose**: Dynamic characters and creatures
- **Characters**: Player (?), monsters (G), NPCs
- **Color**: White for player, red/dark red for monsters

```python
terminal.color((255, 255, 255))  # White for player
terminal.put(x, y, '?')

terminal.color((255, 0, 0))      # Red for alerted monsters
terminal.put(x, y, 'G')
```

### Layer 3: Effects
- **Purpose**: Temporary visual effects
- **Characters**: Attack indicators (*), spell effects
- **Color**: Orange or bright colors for visibility

```python
terminal.color((255, 100, 50))   # Orange
terminal.put(x, y, '*')
```

---

## Rendering Loop Comparison

### BearLibTerminal (Simple & Clean)
```python
while True:
    # Layer 0: Terrain
    for each cell:
        terminal.put(x, y, floor_char)
    
    # Layer 1: Objects
    for each coin:
        terminal.put(x, y, coin_char)    # Composites automatically
    
    # Layer 2: Entities
    for each monster:
        terminal.put(x, y, monster_char) # On top of coin if present
    
    terminal.refresh()
    key = terminal.read()
```

### tcod (Manual Compositing)
```python
while True:
    console.clear()
    
    # Layer 0: Terrain (must be done first)
    for each cell:
        console.print(x, y, floor_char)
    
    # Layer 1-2: Objects & Entities (order matters!)
    for each coin:
        console.print(x, y, coin_char)
    
    for each entity:
        console.print(x, y, entity_char)  # Overwrites coin if same cell
    
    context.present(console)
    # Handle input
```

---

## Character Set (Unicode)

All renderers use Unicode for rich visuals:

| Glyph | Unicode | Name | Layer | Use |
|-------|---------|------|-------|-----|
| · | U+00B7 | Middle Dot | 0 | Floor |
| ? | U+2588 | Full Block | 0 | Wall |
| ? | U+253C | Box Cross | 0 | Door |
| ¤ | U+00A4 | Currency Sign | 1 | Coin |
| ? | U+2666 | Diamond Suit | 2 | Player |
| G | U+0047 | Letter G | 2 | Monster |
| * | U+002A | Asterisk | 3 | Attack |

---

## Adding a New Renderer

To add support for a new backend (e.g., Pygame):

### Step 1: Create new file `render_pygame.py`

```python
import pygame

def render_with_pygame(dg):
    """Render dungeon using Pygame with custom layer system."""
    pygame.init()
    screen = pygame.display.set_mode((1280, 900))
    clock = pygame.time.Clock()
    
    running = True
    while running:
        # Layer 0: Render terrain
        for x, y in all_tiles:
            draw_tile(screen, x, y, terrain_char)
        
        # Layer 1: Render objects
        for coin in coins:
            draw_tile(screen, coin.x, coin.y, coin_char)
        
        # Layer 2: Render entities
        draw_entity(screen, player.x, player.y, player_char)
        
        # Layer 3: Render effects
        if attack_effect:
            draw_effect(screen, attack_effect.x, attack_effect.y)
        
        pygame.display.flip()
        
        # Handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            handle_input(event)
    
    pygame.quit()
```

### Step 2: Update `RLDungeonGenerator.py`

```python
def main():
    parser.add_argument("--renderer", 
        choices=["auto", "tcod", "bearlib", "pygame", "ascii"])
    
    # In renderer selection logic:
    elif renderer == "pygame":
        try:
            from render_pygame import render_with_pygame
            render_with_pygame(dg)
        except Exception as e:
            print(f"Pygame renderer failed: {e}")
            dg.print_map()
```

---

## Performance Considerations

### BearLibTerminal
- **GPU-accelerated**: Very fast even with many entities
- **Recommended for**: Large maps, complex visuals
- **Overhead**: Initial library load (~1-2s)

### tcod
- **CPU-based**: Good performance for standard-sized maps
- **Recommended for**: Classic roguelikes
- **Overhead**: Moderate library complexity

### ASCII
- **Console I/O**: Fastest for small maps
- **Recommended for**: Testing, headless systems
- **Overhead**: Minimal

---

## Game State Architecture

```
RLDungeonGenerator (World State)
??? dungeon[y][x]        ? Tile data (walls, floors, coins)
??? monsters[]           ? Entity list with state
??? player               ? Player position & stats
??? inventory[][]        ? Hotbar + backpack
??? explored[][]         ? Fog-of-war
??? level_template       ? Current difficulty settings

Renderer (View)
??? Camera positioning
??? Layer compositing
??? Color mapping
??? Input handling
```

---

## Extending Layers

To add a new layer (e.g., weather effects):

**BearLibTerminal:**
```python
# Layer 4: Weather
terminal.color((100, 150, 255))
terminal.put(x, y, '?')  # Snow
```

**tcod:**
```python
# Would require additional console or manual compositing
# More complex than BearLibTerminal
```

---

## Testing Layer Rendering

Create a test scene in `render_bearlib.py`:

```python
# After terminal.open(), add test pattern:
for layer in range(4):
    for x in range(10):
        terminal.color((255, 255, 255))
        terminal.put(x, 0 + layer, f"L{layer}")
        if layer == 0:
            terminal.put(x, 5, '·')  # Terrain
        elif layer == 1:
            terminal.put(x, 5, '¤')  # Objects
        elif layer == 2:
            terminal.put(x, 5, 'G')  # Entities
        elif layer == 3:
            terminal.put(x, 5, '*')  # Effects
```

---

## Conclusion

**BearLibTerminal** provides the cleanest multi-layer rendering experience, while **tcod** remains a solid traditional choice. The abstraction allows easy switching between backends without modifying game logic.

Choose BearLibTerminal for modern roguelikes with rich visuals, or tcod for maximum compatibility.
