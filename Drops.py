# Drop item definitions for RLDungeonGenerator.
# Each drop is a dict with:
# - name: the item's name (referenced by monster 'drops' entries in monsters.py)
# - glyph: the item's tileset index (row * 32 + col) used to draw it in the inventory
#
# Monsters list which drops they can yield (and how likely) in monsters.py; those
# entries refer to the drops here by name to determine which glyph to display.
# (Wood/Resin art isn't painted into the tileset yet, so those cells currently
# show the placeholder glyph.)

DROPS = [
    {'name': 'Boar Meat', 'glyph': 10 * 32 + 1},       # Row 10, Column 1
    {'name': 'Leather Scraps', 'glyph': 10 * 32 + 0},  # Row 10, Column 0
    {'name': 'Resin', 'glyph': 10 * 32 + 3},           # Row 10, Column 3 (art TBD)
    {'name': 'Wood', 'glyph': 10 * 32 + 2},            # Row 10, Column 2 (art TBD)
]
