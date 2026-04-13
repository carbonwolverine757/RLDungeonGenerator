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
        'levels': ['Meadows'],
        'aggro_distance': 5,
        'movement_speed': 1.0,  # tiles per second
    },
    {
        'name': 'Greyling',
        'glyph_index': 3 * 32 + 2,  # Row 3, Column 2
        'health': 20,
        'levels': ['Meadows', 'Black Forest'],
        'aggro_distance': 7,
        'movement_speed': 1.5,
    },
]