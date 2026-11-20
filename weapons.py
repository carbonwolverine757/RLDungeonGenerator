# Weapon definitions for RLDungeonGenerator
# Each weapon is a dict with:
# - name: display name
# - damage: numeric damage amount
# - stamina_cost: numeric stamina cost
# - range: maximum distance (in tiles) from the player to the attack centroid.
#   NOTE: a range of 0 disables clamping entirely (see _resolve_attack_target),
#   so the attack lands wherever the player clicked, at any distance.
# - area: radius (in tiles) of the attack arc drawn from the centroid. Any
#   monster whose hitbox the arc touches, even partly, is hit.
# - angle: arc spread in degrees (centered on attack direction)
# - glyph: tileset index (declared by row and column in Glyph_Grimoire.py),
#   drawn in the crafting menu and the inventory. None means the weapon has no
#   icon.
#
# Timing keys (shared with skills.py and monster attacks.py; see
# RLDungeonGenerator.update_attacks for the rules):
# - attack_type: how the attack travels once it goes off. One of
#   'Melee Swing'  the arc sweeps from one edge to the other,
#   'Melee AOE'    the arc grows outward from the attack centroid,
#   'Ranged Arrow' a projectile flies along the aim line until it hits a
#                  hitbox or wall, or reaches 'range' tiles, then bursts,
#   'Ranged AOE'   a projectile flies to the aim point (clamped to 'range'),
#                  bursting early if it hits a hitbox or wall on the way.
# - attack_delay: seconds between clicking and the attack going off.
# - swing_speed: degrees per second the arc sweeps (Melee Swing only).
# - projectile_speed: tiles per second the projectile flies (Ranged types).
# - effect_speed: tiles per second the arc grows outward (Melee AOE, and the
#   burst at the end of either Ranged type).
# A missing or 0 speed makes that stage instant. Damage lands once per target,
# the moment the moving effect touches its hitbox.
#
# Weapons are crafted at the Workbench; see Recipes.py for what each one costs.
# 'Unarmed' must stay first: RLDungeonGenerator equips WEAPONS[0] on startup.

try:
    from .Glyph_Grimoire import WEAPON_SPEAR, WEAPON_SWORD, WEAPON_AXE, WEAPON_BOW
except ImportError:
    from Glyph_Grimoire import WEAPON_SPEAR, WEAPON_SWORD, WEAPON_AXE, WEAPON_BOW

# Weapon art is shared per weapon type; material is not yet distinguished, so
# every spear looks alike, as does every sword and axe. Row 11 is unused (row 10
# holds drop/item art). Art TBD — these cells currently show the placeholder glyph.
SPEAR_GLYPH = WEAPON_SPEAR
SWORD_GLYPH = WEAPON_SWORD
AXE_GLYPH = WEAPON_AXE
BOW_GLYPH = WEAPON_BOW

