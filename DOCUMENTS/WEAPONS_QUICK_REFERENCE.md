# Weapons System - Quick Reference

## What Was Added

A complete **8-parameter weapon system** that supports:
- Multiple weapon types with different stats
- Attack speed limiting (cooldown between attacks)
- Stamina-based resource management
- Ranged and melee attacks
- Single-target and area-of-effect attacks
- Cone/arc attacks with customizable angles
- Full collision detection and damage calculation

## The 8 Weapon Parameters

```python
{
    'name': str,           # Display name
    'glyph_index': int,    # Tileset character index
    'damage': int,         # HP dealt per hit
    'stamina_use': int,    # Stamina consumed per attack
    'attack_speed': float, # Cooldown between attacks (seconds)
    'range': int,          # How far weapon reaches (0=melee)
    'area': int,           # Explosion radius (1=single tile)
    'angle': int,          # Arc spread in degrees (0=straight, 360=circle)
}
```

## Example Weapons

### Melee Weapons
- **Dagger**: Fast (0.6s), low damage (4), cheap (2 stamina)
- **Wooden Sword**: Standard (1.0s), moderate (5), balanced (3 stamina)
- **Iron Sword**: Slower (1.2s), stronger (10), higher cost (5 stamina)
- **Broad Axe**: Slow (2.0s), heavy (15), AoE 90° (8 stamina)
- **War Hammer**: Very slow (2.5s), very strong (16), AoE 180° (10 stamina)

### Ranged Weapons
- **Short Spear**: Range 2, melee damage (8), 1.0s cooldown
- **Long Spear**: Range 3, higher damage (12), 1.5s cooldown
- **Mage Staff**: Range 5, circular explosion (360°), high cost (12 stamina)

## How Attack Speed Works

Attack speed = cooldown between attacks in seconds

```
attack_speed: 0.6  ? Can attack every 0.6s (1.67 attacks/sec)
attack_speed: 1.0  ? Can attack every 1.0s (1.0 attacks/sec)
attack_speed: 1.5  ? Can attack every 1.5s (0.67 attacks/sec)
attack_speed: 2.0  ? Can attack every 2.0s (0.5 attacks/sec)
```

## How Range Works

Range = how far the attack can reach from the player

```
range: 0 ? Melee only (adjacent square)
range: 1 ? Can reach 1 square away
range: 2 ? Can reach 2 squares away
range: 3 ? Can reach 3 squares away
range: 5 ? Long-range attack (like magic)
```

## How Area Works

Area = size of the explosion/AoE from impact point

```
area: 1 ? Single target only
area: 2 ? 2-square radius explosion
area: 3 ? 3-square radius explosion
```

## How Angle Works

Angle = cone/arc width of the attack in degrees

```
angle: 0    ? Straight line (no spread)
angle: 45   ? 45° cone (tight arc)
angle: 90   ? 90° cone (wide swing)
angle: 180  ? 180° semicircle (half-circle)
angle: 360  ? Full circle (explosion in all directions)
```

## Combat Examples

### Example 1: Wooden Sword Attack
```
damage: 5, stamina_use: 3
range: 0, area: 1, angle: 0

Effect: Hits 1 square directly in front
Damage: 5 HP to one target
```

### Example 2: Broad Axe Attack
```
damage: 15, stamina_use: 8
range: 0, area: 2, angle: 90

Effect: Wide 90° swing in melee range
        Hits 2 squares wide
Damage: 15 HP to multiple targets in arc
```

### Example 3: Mage Staff Attack
```
damage: 14, stamina_use: 12
range: 5, area: 2, angle: 360

Effect: Fire magic that travels 5 squares
        Explodes in circular area (2 radius)
        Hits everything in the explosion
Damage: 14 HP to all targets in circle
```

## Weapon Selection

- **Press 1-8** to equip/unequip weapons in hotbar
- **Selected weapon** shows damage/stats in HUD
- **Can switch** weapons mid-combat

## Strategy Tips

### Against Single Strong Enemy
- Use **Dagger** (fast) or **Long Spear** (ranged)
- Hit multiple times or stay at distance

### Against Monster Swarms
- Use **Broad Axe** or **War Hammer** (AoE)
- Hit multiple enemies at once

### Balanced Approach
- Use **Iron Sword** or **Wooden Sword**
- Good damage, fast attacks, reasonable stamina cost

### Ranged Combat
- Use **Long Spear** or **Mage Staff**
- Attack from safe distance

## File Structure

The weapons system is implemented in:
- **RLDungeonGenerator.py**: 
  - `WEAPONS` array - weapon definitions
  - `get_attack_tiles()` - calculate affected tiles
  - `swing_weapon()` - execute attack
  - `get_weapon_info_string()` - display weapon stats
  - `last_attack_time` - track attack cooldown

- **WEAPONS_SYSTEM.md** - full documentation (this file parent)

## Adding New Weapons

Add to the `WEAPONS` array in RLDungeonGenerator.py:

```python
WEAPONS = [
    # ...existing weapons...
    {
        'name': 'Flaming Sword',
        'glyph_index': 9,
        'damage': 12,
        'stamina_use': 6,
        'attack_speed': 1.1,
        'range': 0,
        'area': 1,
        'angle': 0,
    },
]
```

The system will automatically:
- Allow equipping it (1-8 keys)
- Track attack speed
- Calculate stamina cost
- Display weapon info
- Calculate damage and hit detection

## Code Integration Points

### Using Attack Tiles in Effects
```python
affected_tiles = self.get_attack_tiles(
    player_row, player_col,
    facing_row, facing_col,
    weapon
)
```

### Checking Equipment
```python
item = self.inventory[0][self.equipped_slot]
if item and item.get('type') == 'weapon':
    weapon = item
    damage = weapon.get('damage')
```

### Getting Weapon Info
```python
info_string = self.get_weapon_info_string()
# Output: "Iron Sword | DMG:10 | Speed:1.2s | Cost:5 | Melee | Single"
```

## Future Enhancements

- [ ] Weapon drops on monster death
- [ ] Weapon upgrades/enchantments
- [ ] Weapon durability system
- [ ] Special weapon abilities
- [ ] Status effects (poison, stun, burn)
- [ ] Unique legendary weapons
- [ ] Weapon crafting system
- [ ] Different attack patterns (thrust vs swing)

---

**Last Updated**: When weapons system was implemented
**Compatible With**: RLDungeonGenerator with BearLibTerminal support
