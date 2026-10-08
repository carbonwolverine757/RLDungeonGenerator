# Glyph Grimoire: the single reference for everything about the glyph tileset.
#
# The tileset is a grid of square glyph cells, TILESET_COLUMNS wide and
# TILESET_ROWS tall, each GLYPH_SIZE pixels on a side. A glyph is addressed by
# its tileset index, row * TILESET_COLUMNS + col (row and column are 0-based,
# counted from the top-left cell). Every glyph below is declared by its row and
# column through glyph(), so nothing else in the codebase should do that math
# itself or know how wide the sheet is.

import os

# --- Sheet geometry ---------------------------------------------------------

TILESET_FILENAME = 'unicode_tileset_64.png'
TILESET_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'assets', 'tilesets', TILESET_FILENAME)
TILESET_COLUMNS = 32  # glyphs per row
TILESET_ROWS = 25     # rows of glyphs (the sheet is 2048 x 1600 pixels)
GLYPH_SIZE = 64       # pixel width and height of one glyph cell


def glyph(row, col):
    """Return the tileset index of the glyph at (row, col)."""
    assert 0 <= row < TILESET_ROWS, f"glyph row {row} is off the tileset"
    assert 0 <= col < TILESET_COLUMNS, f"glyph column {col} is off the tileset"
    return row * TILESET_COLUMNS + col


def glyph_row_col(index):
    """Return the (row, col) of a tileset index; the inverse of glyph()."""
    return divmod(index, TILESET_COLUMNS)


# --- Row 3: monsters ---------------------------------------------------------

MONSTER_BOAR = glyph(3, 1)
MONSTER_GREYLING = glyph(3, 2)
MONSTER_EIKTHYR = glyph(3, 3)
MONSTER_NECK = glyph(3, 4)      # art TBD
MONSTER_SKELETON = glyph(3, 5)  # art TBD
MONSTER_DRAUGR = glyph(3, 6)    # art TBD

# --- Row 4: objects ----------------------------------------------------------

OBJECT_ROCK = glyph(4, 1)
OBJECT_CAVE_ROCK = glyph(4, 2)  # adjust once tileset glyph confirmed

# --- Row 7: structures and terrain -------------------------------------------

# Workbench sits in the base's top-right interior corner. (Art TBD.)
STRUCTURE_WORKBENCH = glyph(7, 12)
# The fixed "base" structure placed at the center of openspace maps.
STRUCTURE_BASE_DOOR = glyph(7, 13)   # walkable for the player, blocked for monsters
STRUCTURE_BASE_WALL = glyph(7, 14)   # solid border, not walkable
STRUCTURE_BASE_FLOOR = glyph(7, 15)  # walkable interior
# Corridor doors in room-and-corridor dungeons.
STRUCTURE_DOOR = glyph(7, 15)

OBJECT_BEECH_TREE = glyph(7, 14)

# Floor and wall tiles; levels.py picks one of these for each.
TERRAIN_GRASS = glyph(7, 16)
TERRAIN_WATER = glyph(7, 17)
TERRAIN_SNOW = glyph(7, 18)
TERRAIN_STONE = glyph(7, 19)
TERRAIN_DIRT = glyph(7, 20)
TERRAIN_7_21 = glyph(7, 21)  # art TBD
TERRAIN_7_22 = glyph(7, 22)  # art TBD
# Shared wall/floor glyph used before levels chose their own.
TERRAIN_WALL_FLOOR = TERRAIN_GRASS

# --- Row 9: exits ------------------------------------------------------------

STRUCTURE_EXIT = glyph(9, 23)

# --- Row 10: drops / inventory items -----------------------------------------

ITEM_LEATHER_SCRAPS = glyph(10, 0)
ITEM_BOAR_MEAT = glyph(10, 1)
ITEM_WOOD = glyph(10, 2)    # art TBD
ITEM_RESIN = glyph(10, 3)   # art TBD
ITEM_STONE = glyph(10, 4)   # art TBD
ITEM_FLINT = glyph(10, 5)   # art TBD
ITEM_BRONZE = glyph(10, 6)  # art TBD
ITEM_IRON = glyph(10, 7)    # art TBD

# --- Row 11: weapons ---------------------------------------------------------

# Art is shared per weapon type; material is not yet distinguished. (Art TBD.)
WEAPON_SPEAR = glyph(11, 0)
WEAPON_SWORD = glyph(11, 1)
WEAPON_AXE = glyph(11, 2)

# --- Row 23: skills ----------------------------------------------------------

# Art is shared across skill trees; the background color tells them apart.
SKILL_BOLT = glyph(23, 0)
SKILL_LANCE = glyph(23, 1)
SKILL_BALL = glyph(23, 2)
SKILL_BURST = glyph(23, 3)
SKILL_CONE = glyph(23, 4)
SKILL_SPEAR = glyph(23, 5)
SKILL_ARC = glyph(23, 6)
