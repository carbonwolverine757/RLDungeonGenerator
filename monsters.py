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
    },
    {
        'name': 'Greyling',
        'glyph_index': 3 * 32 + 2,  # Row 3, Column 2
        'health': 20,
        'levels': ['Black Forest'],
    },
]