WEAPONS = [
    {
        'name': 'Unarmed',
        'damage': 50.0,
        'stamina_cost': 0,
        'range': 99.5,
        'area': 3.0,
        'angle': 360.0,
        'attack_type': 'Melee AOE',
        'attack_delay': 0.1,
        'effect_speed': 30.0,
        'knockback': 0.0,  # tiles of knockback
        'glyph': None,
    },
    # Spears: a long, narrow cone.
    {
        'name': 'Flint Spear',
        'damage': 10.0,
        'stamina_cost': 6,
        'range': 0.1,
        'area': 4.0,
        'angle': 10.0,
        'attack_type': 'Melee AOE',
        'attack_delay': 0.2,
        'effect_speed': 20.0,
        'knockback': 0.5,  # tiles of knockback
        'glyph': SPEAR_GLYPH,
    },
    {
        'name': 'Bronze Spear',
        'damage': 15.0,
        'stamina_cost': 6,
        'range': 0.1,
        'area': 4.0,
        'angle': 10.0,
        'attack_type': 'Melee AOE',
        'attack_delay': 0.2,
        'effect_speed': 20.0,
        'knockback': 0.5,  # tiles of knockback
        'glyph': SPEAR_GLYPH,
    },
    {
        'name': 'Iron Spear',
        'damage': 20.0,
        'stamina_cost': 6,
        'range': 0.1,
        'area': 4.0,
        'angle': 10.0,
        'attack_type': 'Melee AOE',
        'attack_delay': 0.2,
        'effect_speed': 20.0,
        'knockback': 0.5,  # tiles of knockback
        'glyph': SPEAR_GLYPH,
    },
    # Swords: shorter reach, a wider arc than a spear.
    {
        'name': 'Bronze Sword',
        'damage': 15.0,
        'stamina_cost': 7,
        'range': 0.1,
        'area': 4.0,
        'angle': 60.0,
        'attack_type': 'Melee Swing',
        'attack_delay': 0.2,
        'swing_speed': 480.0,
        'knockback': 0.75,  # tiles of knockback
        'glyph': SWORD_GLYPH,
    },
    {
        'name': 'Iron Sword',
        'damage': 20.0,
        'stamina_cost': 7,
        'range': 0.1,
        'area': 4.0,
        'angle': 60.0,
        'attack_type': 'Melee Swing',
        'attack_delay': 0.2,
        'swing_speed': 480.0,
        'knockback': 0.75,  # tiles of knockback
        'glyph': SWORD_GLYPH,
    },
    # Axes: the widest arc, the heaviest hit, the most stamina.
    {
        'name': 'Bronze Axe',
        'damage': 17.0,
        'stamina_cost': 8,
        'range': 0.1,
        'area': 4.0,
        'angle': 90.0,
        'attack_type': 'Melee Swing',
        'attack_delay': 0.3,
        'swing_speed': 360.0,
        'knockback': 1.0,  # tiles of knockback
        'glyph': AXE_GLYPH,
    },
    {
        'name': 'Iron Axe',
        'damage': 22.0,
        'stamina_cost': 8,
        'range': 0.1,
        'area': 4.0,
        'angle': 90.0,
        'attack_type': 'Melee Swing',
        'attack_delay': 0.3,
        'swing_speed': 360.0,
        'knockback': 1.0,  # tiles of knockback
        'glyph': AXE_GLYPH,
    },
    {
        'name': 'Crude Bow',
        'damage': 22.0,
        'stamina_cost': 6,
        'range': 80.0,
        'area': 0.5,
        'angle': 2.0,
        'attack_type': 'Ranged Arrow',
        'attack_delay': 0.3,
        'projectile_speed': 25.0,
        'effect_speed': 10.0,
        'knockback': 0.3,  # tiles of knockback
        'glyph': BOW_GLYPH,
    },
    {
        'name': 'Finewood Bow',
        'damage': 42.0,
        'stamina_cost': 6,
        'range': 80.0,
        'area': 0.5,
        'angle': 2.0,
        'attack_type': 'Ranged Arrow',
        'attack_delay': 0.3,
        'projectile_speed': 25.0,
        'effect_speed': 10.0,
        'knockback': 0.3,  # tiles of knockback
        'glyph': BOW_GLYPH,
    },
    {
        'name': 'Skull Splittur',
        'damage': 130.0,
        'stamina_cost': 24,
        'range': 0.1,
        'area': 4.0,
        'angle': 200.0,
        'attack_type': 'Melee Swing',
        'attack_delay': 1.3,
        'swing_speed': 360.0,
        'knockback': 4.0,  # tiles of knockback
        'glyph': AXE_GLYPH,
    },
    {
        'name': 'Krom',
        'damage': 150.0,
        'stamina_cost': 20,
        'range': 0.1,
        'area': 4.0,
        'angle': 120.0,
        'attack_type': 'Melee Swing',
        'attack_delay': 0.4,
        'swing_speed': 360.0,
        'knockback': 0.8,  # tiles of knockback
        'glyph': SWORD_GLYPH,
    },
    {
        'name': 'Slayer',
        'damage': 170.0,
        'stamina_cost': 20,
        'range': 0.1,
        'area': 4.0,
        'angle': 120.0,
        'attack_type': 'Melee Swing',
        'attack_delay': 0.4,
        'swing_speed': 360.0,
        'knockback': 0.8,  # tiles of knockback
        'glyph': SWORD_GLYPH,
    },
    {
        'name': 'Arbalest',
        'damage': 200.0,
        'stamina_cost': 12,
        'range': 500.0,
        'area': 0.5,
        'angle': 2.0,
        'attack_type': 'Ranged Arrow',
        'attack_delay': 3.5,
        'projectile_speed': 200.0,
        'effect_speed': 10.0,
        'knockback': 5.0,  # tiles of knockback
        'glyph': BOW_GLYPH,
    },
    {
        'name': 'Nord Sledge',
        'damage': 215.0,
        'stamina_cost': 30,
        'range': 1.1,
        'area': 6.0,
        'angle': 360.0,
        'attack_type': 'Melee AOE',
        'attack_delay': 1.5,
        'effect_speed': 12.0,
        'knockback': 4.0,  # tiles of knockback
        'glyph': AXE_GLYPH,
    }
]
