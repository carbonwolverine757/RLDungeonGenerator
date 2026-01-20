# Weapons System Documentation

## Overview
The weapons system provides a flexible framework for defining different weapons with varied characteristics. Each weapon has 8 parameters that define its behavior in combat.

## Weapon Parameters

### 1. **name** (string)
The display name of the weapon.
- Example: "Iron Sword", "War Hammer", "Mage Staff"

### 2. **glyph_index** (integer)
Index into the tileset for the weapon's visual representation.
- Used to render the weapon in inventory and on ground
- Can be customized later with actual tileset positions

### 3. **damage** (integer)
Amount of HP dealt to enemies per hit.
- Wooden Sword: 5
- Iron Sword: 10
- War Hammer: 16

### 4. **stamina_use** (integer)
How much stamina is consumed per attack.
- Dagger: 2 (cheap)
- Wooden Sword: 3
- Mage Staff: 12 (expensive)

### 5. **attack_speed** (float)
Cooldown between attacks in seconds.
- Dagger: 0.6 (very fast, multiple attacks per second)
- Wooden Sword: 1.0 (once per second)
- War Hammer: 2.5 (slow, powerful attacks)

Formula: `time_since_last_attack >= attack_speed` to allow next attack

### 6. **range** (integer)
How far away from the player the attack can reach.
- 0 = melee only (adjacent square)
- 1 = can reach 1 square away
- 2 = can reach 2 squares away
- 3+ = ranged weapons (spears, staves)

Examples:
- Sword: 0 (melee)
- Short Spear: 2
- Long Spear: 3
- Mage Staff: 5

### 7. **area** (integer)
How many squares the attack spreads outward from the impact point.
- 1 = single target only
- 2 = 2 squares outward from center
- 3+ = larger area of effect

Examples:
- Dagger: 1 (pinpoint)
- Broad Axe: 2 (swings hit nearby)
- War Hammer: 2 (crushes area)
- Mage Staff: 2 (explosion)

### 8. **angle** (integer, degrees)
The spread angle of the attack.
- 0 = single direction (straight line)
- 10-90 = arc/cone attacks
- 180 = half circle
- 360 = full circle (explosion)

Examples:
- Sword: 0 (single target)
- Broad Axe: 90 (90° arc - wide swing)
- War Hammer: 180 (180° arc - crushing half-circle)
- Mage Staff: 360 (360° circle - magic explosion)

## Weapon Examples

### Melee Weapons

**Wooden Sword** (Starter)
```
damage: 5, stamina_use: 3, attack_speed: 1.0
range: 0, area: 1, angle: 0
```
- Basic melee attack, single target
- Once per second, costs 3 stamina

**Broad Axe** (AoE Melee)
```
damage: 15, stamina_use: 8, attack_speed: 2.0
range: 0, area: 2, angle: 90
```
- Hits in a 90° arc, 2 squares wide
- Slow heavy attack, costs 8 stamina

**War Hammer** (Heavy AoE)
```
damage: 16, stamina_use: 10, attack_speed: 2.5
range: 0, area: 2, angle: 180
```
- Hits in a 180° half-circle (wide swing)
- Very slow but very powerful

### Ranged Weapons

**Short Spear** (Close Range)
```
damage: 8, stamina_use: 4, attack_speed: 1.0
range: 2, area: 1, angle: 0
```
- Can reach 2 squares away
- Single target, medium speed

**Long Spear** (Extended Range)
```
damage: 12, stamina_use: 6, attack_speed: 1.5
range: 3, area: 1, angle: 0
```
- Can reach 3 squares away
- Single target, slower

**Mage Staff** (Explosion)
```
damage: 14, stamina_use: 12, attack_speed: 2.0
range: 5, area: 2, angle: 360
```
- Can reach 5 squares away
- Explodes in a circle when it hits
- Very expensive in stamina

### Fast Weapon

**Dagger** (Attack Speed)
```
damage: 4, stamina_use: 2, attack_speed: 0.6
range: 0, area: 1, angle: 0
```
- Can attack every 0.6 seconds (very fast)
- Low damage but cheap, good for hit-and-run

## Weapon Selection System

### Equipping Weapons
- Press number keys 1-8 to equip/unequip weapons in hotbar
- Only weapons in the hotbar can be equipped
- Currently equipped weapon shows damage/stamina in HUD

### Switching Weapons
- Currently equipped weapon shows bright highlight in hotbar
- Press the same key again to unequip
- Can switch mid-combat for strategy

### Future Expansion
- Add weapon drop system on monster death
- Add weapon upgrades (enchantments)
- Add weapon durability
- Add special weapon abilities

