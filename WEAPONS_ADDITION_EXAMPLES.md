# Weapons Data - Example Extensions

This document shows how to easily add new weapons to the weapons_data.py file.

## Quick Addition Examples

### 1. Flaming Sword (Fire Weapon)
```python
{
    'name': 'Flaming Sword',
    'glyph_index': 8,
    'damage': 12,
    'stamina_use': 7,
    'attack_speed': 1.1,
    'range': 0,
    'area': 1,
    'angle': 0,
}
```
- Stronger than Iron Sword (12 vs 10)
- Slightly slower (1.1s vs 1.2s)
- Higher stamina cost (7 vs 5)
- Single target melee
- Good balanced upgrade

### 2. Sniper Bow (Precision Ranged)
```python
{
    'name': 'Sniper Bow',
    'glyph_index': 9,
    'damage': 18,
    'stamina_use': 6,
    'attack_speed': 1.8,
    'range': 7,
    'area': 1,
    'angle': 0,
}
```
- Highest single damage (18)
- Long range (7 squares)
- Slow attack (1.8s)
- Single target precision
- Best for ranged solo targets

### 3. Whip (Extended Reach Melee)
```python
{
    'name': 'Whip',
    'glyph_index': 10,
    'damage': 7,
    'stamina_use': 5,
    'attack_speed': 0.8,
    'range': 2,
    'area': 1,
    'angle': 0,
}
```
- Melee with reach (range=2)
- Fast attacks (0.8s)
- Moderate damage (7)
- Good for hit-and-run
- Better than spears for speed

