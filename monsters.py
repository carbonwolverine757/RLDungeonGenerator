# Monster type definitions for RLDungeonGenerator
# Each monster type is a dict with:
# - name: monster name
# - glyph_index: index in the tileset (row * 32 + col)
# - health: health points
# - levels: list of level names where this monster appears (empty list means all levels)
# - drops: list of items dropped when the monster is defeated. Each item is a dict
#   with 'name', 'drop_chance', and 'glyph'. The drop_chance is the (possibly
#   fractional) number of that item dropped: the integer part always drops, and the
#   fractional part is the probability of dropping one extra (e.g. 0.5 -> 1 half the
#   time; 1.2 -> 1 most of the time, 2 twenty percent of the time). Each entry is
#   rolled independently, even if the same item name appears more than once. The
#   'glyph' is the item's tileset index (row * 32 + col) used to draw it in the
#   inventory. (Wood/Resin art isn't painted into the tileset yet, so those cells
#   currently show the placeholder glyph.)

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
        'drops': [
            {'name': 'Boar Meat', 'drop_chance': 1.5, 'glyph': 10 * 32 + 1},      # Row 10, Column 1
            {'name': 'Leather Scraps', 'drop_chance': 1.2, 'glyph': 10 * 32 + 0},  # Row 10, Column 0
        ],
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
        'drops': [
            {'name': 'Resin', 'drop_chance': 1.0, 'glyph': 10 * 32 + 3},  # Row 10, Column 3 (art TBD)
            {'name': 'Wood', 'drop_chance': 0.5, 'glyph': 10 * 32 + 2},   # Row 10, Column 2 (art TBD)
        ],
    },
]
