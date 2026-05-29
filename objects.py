# Object type definitions for RLDungeonGenerator
# Each object type is a dict with:
# - name: object name
# - health: health points (same system as monsters)
# - glyph_index: index in the tileset (row * 32 + col)
# - levels: list of level names where this object appears (empty list means all levels)
# - spawn_count: total number of this object placed on the map

OBJECT_TYPES = [
    {
        'name': 'Beech Tree',
        'health': 20,
        'glyph_index': 4 * 32 + 0,  # Row 4, Column 0
        'levels': ['Meadows', 'Black Forest'],
        'spawn_count': 8,
    },
    {
        'name': 'Rock',
        'health': 30,
        'glyph_index': 4 * 32 + 1,  # Row 4, Column 1
        'levels': [],  # empty = all levels
        'spawn_count': 5,
    },
]
