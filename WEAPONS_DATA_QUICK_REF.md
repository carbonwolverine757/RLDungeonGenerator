# weapons_data.py - Developer Quick Reference

## What Is It?

A dedicated file containing all weapon definitions for the game. **No game logic here** - just data and helper functions.

## Location

```
RLDungeonGenerator/
??? weapons_data.py  ? This file
```

## How to Use

### Import in Your Code
```python
from weapons_data import WEAPONS, get_weapon_by_name, get_weapon_by_index, get_all_weapons
```

### Access Weapons

#### By Name (Recommended)
```python
sword = get_weapon_by_name("Iron Sword")
if sword:
    damage = sword['damage']
    cost = sword['stamina_use']
```

#### By Index
```python
first_weapon = get_weapon_by_index(0)
all_weapons = get_all_weapons()
```

#### Direct Access
```python
for weapon in WEAPONS:
    print(weapon['name'], weapon['damage'])
```

## The 8 Parameters

| Name | Type | Range | Example |
|------|------|-------|---------|
| `name` | str | any | "Iron Sword" |
| `glyph_index` | int | 0-7 (or higher) | 1 |
| `damage` | int | 4-20 | 10 |
| `stamina_use` | int | 2-18 | 5 |
| `attack_speed` | float | 0.6-3.5 | 1.2 |
| `range` | int | 0-7 | 0 |
| `area` | int | 1-3 | 1 |
| `angle` | int | 0, 45, 90, 180, 360 | 0 |

## Current Weapons

```
0. Wooden Sword (dmg 5)
1. Iron Sword (dmg 10)
2. Broad Axe (dmg 15)
3. Short Spear (dmg 8)
4. Long Spear (dmg 12)
5. War Hammer (dmg 16)
6. Dagger (dmg 4)
7. Mage Staff (dmg 14)
```

## Add a New Weapon

### Copy Template
```python
{
    'name': 'Your Weapon',
    'glyph_index': 8,
    'damage': 12,
    'stamina_use': 7,
    'attack_speed': 1.3,
    'range': 1,
    'area': 1,
    'angle': 0,
},
```

### Edit Values
- Increase `damage` for stronger
- Increase `attack_speed` for slower
- Increase `stamina_use` for more expensive
- Increase `range` for ranged attacks
- Increase `area` for bigger explosions
- Increase `angle` for wider sweeps

### Save & Done!
No other files need editing.

## Balancing Tips

### Fast Weapons (0.6-0.8s)
- Example: Dagger
- Low damage (4)
- Low cost (2)
- Good for rapid attacks

### Normal Weapons (1.0-1.5s)
- Example: Iron Sword
- Medium damage (10)
- Medium cost (5)
- Good for balanced play

### Slow Weapons (2.0-3.5s)
- Example: War Hammer
- High damage (16)
- High cost (10)
- Good for burst damage

### Melee vs Ranged
- Melee (range=0): Adjacent only
- Ranged (range=2-7): Distance attacks
- Ranged typically lower damage

### Single vs AoE
- Single (angle=0): Precise hits
- Arc (angle=45-90): Multiple targets
- Circle (angle=360): Explosion

## Parameter Interactions

### Damage vs Speed
- Higher damage ? typically slower
- Lower damage ? typically faster

### Damage vs Cost
- Higher damage ? more expensive
- Lower damage ? cheaper

### Ranged vs Damage
- Longer range ? lower damage
- Shorter range ? higher damage

### AoE vs Efficiency
- Larger area ? hit multiple
- Smaller area ? precise hits

## Example Weapons

### Balanced Sword
```python
{
    'name': 'Steel Sword',
    'glyph_index': 8,
    'damage': 11,
    'stamina_use': 5,
    'attack_speed': 1.1,
    'range': 0,
    'area': 1,
    'angle': 0,
}
```

### Fast Dagger
```python
{
    'name': 'Silver Dagger',
    'glyph_index': 9,
    'damage': 5,
    'stamina_use': 2,
    'attack_speed': 0.65,
    'range': 0,
    'area': 1,
    'angle': 0,
}
```

### Ranged Spear
```python
{
    'name': 'Javelin',
    'glyph_index': 10,
    'damage': 9,
    'stamina_use': 4,
    'attack_speed': 1.0,
    'range': 4,
    'area': 1,
    'angle': 0,
}
```

### AoE Explosion
```python
{
    'name': 'Lightning Staff',
    'glyph_index': 11,
    'damage': 16,
    'stamina_use': 14,
    'attack_speed': 2.5,
    'range': 4,
    'area': 2,
    'angle': 360,
}
```

## Common Mistakes to Avoid

### ? Too Strong
```python
{
    'damage': 50,         # Way too high!
    'stamina_use': 1,     # Way too cheap!
    'attack_speed': 0.3,  # Way too fast!
}
```

### ? Unbalanced
```python
{
    'damage': 20,
    'stamina_use': 2,  # Should be 15-20!
}
```

### ? Balanced
```python
{
    'damage': 12,
    'stamina_use': 6,  # Proportional
    'attack_speed': 1.3,  # Appropriate
}
```

## Weapon Array Format

```python
WEAPONS = [
    {  # Weapon 0
        'name': '...',
        'glyph_index': 0,
        'damage': ...,
        'stamina_use': ...,
        'attack_speed': ...,
        'range': ...,
        'area': ...,
        'angle': ...,
    },
    {  # Weapon 1
        ...
    },
    # ... more weapons
]
```

## Helper Functions

### get_weapon_by_name(name) ? dict
```python
weapon = get_weapon_by_name("Iron Sword")
# Returns weapon dict or None
```

### get_weapon_by_index(index) ? dict
```python
weapon = get_weapon_by_index(0)
# Returns weapon dict or None (if out of range)
```

### get_all_weapons() ? list
```python
weapons = get_all_weapons()
# Returns list of all weapon dicts (copies)
```

## Notes

- Helper functions return **copies**, not references
- Safe to modify returned weapons
- Doesn't affect WEAPONS array
- Index 0 = first weapon (Wooden Sword)

## File Size

- ~400 lines with documentation
- ~150 lines without documentation
- Easy to parse
- Quick to load

## Maintenance

### Monthly
- Review weapon balance
- Check player feedback
- Tweak parameters as needed
- Save and test

### Per Update
- Add new weapons
- Remove unused weapons
- Modify stats
- Commit changes

## Tips & Tricks

### Quick Duplicate
```python
# Copy an existing weapon
iron_sword = get_weapon_by_name("Iron Sword")
iron_sword['name'] = "Enhanced Iron Sword"
iron_sword['damage'] = 12  # Increased
# Add to WEAPONS array
```

### Compare Weapons
```python
sword = get_weapon_by_name("Iron Sword")
hammer = get_weapon_by_name("War Hammer")

print(f"Sword DPS: {sword['damage'] / sword['attack_speed']}")
print(f"Hammer DPS: {hammer['damage'] / hammer['attack_speed']}")
```

### List All
```python
for w in get_all_weapons():
    print(f"{w['name']}: dmg={w['damage']}, cost={w['stamina_use']}")
```

## Summary

- **What**: Weapon definitions file
- **Where**: weapons_data.py
- **How**: Edit WEAPONS array
- **When**: Anytime
- **Why**: Easy weapon management
- **Status**: Ready to use!

Enjoy adding weapons! ??
