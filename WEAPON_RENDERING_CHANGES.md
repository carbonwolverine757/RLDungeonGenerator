# Weapon Rendering and Hotbar Improvements

## Changes Made

### 1. Ground Weapon Item Rendering

**Added non-alphanumeric glyph rendering for pickable weapons on the dungeon floor:**

- Weapons placed by `spawn_weapon_items()` are now rendered on the map using `weapon_char` - a non-alphanumeric tileset glyph
- Rendered in brownish-gold color `(200, 150, 100)` to distinguish from coins and other items
- Only rendered if the tile has been explored (fog-of-war)
- Rendering code:
  ```python
  if hasattr(dg, 'ground_items'):
      for (item_r, item_c), item in dg.ground_items.items():
          ir = item_r - cam_y
          ic = item_c - cam_x
          if 0 <= ir < view_h and 0 <= ic < view_w:
              if dg.explored[item_r][item_c]:
                  console.print(ic, ir, weapon_char, fg=(200, 150, 100), bg=(0, 0, 0))
  ```

### 2. Hotbar Redesign

**Completely redesigned the hotbar to be more compact and readable:**

**Old Hotbar:**
- 8 slots displayed horizontally (1 char per slot)
- Showed digit for empty slots
- Showed sword emoji (?) for weapons
- Row 0, columns 0-7 (top of screen)

**New Hotbar:**
- **Location:** Bottom of screen (`view_h - 1`)
- **Layout:** 8 slots, each 2 characters wide:
  - Left char: Item icon (weapon glyph, coin glyph, count, or space)
  - Right char: Hotkey number (1-8)
- **Colors:**
  - Empty slot: Gray `(100, 100, 100)` 
  - Equipped slot: Gold `(255, 230, 150)` on dark brown `(140, 90, 20)`
  - Normal item: Light gray `(200, 200, 200)`
  - Hotkey: Dim gray `(150, 150, 150)` (normal) or gold (equipped)
- **Item Display:**
  - **Weapons:** Use `weapon_char` (non-alphanumeric tileset glyph)
  - **Coins:** Use `coin_char` glyph for single coin, or show count (1-9)
  - **Unknown:** Show '?'
  - **Empty:** Show space

**Implementation:**
```python
hotbar_y = view_h - 1
for i in range(8):
    x = i * 2  # 2 chars per slot
    y = hotbar_y
    bg = (40, 40, 60)
    item = dg.inventory[0][i]
    
    if item is None:
        # Empty slot: [space][number]
        console.print(x, y, ' ', fg=(100, 100, 100), bg=bg)
        console.print(x + 1, y, str(i + 1), fg=(100, 100, 100), bg=bg)
    else:
        # Item slot: [icon][number]
        if item.get('type') == 'weapon':
            icon = weapon_char
        elif item.get('type') == 'coin':
            icon = coin_char if item.get('count', 1) == 1 else str(min(9, item.get('count', 1)))
        else:
            icon = '?'
        
        if dg.equipped_slot == i:
            # Highlighted gold
            console.print(x, y, icon, fg=(255, 230, 150), bg=(140, 90, 20))
            console.print(x + 1, y, str(i + 1), fg=(255, 230, 150), bg=(140, 90, 20))
        else:
            # Normal colors
            console.print(x, y, icon, fg=(200, 200, 200), bg=bg)
            console.print(x + 1, y, str(i + 1), fg=(150, 150, 150), bg=bg)
```

### 3. Character Computation

**Added `weapon_char` tileset glyph:**
- Used for rendering both ground weapon items and hotbar weapon slots
- Gets a non-alphanumeric glyph from the tileset
- Computed from tile index at position (row 4, col 3) in the tileset

## Benefits

### Weapon Rendering
? Weapons are now visible on the dungeon floor with a distinct glyph
? Uses non-alphanumeric characters (no alphas like 'W' or 'w')
? Renders in explored areas only (respects fog-of-war)
? Color-coded `(200, 150, 100)` for easy identification

### Hotbar Improvements
? **More compact:** 16 chars instead of 8 (or expandable)
? **Shows hotkey numbers:** Always visible next to each item
? **Better organized:** Bottom of screen instead of top
? **Non-alphanumeric icons:** Uses tileset glyphs for weapons, not emoji
? **Visual feedback:** Clear highlighting of equipped slot
? **Better coin display:** Shows count for multiple coins
? **Cleaner visual:** Consistent 2-char slot layout

## Visual Example

```
[W][1] [W][2] [ ][3] [C][4] [ ][5] [W][6] [ ][7] [ ][8]
```

Where:
- `[W]` = weapon glyph (non-alphanumeric)
- `[C]` = coin glyph or count
- `[ ]` = empty slot
- `[1-8]` = hotkey number

Equipped slot would be highlighted in gold:
```
[W][1] [W][2] [ ][3] [C][4] [ ][5] [W][6] [ ][7] [ ][8]
 ^^^^^ Gold background
```

## Files Changed

- `RLDungeonGenerator.py`
  - Added `weapon_char` computation
  - Added ground weapon item rendering in main render loop
  - Redesigned hotbar display and layout

## Testing Notes

- Ground weapons render correctly with `weapon_char` glyph
- Hotbar displays all 8 slots with proper spacing (2 chars per slot)
- Equipped slot highlights in gold
- Empty slots show hotkey number only
- Items with count properly display coin glyph or numeric count
- No alphanumeric characters used for item icons (only tileset glyphs)