## Attack Calculation System

### Attack Tiles Algorithm

1. **Single Target (angle=0)**
   - Hits one square along the attack direction
   - Up to `range` squares away from player

2. **Arc/Cone (0 < angle < 360)**
   - Spreads in a cone up to `angle` degrees wide
   - Hits all tiles within the arc
   - Extends `area` squares from the impact point

3. **Circle (angle=360)**
   - Hits all tiles in a circle of radius `area`
   - Centered on the attack direction endpoint
   - Ignores angle parameter

### Collision Detection
- Affected tiles must be:
  - Within the dungeon bounds
  - Within range + area distance
  - Within the angle spread (if applicable)
  - Not already in the affected list (no duplicates)

## Balancing Considerations

### Fast vs Slow
- Fast weapons (0.6s): 2-4 attacks/second, low damage, cheap
- Medium weapons (1.0s): 1 attack/second, medium damage
- Slow weapons (2.0s+): high damage, expensive, devastating

### Ranged vs Melee
- Melee (range=0): safer, no positioning required
- Ranged (range=2+): requires positioning, less damage per stamina

### Single vs AoE
- Single target: high damage efficiency
- AoE (area=2+): damage spread across multiple targets

### Example Strategy
- **Swarm fighting**: Dagger or Broad Axe for AoE
- **Boss fighting**: War Hammer for burst damage
- **Kiting**: Long Spear to attack from distance
- **Balanced**: Iron Sword for reliable damage

## Implementation Details

### Attack Speed Calculation
```python
if (time_since_last_attack >= weapon.attack_speed):
    allow_attack = True
```

### Stamina Cost
```python
player_stamina -= weapon.stamina_use
stamina_cooldown_until = now + 1.0  # 1 second before regen starts
```

### Damage Application
```python
for each_monster_in_affected_tiles:
    monster.health -= weapon.damage
    if monster.health <= 0:
        remove_monster()
        drop_coins()
```

## Future Enhancement Ideas

1. **Status Effects**
   - Poison (damage over time)
   - Stun (prevent movement)
   - Slow (reduce attack speed)
   - Burn (damage per turn)

2. **Weapon Upgrades**
   - Increase damage (+5 per level)
   - Reduce cooldown (-0.2s per level)
   - Reduce stamina (-1 per level)
   - Add special abilities (lifesteal, knockback)

3. **Weapon Types**
   - Swords (balanced)
   - Axes (AoE)
   - Spears (ranged)
   - Staves (magic)
   - Bows (precise ranged)
   - Whips (extended reach)

4. **Unique Weapons**
   - Legendary items with special properties
   - Rare drops from bosses
   - Quest rewards
   - Craft-able items

## Code Usage

### Get Attack Tiles
```python
affected_tiles = dg.get_attack_tiles(
    player_row, player_col,
    facing_row, facing_col,
    weapon
)
```

### Apply Attack
```python
for tile_r, tile_c in affected_tiles:
    # Check for monsters at tile
    # Apply damage
    # Apply effects
```

### Get Weapon Info
```python
info = dg.get_weapon_info_string()
# Returns: "Iron Sword | DMG:10 | Speed:1.2s | Cost:5 | Melee | Single"
```

---

## Current Weapons List

| Name | DMG | Stamina | Speed | Range | Area | Angle | Notes |
|------|-----|---------|-------|-------|------|-------|-------|
| Wooden Sword | 5 | 3 | 1.0s | 0 | 1 | 0° | Starter weapon |
| Iron Sword | 10 | 5 | 1.2s | 0 | 1 | 0° | Balanced upgrade |
| Broad Axe | 15 | 8 | 2.0s | 0 | 2 | 90° | AoE melee |
| Short Spear | 8 | 4 | 1.0s | 2 | 1 | 0° | Close range |
| Long Spear | 12 | 6 | 1.5s | 3 | 1 | 0° | Extended range |
| War Hammer | 16 | 10 | 2.5s | 0 | 2 | 180° | Heavy AoE |
| Dagger | 4 | 2 | 0.6s | 0 | 1 | 0° | Fast attack |
| Mage Staff | 14 | 12 | 2.0s | 5 | 2 | 360° | Magic explosion |

---

## Customization

To add a new weapon, add it to the WEAPONS array:

```python
{
    'name': 'Your Weapon',
    'glyph_index': 8,
    'damage': 10,
    'stamina_use': 5,
    'attack_speed': 1.2,
    'range': 1,
    'area': 1,
    'angle': 45,
},
```

Then the system will automatically support it for equipping, displaying, and attacking!
