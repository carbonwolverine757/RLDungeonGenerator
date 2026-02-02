# Weapons System - Visual Attack Patterns

## Attack Pattern Diagrams

### Single Target (angle=0)

```
Wooden Sword, Iron Sword, Dagger
```

```
        ?
        X    ? Hit location
        
P = Player position
X = Affected tile (1 tile in attack direction)
```

### Arc Attack (angle=90)

```
Broad Axe (90° arc)
```

```
    X X X
    X @ X    ? @ is player, X is affected area
      X
      
P = Player
X = Affected tiles (2-tile wide 90° cone)
Hits in a quarter-circle pattern
```

### Wide Arc (angle=180)

```
War Hammer (180° arc)
```

```
  X X X X X
  X X @ X X    ? Hits everything in front and sides
    X @ X
      X
      
Hits in a semicircle - very wide swing
Area=2, range=0, so affects 2 squares out in 180° arc
```

### Ranged Single (range=3, area=1, angle=0)

```
Long Spear
```

```
    X
    X
    X
    P    ? Player shoots straight
    
P = Player
X = Affected tiles (3 squares away in straight line)
Can reach enemies at distance without AoE
```

### Explosion (angle=360, area=2)

```
Mage Staff (360° explosion)
```

```
      X X X
      X X X
    X X P X X    ? Magic explodes in circle
      X X X
      X X X
      
P = Impact point (5 squares away from player)
X = Affected tiles (2-tile radius circle around impact)
Hits everything in a circular area
```

---

## Attack Comparison Chart

```
                    Melee      Ranged     Magic
                    -----      ------     -----
Single Target:   Dagger     Long Spear   (none)
                 [X]        [  X  ]      [    X    ]

Arc Attack:      Broad Axe  (none)      (none)
                 [XXX]
                  [X]

Wide Arc:        War Hammer (none)      (none)
                [XXXXX]
                 [XXX]
                  [X]

Explosion:       (none)     (none)      Mage Staff
                                        [  XXX  ]
                                        [ XXXXX ]
                                        [XXXXXXX]
                                        [ XXXXX ]
                                        [  XXX  ]
```

---

## Attack Type Summary

### 1. Straight Attack
- Parameters: `angle=0, area=1`
- Shape: Single tile line
- Examples: All daggers, swords, spears
- Use: Precise, efficient damage

```
Attack direction ?
        X ? Only this tile hit
```

### 2. Cone Attack
- Parameters: `angle=45-90, area=1-2`
- Shape: Cone or arc
- Examples: Broad Axe, War Hammer
- Use: Multiple targets, crowd control

```
Attack direction ?
      XXX ? All tiles in cone hit
       XX
        X
```

### 3. Ranged Single
- Parameters: `range=2+, angle=0, area=1`
- Shape: Long line
- Examples: Spears
- Use: Attack from distance

```
P ? X ? X ? X ? Can hit tiles far away
```

### 4. Explosion
- Parameters: `angle=360, area=2, range=5`
- Shape: Circle
- Examples: Mage Staff
- Use: Massive AoE, area denial

```
      XXX
     XXXXX
    XXXPXXX ? Explodes in circle
     XXXXX
      XXX
```

---

## Damage Effectiveness

### Against Single Enemy

```
Weapon          Damage  Range   Strategy
------          ------  -----   --------
Dagger          4       0       Fast attacks, kite
Long Spear      12      3       Stay at range
Iron Sword      10      0       Consistent damage
War Hammer      16      0       One strong hit
```

**Best**: Long Spear (safe) or Iron Sword (reliable)

### Against 3+ Enemies

```
Weapon          DMG/Hit  Targets  Total
------          -------  -------  -----
Dagger          4        1        4
Iron Sword      10       1        10
Broad Axe       15       3-5      45-75
War Hammer      16       3-5      48-80
Mage Staff      14       5-9      70-126
```

**Best**: War Hammer or Mage Staff

### Most Efficient (Damage per Stamina)

```
Weapon          DMG / Stamina
------          ------------- 
Dagger          4 / 2 = 2.0
Iron Sword      10 / 5 = 2.0
Wooden Sword    5 / 3 = 1.67
Broad Axe       15 / 8 = 1.88
War Hammer      16 / 10 = 1.6
Mage Staff      14 / 12 = 1.17
```

