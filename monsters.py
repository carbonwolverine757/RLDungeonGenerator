# Monster type definitions for RLDungeonGenerator
# Each monster type is a dict with:
# - name: monster name
# - glyph_index: index in the tileset (row * 32 + col)
# - health: health points
# - size: side length N of the N×N block of tiles the monster occupies (default 1).
#   Movement, collision, pathfinding, and rendering all operate on this footprint.
# - respawns: whether a killed monster may be replaced (default True). Set False for
#   bosses and other one-off encounters: the spawner then counts every monster of that
#   type it has ever created on the current map, so once 'max_count' has been spawned
#   the type is finished for that map even after the player kills it.
# - levels: list of the levels where this monster appears. Each entry is a dict with
#   'name'           the level name,
#   'max_count'      the most of this monster that may be *alive* on that level at once,
#   'spawn_interval' seconds that must pass after a successful spawn before this
#                    monster may spawn again, and
#   'spawn_chance'   the 0.0-1.0 probability that a single spawn attempt succeeds.
#   Maps generate with no monsters at all. Everything arrives through the runtime
#   spawner (RLDungeonGenerator.update_spawning), which runs a tick every few seconds
#   and gives each eligible type one independent attempt. The interval is *global per
#   monster type*, not per region, so at most one of a type can appear per
#   'spawn_interval' no matter how big the map is. A failed chance roll, a map already
#   at 'max_count', or a map with nowhere legal to put the monster all fail the attempt
#   *without* restarting the interval, so the type simply retries on the next tick.
#   Because 'max_count' counts the living, killing one frees a slot for a replacement.
#   An empty 'levels' list means the monster appears on every level using the spawner's
#   built-in defaults; a 'max_count' of None means uncapped, which is not appropriate
#   under a runtime spawner because the population would grow without bound.
# - drops: list of items dropped when the monster is defeated. Each item is a dict
#   with 'name' and 'drop_chance'. The 'name' refers to a drop defined in Drops.py,
#   which supplies the glyph used to draw it. The drop_chance is the (possibly
#   fractional) number of that item dropped: the integer part always drops, and the
#   fractional part is the probability of dropping one extra (e.g. 0.5 -> 1 half the
#   time; 1.2 -> 1 most of the time, 2 twenty percent of the time). Each entry is
#   rolled independently, even if the same item name appears more than once.

MONSTER_TYPES = [
    {
        'name': 'Boar',
        'glyph_index': 3 * 32 + 1,  # Row 3, Column 1
        'health': 10,
        'size': 1,  # occupies a 1x1 block of tiles
        'xp_value': 18,
        'levels': [
            # One boar roughly every 15s (12s interval, then ~1 retry at 60%), so the
            # map reaches its 12 in about three minutes.
            {'name': 'Meadows', 'max_count': 12, 'spawn_interval': 12.0, 'spawn_chance': 0.6},
        ],
        'aggro_distance': 5.0,  # tiles
        'aggro_time': 4.0,  # seconds monster stays aggroed after losing sight of player
        'damage_aggro_time': 10.0,  # seconds monster stays aggroed after taking damage
        'movement_speed': 1.0,  # tiles per second
        'knockback_resistance': 0.7,  # 0-1; higher = less knockback
        'drops': [
            {'name': 'Boar Meat', 'drop_chance': 1.5},
            {'name': 'Leather Scraps', 'drop_chance': 1.2},
        ],
    },
    {
        'name': 'Greyling',
        'glyph_index': 3 * 32 + 2,  # Row 3, Column 2
        'health': 20,
        'size': 1,  # occupies a 1x1 block of tiles
        'xp_value': 18,
        'levels': [
            {'name': 'Meadows', 'max_count': 8, 'spawn_interval': 16.0, 'spawn_chance': 0.5},
            # Their home biome: arrive faster and pack in three times as thick.
            {'name': 'Black Forest', 'max_count': 24, 'spawn_interval': 8.0, 'spawn_chance': 0.75},
        ],
        'aggro_distance': 5.0,  # tiles
        'aggro_time': 4.0,  # seconds monster stays aggroed after losing sight of player
        'damage_aggro_time': 10.0,  # seconds monster stays aggroed after taking damage
        'movement_speed': 1.5,
        'knockback_resistance': 0.5,  # 0-1; higher = less knockback
        'drops': [
            {'name': 'Resin', 'drop_chance': 1.0},
            {'name': 'Wood', 'drop_chance': 0.5},
        ],
    },
    {
        'name': 'Eikthyr',
        'glyph_index': 3 * 32 + 3,  # Row 3, Column 3
        'health': 500,
        'size': 4,  # occupies a 4x4 block of tiles
        'xp_value': 240,
        'respawns': False,  # killed for good; the arena does not refill
        'levels': [
            # Interval 0 and a certain roll put him on the map on the very first spawn
            # tick, so the player never walks into an empty arena.
            {'name': 'Eikthyr Bossfight', 'max_count': 1, 'spawn_interval': 0.0, 'spawn_chance': 1.0},
        ],
        'aggro_distance': 500.0,  # tiles
        'aggro_time': 16.0,  # seconds monster stays aggroed after losing sight of player
        'damage_aggro_time': 40.0,  # seconds monster stays aggroed after taking damage
        'movement_speed': 1.5,
        'knockback_resistance': 0.99,  # 0-1; higher = less knockback
        'drops': [
        ],
    }
]
