# Weapon definitions for RLDungeonGenerator
# Each weapon is a dict with:
# - name: display name
# - damage: numeric damage amount
# - stamina_cost: numeric stamina cost
# - range: maximum distance (in tiles) from the player to the attack centroid.
#   NOTE: a range of 0 disables clamping entirely (see _resolve_attack_target),
#   so the attack lands wherever the player clicked, at any distance.
# - area: radius (in tiles) around the attack centroid that can be affected
# - angle: cone angle in degrees (centered on attack direction)
# - glyph: tileset index (row * 32 + col), drawn in the crafting menu and the
#   inventory. None means the weapon has no icon.
#
# Weapons are crafted at the Workbench; see Recipes.py for what each one costs.
# 'Unarmed' must stay first: RLDungeonGenerator equips WEAPONS[0] on startup.

# Weapon art is shared per weapon type; material is not yet distinguished, so
# every spear looks alike, as does every sword and axe. Row 11 is unused (row 10
# holds drop/item art). Art TBD — these cells currently show the placeholder glyph.
SPEAR_GLYPH = 11 * 32 + 0  # Row 11, Column 0
SWORD_GLYPH = 11 * 32 + 1  # Row 11, Column 1
AXE_GLYPH = 11 * 32 + 2    # Row 11, Column 2

WEAPONS = [
    {
        'name': 'Unarmed',
        'damage': 20.0,
        'stamina_cost': 0,
        'range': 99.5,
        'area': 6.0,
        'angle': 360.0,
        'knockback': 1.0,  # tiles of knockback
        'glyph': None,
    },
    # Spears: a long, narrow cone.
    {
        'name': 'Flint Spear',
        'damage': 10.0,
        'stamina_cost': 6,
        'range': 0,
        'area': 3.0,
        'angle': 10.0,
        'knockback': 0.5,  # tiles of knockback
        'glyph': SPEAR_GLYPH,
    },
    {
        'name': 'Bronze Spear',
        'damage': 15.0,
        'stamina_cost': 6,
        'range': 0,
        'area': 3.0,
        'angle': 10.0,
        'knockback': 0.5,  # tiles of knockback
        'glyph': SPEAR_GLYPH,
    },
    {
        'name': 'Iron Spear',
        'damage': 20.0,
        'stamina_cost': 6,
        'range': 0,
        'area': 3.0,
        'angle': 10.0,
        'knockback': 0.5,  # tiles of knockback
        'glyph': SPEAR_GLYPH,
    },
    # Swords: shorter reach, a wider arc than a spear.
    {
        'name': 'Bronze Sword',
        'damage': 15.0,
        'stamina_cost': 7,
        'range': 0,
        'area': 2.0,
        'angle': 60.0,
        'knockback': 0.75,  # tiles of knockback
        'glyph': SWORD_GLYPH,
    },
    {
        'name': 'Iron Sword',
        'damage': 20.0,
        'stamina_cost': 7,
        'range': 0,
        'area': 2.0,
        'angle': 60.0,
        'knockback': 0.75,  # tiles of knockback
        'glyph': SWORD_GLYPH,
    },
    # Axes: the widest arc, the heaviest hit, the most stamina.
    {
        'name': 'Bronze Axe',
        'damage': 17.0,
        'stamina_cost': 8,
        'range': 0,
        'area': 2.0,
        'angle': 90.0,
        'knockback': 1.0,  # tiles of knockback
        'glyph': AXE_GLYPH,
    },
    {
        'name': 'Iron Axe',
        'damage': 22.0,
        'stamina_cost': 8,
        'range': 0,
        'area': 2.0,
        'angle': 90.0,
        'knockback': 1.0,  # tiles of knockback
        'glyph': AXE_GLYPH,
    },
]
