# Monster type definitions for RLDungeonGenerator
# Each monster type is a dict with:
# - name: monster name
# - glyph_index: index in the tileset (row * 32 + col)
# - health: health points
# - size: side length N of the N×N block of tiles the monster occupies (default 1).
#   Movement, collision, pathfinding, and rendering all operate on this footprint.
# - levels: list of level names where this monster appears (empty list means all levels)
# - drops: list of items dropped when the monster is defeated. Each item is a dict
#   with 'name' and 'drop_chance'. The 'name' refers to a drop defined in Drops.py,
#   which supplies the glyph used to draw it. The drop_chance is the (possibly
#   fractional) number of that item dropped: the integer part always drops, and the
#   fractional part is the probability of dropping one extra (e.g. 0.5 -> 1 half the
#   time; 1.2 -> 1 most of the time, 2 twenty percent of the time). Each entry is
#   rolled independently, even if the same item name appears more than once.

MONSTER_TYPES = [
    {
        'name': 'Boar',
        'glyph_index': 3 * 32 + 1,  # Row 3, Column 1
        'health': 10,
        'size': 1,  # occupies a 1x1 block of tiles
        'xp_value': 18,
        'levels': ['Meadows'],
        'aggro_distance': 5.0,  # tiles
        'aggro_time': 4.0,  # seconds monster stays aggroed after losing sight of player
        'damage_aggro_time': 10.0,  # seconds monster stays aggroed after taking damage
        'movement_speed': 1.0,  # tiles per second
        'knockback_resistance': 0.7,  # 0-1; higher = less knockback
        'drops': [
            {'name': 'Boar Meat', 'drop_chance': 1.5},
            {'name': 'Leather Scraps', 'drop_chance': 1.2},
        ],
    },
    {
        'name': 'Greyling',
        'glyph_index': 3 * 32 + 2,  # Row 3, Column 2
        'health': 20,
        'size': 1,  # occupies a 1x1 block of tiles
        'xp_value': 18,
        'levels': ['Meadows', 'Black Forest'],
        'aggro_distance': 5.0,  # tiles
        'aggro_time': 4.0,  # seconds monster stays aggroed after losing sight of player
        'damage_aggro_time': 10.0,  # seconds monster stays aggroed after taking damage
        'movement_speed': 1.5,
        'knockback_resistance': 0.5,  # 0-1; higher = less knockback
        'drops': [
            {'name': 'Resin', 'drop_chance': 1.0},
            {'name': 'Wood', 'drop_chance': 0.5},
        ],
    },
    {
        'name': 'Eikthyr',
        'glyph_index': 3 * 32 + 3,  # Row 3, Column 3
        'health': 500,
        'size': 4,  # occupies a 4x4 block of tiles
        'xp_value': 240,
        'levels': ['Eikthyr Bossfight'],
        'aggro_distance': 5.0,  # tiles
        'aggro_time': 16.0,  # seconds monster stays aggroed after losing sight of player
        'damage_aggro_time': 40.0,  # seconds monster stays aggroed after taking damage
        'movement_speed': 1.5,
        'knockback_resistance': 0.9,  # 0-1; higher = less knockback
        'drops': [
        ],
    }
]
