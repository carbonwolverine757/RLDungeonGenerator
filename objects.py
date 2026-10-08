# Object type definitions for RLDungeonGenerator
# Each object type is a dict with:
# - name: object name
# - health: health points (same system as monsters)
# - glyph_index: tileset index, declared by row and column in Glyph_Grimoire.py
# - levels: list of the levels where this object appears. Each entry is a dict with
#   'name' (the level name) and 'spawn_count' (how many of this object to place on
#   that level), so the amount can be tuned per level. An empty list means the
#   object appears on all levels, using 'default_spawn_count'.
# - default_spawn_count: count used for levels not listed individually (only
#   consulted when 'levels' is empty)
# - drops: list of items yielded when the object is destroyed, in the same format
#   as monster drops (see monsters.py). Each entry is a dict with 'name' (a drop
#   defined in Drops.py) and 'drop_chance' (integer part always drops; fractional
#   part is the probability of one extra).

try:
    from .Glyph_Grimoire import (
        OBJECT_BEECH_TREE,
        OBJECT_CAVE_ROCK,
        OBJECT_ROCK,
    )
except ImportError:
    from Glyph_Grimoire import (
        OBJECT_BEECH_TREE,
        OBJECT_CAVE_ROCK,
        OBJECT_ROCK,
    )

OBJECT_TYPES = [
    {
        'name': 'Beech Tree',
        'health': 20,
        'glyph_index': OBJECT_BEECH_TREE,
        'levels': [
            {'name': 'Meadows', 'spawn_count': 20},
            {'name': 'Black Forest', 'spawn_count': 625},
        ],
        'display_size': 2,  # renders as 2×2 tiles, centered on anchor tile
        'drops': [
            {'name': 'Wood', 'drop_chance': 4.0},
            {'name': 'Resin', 'drop_chance': 0.5},
        ],
    },
    {
        'name': 'Rock',
        'health': 30,
        'glyph_index': OBJECT_ROCK,
        'levels': [
            {'name': 'Meadows', 'spawn_count': 10},
            {'name': 'Black Forest', 'spawn_count': 10},
            {'name': 'Swamps', 'spawn_count': 10},
            {'name': 'Plains', 'spawn_count': 10},
            {'name': 'Fuling Village', 'spawn_count': 10},
            {'name': 'Ashlands', 'spawn_count': 10},
            {'name': 'Ashlands (Inland)', 'spawn_count': 10},
            {'name': 'Ashlands Coast', 'spawn_count': 10},
        ],
        'drops': [
            {'name': 'Stone', 'drop_chance': 3.0},
            {'name': 'Flint', 'drop_chance': 0.3},
        ],
    },
    {
        'name': 'Cave Rock',
        'health': 30,
        'glyph_index': OBJECT_CAVE_ROCK,
        'levels': [
            {'name': 'Burial Chambers', 'spawn_count': 5},
            {'name': 'Troll Cave', 'spawn_count': 5},
            {'name': 'Smoldering Tomb', 'spawn_count': 5},
            {'name': 'Sunken Crypts', 'spawn_count': 5},
            {'name': 'Mountains', 'spawn_count': 5},
            {'name': 'Ice Caves', 'spawn_count': 5},
            {'name': 'Howling Caverns', 'spawn_count': 5},
            {'name': 'Mistlands', 'spawn_count': 5},
            {'name': 'Mistlands Coast', 'spawn_count': 5},
            {'name': 'Dvergr Outpost', 'spawn_count': 5},
            {'name': 'Giant Remains', 'spawn_count': 5},
            {'name': 'Infested Mines', 'spawn_count': 5},
            {'name': 'Sealed Tower', 'spawn_count': 5},
            {'name': 'Putrid Hole', 'spawn_count': 5},
            {'name': 'Charred Fortress', 'spawn_count': 5},
            {'name': 'First Mysterious Location', 'spawn_count': 5},
            {'name': 'Second Mysterious Location', 'spawn_count': 5},
            {'name': 'Tomb of Lord Reto', 'spawn_count': 5},
        ],
        'drops': [
            {'name': 'Stone', 'drop_chance': 3.0},
        ],
    },
]
