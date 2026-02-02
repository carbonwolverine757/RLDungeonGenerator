# Examples: Extending the Layer System

This file demonstrates how to extend BearLibTerminal's native layer system with new visual effects.

## Example 1: Adding a Particle Effect Layer

### Add to `render_bearlib.py` after entity rendering:

```python
# ===== LAYER 3.5: Particle Effects (NEW) =====
for particle in dg.active_particles:
    pr = particle['row'] - cam_y
    pc = particle['col'] - cam_x
    if 0 <= pr < view_h and 0 <= pc < view_w:
        # Fade color based on age
        age_ratio = particle['age'] / particle['lifetime']
        alpha = int(255 * (1 - age_ratio))
        
        terminal.color(terminal.color_from_argb(alpha, 
            particle['color'][0],
            particle['color'][1],
            particle['color'][2]))
        terminal.put(pc, pr, particle['char'])
```

### Add to RLDungeonGenerator class:

```python
def __init__(self, w, h, level=0):
    # ...existing code...
    self.active_particles = []

def spawn_particle(self, row, col, char, color, lifetime):
    """Spawn a particle effect."""
    self.active_particles.append({
        'row': row,
        'col': col,
        'char': char,
        'color': color,
        'age': 0,
        'lifetime': lifetime
    })

def update_particles(self, dt):
    """Update particle lifetimes."""
    for particle in list(self.active_particles):
        particle['age'] += dt
        if particle['age'] >= particle['lifetime']:
            self.active_particles.remove(particle)
```

### Use in combat:

```python
def swing_weapon(self):
    # ...existing attack code...
    if m['health'] <= 0:
        # Spawn blood effect
        for _ in range(3):
            self.spawn_particle(
                tr, tc,
                char='*',
                color=(200, 0, 0),      # Red
                lifetime=0.3
            )
```

---

## Example 2: Adding a Lighting System

### Create `lighting_system.py`:

```python
import math

class LightSource:
    def __init__(self, row, col, intensity, radius):
        self.row = row
        self.col = col
        self.intensity = intensity
        self.radius = radius

def calculate_light_at(light_sources, row, col, ambient=0.2):
    """Calculate light intensity at a position."""
    light_level = ambient
    
    for light in light_sources:
        dist = math.sqrt((row - light.row)**2 + (col - light.col)**2)
        if dist <= light.radius:
            # Inverse square falloff
            attenuation = 1.0 - (dist / light.radius)
            light_level += light.intensity * (attenuation ** 2)
    
    return min(1.0, light_level)

def darken_color(color, intensity):
    """Darken a color based on light intensity."""
    return tuple(int(c * intensity) for c in color)
```

### Use in `render_bearlib.py`:

```python
from lighting_system import LightSource, calculate_light_at, darken_color

# In render loop, add light sources:
light_sources = [
    LightSource(dg.player_row, dg.player_col, 1.0, 10),  # Player's light
]

# When rendering terrain:
for r in range(view_h):
    wr = cam_y + r
    for c in range(view_w):
        wc = cam_x + c
        
        # Calculate light at this position
        light = calculate_light_at(light_sources, wr, wc)
        
        # Darken floor color based on light
        darkened_fg = darken_color(floor_fg, light)
        
        terminal.color(terminal.color_from_argb(255, *darkened_fg))
        terminal.put(c, r, chars['floor'])
```

---

## Example 3: Adding a Visual Status Effect Layer

### Add to `render_bearlib.py` after monster rendering:

```python
# ===== LAYER 2.5: Status Effects (NEW) =====
for m in getattr(dg, 'monsters', []):
    mr = m['row'] - cam_y
    mc = m['col'] - cam_x
    if 0 <= mr < view_h and 0 <= mc < view_w:
        # Render status effect above monster
        if m.get('poisoned'):
            terminal.color(terminal.color_from_argb(255, 0, 255, 0))  # Green
            terminal.put(mc, mr - 1, '?')  # Poison indicator
        
        if m.get('burning'):
            terminal.color(terminal.color_from_argb(255, 255, 100, 0))  # Orange
            terminal.put(mc, mr - 1, '?')  # Fire indicator
        
        if m.get('stunned'):
            terminal.color(terminal.color_from_argb(255, 255, 255, 0))  # Yellow
            terminal.put(mc, mr - 1, '?')  # Stun indicator
```

### Add to RLDungeonGenerator:

```python
def apply_poison(self, monster):
    """Apply poison status effect."""
    monster['poisoned'] = True
    monster['poison_damage_rate'] = 1.0  # HP/second

def update_status_effects(self, dt):
    """Update and apply status effect damage."""
    for m in self.monsters:
        if m.get('poisoned'):
            m['health'] -= m['poison_damage_rate'] * dt
            m['poison_duration'] -= dt
            if m['poison_duration'] <= 0:
                m['poisoned'] = False
```

