# Weapons System - Quick Start Guide

## 5-Minute Setup

### 1. Run the Game
```bash
python RLDungeonGenerator.py --renderer bearlib
```

### 2. Equip a Weapon
Press **1** to equip the Wooden Sword (in hotbar slot 1)

### 3. Attack Enemies
- Click on an enemy to attack
- Or press spacebar to attack in facing direction

### 4. Switch Weapons
Press **2** through **8** to try different weapons in the hotbar

### 5. Observe Effects
- **Dagger (1)**: Fast attacks, weak
- **Wooden Sword (1)**: Balanced starter
- **Iron Sword (2)**: Stronger
- **Broad Axe (3)**: Wide arc attack
- **Short Spear (4)**: Range 2
- **Long Spear (5)**: Range 3
- **War Hammer (6)**: Heavy AoE
- **Mage Staff (7)**: Explosion magic

---

## Testing Checklist

### ? Basic Attack
- [ ] Equip weapon (press 1-8)
- [ ] Click on enemy to attack
- [ ] Enemy takes damage
- [ ] Monster dies and drops coins

### ? Attack Speed
- [ ] Attack once
- [ ] Try to attack immediately
- [ ] Can't attack (cooldown)
- [ ] Wait for cooldown
- [ ] Can attack again

### ? Stamina
- [ ] Note current stamina
- [ ] Attack (stamina decreases)
- [ ] Stamina slowly regenerates
- [ ] After 1 second, regen speeds up
- [ ] Run out of stamina
- [ ] Can't attack (no stamina)
- [ ] Stamina refills
- [ ] Can attack again

### ? Range Attacks
- [ ] Equip Long Spear (slot 5)
- [ ] Move 3 squares away from monster
- [ ] Attack (can hit at distance)
- [ ] Move back to melee range
- [ ] Try with short spear (range=2)
- [ ] Verify range difference

### ? AoE Attacks
- [ ] Get multiple monsters together
- [ ] Equip War Hammer (slot 6)
- [ ] Attack with hammer
- [ ] Multiple monsters take damage
- [ ] Try Mage Staff (slot 7)
- [ ] Attack from distance
- [ ] See circular explosion effect

### ? Weapon Switching
- [ ] Start combat with one weapon
- [ ] Switch to different weapon (press key)
- [ ] Attack with new weapon
- [ ] Different damage/range applied
- [ ] Switch back and forth

---

## Weapon Comparison Test

### Speed Test (Fastest vs Slowest)
```
Dagger (0.6s):      Can attack every 0.6 seconds
War Hammer (2.5s):  Can attack every 2.5 seconds

Attack Dagger multiple times rapidly.
Try same with War Hammer - notice slow attacks.
```

### Damage Test (Weakest vs Strongest)
```
Dagger (4 dmg):     4 damage per hit
War Hammer (16 dmg): 16 damage per hit

Attack same monster with both.
War Hammer kills in 2 hits, Dagger needs 4 hits.
```

### AoE Test (Single vs Multi)
```
Dagger (area=1):       Hits 1 tile
Broad Axe (area=2):    Hits 2-tile arc

Get 3 monsters close together.
Dagger attacks 1, Broad Axe hits all 3.
```

### Range Test (Melee vs Ranged)
```
Dagger (range=0):      Melee only
Long Spear (range=3):  3 squares away

Try attacking monster at different distances.
Dagger needs adjacent square.
Long Spear can hit from 3 away.
```

---

## What Each Weapon Does

### 1. Dagger (fastest, cheap)
```
Damage:      4
Speed:       0.6s (FAST)
Stamina:     2 (CHEAP)
Range:       0 (melee)
AoE:         Single target

Best for: Quick attacks, hit-and-run
Test: Attack enemy rapidly, notice fast pace
```

### 2. Wooden Sword (starter)
```
Damage:      5
Speed:       1.0s
Stamina:     3
Range:       0 (melee)
AoE:         Single target

Best for: Learning the game
Test: Standard melee attack
```

### 3. Iron Sword (balanced)
```
Damage:      10 (DOUBLE Wooden)
Speed:       1.2s
Stamina:     5
Range:       0 (melee)
AoE:         Single target

Best for: Overall best DPS
Test: Stronger than Wooden, still fast
```

### 4. Broad Axe (wide swing)
```
Damage:      15
Speed:       2.0s (slow)
Stamina:     8
Range:       0 (melee)
AoE:         90° arc (2 squares wide)

Best for: Multiple nearby enemies
Test: Get 3 enemies in a line, attack hits all
```

### 5. Short Spear (close range)
```
Damage:      8
Speed:       1.0s
Stamina:     4
Range:       2 squares away
AoE:         Single target

Best for: Safer melee
Test: Stand 2 squares from enemy, attack hits
```

### 6. Long Spear (extended range)
```
Damage:      12
Speed:       1.5s
Stamina:     6
Range:       3 squares away
AoE:         Single target

Best for: Safe ranged combat
Test: Stand far away, spear hits distant target
```

