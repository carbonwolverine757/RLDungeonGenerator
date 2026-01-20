# Weapons System - Complete Documentation Index

## Quick Navigation

### For New Users
1. **[WEAPONS_QUICK_REFERENCE.md](WEAPONS_QUICK_REFERENCE.md)** - 5-minute overview
2. **[WEAPONS_VISUAL_GUIDE.md](WEAPONS_VISUAL_GUIDE.md)** - See attack patterns
3. **[WEAPONS_CODE_EXAMPLES.md](WEAPONS_CODE_EXAMPLES.md)** - How to use in code

### For Developers
1. **[WEAPONS_SYSTEM.md](WEAPONS_SYSTEM.md)** - Full technical documentation
2. **[WEAPONS_CODE_EXAMPLES.md](WEAPONS_CODE_EXAMPLES.md)** - Complete code examples
3. **[WEAPONS_IMPLEMENTATION_SUMMARY.md](WEAPONS_IMPLEMENTATION_SUMMARY.md)** - What was built

### For Game Balance
1. **[WEAPONS_QUICK_REFERENCE.md](WEAPONS_QUICK_REFERENCE.md#strategy-tips)** - Combat strategies
2. **[WEAPONS_VISUAL_GUIDE.md](WEAPONS_VISUAL_GUIDE.md#damage-effectiveness)** - Weapon comparison

---

## File Descriptions

### WEAPONS_QUICK_REFERENCE.md
**Best for:** Fast lookup, quick decisions
- The 8 weapon parameters
- All 8 current weapons with stats
- Combat examples
- Strategy tips
- How to add new weapons

### WEAPONS_SYSTEM.md
**Best for:** Understanding the full system
- 100+ lines of detailed documentation
- Parameter explanations
- Weapon examples
- Balancing considerations
- Future enhancement ideas
- Implementation details

### WEAPONS_VISUAL_GUIDE.md
**Best for:** Seeing attack patterns
- ASCII art diagrams of attack patterns
- Attack type comparisons
- Damage effectiveness charts
- Decision tree for weapon selection
- Timeline comparisons
- Visual matrices

### WEAPONS_CODE_EXAMPLES.md
**Best for:** Learning how to use the code
- 200+ lines of code examples
- Weapon definition examples
- `get_attack_tiles()` usage
- `swing_weapon()` implementation
- Weapon stat checking
- Strategy algorithm examples

### WEAPONS_IMPLEMENTATION_SUMMARY.md
**Best for:** Understanding what was built
- What was implemented
- Core components overview
- Weapon types list
- Key features
- Integration points
- Testing checklist

---

## Features Implemented

### 8 Parameters Per Weapon
1. **name** - Display name
2. **glyph_index** - Tileset character
3. **damage** - HP dealt
4. **stamina_use** - Stamina cost
5. **attack_speed** - Cooldown (seconds)
6. **range** - Maximum reach
7. **area** - Explosion radius
8. **angle** - Arc width (degrees)

### 8 Weapons Included
1. Dagger (fast, cheap)
2. Wooden Sword (starter)
3. Iron Sword (balanced)
4. Broad Axe (AoE melee)
5. Short Spear (close ranged)
6. Long Spear (extended ranged)
7. War Hammer (heavy AoE)
8. Mage Staff (magic explosion)

### Attack Types Supported
- Single-target attacks (angle=0)
- Arc/cone attacks (0 < angle < 360)
- Circular explosions (angle=360)
- Ranged attacks (range > 0)
- Melee attacks (range=0)
- Area effects (area > 1)

---

## Quick Start

### For Players
1. Press **1-8** to equip weapons in hotbar
2. Click or press space to attack
3. Different weapons have different effects:
   - Fast weapons (Dagger): 0.6s cooldown
   - Balanced (Iron Sword): 1.0s cooldown
   - Slow weapons (War Hammer): 2.5s cooldown

### For Developers
1. Look at `WEAPONS` array in RLDungeonGenerator.py
2. Add new weapon to array
3. System automatically supports it
4. Check `get_attack_tiles()` for geometry
5. Use `swing_weapon()` for attacks

### For Modders
1. Copy weapon array entry
2. Modify 8 parameters
3. Test in game
4. Add more weapons as needed
5. No code changes needed!

---

## Common Questions

### Q: How do I add a new weapon?
**A:** Add an entry to the `WEAPONS` array in RLDungeonGenerator.py:
```python
{
    'name': 'Your Weapon',
    'glyph_index': 8,
    'damage': 10,
    'stamina_use': 5,
    'attack_speed': 1.2,
    'range': 0,
    'area': 1,
    'angle': 0,
}
```

### Q: How do attack speeds work?
**A:** `attack_speed` is cooldown in seconds. Lower = faster.
- 0.6 = once every 0.6s (fast)
- 1.0 = once per second (normal)
- 2.5 = once every 2.5s (slow)

### Q: What does "area" do?
**A:** Size of explosion from impact point.
- area=1: single tile
- area=2: 2-tile radius
- area=3: 3-tile radius

### Q: What does "angle" do?
**A:** Width of attack spread in degrees.
- angle=0: straight line only
- angle=90: 90° arc
- angle=180: semicircle
- angle=360: full circle

### Q: Can I mix parameters?
**A:** Yes! Any combination works:
- Ranged + AoE (Mage Staff)
- Melee + AoE (Broad Axe)
- Fast + Low Damage (Dagger)
- Slow + High Damage (War Hammer)

---

## System Architecture

```
RLDungeonGenerator
??? WEAPONS array (8 weapons)
??? get_attack_tiles()
?   ??? Calculate range
?   ??? Calculate area
?   ??? Calculate angle
?   ??? Return affected tiles
??? swing_weapon()
?   ??? Check equipped weapon
?   ??? Check attack speed
?   ??? Check stamina
?   ??? Apply cooldown
?   ??? Get affected tiles
?   ??? Apply damage
?   ??? Apply effects
??? get_weapon_info_string()
    ??? Return formatted stats
```

---

## Integration Points

- **Inventory System**: Weapons stored in hotbar
- **Stamina System**: Attack cost and cooldown
- **Damage System**: Apply damage to monsters
- **Map System**: Destroy doors, drop coins
- **Time System**: Attack speed tracking

---

## Statistics

| Metric | Value |
|--------|-------|
| Weapons Included | 8 |
| Parameters Per Weapon | 8 |
| Code Files Modified | 1 |
| New Methods Added | 2 |
| Lines of Code | ~200 |
| Documentation Pages | 5 |
| Examples Provided | 20+ |
| Weapon Types Supported | 8 |
| Attack Geometries | 4 |

---

## Testing Checklist

- ? Weapon loading
- ? Attack speed cooldown
- ? Stamina deduction
- ? Damage application
- ? Single-target attacks
- ? AoE attacks
- ? Ranged attacks
- ? Circular attacks
- ? Arc attacks
- ? Door destruction
- ? Weapon switching
- ? Code compilation
- ? System integration

---

## Performance

- **Attack Tile Calculation**: O(range × area)
- **Damage Application**: O(affected_tiles × monsters)
- **Memory Usage**: Minimal (8 weapon dicts)
- **Overhead**: Negligible

---

## Future Enhancements

1. **Status Effects** - Poison, stun, burn, slow
2. **Weapon Upgrades** - Increase stats
3. **More Weapons** - Bows, whips, shields
4. **Weapon Drops** - Get weapons from monsters
5. **Weapon Crafting** - Create custom weapons
6. **Unique Weapons** - Legendary items
7. **Weapon Abilities** - Special moves
8. **Combo System** - Chained attacks

---

## Key Classes and Methods

### Weapon Object
```python
weapon = {
    'name': str,
    'glyph_index': int,
    'damage': int,
    'stamina_use': int,
    'attack_speed': float,
    'range': int,
    'area': int,
    'angle': int,
}
```

### get_attack_tiles()
```python
affected_tiles = dg.get_attack_tiles(
    center_row, center_col,
    direction_row, direction_col,
    weapon
)
# Returns: [(row, col), (row, col), ...]
```

### swing_weapon()
```python
dg.swing_weapon()
# Executes complete attack with weapon
```

### get_weapon_info_string()
```python
info = dg.get_weapon_info_string()
# Returns: "Iron Sword | DMG:10 | Speed:1.2s | Cost:5 | Melee | Single"
```

---

## Code Location

**Main implementation**: `RLDungeonGenerator.py`

- Line ~30: WEAPONS array definition
- Line ~180: Last attack time tracking
- Method `get_attack_tiles()`: Full attack geometry
- Method `swing_weapon()`: Attack execution
- Method `get_weapon_info_string()`: Display stats

---

## Support & Help

1. **For questions about parameters**: See WEAPONS_QUICK_REFERENCE.md
2. **For code examples**: See WEAPONS_CODE_EXAMPLES.md
3. **For visual understanding**: See WEAPONS_VISUAL_GUIDE.md
4. **For technical details**: See WEAPONS_SYSTEM.md
5. **For implementation**: See WEAPONS_IMPLEMENTATION_SUMMARY.md

---

## Summary

A complete, production-ready weapons system with:
- ? 8 configurable weapon parameters
- ? 8 pre-built weapons
- ? Attack speed limiting
- ? Stamina cost tracking
- ? Range and AoE support
- ? Angle-based arc attacks
- ? Complete documentation
- ? Code examples
- ? Visual guides

**Status**: Ready for gameplay and modification!

---

**Documentation Index Version**: 1.0
**Last Updated**: With weapons system implementation
**Next Review**: When new weapons added