---

## Example 4: Adding a Spell Effect Layer

### Create `spell_system.py`:

```python
class Spell:
    def __init__(self, name, char, color, radius, effect):
        self.name = name
        self.char = char
        self.color = color
        self.radius = radius
        self.effect = effect  # Function to apply effect

class FireBall:
    def __init__(self, center_row, center_col, radius=3):
        self.row = center_row
        self.col = center_col
        self.radius = radius
        self.age = 0
        self.lifetime = 1.0
    
    def get_affected_cells(self):
        """Get all cells affected by this spell."""
        cells = []
        for r in range(self.row - self.radius, self.row + self.radius + 1):
            for c in range(self.col - self.radius, self.col + self.radius + 1):
                dist = ((r - self.row)**2 + (c - self.col)**2) ** 0.5
                if dist <= self.radius:
                    cells.append((r, c))
        return cells
```

### Use in combat:

```python
def cast_fireball(self, center_row, center_col, radius=3):
    """Cast a fireball spell."""
    spell = FireBall(center_row, center_col, radius)
    
    for r, c in spell.get_affected_cells():
        # Damage all monsters in area
        for m in self.monsters:
            if m['row'] == r and m['col'] == c:
                m['health'] -= 10
                m['burning'] = True
        
        # Spawn particle effects
        self.spawn_particle(r, c, '?', (255, 100, 0), 0.5)
```

### Render in `render_bearlib.py`:

```python
# ===== LAYER 4: Spell Effects (NEW) =====
for spell in dg.active_spells:
    age_ratio = spell.age / spell.lifetime
    alpha = int(255 * (1 - age_ratio))
    
    for r, c in spell.get_affected_cells():
        sr = r - cam_y
        sc = c - cam_x
        if 0 <= sr < view_h and 0 <= sc < view_w:
            terminal.color(terminal.color_from_argb(alpha, 255, 100, 0))
            terminal.put(sc, sr, '?')
```

---

## Example 5: Adding a Debug Overlay Layer

### Render debugging info on top of everything:

```python
# ===== DEBUG LAYER (Optional) =====
if dg.debug_mode:
    terminal.color(terminal.color_from_argb(255, 0, 255, 0))  # Green
    debug_text = f"FPS: {1/dt:.1f} | Monsters: {len(dg.monsters)}"
    for i, ch in enumerate(debug_text):
        terminal.put(i, 0, ch)
    
    # Show monster positions
    for m in dg.monsters:
        mr = m['row'] - cam_y
        mc = m['col'] - cam_x
        if 0 <= mr < view_h and 0 <= mc < view_w:
            terminal.color(terminal.color_from_argb(100, 0, 255, 0))
            terminal.put(mc, mr, 'X')
```

---

## Layer Rendering Order (Updated)

```
Screen Output
    ?
???????????????????????????????
?  DEBUG LAYER (optional)     ?  ? Only in debug mode
?  SPELL EFFECTS LAYER (4)    ?  ? Spells & area effects
?  PARTICLE EFFECTS LAYER 3.5 ?  ? Fade-out effects
?  EFFECTS LAYER (3)          ?  ? Attack flashes
?  STATUS EFFECTS LAYER 2.5   ?  ? Poison, burn, stun
?  ENTITIES LAYER (2)         ?  ? Player, monsters
?  OBJECTS LAYER (1)          ?  ? Coins, items
?  LIGHTING LAYER 0.5         ?  ? Darkness overlay
?  TERRAIN LAYER (0)          ?  ? Floors, walls
???????????????????????????????
    ?
Display Cell [x,y]
```

---

## Best Practices for Layers

1. **Keep layers organized** — Define layer constants
2. **Minimize alpha blending** — Use opaque colors when possible
3. **Cache calculations** — Pre-calculate lighting/effects
4. **Limit particles** — Cap max active particles to maintain performance
5. **Use pools** — Reuse particle/effect objects instead of creating new ones
6. **Test visually** — Make sure layers don't overlap confusingly

---

## Performance Tips

- **Limit particles**: Cap at 100-200 per frame
- **Batch rendering**: Render all of layer X before layer X+1
- **Avoid overdraw**: Only render visible cells
- **Use simple characters**: Unicode is fine, but avoid very large fonts
- **Cache colors**: Store color_from_argb results

Example:
```python
# Cache color calculations
color_cache = {}
def get_color(r, g, b):
    key = (r, g, b)
    if key not in color_cache:
        color_cache[key] = terminal.color_from_argb(255, r, g, b)
    return color_cache[key]
```

---

## Conclusion

BearLibTerminal's native layer system makes it trivial to add:
- Particle effects
- Lighting & fog
- Status indicators
- Spell effects
- Visual polish

Just add more `terminal.put()` calls in the appropriate layer order!
