# Drop item definitions for RLDungeonGenerator.
# Each drop is a dict with:
# - name: the item's name (referenced by monster 'drops' entries in monsters.py)
# - glyph: the item's tileset index (declared by row and column in Glyph_Grimoire.py)
#   used to draw it in the inventory
#
# Monsters list which drops they can yield (and how likely) in monsters.py; those
# entries refer to the drops here by name to determine which glyph to display.
# (Wood/Resin art isn't painted into the tileset yet, so those cells currently
# show the placeholder glyph.)

try:
    from .Glyph_Grimoire import (
        ITEM_BOAR_MEAT,
        ITEM_BRONZE,
        ITEM_FLINT,
        ITEM_IRON,
        ITEM_LEATHER_SCRAPS,
        ITEM_RESIN,
        ITEM_STONE,
        ITEM_WOOD,
    )
except ImportError:
    from Glyph_Grimoire import (
        ITEM_BOAR_MEAT,
        ITEM_BRONZE,
        ITEM_FLINT,
        ITEM_IRON,
        ITEM_LEATHER_SCRAPS,
        ITEM_RESIN,
        ITEM_STONE,
        ITEM_WOOD,
    )

DROPS = [
    {'name': 'Boar Meat', 'glyph': ITEM_BOAR_MEAT},
    {'name': 'Leather Scraps', 'glyph': ITEM_LEATHER_SCRAPS},
    {'name': 'Resin', 'glyph': ITEM_RESIN},
    {'name': 'Wood', 'glyph': ITEM_WOOD},
    # Crafting materials. Recipes in Recipes.py spend these; the monsters that
    # yield them are tiered by biome (Neck/Meadows, Skeleton/Black Forest,
    # Draugr/Swamps) so the better materials arrive with the later levels.
    {'name': 'Stone', 'glyph': ITEM_STONE},
    {'name': 'Flint', 'glyph': ITEM_FLINT},
    {'name': 'Bronze', 'glyph': ITEM_BRONZE},
    {'name': 'Iron', 'glyph': ITEM_IRON},
]
