# Weapons Data File - Organization Guide

## File Structure

The weapons system is now organized as follows:

```
RLDungeonGenerator/
??? RLDungeonGenerator.py       (main game engine)
??? weapons_data.py             (NEW: weapon definitions)
??? weapons_data.py            (NEW: weapon data file)
??? [other files...]
```

## weapons_data.py Overview

### Contents

The `weapons_data.py` file contains:

1. **WEAPONS Array** - All weapon definitions
2. **Helper Functions** - Access weapons by name/index
3. **Documentation** - Complete parameter descriptions

### WEAPONS Array

```python
WEAPONS = [
    {
        'name': 'Wooden Sword',
        'glyph_index': 0,
        'damage': 5,
        'stamina_use': 3,
        'attack_speed': 1.0,
        'range': 0,
        'area': 1,
        'angle': 0,
    },
    # ... 7 more weapons
]
```

Each weapon is a dictionary with 8 parameters.

### Helper Functions

#### get_weapon_by_name(name)
```python
weapon = get_weapon_by_name("Iron Sword")
# Returns: {name, glyph_index, damage, stamina_use, attack_speed, range, area, angle}
```

#### get_weapon_by_index(index)
```python
weapon = get_weapon_by_index(0)  # Gets first weapon (Wooden Sword)
# Returns: weapon dict or None
```

#### get_all_weapons()
```python
all_weapons = get_all_weapons()
# Returns: list of all weapon dicts (copies)
```

## Using in RLDungeonGenerator.py

### Import
```python
from weapons_data import WEAPONS, get_weapon_by_name, get_weapon_by_index, get_all_weapons
```

### Initialize with Weapon
```python
wooden_sword = get_weapon_by_name("Wooden Sword")
if wooden_sword:
    wooden_sword['type'] = 'weapon'
    self.inventory[0][0] = wooden_sword
```

### Get Weapon Stats
```python
weapon = self.inventory[0][equipped_slot]
damage = weapon.get('damage')
stamina_cost = weapon.get('stamina_use')
attack_speed = weapon.get('attack_speed')
```

## The 8 Parameters Explained

### 1. name (string)
- Display name shown to player
- Used for lookups: `get_weapon_by_name("Iron Sword")`
- Examples: "Wooden Sword", "War Hammer", "Mage Staff"

### 2. glyph_index (integer)
- Index into tileset for visual representation
- Range: 0-7 (current), can extend higher
- Currently placeholders (0-7)
- Can be customized to match tileset positions

### 3. damage (integer)
- HP dealt to monsters per hit
- Range: 4-16 (in current weapons)
- Higher damage usually = slower/more expensive
- Applied once per attack

### 4. stamina_use (integer)
- Stamina consumed per attack
- Range: 2-12 (in current weapons)
- Deducted immediately when attacking
- Higher cost = more powerful typically

### 5. attack_speed (float)
- Cooldown between attacks in seconds
- Range: 0.6-2.5 (in current weapons)
- Formula: `current_time - last_attack_time >= attack_speed`
- Lower = faster (more attacks per second)
  - 0.6 = 1.67 attacks per second
  - 1.0 = 1.0 attacks per second
  - 2.5 = 0.4 attacks per second

### 6. range (integer)
- Maximum distance weapon can reach
- 0 = melee only (adjacent square)
- 1-3 = spear attacks (at distance)
- 5+ = long-range magic
- Weapon hits up to this many squares away
- Attack originates from player, travels range squares

### 7. area (integer)
- Size of explosion/AoE from impact point
- 1 = single tile only
- 2+ = larger splash radius
- Combined with angle for effect pattern
- Ignored if angle = 0

### 8. angle (integer, degrees)
- Arc/cone width of attack spread
- 0 = straight line, no spread (ignores area)
- 45-90 = cone/arc attacks
- 180 = semicircle (half-circle)
- 360 = full circle (explosion)
- Determines attack shape pattern

## Current Weapons Summary

| Weapon | DMG | Stamina | Speed | Range | Area | Angle | Notes |
|--------|-----|---------|-------|-------|------|-------|-------|
| Dagger | 4 | 2 | 0.6s | 0 | 1 | 0° | Fast, cheap |
| Wooden Sword | 5 | 3 | 1.0s | 0 | 1 | 0° | Starter |
| Iron Sword | 10 | 5 | 1.2s | 0 | 1 | 0° | Best DPS |
| Broad Axe | 15 | 8 | 2.0s | 0 | 2 | 90° | Wide swing |
| Short Spear | 8 | 4 | 1.0s | 2 | 1 | 0° | Close range |
| Long Spear | 12 | 6 | 1.5s | 3 | 1 | 0° | Extended |
| War Hammer | 16 | 10 | 2.5s | 0 | 2 | 180° | Heavy AoE |
| Mage Staff | 14 | 12 | 2.0s | 5 | 2 | 360° | Magic |

