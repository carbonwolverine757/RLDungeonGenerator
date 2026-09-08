# Crafting recipe definitions for RLDungeonGenerator.
# Each recipe is a dict with:
# - 'Name': the recipe's display name, shown on its button in the crafting menu.
#   It matches the name of the weapon in weapons.py that the recipe produces.
# - 'Crafting Cost': list of what the craft consumes. Each entry has a 'Name'
#   that refers to a drop in Drops.py and a 'Count' of how many are required.
# - 'Crafted Item': list of what the craft produces. Each entry has a 'Name' and
#   a 'Count' of how many are made. Today every recipe produces the weapon it is
#   named after, but the shape allows a recipe to yield drops or several items.
#
# The player crafts at the Workbench in the top-right corner of the base
# structure. Costs are spent from, and products added to, the same inventory
# that monster drops fill, so a 'Crafted Item' name may refer to either a drop
# in Drops.py or a weapon in weapons.py.
#
# Materials are tiered by the biome of the monster that drops them: Flint and
# Stone in the Meadows, Bronze in the Black Forest, Iron in the Swamps.

RECIPES = [
    {
        'Name': 'Flint Spear',
        'Crafting Cost': [
            {'Name': 'Wood', 'Count': 10},
            {'Name': 'Flint', 'Count': 4},
            {'Name': 'Stone', 'Count': 2},
        ],
        'Crafted Item': [
            {'Name': 'Flint Spear', 'Count': 1},
        ],
    },
    {
        'Name': 'Bronze Spear',
        'Crafting Cost': [
            {'Name': 'Wood', 'Count': 10},
            {'Name': 'Bronze', 'Count': 6},
            {'Name': 'Leather Scraps', 'Count': 2},
        ],
        'Crafted Item': [
            {'Name': 'Bronze Spear', 'Count': 1},
        ],
    },
    {
        'Name': 'Iron Spear',
        'Crafting Cost': [
            {'Name': 'Wood', 'Count': 10},
            {'Name': 'Iron', 'Count': 8},
            {'Name': 'Leather Scraps', 'Count': 2},
        ],
        'Crafted Item': [
            {'Name': 'Iron Spear', 'Count': 1},
        ],
    },
    {
        'Name': 'Bronze Sword',
        'Crafting Cost': [
            {'Name': 'Wood', 'Count': 8},
            {'Name': 'Bronze', 'Count': 8},
            {'Name': 'Leather Scraps', 'Count': 2},
        ],
        'Crafted Item': [
            {'Name': 'Bronze Sword', 'Count': 1},
        ],
    },
    {
        'Name': 'Iron Sword',
        'Crafting Cost': [
            {'Name': 'Wood', 'Count': 8},
            {'Name': 'Iron', 'Count': 10},
            {'Name': 'Leather Scraps', 'Count': 3},
        ],
        'Crafted Item': [
            {'Name': 'Iron Sword', 'Count': 1},
        ],
    },
    {
        'Name': 'Bronze Axe',
        'Crafting Cost': [
            {'Name': 'Wood', 'Count': 6},
            {'Name': 'Bronze', 'Count': 8},
            {'Name': 'Leather Scraps', 'Count': 3},
        ],
        'Crafted Item': [
            {'Name': 'Bronze Axe', 'Count': 1},
        ],
    },
    {
        'Name': 'Iron Axe',
        'Crafting Cost': [
            {'Name': 'Wood', 'Count': 6},
            {'Name': 'Iron', 'Count': 10},
            {'Name': 'Leather Scraps', 'Count': 4},
        ],
        'Crafted Item': [
            {'Name': 'Iron Axe', 'Count': 1},
        ],
    },
]
