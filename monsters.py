# Monster type definitions for RLDungeonGenerator
# Each monster type is a dict with:
# - name: monster name
# - glyph_index: index in the tileset (row * 32 + col)
# - health: health points
# - levels: list of level names where this monster appears (empty list means all levels)

MONSTER_TYPES = [
    {
        'name': 'Boar',
        'glyph_index': 3 * 32 + 1,  # Row 3, Column 1
        'health': 10,
        'xp_value': 18,
        'levels': ['Meadows', 'Eikthyr Bossfight'],
        'aggro_distance': 5.0,  # tiles
        'aggro_time': 4.0,  # seconds monster stays aggroed after losing sight of player
        'damage_aggro_time': 10.0,  # seconds monster stays aggroed after taking damage
        'movement_speed': 1.0,  # tiles per second
        'knockback_resistance': 0.7,  # 0-1; higher = less knockback
    },
    {
        'name': 'Greyling',
        'glyph_index': 3 * 32 + 2,  # Row 3, Column 2
        'health': 20,
        'xp_value': 18,
        'levels': ['Meadows', 'Eikthyr Bossfight', 'Black Forest', 'Troll Cave', 'The Elder Bossfight', 'Ocean'],
        'aggro_distance': 5.0,  # tiles
        'aggro_time': 4.0,  # seconds monster stays aggroed after losing sight of player
        'damage_aggro_time': 10.0,  # seconds monster stays aggroed after taking damage
        'movement_speed': 1.5,
        'knockback_resistance': 0.5,  # 0-1; higher = less knockback
    },
]