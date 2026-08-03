# Object type definitions for RLDungeonGenerator
# Each object type is a dict with:
# - name: object name
# - health: health points (same system as monsters)
# - glyph_index: index in the tileset (row * 32 + col)
# - levels: list of the levels where this object appears. Each entry is a dict with
#   'name' (the level name) and 'spawn_count' (how many of this object to place on
#   that level), so the amount can be tuned per level. An empty list means the
#   object appears on all levels, using 'default_spawn_count'.
# - default_spawn_count: count used for levels not listed individually (only
#   consulted when 'levels' is empty)

OBJECT_TYPES = [
    {
        'name': 'Beech Tree',
        'health': 20,
        'glyph_index': 7 * 32 + 14,  # Row 7, Column 14
        'levels': [
            {'name': 'Meadows', 'spawn_count': 20},
            {'name': 'Black Forest', 'spawn_count': 625},
        ],
        'display_size': 2,  # renders as 2×2 tiles, centered on anchor tile
    },
    {
        'name': 'Rock',
        'health': 30,
        'glyph_index': 4 * 32 + 1,  # Row 4, Column 1
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
    },
    {
        'name': 'Cave Rock',
        'health': 30,
        'glyph_index': 4 * 32 + 2,  # Row 4, Column 2 — adjust once tileset glyph confirmed
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
    },
]
