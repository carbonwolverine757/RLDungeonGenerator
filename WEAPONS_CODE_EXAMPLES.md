# Weapons System - Code Examples

## Overview

This guide shows how the weapons system works in code with concrete examples.

---

## 1. Weapon Definition

### Basic Structure

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
    # ... more weapons
]
```

### All Current Weapons

```python
WEAPONS = [
    # Melee starter
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
    
    # Balanced upgrade
    {
        'name': 'Iron Sword',
        'glyph_index': 1,
        'damage': 10,
        'stamina_use': 5,
        'attack_speed': 1.2,
        'range': 0,
        'area': 1,
        'angle': 0,
    },
    
    # Heavy AoE
    {
        'name': 'Broad Axe',
        'glyph_index': 2,
        'damage': 15,
        'stamina_use': 8,
        'attack_speed': 2.0,
        'range': 0,
        'area': 2,
        'angle': 90,
    },
    
    # Ranged melee
    {
        'name': 'Short Spear',
        'glyph_index': 3,
        'damage': 8,
        'stamina_use': 4,
        'attack_speed': 1.0,
        'range': 2,
        'area': 1,
        'angle': 0,
    },
    
    # Extended range
    {
        'name': 'Long Spear',
        'glyph_index': 4,
        'damage': 12,
        'stamina_use': 6,
        'attack_speed': 1.5,
        'range': 3,
        'area': 1,
        'angle': 0,
    },
    
    # Heavy AoE
    {
        'name': 'War Hammer',
        'glyph_index': 5,
        'damage': 16,
        'stamina_use': 10,
        'attack_speed': 2.5,
        'range': 0,
        'area': 2,
        'angle': 180,
    },
    
    # Fast attack
    {
        'name': 'Dagger',
        'glyph_index': 6,
        'damage': 4,
        'stamina_use': 2,
        'attack_speed': 0.6,
        'range': 0,
        'area': 1,
        'angle': 0,
    },
    
    # Magic AOE
    {
        'name': 'Mage Staff',
        'glyph_index': 7,
        'damage': 14,
        'stamina_use': 12,
        'attack_speed': 2.0,
        'range': 5,
        'area': 2,
        'angle': 360,
    },
]
```

---

## 2. Getting Attack Tiles

### Single Target Attack (Sword)

```python
# Player at (25, 40), facing northeast (1, 1)
affected_tiles = dg.get_attack_tiles(
    center_row=25, center_col=40,
    direction_row=1, direction_col=1,
    weapon=WEAPONS[0]  # Wooden Sword
)

# Result: [(26, 41)]  - One square in attack direction
```

### AoE Attack (Broad Axe)

```python
# Same position, Broad Axe with 90° angle
affected_tiles = dg.get_attack_tiles(
    center_row=25, center_col=40,
    direction_row=0, direction_col=1,  # Facing right
    weapon=WEAPONS[2]  # Broad Axe (area=2, angle=90)
)

# Result: Multiple tiles in 90° arc
# [(26, 40), (26, 41), (25, 41), (25, 42), ...]
```

### Ranged Attack (Long Spear)

```python
# Long Spear can reach 3 squares away
affected_tiles = dg.get_attack_tiles(
    center_row=25, center_col=40,
    direction_row=-1, direction_col=0,  # Facing up
    weapon=WEAPONS[4]  # Long Spear (range=3)
)

# Result: [(24, 40), (23, 40), (22, 40)]
# Hits 3 squares in the attack direction
```

### Explosion Attack (Mage Staff)

```python
# Mage Staff 360° explosion
affected_tiles = dg.get_attack_tiles(
    center_row=25, center_col=40,
    direction_row=1, direction_col=1,
    weapon=WEAPONS[7]  # Mage Staff (range=5, area=2, angle=360)
)