**Best**: Dagger (fast) or Iron Sword (strong)

---

## Decision Tree: Which Weapon?

```
                    Choose Weapon
                         |
                    _____|_____
                   /           \
              Alone?        Swarm?
                |              |
                |              |
          ______|______    _____|____
         /      |      \  /    |    \
     Melee   Range   AoE Melee Range Magic
      |       |      |    |     |     |
    Dagger Long Sp  Axe  Axe  Spear Staff
     fast    safe   area crowd  safety  explosion
     |       |      |     |     |       |
     Best for high DPS, Broad Axe is good all-rounder
     attack from                War Hammer if max damage
     distance or               needed
     use Axe for
     some AoE
```

---

## Stamina Cost vs Benefit

```
HIGH COST (12)     MEDIUM COST (5-8)    LOW COST (2-4)
  Mage Staff         Iron Sword          Dagger
  (14 damage)        (10 damage)         (4 damage)
  (5 range)          (0 range)           (0 range)
  (360° AoE)         (single)            (single)
     |                    |                  |
   Best for range      Best balanced    Best for multiple
   and AoE combat      play style       quick attacks
```

---

## Range Visualization

```
Melee (range=0):
P X         ? Attack adjacent square only
  ^

Close Range (range=2):
P X X X     ? Attack up to 2 squares away
  ^

Extended Range (range=3):
P X X X X   ? Attack up to 3 squares away
  ^

Long Range (range=5):
P X X X X X X     ? Attack up to 5 squares away
  ^
```

---

## Area of Effect Visualization

```
Area=1 (Single):        Area=2 (Splash):
      X                     XXX
      ?                     XXX
    Only 1 tile          Total 5-9 tiles
                         (depends on shape)


Circle (360°):          Cone (90°):
    XXX                     XXX
   XXXXX                     XX
  XXXXXXX                     X
   XXXXX              (smaller, more precise)
    XXX
```

---

## Attack Speed Timeline

```
Dagger (0.6s):
|--Attack--|
|--0.6s----|--Attack--|
|----1.2s----|--Attack--|
2-3 attacks per second

Wooden Sword (1.0s):
|---Attack---|
|----1.0s----|---Attack---|
|-----2.0s-----|---Attack---|
1 attack per second

War Hammer (2.5s):
|----------Attack----------|
|----------2.5s----------|----------Attack----------|
0.4 attacks per second (very slow but powerful)
```

---

## Combined Attack Example

**Player attacks with Mage Staff (staff=5, area=2, angle=360)**

1. Player at position (10, 10)
2. Facing northeast toward (5, 5)
3. Magic travels 5 squares to (5, 5)
4. Explodes in 2-tile radius circle
5. All tiles within 2 squares of (5, 5) take 14 damage

```
Player position       Impact & explosion
(10, 10)              (5, 5)
    ?                   ?
    ???????????        ???????
    ?         ?        ???????
    ?         ?   ?    ???P???  (P = explosion center)
    ?       P ?        ???????
    ???????????        ???????
    
All X tiles hit:
    X X X
   X X P X X
  X X X P X X X
   X X P X X
    X X X
```

---

## Weapon Selection Matrix

```
                Damage | Speed | Range | AoE  | Stamina
                -------|-------|-------|------|--------
Dagger            Low   | Fast  |   0   |  No  |   Low
Wooden Sword     Low    | Fast  |   0   |  No  |  Med-Low
Iron Sword       Med    | Med   |   0   |  No  |  Medium
Broad Axe        High   | Slow  |   0   | Yes  |  Medium
Short Spear      Med    | Fast  |  2    |  No  |  Medium
Long Spear       High   | Med   |  3    |  No  |  Medium
War Hammer       V.High | V.Slow|   0   | Yes  |  High
Mage Staff       High   | Slow  |  5    | Yes  | V.High
```

---

**Use this guide to:**
- Visualize attack patterns
- Choose weapons for situations
- Plan combat tactics
- Understand game balance

All patterns scale with area/range/angle parameters!