## Adding New Weapons

### In weapons_data.py

Simply add a new entry to the WEAPONS array:

```python
WEAPONS = [
    # ... existing weapons ...
    {
        'name': 'Flaming Sword',
        'glyph_index': 8,
        'damage': 12,
        'stamina_use': 7,
        'attack_speed': 1.1,
        'range': 0,
        'area': 1,
        'angle': 0,
    },
]
```

That's it! The system automatically supports it:
- Can be used in attacks
- Can be equipped (if added to inventory)
- Works with all game mechanics
- No code changes needed in RLDungeonGenerator.py

### Example: Scythe (AoE ranged)

```python
{
    'name': 'Scythe',
    'glyph_index': 9,
    'damage': 13,
    'stamina_use': 9,
    'attack_speed': 1.8,
    'range': 1,
    'area': 2,
    'angle': 120,
},
```

### Example: Sniper Bow

```python
{
    'name': 'Sniper Bow',
    'glyph_index': 10,
    'damage': 20,
    'stamina_use': 8,
    'attack_speed': 2.2,
    'range': 7,
    'area': 1,
    'angle': 0,
},
```

## Benefits of Separate File

### Organization
- Weapons data separated from game logic
- Easy to find and modify weapon definitions
- Clean separation of concerns

### Maintainability
- All weapons in one place
- Easy to add/remove/modify weapons
- Parameters clearly documented
- No need to edit main game file

### Extensibility
- Add as many weapons as needed
- Helper functions for lookups
- Easy to create weapon variants
- Can import functions elsewhere

### Version Control
- Easier to track weapon balance changes
- Can diff weapon changes separately
- Cleaner Git history
- Weapon tweaks don't affect game code

## Importing in Other Files

### In RLDungeonGenerator.py
```python
from weapons_data import WEAPONS, get_weapon_by_name, get_weapon_by_index, get_all_weapons
```

### Create weapon in inventory
```python
weapon = get_weapon_by_name("Iron Sword")
inventory[0][0] = weapon
```

### Get all weapons for UI
```python
all_weapons = get_all_weapons()
for weapon in all_weapons:
    print(f"{weapon['name']}: DMG={weapon['damage']}")
```

## File Modifications

### RLDungeonGenerator.py Changes
1. Added import from weapons_data.py
2. Removed inline WEAPONS array
3. Updated inventory initialization to use get_weapon_by_name()

### weapons_data.py (NEW)
- Contains WEAPONS array
- Helper functions
- Complete documentation

## Design Rationale

### Why Separate File?
1. **Single Responsibility** - weapons_data.py only handles weapons
2. **Reusability** - can import in other files
3. **Maintainability** - easier to tweak balance
4. **Clarity** - weapon data clearly visible
5. **Growth** - easier to expand weapon system

### Why Helper Functions?
1. **Encapsulation** - don't directly access WEAPONS array
2. **Flexibility** - can change storage format later
3. **Safety** - returns copies, not references
4. **Convenience** - easy to look up weapons

### Why 8 Parameters?
1. **Damage** - how strong the attack is
2. **Stamina** - resource cost
3. **Speed** - attack frequency
4. **Range** - where weapon reaches
5. **Area** - splash radius
6. **Angle** - spread pattern
7. **Name** - display/lookup
8. **Glyph** - visual representation

## Future Extensions

### Possible Additions
- Weapon effects (poison, burn, stun)
- Weapon upgrades/enchantments
- Weapon rarity (common, rare, legendary)
- Weapon special abilities
- Weapon durability
- Weapon crafting recipes

### Easy to Add
```python
{
    'name': 'Enhanced Sword',
    'glyph_index': 11,
    'damage': 15,
    'stamina_use': 6,
    'attack_speed': 1.0,
    'range': 0,
    'area': 1,
    'angle': 0,
    'effect': 'fire',           # NEW
    'rarity': 'rare',           # NEW
    'durability': 100,          # NEW
}
```

Just add the new fields and they're available!

## Summary

The weapons system is now cleanly organized:

? Weapons data in separate file (weapons_data.py)
? Game logic in main file (RLDungeonGenerator.py)
? Helper functions for access
? Easy to add new weapons
? Fully documented parameters
? Production-ready structure

Ready to expand with more weapons!
