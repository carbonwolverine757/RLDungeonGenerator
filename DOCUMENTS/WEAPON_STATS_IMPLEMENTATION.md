# Weapon Stats and Glyph Implementation

## Summary of Changes

### 1. Weapon Data Structure (weapons_data.py)

Changed from `glyph_index` to `glyph_codepoint` for direct Unicode rendering:

**Before:**
```python
{
    'name': 'Iron Sword',
    'glyph_index': 1,
    'damage': 10,
    ...
}
```

**After:**
```python
{
    'name': 'Iron Sword',
    'glyph_codepoint': 0x2192,  # Rightwards arrow
    'damage': 10,
    ...
}
```

### 2. Weapon Glyphs

Each weapon now has a unique Unicode symbol that reflects its function:

| Weapon | Glyph | Codepoint | Description |
|--------|-------|-----------|-------------|
| Dagger | ? | 0x2191 | Upwards arrow (fast strike) |
| Wooden Sword | ? | 0x2197 | North East arrow (slash) |
| Iron Sword | ? | 0x2192 | Rightwards arrow (thrust) |
| Broad Axe | ? | 0x2715 | Multiplication X (wide swing) |
| Short Spear | ? | 0x2191 | Upwards arrow (spear thrust) |
| Long Spear | ? | 0x21E1 | Upwards dashed arrow (long reach) |
| War Hammer | ? | 0x25A0 | Black square (heavy impact) |
| Mage Staff | ? | 0x2731 | Heavy asterisk (magical burst) |

### 3. Weapon Combat Stats

Each weapon now has differentiated stats that affect gameplay:

**Damage**
- Dagger: 4 (lowest, but fast)
- Wooden Sword: 5 (starter weapon)
- Short Spear: 8 (melee range attack)
- Iron Sword: 10 (balanced)
- Long Spear: 12 (extended reach)
- Mage Staff: 14 (ranged magic)
- Broad Axe: 15 (heavy melee)
- War Hammer: 16 (highest, slowest)

**Stamina Cost**
- Dagger: 2 (cheap, spam-friendly)
- Wooden Sword: 3 (affordable)
- Short Spear: 4 (low-mid cost)
- Iron Sword: 5 (balanced)
- Long Spear: 6 (mid cost)
- Broad Axe: 8 (expensive)
- Mage Staff: 12 (very expensive)
- War Hammer: 10 (heavy)

**Attack Speed (cooldown in seconds)**
- Dagger: 0.6 (fastest, 1.67 attacks/sec)
- Wooden Sword: 1.0 (1 attack/sec)
- Short Spear: 1.0 (1 attack/sec)
- Iron Sword: 1.2 (0.83 attacks/sec)
- Long Spear: 1.5 (0.67 attacks/sec)
- Mage Staff: 2.0 (0.5 attacks/sec)
- Broad Axe: 2.0 (0.5 attacks/sec)
- War Hammer: 2.5 (0.4 attacks/sec)

**Range (distance)**
- Melee weapons: 0 (adjacent only)
- Short Spear: 2 (2 tiles away)
- Long Spear: 3 (3 tiles away)
- Mage Staff: 5 (5 tiles away)

### 4. Updated swing_weapon() Method

The attack system now:

1. **Uses actual weapon stats** from the weapon dictionary
2. **Respects attack cooldowns** based on `attack_speed`
3. **Applies weapon damage** instead of fixed 5 damage
4. **Requires weapon-specific stamina** instead of fixed 3
5. **Supports weapon range** - can hit targets up to `range` tiles away
6. **Stops at walls** - respects dungeon geometry
7. **Stops after first hit** - doesn't pass through enemies

### 5. Rendering Updates

Weapon display updated in multiple places:

- **Hotbar**: Shows weapon's `glyph_codepoint` with colored highlighting for equipped weapons
- **Ground items**: Displays weapon glyphs in dungeon so players can see loot
- **Inventory screen**: Shows weapon glyphs instead of generic sword emoji
- **Inventory summary**: Uses weapon glyphs with count for each weapon type

### 6. Weapon Balance

The weapon progression follows a clear trade-off pattern:

- **Fast & Cheap**: Dagger (low damage, low cost, fast)
- **Balanced**: Wooden Sword, Iron Sword (medium stats)
- **Ranged**: Spears (can hit from distance)
- **Magic**: Mage Staff (long range, expensive)
- **Heavy**: Broad Axe, War Hammer (high damage, slow, expensive)

## Testing Notes

? Each weapon now has distinct stats
? Weapon glyphs are visible Unicode symbols (not blank tiles)
? Attack speed cooldown is enforced per weapon
? Stamina cost varies by weapon
? Damage varies significantly by weapon
? Range attacks work up to specified distance
? Hotbar displays weapon glyphs correctly
? Ground loot displays weapon glyphs

## Future Enhancements

- Add AoE damage calculation for Broad Axe and War Hammer
- Add angle/cone attack patterns
- Add critical strike chance
- Add elemental effects to weapons
- Implement weapon durability
- Add weapon enchantments