# Result: All tiles in 2-square radius circle
# Forms a circular explosion pattern
```

---

## 3. Attack Execution

### The swing_weapon() Method

```python
def swing_weapon(self):
    """Complete attack execution"""
    
    # 1. Get equipped weapon
    if self.equipped_slot is None:
        return
    
    item = self.inventory[0][self.equipped_slot]
    if item is None or item.get("type") != "weapon":
        return
    
    weapon = item
    now = time.time()
    
    # 2. Check attack speed cooldown
    attack_speed = weapon.get('attack_speed', 1.0)
    time_since_last_attack = now - self.last_attack_time
    
    if time_since_last_attack < attack_speed:
        return  # Still in cooldown
    
    # 3. Check stamina
    stamina_use = weapon.get('stamina_use', 3)
    if self.player_stamina < stamina_use:
        return  # Not enough stamina
    
    # 4. Apply cooldown and consume stamina
    self.player_stamina -= stamina_use
    self.stamina_cooldown_until = now + 1.0  # 1 second regen cooldown
    self.last_attack_time = now  # Update attack cooldown
    
    # 5. Calculate affected tiles
    affected_tiles = self.get_attack_tiles(
        self.player_row, self.player_col,
        self.facing[0], self.facing[1],
        weapon
    )
    
    # 6. Apply damage to each affected tile
    damage = weapon.get('damage', 5)
    
    for target_r, target_c in affected_tiles:
        ch = self.dungeon[target_r][target_c].get_ch()
        
        # Check for monsters
        for i, m in enumerate(list(self.monsters)):
            if m['row'] == target_r and m['col'] == target_c:
                m['health'] -= damage
                
                if m['health'] <= 0:
                    # Remove dead monster
                    self.monsters.pop(i)
                    # Drop coins
                    self.dungeon[target_r][target_c] = DungeonSqr('o')
                    self.explored[target_r][target_c] = True
        
        # Break doors
        if ch == '+':
            self.dungeon[target_r][target_c] = DungeonSqr('.')
```

---

## 4. Using Weapon Stats

### Check if Can Attack

```python
def can_attack(self):
    """Check if player can perform an attack"""
    if self.equipped_slot is None:
        return False
    
    item = self.inventory[0][self.equipped_slot]
    weapon = item
    
    # Check stamina
    stamina_use = weapon.get('stamina_use', 3)
    if self.player_stamina < stamina_use:
        print(f"Need {stamina_use} stamina, have {self.player_stamina}")
        return False
    
    # Check attack speed
    attack_speed = weapon.get('attack_speed', 1.0)
    time_since_last = time.time() - self.last_attack_time
    if time_since_last < attack_speed:
        print(f"Weapon ready in {attack_speed - time_since_last:.1f}s")
        return False
    
    return True
```

### Get Weapon Damage Range

```python
def get_damage_range(self):
    """Get damage and affected area of current weapon"""
    if self.equipped_slot is None:
        return None
    
    weapon = self.inventory[0][self.equipped_slot]
    
    return {
        'damage': weapon.get('damage'),
        'range': weapon.get('range'),
        'area': weapon.get('area'),
        'angle': weapon.get('angle'),
        'stamina_cost': weapon.get('stamina_use'),
        'attack_speed': weapon.get('attack_speed'),
    }
```

### Display Weapon Info

```python
def get_weapon_info_string(self):
    """Get formatted weapon info"""
    if self.equipped_slot is None:
        return "No weapon equipped"
    
    weapon = self.inventory[0][self.equipped_slot]
    
    name = weapon.get('name', 'Unknown')
    damage = weapon.get('damage', 0)
    attack_speed = weapon.get('attack_speed', 1.0)
    stamina_use = weapon.get('stamina_use', 0)
    weapon_range = weapon.get('range', 0)
    area = weapon.get('area', 1)
    angle = weapon.get('angle', 0)
    
    range_str = f"Range:{weapon_range}" if weapon_range > 0 else "Melee"
    area_str = f"Area:{area}" if area > 1 else "Single"
    angle_str = f"Angle:{angle}°" if angle > 0 else "Direct"
    
    return f"{name} | DMG:{damage} | Speed:{attack_speed:.1f}s | Cost:{stamina_use} | {range_str} | {area_str}"

# Output examples:
# "Wooden Sword | DMG:5 | Speed:1.0s | Cost:3 | Melee | Single"
# "Broad Axe | DMG:15 | Speed:2.0s | Cost:8 | Melee | Area:2"
# "Mage Staff | DMG:14 | Speed:2.0s | Cost:12 | Range:5 | Area:2"
```

---

## 5. Weapon Comparisons

### Damage Per Stamina

```python
def damage_per_stamina(weapon):
    """Efficiency metric"""
    damage = weapon.get('damage', 5)
    stamina = weapon.get('stamina_use', 3)
    return damage / stamina

# Results:
# Dagger: 4 / 2 = 2.0
# Wooden Sword: 5 / 3 = 1.67
# Iron Sword: 10 / 5 = 2.0
# Broad Axe: 15 / 8 = 1.875
# War Hammer: 16 / 10 = 1.6
# Mage Staff: 14 / 12 = 1.17

