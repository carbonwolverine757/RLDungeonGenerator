# This code is released into the Public Domain.
"""
Weapons data and definitions for RLDungeonGenerator.

Each weapon has 8 parameters:
- name: Display name
- glyph_index: Tileset character index
- damage: HP dealt per hit
- stamina_use: Stamina consumed per attack
- attack_speed: Cooldown between attacks (seconds)
- range: Maximum reach from player (0=melee)
- area: Explosion radius (1=single tile)
- angle: Arc width in degrees (0=straight, 360=circle)
"""

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


def get_weapon_by_name(name):
    """Get weapon data by name."""
    for weapon in WEAPONS:
        if weapon['name'] == name:
            return weapon.copy()
    return None


def get_weapon_by_index(index):
    """Get weapon data by index."""
    if 0 <= index < len(WEAPONS):
        return WEAPONS[index].copy()
    return None


def get_all_weapons():
    """Get all weapons as copies."""
    return [weapon.copy() for weapon in WEAPONS]


# Weapon parameter documentation
__doc__ = """
Weapons System Documentation

Each weapon has 8 parameters:

1. name (str)
   - Display name of the weapon
   - Examples: "Wooden Sword", "War Hammer", "Mage Staff"

2. glyph_index (int)
   - Index into the tileset for visual representation
   - Range: 0-7 (current weapons) or higher if extended
   - Used for inventory display

3. damage (int)
   - HP dealt to enemies per hit
   - Range: 4-16 in current weapons
   - Higher damage = slower/more expensive typically

4. stamina_use (int)
   - Stamina consumed per attack
   - Range: 2-12 in current weapons
   - Higher use = more powerful typically

5. attack_speed (float)
   - Cooldown between attacks in seconds
   - Range: 0.6-2.5 in current weapons
   - Lower = faster (more attacks per second)
   - Formula: can_attack if (time_since_last_attack >= attack_speed)

6. range (int)
   - Maximum distance weapon can reach
   - 0 = melee only (adjacent square)
   - 1-3 = spear range attacks
   - 5+ = long-range magic
   - Weapon can hit up to this many squares away

7. area (int)
   - Size of explosion/AoE from impact point
   - 1 = single tile only
   - 2+ = larger splash radius
   - Combined with angle for effect shape

8. angle (int, degrees)
   - Arc/cone width of the attack
   - 0 = straight line only (no spread)
   - 45-90 = arc/cone attacks
   - 180 = semicircle (half-circle)
   - 360 = full circle (explosion)
   - Angle of 0 ignores the area parameter

Current Weapons:

1. Dagger
   - damage=4, stamina_use=2, attack_speed=0.6
   - range=0, area=1, angle=0
   - Fast melee attacks, cheap, low damage

2. Wooden Sword
   - damage=5, stamina_use=3, attack_speed=1.0
   - range=0, area=1, angle=0
   - Balanced starter weapon

3. Iron Sword
   - damage=10, stamina_use=5, attack_speed=1.2
   - range=0, area=1, angle=0
   - Stronger, best overall DPS

4. Broad Axe
   - damage=15, stamina_use=8, attack_speed=2.0
   - range=0, area=2, angle=90
   - Wide 90 degree swing, hits multiple in melee

5. Short Spear
   - damage=8, stamina_use=4, attack_speed=1.0
   - range=2, area=1, angle=0
   - Close-range weapon, attack from distance

6. Long Spear
   - damage=12, stamina_use=6, attack_speed=1.5
   - range=3, area=1, angle=0
   - Extended range, single target

7. War Hammer
   - damage=16, stamina_use=10, attack_speed=2.5
   - range=0, area=2, angle=180
   - Heavy, slow, hits in 180 degree arc

8. Mage Staff
   - damage=14, stamina_use=12, attack_speed=2.0
   - range=5, area=2, angle=360
   - Long-range magical explosion

To add a new weapon:

1. Add entry to WEAPONS array
2. Set all 8 parameters
3. System automatically supports it

Example:
{
    'name': 'Your Weapon',
    'glyph_index': 8,
    'damage': 12,
    'stamina_use': 7,
    'attack_speed': 1.3,
    'range': 1,
    'area': 1,
    'angle': 45,
}
"""
