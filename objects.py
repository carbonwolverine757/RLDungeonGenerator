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
        'name': 'Outdoor Rock',
        'health': 30,
        'glyph_index': 4 * 32 + 1,  # Row 4, Column 1
        'levels': ['Meadows', 'Black Forest', 'Swamps', 'Plains',
                   'Fuling Village', 'Ashlands', 'Ashlands (Inland)', 'Ashlands Coast'],
        'spawn_count': 5,
    },
    {
        'name': 'Cave Rock',
        'health': 30,
        'glyph_index': 4 * 32 + 2,  # Row 4, Column 2 — adjust once tileset glyph confirmed
        'levels': ['Burial Chambers', 'Troll Cave', 'Smoldering Tomb', 'Sunken Crypts',
                   'Mountains', 'Ice Caves', 'Howling Caverns', 'Mistlands',
                   'Mistlands Coast', 'Dvergr Outpost', 'Giant Remains', 'Infested Mines',
                   'Sealed Tower', 'Putrid Hole', 'Charred Fortress',
                   'First Mysterious Location', 'Second Mysterious Location', 'Tomb of Lord Reto'],
        'spawn_count': 5,
    },
]
