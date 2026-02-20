# Level definitions for RLDungeonGenerator
# Each level is a dict with:
# - name: level name
# - floor_glyph: character used for floor tiles
# - wall_glyph: character used for wall tiles
# - fog_glyph: character used when showing unexplored tiles (optional)
# - floor_bg: RGB tuple for floor background color
# - wall_bg: RGB tuple for wall background color
# - fog_bg: RGB tuple for fog background color
# - floor_fg, wall_fg, fog_fg: optional foreground colors

LEVELS = [
    {
        'name': 'Meadows',
        'floor_glyph': '\u00B7',
        'wall_glyph': '\u2588',
        'fog_glyph': ' ',
        'floor_bg': (101, 164, 34),
        'wall_bg': (50, 82, 17),
        'fog_bg': (75, 123, 25),
        'floor_fg': (40, 160, 30),
        'wall_fg': (20, 100, 20),
        'fog_fg': (35, 140, 20),
    },
    {
        'name': 'Black Forest',
        'floor_glyph': '\u00B7',
        'wall_glyph': '\u2588',
        'fog_glyph': ' ',
        'floor_bg': (90, 80, 50),
        'wall_bg': (50, 82, 17),
        'fog_bg': (75, 123, 25),
        'floor_fg': (200, 200, 200),
        'wall_fg': (180, 180, 180),
        'fog_fg': (120, 120, 120),
    },
    {
        'name': 'Sandy Halls',
        'floor_glyph': ',',
        'wall_glyph': '%',
        'fog_glyph': ' ',
        'floor_bg': (101, 164, 34),
        'wall_bg': (50, 82, 17),
        'fog_bg': (75, 123, 25),
        'floor_fg': (120, 80, 40),
        'wall_fg': (90, 60, 30),
        'fog_fg': (100, 90, 70),
    },
]