### 7. War Hammer (heavy AoE)
```
Damage:      16 (HIGHEST)
Speed:       2.5s (SLOWEST)
Stamina:     10
Range:       0 (melee)
AoE:         180° semicircle (wide!)

Best for: Heavy damage, wide coverage
Test: Surround yourself with enemies, massive swing
```

### 8. Mage Staff (magic explosion)
```
Damage:      14
Speed:       2.0s
Stamina:     12 (MOST EXPENSIVE)
Range:       5 squares
AoE:         360° circle (explosion!)

Best for: Range + AoE magic
Test: Attack from 5 squares away, all nearby enemies damaged
```

---

## Stamina Budget Examples

### Dagger Strategy (Cheap)
```
Max Stamina: 50
Per Attack:  2
Max Attacks: 25 attacks before empty!
```

### Iron Sword Strategy (Balanced)
```
Max Stamina: 50
Per Attack:  5
Max Attacks: 10 attacks before empty
```

### Mage Staff Strategy (Expensive)
```
Max Stamina: 50
Per Attack:  12
Max Attacks: 4 attacks before empty
         (need to wait for regen)
```

---

## Learning Progression

### Beginner (Just Started)
1. Use **Wooden Sword** (slot 1)
2. Attack monsters
3. Learn attack mechanics
4. Understand stamina

### Intermediate (Comfortable)
1. Try different weapons
2. Notice speed differences
3. Test range attacks
4. Manage stamina efficiently

### Advanced (Expert)
1. Switch weapons in combat
2. Use AoE for swarms
3. Use ranged for safety
4. Perfect stamina management

---

## Experiment Ideas

### Speed Comparison
```
1. Equip Dagger (0.6s)
2. Attack enemy continuously
3. Count attacks per second (should be ~1.7)
4. Switch to War Hammer (2.5s)
5. Count attacks per second (should be ~0.4)
6. Notice huge difference!
```

### Damage Comparison
```
1. Find weakest monster
2. Attack with Dagger (4 dmg)
3. Note how many hits to kill
4. Switch to War Hammer (16 dmg)
5. Kill similar monster
6. Note fewer hits needed
```

### Stamina Efficiency
```
1. Track stamina
2. Attack with Dagger 5 times (uses 10 stamina)
3. Check damage dealt (20 total)
4. Attack with Iron Sword once (uses 5 stamina)
5. Compare efficiency
6. Dagger: 2 dmg/stamina, Sword: 2 dmg/stamina
```

### Range Testing
```
1. Move exactly 1 square away
2. Dagger can't hit (range=0)
3. Short Spear can hit (range=2)
4. Move 3 squares away
5. Long Spear can hit (range=3)
6. Mage Staff can hit from 5 away
```

### AoE Testing
```
1. Group 3+ enemies together
2. Attack with Dagger (hits 1)
3. Attack with Broad Axe (hits multiple)
4. Attack with Mage Staff (hits all in circle)
5. See damage increase as enemies increase
```

---

## Troubleshooting

### "Attack didn't work"
- Check if equipped weapon is visible in hotbar
- Verify stamina is high enough
- Wait for attack cooldown

### "Can't reach enemy"
- Check weapon range (0=melee, 2-3=spear, 5=staff)
- Move closer for melee weapons
- Use ranged weapons to attack from distance

### "Out of stamina"
- Wait for stamina to regenerate
- Use cheaper weapons (Dagger)
- Take less risky attacks

### "Weapon not equipping"
- Press number key 1-8 matching slot
- Check weapon is in hotbar
- Weapon should light up when selected

---

## Key Controls

| Key | Action |
|-----|--------|
| 1-8 | Equip weapon in hotbar |
| Space | Attack facing direction |
| Click | Attack target |
| Arrow Keys | Move |
| WASD | Move (alternative) |
| I | Inventory |
| ESC | Quit |

---

## Expected Behavior

### Attack Speed
```
Time between attacks = weapon.attack_speed
Cooldown tracked with last_attack_time
System prevents attacking before cooldown
```

### Stamina Cost
```
Cost deducted immediately when attacking
Regen starts 1 second after attack
Prevents attacking if not enough stamina
```

### Damage
```
Damage applied to all tiles in attack area
Multiple enemies can be hit at once
Monsters die when health reaches 0
Coins drop where monster died
```

### Range
```
Attack range = weapon.range squares away
Area effect adds to range calculation
Angle spreads the attack width
All geometry validated for bounds
```

---

## Next Steps

### After Testing Weapons
1. Read WEAPONS_QUICK_REFERENCE.md for details
2. Check WEAPONS_VISUAL_GUIDE.md for diagrams
3. Look at code in WEAPONS_CODE_EXAMPLES.md
4. Create custom weapons if interested

### To Add New Weapon
1. Open RLDungeonGenerator.py
2. Find WEAPONS array
3. Add new weapon entry
4. Play test in game!

---

## Summary

The weapons system is:
- ? Ready to play
- ? Easy to test
- ? Simple to understand
- ? Fun to experiment with
- ? Easy to extend

Start with Wooden Sword, try different weapons, have fun!

---

**Happy Testing!**
Enjoy the weapons system!
