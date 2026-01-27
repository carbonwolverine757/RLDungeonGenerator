# Weapon Targeting System - Mouse-Driven Attacks

## Overview
Weapons now target where the mouse is pointing instead of using a fixed attack direction. This gives the player precise control over where attacks land.

## How It Works

### Target Selection Logic
1. **If mouse tile is within weapon range**: Attack the exact tile the mouse is hovering over
2. **If mouse tile is beyond weapon range**: Attack the farthest tile in that direction within the weapon's range

### Example Scenarios

**Scenario 1: Short-range weapon (Range = 2)**
```
Player has a Dagger (range = 2)
         X X
       X X X X
       X X @ X X
       X X X X
         X X

- Mouse hovering at distance 1 ? Attack that tile directly
- Mouse hovering at distance 3 (beyond range) ? Attack farthest tile in that direction (distance 2)
```

**Scenario 2: Long-range weapon (Range = 5)**
```
Player has a Mage Staff (range = 5)
Staff has range of 5 tiles in any direction

- Mouse at 3 tiles away ? Attack that exact tile
- Mouse at 7 tiles away ? Attack the 5-tile-away point in that direction
```

## Technical Details

### Distance Calculation
- Uses **Chebyshev distance** (max of absolute differences in row and column)
- This allows diagonal attacks just like orthogonal ones
- Formula: `distance = max(abs(row_diff), abs(col_diff))`

### Direction Normalization
- Direction is calculated by taking the sign of each component
- Results in moving only 1 square per attack distance (no diagonal skipping)
- Prevents attacking multiple enemies in one swing (stops after first hit)

### Attack Pattern
- Attacks travel in a straight line from player toward target
- Walls stop the attack progression
- First monster hit stops further tiles from being damaged
- Doors are opened but don't stop the attack

## Weapon Range Examples

| Weapon | Range | Attack Pattern |
|--------|-------|----------------|
| Dagger | 0 | Adjacent tile only (melee) |
| Wooden Sword | 0 | Adjacent tile only (melee) |
| Short Spear | 2 | Up to 2 tiles away |
| Long Spear | 3 | Up to 3 tiles away |
| Mage Staff | 5 | Up to 5 tiles away |

## Benefits

- **Precision**: Aim exactly where you want to attack
- **Tactical**: Can choose between closer and farther targets
- **Intuitive**: Mouse position = attack target
- **Flexible**: Works with all weapon ranges seamlessly
- **Diagonal support**: Attacks work in any direction, not just 4 cardinal directions

## Implementation Details

### Key Method: `swing_weapon()`
- Reads `self.mouse_tile` (updated every frame from mouse position)
- Calculates distance using Chebyshev distance
- Determines target location based on range vs. distance
- Applies damage to first enemy in line of attack
- Marks last_swing location for visual feedback

### State Variables Used
- `mouse_tile`: Current (row, col) where mouse is pointing
- `equipped_slot`: Currently equipped weapon slot
- `last_swing`: Last attacked tile (for attack animation)
- `player_stamina`: Deducted on attack
- `last_attack_time`: Enforces attack cooldown

### Side Effects
- Opens doors in the attack path
- Updates explored tiles for visibility
- Sets last_swing location (drawn with attack_char color)
- Deducts stamina and enforces cooldown

## Edge Cases Handled

- **Out of bounds**: Attack stops at map edges
- **Walls blocking**: Attack stops at walls
- **Multiple monsters**: Only first monster hit takes damage
- **No target**: Attack still animates visually
- **Inventory open**: Mouse tracking paused, but attacks still work
- **No stamina**: Attack fails silently
- **On cooldown**: Attack fails silently

## Future Enhancements

Potential additions for more complex combat:
- Area-of-effect weapons (radial damage)
- Cone/arc attacks based on angle parameter
- Multiple target hits (with area parameter)
- Knockback effects
- Charge-up attacks with range scaling
- Weapon special abilities on certain targets