### 4. Scythe (AoE Melee)
```python
{
    'name': 'Scythe',
    'glyph_index': 11,
    'damage': 13,
    'stamina_use': 9,
    'attack_speed': 1.8,
    'range': 0,
    'area': 2,
    'angle': 120,
}
```
- 120° arc attack (wider than Broad Axe's 90°)
- Moderate damage (13)
- Heavy stamina cost (9)
- Good for crowds
- Slower than Broad Axe (1.8s vs 2.0s) - faster but less damage

### 5. Chain Mail Whip (AoE Ranged)
```python
{
    'name': 'Chain Mail Whip',
    'glyph_index': 12,
    'damage': 11,
    'stamina_use': 8,
    'attack_speed': 2.0,
    'range': 3,
    'area': 2,
    'angle': 90,
}
```
- Ranged whip (range=3)
- AoE in 90° arc
- Combo ranged + AoE
- Heavy stamina (8)
- Slower (2.0s)

### 6. Holy Light (Instant Heal Weapon)
```python
{
    'name': 'Holy Staff',
    'glyph_index': 13,
    'damage': 8,
    'stamina_use': 15,
    'attack_speed': 3.0,
    'range': 4,
    'area': 3,
    'angle': 360,
}
```
- Large circular AoE (area=3)
- Long range (4)
- Heals on hit (custom effect)
- Very expensive (15 stamina)
- Very slow (3.0s)
- Support weapon

### 7. Crossbow (Burst Weapon)
```python
{
    'name': 'Crossbow',
    'glyph_index': 14,
    'damage': 9,
    'stamina_use': 4,
    'attack_speed': 0.7,
    'range': 6,
    'area': 1,
    'angle': 0,
}
```
- Very fast (0.7s, second only to Dagger at 0.6s)
- Long range (6)
- Moderate damage (9)
- Low stamina (4)
- Good DPS at range

### 8. Meteor Staff (Ultimate Magic)
```python
{
    'name': 'Meteor Staff',
    'glyph_index': 15,
    'damage': 20,
    'stamina_use': 18,
    'attack_speed': 3.5,
    'range': 6,
    'area': 3,
    'angle': 360,
}
```
- Highest damage (20)
- Huge AoE (area=3, angle=360)
- Very expensive (18 stamina)
- Very slow (3.5s)
- Ultimate weapon

## Parameter Ranges for Balancing

### Damage Guidelines
```
Low:     4-6   (Dagger: 4, Wooden Sword: 5)
Medium:  8-12  (Swords: 10, Spears: 8-12)
High:    14-16 (Axe: 15, Hammer: 16)
Extreme: 18-20 (Sniper: 18, Meteor: 20)
```

### Stamina Cost Guidelines
```
Cheap:    2-4   (Dagger: 2, Spear: 4)
Medium:   5-8   (Swords: 5, Axe: 8)
Expensive: 10-12 (Hammer: 10, Staff: 12)
Ultimate: 15-18 (Support/Meteor: 15-18)
```

### Attack Speed Guidelines
```
Fast:     0.6-0.8  (Dagger: 0.6, Crossbow: 0.7)
Normal:   1.0-1.5  (Swords: 1.0-1.2, Spears: 1.0-1.5)
Slow:     1.8-2.0  (Axe: 2.0, Whip: 1.8)
V.Slow:   2.5-3.5  (Hammer: 2.5, Meteor: 3.5)
```

### Range Guidelines
```
Melee:    0      (Swords, Axes, Hammers)
Close:    1-2    (Whips: 2)
Medium:   2-3    (Spears: 2-3)
Long:     4-6    (Bows, Magic: 4-7)
Ultimate: 6-7    (Sniper: 7, Meteor: 6)
```

### Area Guidelines
```
Single:   1      (Most weapons)
Small:    2      (Axe, Hammer, Staff: 2)
Medium:   3      (Holy Staff, Meteor: 3)
Large:    4+     (Future expansions)
```

### Angle Guidelines
```
Straight: 0      (Swords, Spears, Bows)
Cone:     45-90  (Broad Axe: 90°)
Wide:     120-180 (Scythe: 120°, Hammer: 180°)
Circle:   360    (Staves, Meteor: 360°)
```

## How to Add to weapons_data.py

1. Open `weapons_data.py`
2. Find the `WEAPONS = [` array
3. Add before the closing `]`:

```python
    {
        'name': 'Your Weapon Name',
        'glyph_index': X,        # Use next available (8+)
        'damage': Y,
        'stamina_use': Z,
        'attack_speed': A.B,
        'range': C,
        'area': D,
        'angle': E,
    },
```

4. Save file
5. System automatically supports new weapon!

## Complete Example: Adding a Plasma Blade

Let's say we want a fast, high-damage melee weapon:

### Decision
- Fast attacks (0.7s) like Crossbow
- High damage (14) like Mage Staff
- Moderate stamina (7)
- Single target melee
- Slight arc attack (45°)

### Add to weapons_data.py
```python
    {
        'name': 'Plasma Blade',
        'glyph_index': 16,
        'damage': 14,
        'stamina_use': 7,
        'attack_speed': 0.7,
        'range': 0,
        'area': 1,
        'angle': 45,
    },
```

### Result
- Second fastest weapon after Dagger
- High damage for speed
- Costs moderate stamina
- Small cone attack (45°)
- Can hit 2 targets in close range
- Good for aggressive combat

### Usage
```python
# In game, player can equip:
weapon = get_weapon_by_name("Plasma Blade")

# Or access by index (if added at position 15):
weapon = get_weapon_by_index(15)

# Stats would be:
# - Damage: 14
# - Cost: 7 stamina
# - Speed: 0.7s cooldown
# - Range: Melee only
# - Hits in 45° cone
```

## Testing New Weapons

### Quick Balance Check

For any new weapon:
1. **Damage vs Speed**: Higher damage = slower typically
2. **Stamina vs Damage**: Higher damage = higher cost typically
3. **Range vs Damage**: Ranged weapons often lower damage
4. **AoE vs Single**: AoE trades precision for coverage

### Example Imbalance Tests

**Too Strong:**
```python
{
    'name': 'Broken Sword',
    'damage': 25,        # Too high!
    'stamina_use': 2,    # Too cheap!
    'attack_speed': 0.5, # Too fast!
    # Result: Overpowered
}
```

**Too Weak:**
```python
{
    'name': 'Useless Stick',
    'damage': 1,
    'stamina_use': 20,
    'attack_speed': 3.0,
    # Result: Never use this
}
```

**Balanced:**
```python
{
    'name': 'Good Weapon',
    'damage': 12,        # Medium-high
    'stamina_use': 6,    # Proportional cost
    'attack_speed': 1.4, # Proportional speed
    # Result: Viable choice
}
```

## Weapon Tier System

### Tier 1: Starter
- Damage: 4-6
- Cost: 2-4
- Speed: 0.6-1.0
- Example: Dagger, Wooden Sword

### Tier 2: Common
- Damage: 8-10
- Cost: 4-6
- Speed: 0.8-1.2
- Example: Iron Sword, Short Spear

### Tier 3: Uncommon
- Damage: 12-14
- Cost: 6-8
- Speed: 1.2-1.8
- Example: Long Spear, Mage Staff

### Tier 4: Rare
- Damage: 15-18
- Cost: 8-12
- Speed: 1.8-2.5
- Example: Broad Axe, War Hammer, Sniper Bow

### Tier 5: Legendary
- Damage: 20+
- Cost: 12+
- Speed: 2.5+
- Example: Meteor Staff, Plasma Blade

## Summary

Adding weapons is as simple as:
1. Add entry to WEAPONS array
2. Set 8 parameters
3. Save file
4. Done!

No code changes needed. System handles everything automatically.

The example weapons above show various strategies:
- Fast vs Slow
- Melee vs Ranged
- Single vs AoE
- Low vs High cost

Mix and match to create your weapon arsenal!