# Best efficiency: Dagger and Iron Sword
```

### Damage Per Second (DPS)

```python
def damage_per_second(weapon):
    """Attack rate metric"""
    damage = weapon.get('damage', 5)
    attack_speed = weapon.get('attack_speed', 1.0)
    attacks_per_second = 1.0 / attack_speed
    return damage * attacks_per_second

# Results:
# Dagger (4 dmg, 0.6s): 4 / 0.6 = 6.67 DPS
# Wooden Sword (5, 1.0s): 5 / 1.0 = 5.0 DPS
# Iron Sword (10, 1.2s): 10 / 1.2 = 8.33 DPS
# War Hammer (16, 2.5s): 16 / 2.5 = 6.4 DPS

# Best DPS: Iron Sword
```

### AoE Efficiency

```python
def aoe_coverage(weapon):
    """How many tiles the attack covers"""
    angle = weapon.get('angle', 0)
    area = weapon.get('area', 1)
    weapon_range = weapon.get('range', 0)
    
    if angle == 0:
        return 1  # Single target
    elif angle == 360:
        return (2 * area + 1) ** 2  # Approximate circular area
    else:
        # Approximate cone area
        return area * (angle / 360)

# Results:
# Dagger: 1 (single)
# Wooden Sword: 1 (single)
# Broad Axe: 2 (90° arc)
# War Hammer: 2 (180° arc)
# Mage Staff: 25 (circular explosion)
```

---

## 6. Strategy Examples

### Best Against Single Enemy

```python
best_vs_single = {
    'weapon': 'Long Spear',
    'reason': 'Can stay at range (3 squares away)',
    'strategy': 'Attack from distance, avoid damage'
}

# Alternative: Dagger
alternative = {
    'weapon': 'Dagger',
    'reason': 'Fast attacks, high DPS',
    'strategy': 'Hit multiple times quickly, dodge attacks'
}
```

### Best Against Swarms

```python
best_vs_swarm = {
    'weapon': 'War Hammer',
    'reason': 'Massive AoE (180°), high damage (16)',
    'strategy': 'Center yourself, swing in wide arc'
}

# Alternative: Broad Axe
alternative = {
    'weapon': 'Broad Axe',
    'reason': 'Faster (2.0s vs 2.5s), still AoE',
    'strategy': 'More frequent wide attacks'
}
```

### Best Balanced

```python
balanced = {
    'weapon': 'Iron Sword',
    'reason': 'Best DPS (8.33), balanced stamina cost',
    'strategy': 'Reliable damage with good attack speed'
}
```

### Best for Resources

```python
resource_efficient = {
    'weapon': 'Dagger',
    'reason': 'Lowest stamina cost (2), good efficiency',
    'strategy': 'Attack frequently without running out of stamina'
}
```

---

## 7. Adding New Weapons

### Template

```python
{
    'name': 'Your Weapon Name',
    'glyph_index': 8,  # Next available index
    'damage': 12,      # Balanced at 10-15
    'stamina_use': 6,  # Proportional to damage
    'attack_speed': 1.2,  # Slower = more powerful
    'range': 1,        # 0 for melee, 2+ for ranged
    'area': 1,         # 1 for single, 2+ for AoE
    'angle': 45,       # 0 for straight, >0 for cone
},
```

### Example: Custom Flaming Sword

```python
{
    'name': 'Flaming Sword',
    'glyph_index': 9,
    'damage': 12,      # Slightly stronger
    'stamina_use': 7,  # Higher cost due to flame
    'attack_speed': 1.1,  # Slightly slower
    'range': 0,        # Melee
    'area': 2,         # Small AoE from flames
    'angle': 60,       # Cone attack
},
```

### Example: Sniper Bow

```python
{
    'name': 'Sniper Bow',
    'glyph_index': 10,
    'damage': 20,      # Very high
    'stamina_use': 8,  # Expensive
    'attack_speed': 2.0,  # Very slow
    'range': 7,        # Very long range
    'area': 1,         # Precise
    'angle': 0,        # Single target
},
```

---

## Summary

The weapons system provides:
1. **Flexible weapon definitions** - 8 parameters per weapon
2. **Attack calculation** - `get_attack_tiles()` handles all geometry
3. **Damage execution** - `swing_weapon()` applies damage correctly
4. **Display functions** - `get_weapon_info_string()` shows stats
5. **Resource management** - Stamina and attack speed tracking

All integrated into the existing game system!
