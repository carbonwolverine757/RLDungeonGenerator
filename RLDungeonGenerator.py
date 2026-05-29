# This code is released into the Public Domain.
from math import sqrt
from random import random
from random import randrange
from random import choice
import argparse
import os
import sys
import time
import traceback
import logging
from collections import deque

# Glyph index for walls & floors in the generated Unicode tilesheet.
# The tilesheet is built by `generate_unicode_tileset.py` with `cols=32`,
# so each row has 32 tiles. We want the glyph at:
#   - row = 7 (0-based, i.e. 8th row from top)
#   - col = 16 (0-based, i.e. 17th column from left)
# Index = row * cols + col = 7 * 32 + 16 = 240.
WALL_FLOOR_GLYPH_INDEX = 7 * 32 + 16
# Glyph index for doors in the generated Unicode tilesheet.
# Use tile at row = 7, col = 15 (0-based). Index = 7 * 32 + 15 = 239.
DOOR_GLYPH_INDEX = 7 * 32 + 15
# Glyph index for exits in the generated Unicode tilesheet.
# Use tile at row = 7, col = 17 (0-based). Index = 7 * 32 + 17 = 241.
EXIT_GLYPH_INDEX = 7 * 32 + 17

# Visual tuning (higher contrast)
# - Walls vs floors are differentiated primarily by background color.
# - Fog-of-war is rendered much darker than explored tiles.
COLOR_WALL_BG = (50, 82, 17)
COLOR_FLOOR_BG = (101, 164, 34)
# Fog-of-war background for unexplored tiles (green tint)
COLOR_FOG_BG = (75, 123, 25)
# Foreground (glyph) colors
COLOR_WALL_FG = (20, 100, 20)
COLOR_FLOOR_FG = (40, 160, 30)
COLOR_FOG_FG = (35, 140, 20)

try:
    import pygame
    _pygame_import_error = None
except Exception:
    pygame = None
    import traceback as _tb2
    _pygame_import_error = _tb2.format_exc()

# Level configurations live in `levels.py`
try:
    from .levels import LEVELS
except Exception:
    try:
        from levels import LEVELS
    except Exception:
        LEVELS = []

# Monster type configurations live in `monsters.py`
try:
    from .monsters import MONSTER_TYPES
except Exception:
    try:
        from monsters import MONSTER_TYPES
    except Exception:
        MONSTER_TYPES = []

# Weapon configurations live in `weapons.py`
try:
    from .weapons import WEAPONS
except Exception:
    try:
        from weapons import WEAPONS
    except Exception:
        WEAPONS = []

# Object type configurations live in `objects.py`
try:
    from .objects import OBJECT_TYPES
except Exception:
    try:
        from objects import OBJECT_TYPES
    except Exception:
        OBJECT_TYPES = []

# Prefer tcod for alternative rendering when available (import after pygame to avoid SDL DLL conflicts)
try:
    import tcod
    import tcod.tileset
    import tcod.image
    _tcod_import_error = None
except Exception as e:
    tcod = None
    import traceback as _tb
    _tcod_import_error = _tb.format_exc()

# Configure simple console logging so import/initialization diagnostics are visible
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

def _print_pygame_diagnostics():
    if pygame is None:
        logging.error("pygame import failed. Traceback:\n%s", _pygame_import_error)
        return
    # pygame imported successfully; show useful attributes
    try:
        logging.info("pygame imported from: %s", getattr(pygame, '__file__', '<builtin>'))
    except Exception:
        logging.exception("Failed reading pygame.__file__")
    try:
        ver = None
        if hasattr(pygame, 'version'):
            try:
                # pygame.version may be a module or object
                ver = getattr(pygame.version, 'ver', None) or getattr(pygame, 'version', None)
            except Exception:
                ver = getattr(pygame, 'version', None)
        logging.info("pygame version: %s", ver)
    except Exception:
        logging.exception("Failed reading pygame version")
    try:
        init_state = None
        if hasattr(pygame, 'get_init'):
            init_state = pygame.get_init()
            logging.info("pygame.get_init()=%s", init_state)
    except Exception:
        logging.exception("pygame.get_init() check failed")

    # Attempt a non-invasive init check: call pygame.init() inside try/except so any
    # failures are printed but won't crash the module import.
    try:
        init_ret = pygame.init()
        logging.info("pygame.init() returned: %s", init_ret)
    except Exception:
        logging.exception("pygame.init() raised an exception")

# Print diagnostics immediately so the console shows why pygame may be unavailable
_print_pygame_diagnostics()

# numpy is optional only required for pixel rendering path
try:
    import numpy as np
except Exception:
    np = None

class DungeonSqr:
    # Tile types
    WALL = 'wall'
    FLOOR = 'floor'
    DOOR = 'door'
    EXIT = 'exit'
    
    def __init__(self, glyph: str, tile_type: str = 'wall'):
        self.glyph = glyph
        self.tile_type = tile_type

    def get_ch(self) -> str:
        """Return the glyph character for rendering."""
        return self.glyph

class Room:
    def __init__(self, r, c, h, w):
        self.row = r
        self.col = c
        self.height = h
        self.width = w

class RLDungeonGenerator:
    def __init__(self, w, h):
        self.MAX = 15 # Cutoff for when we want to stop dividing sections
        self.width = w
        self.height = h
        self.leaves = []
        self.dungeon = []
        self.rooms = []
        self.player_row = 0
        self.player_col = 0
        self.tile_size = 16
        self.player_x = 0.0
        self.player_y = 0.0
        # Movement speed expressed as tiles per second; converted to pixels/sec below
        self.player_speed_tiles_per_sec = 3.0
        self.player_speed_pixels = self.player_speed_tiles_per_sec * self.tile_size
        self.player_radius = self.tile_size * 0.5
        self.last_revealed_tile = (-1, -1)
        # Levels and current index
        self.levels = LEVELS or []
        self.current_level_index = 0
        # Exit position (row, col) when placed
        self.exit_pos = None
        # Whether current level uses openspace generation
        self.uses_openspace = False
        # Player health and stamina
        self.max_health = 25
        self.health = self.max_health
        self.max_stamina = 50
        self.stamina = self.max_stamina
        # Monsters list (each monster is a dict with 'type', 'row', 'col', 'health')
        self.monsters = []
        # Objects list (each object is a dict with 'type', 'row', 'col', 'health')
        self.objects = []
        # Equipped weapon (defaults to first weapon in WEAPONS)
        self.equipped_weapon = WEAPONS[0] if WEAPONS else None
        # Active attack effects (visual only)
        self.attack_effects = []  # each entry: {'tiles': set((r,c)), 'expires_at': float}
        # Damage popups (visual feedback for damage dealt)
        self.damage_popups = []  # each entry: {'row': int, 'col': int, 'damage': int, 'expires_at': float}
        # Apply initial level (sets glyphs/colors)
        self.apply_level(self.current_level_index)
        # Exit position (row, col) when placed
        self.exit_pos = None

        for h in range(self.height):
            row = []
            for w in range(self.width):
                row.append(DungeonSqr(self.wall_glyph))
            self.dungeon.append(row)

        # Fog-of-war explored grid (all unexplored initially)
        self.explored = [[False for _ in range(self.width)] for _ in range(self.height)]

    def random_split(self, min_row, min_col, max_row, max_col):
        # We want to keep splitting until the sections get down to the threshold
        seg_height = max_row - min_row
        seg_width = max_col - min_col

        if seg_height < self.MAX and seg_width < self.MAX:
            self.leaves.append((min_row, min_col, max_row, max_col))
        elif seg_height < self.MAX and seg_width >= self.MAX:
            self.split_on_vertical(min_row, min_col, max_row, max_col)
        elif seg_height >= self.MAX and seg_width < self.MAX:
            self.split_on_horizontal(min_row, min_col, max_row, max_col)
        else:
                if random() < 0.5:
                    self.split_on_horizontal(min_row, min_col, max_row, max_col)
                else:
                    self.split_on_vertical(min_row, min_col, max_row, max_col)
     
    def split_on_horizontal(self, min_row, min_col, max_row, max_col):
        split = (min_row + max_row) // 2 + choice((-2, -1, 0, 1, 2))
        self.random_split(min_row, min_col, split, max_col)
        self.random_split(split + 1, min_col, max_row, max_col)

    def split_on_vertical(self, min_row, min_col, max_row, max_col):        
        split = (min_col + max_col) // 2 + choice((-2, -1, 0, 1, 2))
        self.random_split(min_row, min_col, max_row, split)
        self.random_split(min_row, split + 1, max_row, max_col)

    def carve_rooms(self):
        for leaf in self.leaves:
            # We don't want to fill in every possible room or the 
            # dungeon looks too uniform
            if random() > 0.80: continue
            section_width = leaf[3] - leaf[1]
            section_height = leaf[2] - leaf[0]

            # The actual room's height and width will be 60-100% of the 
            # available section. 
            room_width = round(randrange(60, 100) / 100 * section_width)
            room_height = round(randrange(60, 100) / 100 * section_height)

            # If the room doesn't occupy the entire section we are carving it from,
            # 'jiggle' it a bit in the square
            if section_height > room_height:
                room_start_row = leaf[0] + randrange(section_height - room_height)
            else:
                room_start_row = leaf[0]

            if section_width > room_width:
                room_start_col = leaf[1] + randrange(section_width - room_width)
            else:
                room_start_col = leaf[1]
    
            self.rooms.append(Room(room_start_row, room_start_col, room_height, room_width))
            for r in range(room_start_row, room_start_row + room_height):
                for c in range(room_start_col, room_start_col + room_width):
                    self.dungeon[r][c] = DungeonSqr(self.floor_glyph, DungeonSqr.FLOOR)

    def generate_openspace_map(self):
        """Generate an openspace map: huge open area with walls at edges."""
        # Fill most of the dungeon with floor tiles
        for r in range(self.height):
            for c in range(self.width):
                # Create walls at the edges (1 tile border)
                if r == 0 or r == self.height - 1 or c == 0 or c == self.width - 1:
                    self.dungeon[r][c] = DungeonSqr(self.wall_glyph, DungeonSqr.WALL)
                else:
                    self.dungeon[r][c] = DungeonSqr(self.floor_glyph, DungeonSqr.FLOOR)
        
        # Create one room in the middle for the map structure
        room_width = max(5, self.width // 4)
        room_height = max(5, self.height // 4)
        room_row = (self.height - room_height) // 2
        room_col = (self.width - room_width) // 2
        
        self.rooms.append(Room(room_row, room_col, room_height, room_width))
        for r in range(room_row, room_row + room_height):
            for c in range(room_col, room_col + room_width):
                self.dungeon[r][c] = DungeonSqr(self.floor_glyph, DungeonSqr.FLOOR)

    def are_rooms_adjacent(self, room1, room2):
        adj_rows = []
        adj_cols = []
        for r in range(room1.row, room1.row + room1.height):
            if r >= room2.row and r < room2.row + room2.height:
                adj_rows.append(r)

        for c in range(room1.col, room1.col + room1.width):
            if c >= room2.col and c < room2.col + room2.width:
                adj_cols.append(c)

        return (adj_rows, adj_cols)

    def distance_between_rooms(self, room1, room2):
        centre1 = (room1.row + room1.height // 2, room1.col + room1.width // 2)
        centre2 = (room2.row + room2.height // 2, room2.col + room2.width // 2)

        return sqrt((centre1[0] - centre2[0]) ** 2 + (centre1[1] - centre2[1]) ** 2)

    def carve_corridor_between_rooms(self, room1, room2):
        if room2[2] == 'rows':
            row = choice(room2[1])
            # Figure out which room is to the left of the other
            if room1.col + room1.width < room2[0].col:
                start_col = room1.col + room1.width
                end_col = room2[0].col
            else:
                start_col = room2[0].col + room2[0].width
                end_col = room1.col                
            for c in range(start_col, end_col):
                self.dungeon[row][c] = DungeonSqr(self.floor_glyph, DungeonSqr.FLOOR)  # Use current level's floor glyph

            if end_col - start_col >= 4:
                self.dungeon[row][start_col] = DungeonSqr('+', DungeonSqr.DOOR)
                self.dungeon[row][end_col - 1] = DungeonSqr('+', DungeonSqr.DOOR)
            elif start_col == end_col - 1:
                self.dungeon[row][start_col] = DungeonSqr('+', DungeonSqr.DOOR)
        else:
            col = choice(room2[1])
            # Figure out which room is above the other
            if room1.row + room1.height < room2[0].row:
                start_row = room1.row + room1.height
                end_row = room2[0].row
            else:
                start_row = room2[0].row + room2[0].height
                end_row = room1.row

            for r in range(start_row, end_row):
                self.dungeon[r][col] = DungeonSqr(self.floor_glyph, DungeonSqr.FLOOR)  # Use current level's floor glyph

            if end_row - start_row >= 4:
                self.dungeon[start_row][col] = DungeonSqr('+', DungeonSqr.DOOR)
                self.dungeon[end_row - 1][col] = DungeonSqr('+', DungeonSqr.DOOR)
            elif start_row == end_row - 1:
                self.dungeon[start_row][col] = DungeonSqr('+', DungeonSqr.DOOR)

    # Find two nearby rooms that are in difference groups, draw
    # a corridor between them and merge the groups
    def find_closest_unconnect_groups(self, groups, room_dict):
        shortest_distance = 99999
        start = None
        start_group = None
        nearest = None

        for group in groups:
            for room in group:
                key = (room.row, room.col)
                for other in room_dict[key]:
                    if not other[0] in group and other[3] < shortest_distance:
                        shortest_distance = other[3]
                        start = room
                        nearest = other
                        start_group = group

        self.carve_corridor_between_rooms(start, nearest)

        # Merge the groups
        other_group = None
        for group in groups:
            if nearest[0] in group:
                other_group = group
                break

        start_group += other_group
        groups.remove(other_group)
        
    def connect_rooms(self):
        # Build a dictionary containing an entry for each room. Each bucket will
        # hold a list of the adjacent rooms, weather they are adjacent along rows or 
        # columns and the distance between them.
        #
        # Also build the initial groups (which start of as a list of individual rooms)
        groups = []
        room_dict = {}
        for room in self.rooms:
            key = (room.row, room.col)
            room_dict[key] = []
            for other in self.rooms:
                other_key = (other.row, other.col)
                if key == other_key: continue
                adj = self.are_rooms_adjacent(room, other)
                if len(adj[0]) > 0:
                    room_dict[key].append((other, adj[0], 'rows', self.distance_between_rooms(room, other)))
                elif len(adj[1]) > 0:
                    room_dict[key].append((other, adj[1], 'cols', self.distance_between_rooms(room, other)))
        
            groups.append([room])
    
        while len(groups) > 1:
            self.find_closest_unconnect_groups(groups, room_dict)

    def generate_map(self):
        # Reset generation state so this can be called multiple times (e.g. when exiting)
        self.leaves = []
        self.rooms = []
        self.monsters = []  # Reset monsters list
        self.objects = []   # Reset objects list
        # Recreate dungeon filled with walls
        self.dungeon = []
        for h in range(self.height):
            row = []
            for w in range(self.width):
                row.append(DungeonSqr(self.wall_glyph, DungeonSqr.WALL))
            self.dungeon.append(row)

        # Reset fog-of-war
        self.explored = [[False for _ in range(self.width)] for _ in range(self.height)]

        # Generate using either openspace or procedural maze layout
        if self.uses_openspace:
            self.generate_openspace_map()
        else:
            # (re-)generate layout
            self.random_split(1, 1, self.height - 1, self.width - 1)
            self.carve_rooms()
            self.connect_rooms()
        
        # Place an exit tile somewhere meaningful
        self.place_exit()
        # Place the player and reveal nearby area
        self.spawn_player()
        # Place monsters scattered across the map
        self.place_monsters()
        # Place static objects across the map
        self.place_objects()
        self.reveal_current_area()

    def is_walkable(self, r, c, ignore_monster=None):
        """Return True if the tile at the given coordinates can be entered.

        Walkable tiles are floors, doors, and exits. Walls and monsters are not walkable.
        This determination is based on tile *type*, not glyph, so multiple
        characters can represent walls or floors without affecting logic.
        """
        if r < 0 or c < 0 or r >= self.height or c >= self.width:
            return False
        # Check if there's a monster at this position
        for monster in self.monsters:
            if monster is ignore_monster:
                continue
            if monster['row'] == r and monster['col'] == c:
                return False
        # Check if there's an object at this position
        for obj in self.objects:
            if obj['row'] == r and obj['col'] == c:
                return False
        tile = self.dungeon[r][c]
        return tile.tile_type in (DungeonSqr.FLOOR, DungeonSqr.DOOR, DungeonSqr.EXIT)

    # internal helpers
    def _is_floor_char(self, ch: str) -> bool:
        """Check whether *ch* represents a floor-like tile.

        The set currently includes the configured floor glyph plus door/exit
        symbols.  Anything not in this group is interpreted as a wall.
        """
        return ch in (self.floor_glyph, '+', self.exit_glyph)

    def _is_wall_char(self, ch: str) -> bool:
        """True for any character that isn’t considered floor/door/exit.

        Used by rendering and generation logic that previously compared to
        ``self.wall_glyph`` directly.  Keeping a separate method makes it
        straightforward to change behaviour later (for example, treat
        additional glyphs as non-wall).
        """
        return not self._is_floor_char(ch)

    def spawn_player(self):
        # Prefer the center of the first room if available, otherwise another tile in the same room
        if len(self.rooms) > 0:
            room = self.rooms[0]
            r = room.row + room.height // 2
            c = room.col + room.width // 2
            if self.is_walkable(r, c) and (r, c) != self.exit_pos:
                self.set_player_position(r, c)
                return
            # If center is not available, search within the room for another suitable tile
            for rr in range(room.row, room.row + room.height):
                for cc in range(room.col, room.col + room.width):
                    if self.is_walkable(rr, cc) and (rr, cc) != self.exit_pos:
                        self.set_player_position(rr, cc)
                        return
        # Fallback: search the entire map
        for r in range(self.height):
            for c in range(self.width):
                if self.is_walkable(r, c) and (r, c) != self.exit_pos:
                    self.set_player_position(r, c)
                    return

    def set_player_position(self, row, col):
        self.player_row = row
        self.player_col = col
        self.player_x = (col + 0.5) * self.tile_size
        self.player_y = (row + 0.5) * self.tile_size
        self.last_revealed_tile = (row, col)
        self.reveal_current_area()

    def update_movement(self, delta_time, input_vector):
        dx, dy = input_vector
        if dx != 0.0 or dy != 0.0:
            length = sqrt(dx * dx + dy * dy)
            dx /= length
            dy /= length
        speed = self.player_speed_pixels
        move_x = dx * speed * delta_time
        move_y = dy * speed * delta_time
        
        # Store intended direction for knockback
        intended_dx = 1 if dx > 0 else (-1 if dx < 0 else 0)
        intended_dy = 1 if dy > 0 else (-1 if dy < 0 else 0)
        
        if move_x != 0.0:
            nx = self.player_x + move_x
            if self._can_move_to(nx, self.player_y):
                self.player_x = nx
        if move_y != 0.0:
            ny = self.player_y + move_y
            if self._can_move_to(self.player_x, ny):
                self.player_y = ny
        self._update_tile_position()
        
        # Apply melee knockback based on intended movement direction
        # This applies even if the player couldn't move due to collision
        if intended_dx != 0 or intended_dy != 0:
            self.apply_melee_knockback(intended_dx, intended_dy)

    def move_by_pixels(self, dx, dy, pixels=1):
        """
        Nudge the player by a given number of pixels in integer direction (dx,dy should be -1/0/1).
        Movement is attempted axis-by-axis with collision checks.
        """
        if pixels == 0:
            return
        # Store old position to detect actual movement
        old_x = self.player_x
        old_y = self.player_y
        
        # Apply horizontal nudge
        if dx != 0:
            nx = self.player_x + dx * pixels
            if self._can_move_to(nx, self.player_y):
                self.player_x = nx
        # Apply vertical nudge
        if dy != 0:
            ny = self.player_y + dy * pixels
            if self._can_move_to(self.player_x, ny):
                self.player_y = ny
        self._update_tile_position()
        
        # Apply melee knockback if player actually moved
        actual_dx = 1 if self.player_x > old_x else (-1 if self.player_x < old_x else 0)
        actual_dy = 1 if self.player_y > old_y else (-1 if self.player_y < old_y else 0)
        if actual_dx != 0 or actual_dy != 0:
            self.apply_melee_knockback(actual_dx, actual_dy)

    def apply_melee_knockback(self, move_dx, move_dy):
        """
        Apply knockback to monsters in melee range when the player moves.
        
        Monsters adjacent to the player (within ~1.5 tiles) are pushed away
        in the direction of the player's movement, scaled by their
        knockback resistance.
        
        Args:
            move_dx, move_dy: The direction the player actually moved (-1, 0, or 1 per axis)
        """
        if not self.monsters:
            return
        
        # Base knockback distance in tiles when player moves into melee
        MELEE_KNOCKBACK_BASE = 2.0
        # Melee range in tiles (approximately 1.5 tiles = 1.5 diagonal distance)
        MELEE_RANGE = 1.5
        
        try:
            for i, monster in enumerate(self.monsters):
                # Get monster's position
                mx = monster.get('x', (monster.get('col', 0) + 0.5) * self.tile_size)
                my = monster.get('y', (monster.get('row', 0) + 0.5) * self.tile_size)
                
                # Calculate distance from player to monster (in tiles)
                dx_tiles = (mx - self.player_x) / self.tile_size
                dy_tiles = (my - self.player_y) / self.tile_size
                dist_tiles = sqrt(dx_tiles * dx_tiles + dy_tiles * dy_tiles)
                
                # Check if monster is in melee range
                if dist_tiles <= MELEE_RANGE:
                    # Skip monsters behind the player — pushing them in the movement direction
                    # would shove them through the player to the opposite side.
                    dot = dx_tiles * move_dx + dy_tiles * move_dy
                    if dot <= 0:
                        continue

                    # Get monster's knockback resistance (0-1; 1 = full knockback, 0 = immune)
                    monster_type = monster.get('type', {})
                    resistance = float(monster_type.get('knockback_resistance', 0.5))
                    resistance = max(0.0, min(1.0, resistance))  # Clamp to [0, 1]
                    
                    # Calculate knockback distance based on resistance
                    knockback_tiles = MELEE_KNOCKBACK_BASE * resistance
                    
                    if knockback_tiles > 0:
                        # Direction: along player's movement axis
                        if move_dx != 0 or move_dy != 0:
                            dir_x = float(move_dx)
                            dir_y = float(move_dy)
                            # Normalize if diagonal
                            dist = sqrt(dir_x * dir_x + dir_y * dir_y)
                            if dist > 0:
                                dir_x /= dist
                                dir_y /= dist
                        else:
                            # No movement direction; use direction away from player
                            dir_x = dx_tiles
                            dir_y = dy_tiles
                            dist = sqrt(dir_x * dir_x + dir_y * dir_y)
                            if dist > 0:
                                dir_x /= dist
                                dir_y /= dist
                            else:
                                # Monster at player center; default push
                                dir_x, dir_y = 1.0, 0.0
                        
                        # Apply knockback in pixels
                        knockback_px = knockback_tiles * self.tile_size
                        new_x = mx + dir_x * knockback_px
                        new_y = my + dir_y * knockback_px
                        
                        # Check if new position is valid (walkable, not in bounds)
                        new_r = int(new_y / self.tile_size)
                        new_c = int(new_x / self.tile_size)
                        
                        # Bounds check
                        if new_r < 0 or new_r >= self.height or new_c < 0 or new_c >= self.width:
                            continue

                        # Don't land on the player's tile
                        player_r = int(self.player_y / self.tile_size)
                        player_c = int(self.player_x / self.tile_size)
                        if new_r == player_r and new_c == player_c:
                            continue

                        # Check for other monsters at the target position
                        other_monster_there = False
                        for other_m in self.monsters:
                            if other_m is monster:
                                continue
                            if other_m.get('row') == new_r and other_m.get('col') == new_c:
                                other_monster_there = True
                                break
                        
                        # Check walkability (ignore other monsters and player overlap for knockback)
                        tile = self.dungeon[new_r][new_c]
                        if tile.tile_type not in (DungeonSqr.FLOOR, DungeonSqr.DOOR, DungeonSqr.EXIT) or other_monster_there:
                            # Can't move to a wall or occupied tile, try axis-by-axis
                            new_r_x = int(new_x / self.tile_size)
                            new_r_y = int(monster['y'] / self.tile_size)
                            if (0 <= new_r_x < self.width and 0 <= new_r_y < self.height):
                                tile_x = self.dungeon[new_r_y][new_r_x]
                                # Check if another monster is there
                                x_occupied = False
                                for other_m in self.monsters:
                                    if other_m is monster:
                                        continue
                                    if other_m.get('row') == new_r_y and other_m.get('col') == new_r_x:
                                        x_occupied = True
                                        break
                                
                                if tile_x.tile_type in (DungeonSqr.FLOOR, DungeonSqr.DOOR, DungeonSqr.EXIT) and not x_occupied:
                                    monster['x'] = new_x
                            
                            new_r_x = int(monster['x'] / self.tile_size)
                            new_r_y = int(new_y / self.tile_size)
                            if (0 <= new_r_x < self.width and 0 <= new_r_y < self.height):
                                tile_y = self.dungeon[new_r_y][new_r_x]
                                # Check if another monster is there
                                y_occupied = False
                                for other_m in self.monsters:
                                    if other_m is monster:
                                        continue
                                    if other_m.get('row') == new_r_y and other_m.get('col') == new_r_x:
                                        y_occupied = True
                                        break
                                
                                if tile_y.tile_type in (DungeonSqr.FLOOR, DungeonSqr.DOOR, DungeonSqr.EXIT) and not y_occupied:
                                    monster['y'] = new_y
                        else:
                            # Full diagonal movement is OK
                            monster['x'] = new_x
                            monster['y'] = new_y
                        
                        # Update tile position
                        monster['col'] = int(monster['x'] / self.tile_size)
                        monster['row'] = int(monster['y'] / self.tile_size)
        except Exception as e:
            logging.exception(f"Error in apply_melee_knockback: {e}")


    def _update_tile_position(self):
        # Use float division to preserve sub-tile positions when converting to tile indices
        new_col = int(self.player_x / self.tile_size)
        new_row = int(self.player_y / self.tile_size)
        if new_row != self.player_row or new_col != self.player_col:
            self.player_row = new_row
            self.player_col = new_col
            # If player stepped on the exit, generate a new map
            try:
                if self.dungeon[new_row][new_col].get_ch() == self.exit_glyph:
                    # Advance to next level configuration and regenerate
                    self.advance_level()
                    return
            except Exception:
                pass

            if (new_row, new_col) != self.last_revealed_tile:
                self.last_revealed_tile = (new_row, new_col)
                self.reveal_current_area()

    def _resolve_attack_target(self, target_row, target_col, weapon=None):
        """Resolve the actual attack center and direction based on a clicked tile."""
        weapon = weapon or self.equipped_weapon
        if weapon is None:
            return (target_row + 0.5, target_col + 0.5, 1.0, 0.0)

        player_center_row = self.player_row + 0.5
        player_center_col = self.player_col + 0.5
        target_center_row = target_row + 0.5
        target_center_col = target_col + 0.5

        dr = target_center_row - player_center_row
        dc = target_center_col - player_center_col
        dist = sqrt(dr * dr + dc * dc)
        if dist == 0.0:
            return (player_center_row, player_center_col, 1.0, 0.0)

        dir_row = dr / dist
        dir_col = dc / dist

        max_range = float(weapon.get('range', 0))
        if max_range > 0 and dist > max_range:
            target_center_row = player_center_row + dir_row * max_range
            target_center_col = player_center_col + dir_col * max_range

        return (target_center_row, target_center_col, dir_row, dir_col)

    def _compute_attack_tiles(self, center_row, center_col, dir_row, dir_col, weapon=None):
        """Compute the set of tiles affected by an attack cone."""
        weapon = weapon or self.equipped_weapon
        if weapon is None:
            return set()

        import math

        area = float(weapon.get('area', 0))
        half_angle_rad = math.radians(float(weapon.get('angle', 360)) * 0.5)
        include_all = weapon.get('angle', 360) >= 360

        tiles = set()
        max_dist = int(math.ceil(area))

        for dr in range(-max_dist, max_dist + 1):
            for dc in range(-max_dist, max_dist + 1):
                tr = int(center_row) + dr
                tc = int(center_col) + dc
                if tr < 0 or tr >= self.height or tc < 0 or tc >= self.width:
                    continue

                vec_r = (tr + 0.5) - center_row
                vec_c = (tc + 0.5) - center_col
                dist = math.hypot(vec_r, vec_c)
                if dist > area:
                    continue

                if include_all or (dir_row == 0 and dir_col == 0):
                    tiles.add((tr, tc))
                    continue

                dot = dir_row * vec_r + dir_col * vec_c
                if dist == 0:
                    tiles.add((tr, tc))
                    continue
                cos_theta = max(-1.0, min(1.0, dot / dist))
                if math.acos(cos_theta) <= half_angle_rad:
                    tiles.add((tr, tc))

        return tiles

    def _add_attack_effect(self, tiles, duration=0.25):
        """Add a short-lived visual effect for an attack."""
        if not tiles:
            return
        self.attack_effects.append({
            'tiles': set(tiles),
            'expires_at': time.time() + duration,
        })

    def _update_attack_effects(self, current_time=None):
        if current_time is None:
            current_time = time.time()
        self.attack_effects = [e for e in self.attack_effects if e['expires_at'] > current_time]

    def _update_damage_popups(self, current_time=None):
        """Prune expired damage popups.

        Each popup is expected to have an 'expires_at' timestamp (float).
        This is called every frame from the renderer.
        """
        if current_time is None:
            current_time = time.time()
        # Keep only popups that haven't expired yet
        self.damage_popups = [p for p in self.damage_popups if p.get('expires_at', 0) > current_time]

    def perform_attack(self, target_row, target_col, weapon=None):
        """Perform an attack aimed at the given tile."""
        weapon = weapon or self.equipped_weapon
        if weapon is None:
            return

        target_center_row, target_center_col, dir_row, dir_col = self._resolve_attack_target(target_row, target_col, weapon)
        tiles = self._compute_attack_tiles(target_center_row, target_center_col, dir_row, dir_col, weapon)
        self._add_attack_effect(tiles)

        # Track which monsters were hit for knockback
        hit_monsters = []

        # Deal damage to monsters in the attack area
        try:
            damage = float(weapon.get('damage', 0))
            if damage > 0:
                for monster in self.monsters:
                    monster_row = monster['row']
                    monster_col = monster['col']
                    if (monster_row, monster_col) in tiles:
                        monster['health'] -= damage
                        hit_monsters.append(monster)
                        monster['damage_aggro_timer'] = max(0.0, float(monster['type'].get('damage_aggro_time', 0)))
                        # Add damage popup
                        created = time.time()
                        self.damage_popups.append({
                            'row': monster_row,
                            'col': monster_col,
                            'damage': int(damage),
                            'created_at': created,
                            'expires_at': created + 2.0,  # Show for 2 seconds
                        })
        except Exception:
            pass

        # Apply knockback to hit monsters
        try:
            knockback = float(weapon.get('knockback', 0))
            if knockback > 0 and hit_monsters:
                for monster in hit_monsters:
                    # Get monster's knockback resistance (0-1; higher = less knockback)
                    monster_type = monster.get('type', {})
                    resistance = float(monster_type.get('knockback_resistance', 0.5))
                    resistance = max(0.0, min(1.0, resistance))  # Clamp to [0, 1]

                    # Calculate knockback distance in tiles
                    knockback_tiles = knockback * resistance

                    if knockback_tiles > 0:
                        # Calculate direction away from player (from player to monster)
                        mx = monster.get('x', (monster['col'] + 0.5) * self.tile_size)
                        my = monster.get('y', (monster['row'] + 0.5) * self.tile_size)
                        dx = mx - self.player_x
                        dy = my - self.player_y
                        dist = sqrt(dx * dx + dy * dy)

                        if dist > 0:
                            # Normalize direction
                            dir_x = dx / dist
                            dir_y = dy / dist
                        else:
                            # Monster is at player center; push in a default direction
                            dir_x, dir_y = 1.0, 0.0

                        # Move monster away by knockback_tiles * tile_size pixels
                        knockback_px = knockback_tiles * self.tile_size
                        new_x = mx + dir_x * knockback_px
                        new_y = my + dir_y * knockback_px

                        # Check if the new position is valid; if not, try axis-by-axis
                        if self._can_move_monster_to(new_x, new_y, monster):
                            monster['x'] = new_x
                            monster['y'] = new_y
                        else:
                            # Try moving only in x direction
                            if self._can_move_monster_to(new_x, monster['y'], monster):
                                monster['x'] = new_x
                            # Try moving only in y direction
                            elif self._can_move_monster_to(monster['x'], new_y, monster):
                                monster['y'] = new_y

                        # Update tile position
                        monster['col'] = int(monster['x'] / self.tile_size)
                        monster['row'] = int(monster['y'] / self.tile_size)
        except Exception:
            pass

        # Deduct stamina if possible (does not block attacks)
        try:
            cost = float(weapon.get('stamina_cost', 0))
            if cost > 0 and hasattr(self, 'stamina'):
                self.stamina = max(0, self.stamina - cost)
        except Exception:
            pass

        # Remove dead monsters
        self._cleanup_dead_monsters()

    def _cleanup_dead_monsters(self):
        """Remove monsters with health <= 0 from the monsters list."""
        self.monsters = [m for m in self.monsters if m.get('health', 1) > 0]

    def screen_to_tile(self, pixel_x, pixel_y, cam_tx, cam_ty, offset_x, offset_y, view_w, view_h):
        """Convert screen pixel coordinates to a dungeon tile (row, col).

        Returns None if the pixel is outside the visible tile area.
        """
        local_x = pixel_x - offset_x
        local_y = pixel_y - offset_y
        if local_x < 0 or local_y < 0:
            return None

        tile_x = int(local_x // self.tile_size)
        tile_y = int(local_y // self.tile_size)
        if tile_x < 0 or tile_y < 0 or tile_x >= view_w or tile_y >= view_h:
            return None

        return (cam_ty + tile_y, cam_tx + tile_x)

    def bresenham_line(self, r0, c0, r1, c1):
        """Return list of (row,col) tiles along a Bresenham line from (r0,c0) to (r1,c1).

        Includes both endpoints and the start tile. Useful for ray checks.
        """
        # Use canonical Bresenham algorithm where column is x and row is y
        tiles = []
        x0, y0 = c0, r0
        x1, y1 = c1, r1
        dx = abs(x1 - x0)
        sx = 1 if x0 < x1 else -1
        dy = -abs(y1 - y0)
        sy = 1 if y0 < y1 else -1
        err = dx + dy  # error value

        x, y = x0, y0
        while True:
            tiles.append((y, x))
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

        return tiles

    def _can_move_to(self, px, py):
        # Enforce that the player's outer radius does not overlap any non-walkable
        # tile. This allows the player's edge to touch the wall but prevents
        # intersection/overlap with the wall tile.
        min_dist = self.player_radius
        # Compute bounding tile range to test
        min_col = int((px - min_dist) / self.tile_size)
        max_col = int((px + min_dist) / self.tile_size)
        min_row = int((py - min_dist) / self.tile_size)
        max_row = int((py + min_dist) / self.tile_size)
        min_dist_sq = min_dist * min_dist

        for r in range(min_row, max_row + 1):
            for c in range(min_col, max_col + 1):
                if not self.is_walkable(r, c):
                    # Tile rectangle in pixels
                    tx0 = c * self.tile_size
                    ty0 = r * self.tile_size
                    tx1 = tx0 + self.tile_size
                    ty1 = ty0 + self.tile_size

                    # Closest point on tile rect to player's center
                    closest_x = min(max(px, tx0), tx1)
                    closest_y = min(max(py, ty0), ty1)

                    dx = px - closest_x
                    dy = py - closest_y
                    if dx * dx + dy * dy < min_dist_sq:
                        return False

        return True

    def _tile_overlaps_player(self, r, c) -> bool:
        """Return True if the tile at (r,c) intersects the player's hitbox."""
        if r < 0 or c < 0 or r >= self.height or c >= self.width:
            return False
        tx0 = c * self.tile_size
        ty0 = r * self.tile_size
        tx1 = tx0 + self.tile_size
        ty1 = ty0 + self.tile_size

        # Closest point on tile rect to player's center
        closest_x = min(max(self.player_x, tx0), tx1)
        closest_y = min(max(self.player_y, ty0), ty1)

        dx = self.player_x - closest_x
        dy = self.player_y - closest_y
        return (dx * dx + dy * dy) < (self.player_radius * self.player_radius)

    def _is_tile_enterable_by_monster(self, r, c, monster=None) -> bool:
        """Return True if a monster may occupy tile (r,c).

        This enforces: in-bounds, walkable tile (respecting other monsters),
        and not overlapping the player's hitbox.
        """
        if r < 0 or c < 0 or r >= self.height or c >= self.width:
            return False
        # Block tiles that overlap the player's hitbox so monsters cannot move into it
        if self._tile_overlaps_player(r, c):
            return False

        # Use existing walkability check (pass through monster ignore so tile type is checked)
        if not self.is_walkable(r, c, monster):
            return False

        # Check whether another monster already occupies the tile
        for m in self.monsters:
            if m is monster:
                continue
            if m.get('row') == r and m.get('col') == c:
                return False

        return True

    def _can_move_monster_to(self, px, py, monster, radius=None):
        """Check if monster can move its center to (px, py)."""
        r = int(py / self.tile_size)
        c = int(px / self.tile_size)
        # Debug: check bounds
        if r < 0 or r >= self.height or c < 0 or c >= self.width:
            return False
        return self._is_tile_enterable_by_monster(r, c, monster)

    def _find_monster_next_step(self, monster):
        """Find the next tile along a walkable path from a monster to the player."""
        start_r = monster.get('row', int(monster.get('y', 0) / self.tile_size))
        start_c = monster.get('col', int(monster.get('x', 0) / self.tile_size))
        target_r = self.player_row
        target_c = self.player_col

        if (start_r, start_c) == (target_r, target_c):
            return None

        queue = deque()
        queue.append((start_r, start_c))
        came_from = {(start_r, start_c): None}
        while queue:
            r, c = queue.popleft()
            if (r, c) == (target_r, target_c):
                break

                for dr, dc in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                    nr, nc = r + dr, c + dc
                    if (nr, nc) in came_from:
                        continue
                    if nr < 0 or nc < 0 or nr >= self.height or nc >= self.width:
                        continue
                    # For monster pathfinding, require tiles to be enterable by monsters.
                    # This also prevents monsters from pathing into the player's hitbox.
                    if not self._is_tile_enterable_by_monster(nr, nc, monster):
                        continue
                    came_from[(nr, nc)] = (r, c)
                    queue.append((nr, nc))

        if (target_r, target_c) not in came_from:
            return None

        current = (target_r, target_c)
        while came_from[current] != (start_r, start_c):
            current = came_from[current]
            if current is None:
                return None
        return current

    def reveal_current_area(self):
        # Reveal the entire room when inside one; otherwise reveal a small radius (corridor)
        current_room = None
        for room in self.rooms:
            if (self.player_row >= room.row and self.player_row < room.row + room.height and
                self.player_col >= room.col and self.player_col < room.col + room.width):
                current_room = room
                break

        if current_room is not None:
            # Reveal the room AND a one-tile wall border around it so doors are visible
            r0 = max(0, current_room.row - 1)
            c0 = max(0, current_room.col - 1)
            r1 = min(self.height, current_room.row + current_room.height + 1)
            c1 = min(self.width, current_room.col + current_room.width + 1)
            for r in range(r0, r1):
                for c in range(c0, c1):
                    self.explored[r][c] = True
        else:
            # Use larger radius for openspace maps, smaller for corridors
            radius = 8 if self.uses_openspace else 2
            rr = self.player_row
            cc = self.player_col
            for dr in range(-radius, radius + 1):
                for dc in range(-radius, radius + 1):
                    r = rr + dr
                    c = cc + dc
                    if 0 <= r < self.height and 0 <= c < self.width:
                        if dr*dr + dc*dc <= radius*radius:
                            self.explored[r][c] = True

    def update_monsters(self, delta_time):
        """Update monsters: alert checking and movement towards player when alerted."""
        if not self.monsters:
            return

        for monster in list(self.monsters):
            mt = monster.get('type', {})
            # Ensure monster has pixel position
            if 'x' not in monster or 'y' not in monster:
                monster['x'] = (monster.get('col', 0) + 0.5) * self.tile_size
                monster['y'] = (monster.get('row', 0) + 0.5) * self.tile_size

            # Aggro check (distance in tiles)
            dx_tiles = (monster['x'] - self.player_x) / self.tile_size
            dy_tiles = (monster['y'] - self.player_y) / self.tile_size
            dist_tiles = sqrt(dx_tiles * dx_tiles + dy_tiles * dy_tiles)
            aggro = max(0.0, float(mt.get('aggro_distance', 0)))
            aggro_time = max(0.0, float(mt.get('aggro_time', 0)))
            damage_aggro_time = max(0.0, float(mt.get('damage_aggro_time', 0)))

            monster.setdefault('aggro_timer', 0.0)
            monster.setdefault('damage_aggro_timer', 0.0)

            within_aggro_distance = dist_tiles <= aggro if aggro > 0 else False
            if within_aggro_distance:
                monster['aggro_timer'] = aggro_time

            monster['damage_aggro_timer'] = max(0.0, monster['damage_aggro_timer'] - delta_time)
            if not within_aggro_distance:
                monster['aggro_timer'] = max(0.0, monster['aggro_timer'] - delta_time)

            alerted = within_aggro_distance or monster['aggro_timer'] > 0.0 or monster['damage_aggro_timer'] > 0.0
            monster['alerted'] = alerted

            if alerted:
                # Movement towards player in pixels/sec
                speed_tiles = float(mt.get('movement_speed', 0))
                if speed_tiles <= 0:
                    continue
                speed_px = speed_tiles * self.tile_size

                next_step = self._find_monster_next_step(monster)
                if next_step is not None:
                    target_r, target_c = next_step
                    target_x = (target_c + 0.5) * self.tile_size
                    target_y = (target_r + 0.5) * self.tile_size
                else:
                    target_x = self.player_x
                    target_y = self.player_y

                dx = target_x - monster['x']
                dy = target_y - monster['y']
                dist = sqrt(dx * dx + dy * dy)
                if dist == 0:
                    continue
                dir_x = dx / dist
                dir_y = dy / dist
                move_x = dir_x * speed_px * delta_time
                move_y = dir_y * speed_px * delta_time

                # Don't overshoot the target tile center.
                if abs(move_x) > abs(target_x - monster['x']):
                    move_x = target_x - monster['x']
                if abs(move_y) > abs(target_y - monster['y']):
                    move_y = target_y - monster['y']

                new_x = monster['x'] + move_x
                new_y = monster['y'] + move_y
                can_move_diag = self._can_move_monster_to(new_x, new_y, monster)
                if can_move_diag:
                    monster['x'] = new_x
                    monster['y'] = new_y
                else:
                    can_move_x = self._can_move_monster_to(monster['x'] + move_x, monster['y'], monster)
                    can_move_y = self._can_move_monster_to(monster['x'], monster['y'] + move_y, monster)
                    if can_move_x:
                        monster['x'] += move_x
                    elif can_move_y:
                        monster['y'] += move_y

                # Update integer tile coords
                monster['col'] = int(monster['x'] / self.tile_size)
                monster['row'] = int(monster['y'] / self.tile_size)

    def apply_level(self, index: int) -> None:
        """Apply level settings by index from self.levels."""
        if not self.levels:
            # defaults (match original constants); stored as codepoints
            level = {
                'name': 'default',
                'floor_glyph': 0x00B7,  # middle dot
                'wall_glyph': 0x2588,   # full block
                'fog_glyph': ord(' '),
                'floor_bg': COLOR_FLOOR_BG,
                'wall_bg': COLOR_WALL_BG,
                'fog_bg': COLOR_FOG_BG,
                'floor_fg': COLOR_FLOOR_FG,
                'wall_fg': COLOR_WALL_FG,
                'fog_fg': COLOR_FOG_FG,
                'openspace': False,
            }
        else:
            level = self.levels[index % len(self.levels)]

        # allow glyphs to be stored as either codepoints (int) or chars
        self.floor_glyph = level.get('floor_glyph', 0x00B7)
        self.wall_glyph = level.get('wall_glyph', 0x2588)
        self.fog_glyph = level.get('fog_glyph', ord(' '))
        self.exit_glyph = level.get('exit_glyph', EXIT_GLYPH_INDEX)
        # convert ints to characters for internal comparisons
        if isinstance(self.floor_glyph, int):
            self.floor_glyph = chr(self.floor_glyph)
        if isinstance(self.wall_glyph, int):
            self.wall_glyph = chr(self.wall_glyph)
        if isinstance(self.fog_glyph, int):
            self.fog_glyph = chr(self.fog_glyph)
        if isinstance(self.exit_glyph, int):
            self.exit_glyph = chr(self.exit_glyph)
        self.color_floor_bg = level.get('floor_bg', COLOR_FLOOR_BG)
        self.color_wall_bg = level.get('wall_bg', COLOR_WALL_BG)
        self.color_fog_bg = level.get('fog_bg', COLOR_FOG_BG)
        self.color_floor_fg = level.get('floor_fg', COLOR_FLOOR_FG)
        self.color_wall_fg = level.get('wall_fg', COLOR_WALL_FG)
        self.color_fog_fg = level.get('fog_fg', COLOR_FOG_FG)
        self.uses_openspace = level.get('openspace', False)
        self.current_level_index = index % (len(self.levels) or 1)

    def advance_level(self) -> None:
        """Advance to the next level and regenerate the map."""
        if not self.levels:
            self.generate_map()
            return
        self.current_level_index = (self.current_level_index + 1) % len(self.levels)
        self.apply_level(self.current_level_index)
        # Restore health and stamina on level advancement
        self.health = self.max_health
        self.stamina = self.max_stamina
        self.generate_map()

    def get_current_level_name(self) -> str:
        """Get the name of the current level."""
        if self.levels and 0 <= self.current_level_index < len(self.levels):
            return self.levels[self.current_level_index].get('name', 'Unknown')
        return 'Unknown'

    def place_exit(self):
        """Place an exit tile in the centre of the starting room.

        The previous implementation picked a random room (avoiding the one the
        player was standing in if possible).  The new behaviour fixes the
        exit in the first room carved when the map was generated.  This keeps
        the exit near the player’s spawn point and makes the level layout more
        predictable for testing and early exploration.

        If for some reason the very centre isn’t a floor tile we fall back to
        the first walkable tile we can find within the starting room.  We also
        try not to place the exit directly on the player; if the centre happens
        to coincide with the player position we search for another suitable
        floor tile in that room.
        """
        if not self.rooms:
            self.exit_pos = None
            return

        # Always use the first room (spawn point) as the exit room.
        room = self.rooms[0]

        # target the centre of that room
        er = room.row + room.height // 2
        ec = room.col + room.width // 2

        # if centre isn’t a floor or it’s where the player currently sits,
        # search the room for any other floor tile that isn’t the player.
        if (self.dungeon[er][ec].get_ch() != self.floor_glyph or
                (er, ec) == (self.player_row, self.player_col)):
            placed = False
            for r in range(room.row, room.row + room.height):
                for c in range(room.col, room.col + room.width):
                    if (self.dungeon[r][c].get_ch() == self.floor_glyph and
                            (r, c) != (self.player_row, self.player_col)):
                        er, ec = r, c
                        placed = True
                        break
                if placed:
                    break

        # finally set the exit glyph (fallbacks handled above)
        try:
            self.dungeon[er][ec] = DungeonSqr(self.exit_glyph, DungeonSqr.EXIT)
            self.exit_pos = (er, ec)
        except Exception:
            self.exit_pos = None

    def place_monsters(self):
        """Place monsters scattered across walkable areas of the map."""
        self.monsters = []
        
        # Get current level name
        current_level_name = self.get_current_level_name()
        
        # Filter monster types to those that explicitly list this level.
        # Only monster types whose `levels` list contains the current level
        # name will be considered for placement.
        available_monster_types = [
            mt for mt in MONSTER_TYPES
            # empty `levels` list means the monster can appear on any level
            if not mt.get('levels') or current_level_name in mt.get('levels', [])
        ]
        
        if not available_monster_types:
            return  # No monsters available for this level
        
        # Determine number of monsters based on map size (roughly 1 monster per 50 tiles)
        num_monsters = max(1, (self.width * self.height) // 50)
        
        # Collect all walkable positions (excluding player and exit positions)
        walkable_positions = []
        for r in range(self.height):
            for c in range(self.width):
                if self.is_walkable(r, c) and (r, c) != (self.player_row, self.player_col) and (r, c) != self.exit_pos:
                    walkable_positions.append((r, c))
        
        # Randomly select positions for monsters and ensure every available
        # monster type appears at least once. Also prefer at least two
        # monsters on the map when possible.
        if len(walkable_positions) > 0:
            import random
            max_positions = len(walkable_positions)
            # Ensure we have room to place all monster types at least once
            desired = max(num_monsters, len(available_monster_types))
            # Prefer at least two monsters for variety
            desired = max(desired, 2)
            desired = min(desired, max_positions)

            monster_positions = random.sample(walkable_positions, desired)

            # First, assign one instance of each monster type (if possible)
            self.monsters = []
            pos_idx = 0
            for mt in available_monster_types:
                if pos_idx >= len(monster_positions):
                    break
                r, c = monster_positions[pos_idx]
                self.monsters.append({
                    'type': mt,
                    'row': r,
                    'col': c,
                    'health': mt['health'],
                    # Pixel-precise position so monsters can move smoothly
                    'x': (c + 0.5) * self.tile_size,
                    'y': (r + 0.5) * self.tile_size,
                    'alerted': False,
                    'aggro_timer': 0.0,
                    'damage_aggro_timer': 0.0,
                })
                pos_idx += 1

            # Fill remaining slots with random choices from available types
            while pos_idx < len(monster_positions):
                r, c = monster_positions[pos_idx]
                mt = random.choice(available_monster_types)
                self.monsters.append({
                    'type': mt,
                    'row': r,
                    'col': c,
                    'health': mt['health'],
                    # Pixel-precise position so monsters can move smoothly
                    'x': (c + 0.5) * self.tile_size,
                    'y': (r + 0.5) * self.tile_size,
                    'alerted': False,
                    'aggro_timer': 0.0,
                    'damage_aggro_timer': 0.0,
                })
                pos_idx += 1

    def place_objects(self):
        """Place static objects on walkable floor tiles."""
        import random
        current_level_name = self.get_current_level_name()
        available = [
            ot for ot in OBJECT_TYPES
            if not ot.get('levels') or current_level_name in ot.get('levels', [])
        ]
        if not available:
            return

        walkable = [
            (r, c)
            for r in range(self.height)
            for c in range(self.width)
            if self.is_walkable(r, c)
            and (r, c) != (self.player_row, self.player_col)
            and (self.exit_pos is None or (r, c) != self.exit_pos)
        ]
        random.shuffle(walkable)

        pos_idx = 0
        for ot in available:
            count = min(ot['spawn_count'], len(walkable) - pos_idx)
            for _ in range(count):
                r, c = walkable[pos_idx]
                self.objects.append({
                    'type': ot,
                    'row': r,
                    'col': c,
                    'health': ot['health'],
                })
                pos_idx += 1

def render_with_tcod(dg: RLDungeonGenerator) -> None:
    # Provide detailed diagnostic instead of exiting so debugger / logs show why import failed
    info = (
        f"tcod is not installed or failed to import.\n"
        f"Python executable: {sys.executable}\n"
        f"sys.version: {sys.version}\n"
        f"sys.path: {sys.path}\n"
        f"Import traceback:\n{_tcod_import_error}\n"
    )
    print(info)
    raise ImportError(info)

    # Prefer a project-local bitmap tileset first
    tileset = None
    png_tileset_path = os.path.join(os.path.dirname(__file__), 'assets', 'tilesets', 'unicode_tileset.png')
    if os.path.exists(png_tileset_path):
        try:
            # Assumes CP437 16x16 grid tilesheet
            tileset = tcod.tileset.load_tilesheet(png_tileset_path, 16, 16, tcod.tileset.CHARMAP_CP437)
        except Exception:
            tileset = None

    # If PNG load failed, attempt to load a TrueType font from system Consolas
    if tileset is None:
        default_ttf_paths = [
            os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'consola.ttf'),
            os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'consolab.ttf'),
        ]

        for path in default_ttf_paths:
            if os.path.exists(path):
                try:
                    tileset = tcod.tileset.load_truetype_font(path, 16, tcod.tileset.CHARMAP_CP437)
                    break
                except Exception:
                    continue

    if tileset is None:
        print("Could not load a TrueType font from system. Falling back to ASCII output. Run with --ascii to skip this attempt.")
        dg.print_map()
        return

    # Choose pixel-render path only if numpy is available and tileset has a bitmap
    use_pixel_render = False
    if np is not None:
        # Tileset loaded from a PNG has .bitmap attribute in tcod; TrueType does not
        if hasattr(tileset, 'bitmap'):
            use_pixel_render = True

    # Viewport size (camera window). Smaller than full map = zoomed-in view.
    view_w = min(40, dg.width)
    view_h = min(25, dg.height)

    # If we can do pixel rendering, compute pixel viewport size
    pixel_view_w = view_w * dg.tile_size
    pixel_view_h = view_h * dg.tile_size

    console = tcod.console.Console(view_w, view_h, order="F")
    movement_key_map = {
        tcod.event.K_UP: (0.0, -1.0),
        tcod.event.K_w: (0.0, -1.0),
        tcod.event.K_KP_8: (0.0, -1.0),
        tcod.event.K_DOWN: (0.0, 1.0),
        tcod.event.K_s: (0.0, 1.0),
        tcod.event.K_KP_2: (0.0, 1.0),
        tcod.event.K_LEFT: (-1.0, 0.0),
        tcod.event.K_a: (-1.0, 0.0),
        tcod.event.K_KP_4: (-1.0, 0.0),
        tcod.event.K_RIGHT: (1.0, 0.0),
        tcod.event.K_d: (1.0, 0.0),
        tcod.event.K_KP_6: (1.0, 0.0),
    }
    # Track held directions for frame-based single-pixel movement
    held_directions = []
    shift_held = False

    with tcod.context.new(
        columns=view_w,
        rows=view_h,
        tileset=tileset,
        title="RLDungeonGenerator",
        vsync=True,
    ) as context:
        last_frame_time = time.time()

        # Pre-extract tile bitmaps if pixel rendering
        tile_bitmaps = None
        if use_pixel_render:
            # tileset.bitmap is a PIL.Image in newer tcod; convert to numpy array
            try:
                bmp = tileset.bitmap.convert('RGBA')
                tile_w = dg.tile_size
                tile_h = dg.tile_size
                cols = bmp.width // tile_w
                rows = bmp.height // tile_h
                tile_bitmaps = []
                for ty in range(rows):
                    for tx in range(cols):
                        box = (tx * tile_w, ty * tile_h, (tx + 1) * tile_w, (ty + 1) * tile_h)
                        tile = bmp.crop(box)
                        tile_bitmaps.append(np.array(tile))
            except Exception:
                use_pixel_render = False
                tile_bitmaps = None

        while True:
            current_time = time.time()
            delta_time = current_time - last_frame_time
            last_frame_time = current_time
            # Cap delta_time to prevent large jumps
            if delta_time > 0.1:
                delta_time = 0.1

            dg.update_movement(delta_time, (0.0, 0.0))
            # Update monster AI/movement after player moves
            dg.update_monsters(delta_time)
            # Frame-based held-key single-pixel movement: if any directions are held,
            # compute a signed dx/dy and nudge the player by 1 pixel this frame.
            if held_directions:
                sum_dx = sum(d[0] for d in held_directions)
                sum_dy = sum(d[1] for d in held_directions)
                # convert to -1/0/1 per axis
                def sign(v):
                    return 1 if v > 0 else (-1 if v < 0 else 0)
                mdx = sign(sum_dx)
                mdy = sign(sum_dy)
                if mdx != 0 or mdy != 0:
                    # Increase movement when sprinting (shift held) - move 7x per second
                    if shift_held:
                        dg.move_by_pixels(int(mdx), int(mdy), pixels=1)
                        dg.move_by_pixels(int(mdx), int(mdy), pixels=1)
                    dg.move_by_pixels(int(mdx), int(mdy), pixels=1)

            if use_pixel_render and tile_bitmaps is not None:
                # Build pixel buffer - fill with dark background first
                buf = np.zeros((pixel_view_h, pixel_view_w, 4), dtype=np.uint8)
                # Fill entire buffer with dark gray background
                buf[:, :, :3] = (10, 10, 10)  # Dark background
                buf[:, :, 3] = 255  # Fully opaque

                # Camera top-left in tiles
                cam_ty = int(dg.player_y / dg.tile_size) - view_h // 2
                cam_tx = int(dg.player_x / dg.tile_size) - view_w // 2
                cam_px = cam_tx * dg.tile_size
                cam_py = cam_ty * dg.tile_size

                # Blit map tiles into buffer
                for ty in range(view_h):
                    for tx in range(view_w):
                        wr = cam_ty + ty
                        wc = cam_tx + tx
                        # Fill out-of-bounds areas with dark background
                        if wr < 0 or wr >= dg.height or wc < 0 or wc >= dg.width:
                            y0 = ty * dg.tile_size
                            x0 = tx * dg.tile_size
                            buf[y0:y0+dg.tile_size, x0:x0+dg.tile_size, :3] = (10, 10, 10)
                            buf[y0:y0+dg.tile_size, x0:x0+dg.tile_size, 3] = 255
                            continue
                        ch = dg.dungeon[wr][wc].get_ch()
                        # Handle unexplored areas with dark background (high contrast fog-of-war)
                        if not dg.explored[wr][wc]:
                            y0 = ty * dg.tile_size
                            x0 = tx * dg.tile_size
                            buf[y0:y0+dg.tile_size, x0:x0+dg.tile_size, :3] = dg.color_fog_bg
                            buf[y0:y0+dg.tile_size, x0:x0+dg.tile_size, 3] = 255
                            continue

                        # Fill per-tile background first so walls/floors differ even with the same glyph.
                        y0 = ty * dg.tile_size
                        x0 = tx * dg.tile_size
                        tile = dg.dungeon[wr][wc]
                        if tile.tile_type == DungeonSqr.WALL:  # wall
                            buf[y0:y0+dg.tile_size, x0:x0+dg.tile_size, :3] = dg.color_wall_bg
                        elif tile.tile_type == DungeonSqr.FLOOR:  # floor
                            buf[y0:y0+dg.tile_size, x0:x0+dg.tile_size, :3] = dg.color_floor_bg
                        else:
                            buf[y0:y0+dg.tile_size, x0:x0+dg.tile_size, :3] = (10, 10, 10)
                        buf[y0:y0+dg.tile_size, x0:x0+dg.tile_size, 3] = 255

                        # choose tile based on actual glyph value
                        if ch == dg.wall_glyph or ch == dg.floor_glyph:
                            idx = ord(ch)
                        elif ch == '+':
                            idx = DOOR_GLYPH_INDEX
                        else:
                            idx = ord(ch)
                        # Map CP437 indices to tilesheet index - assumes tilesheet arranged by codepoint
                        if idx < len(tile_bitmaps):
                            tile_img = tile_bitmaps[idx]
                            # Simple alpha blit
                            alpha = tile_img[:, :, 3:4] / 255.0
                            buf[y0:y0+dg.tile_size, x0:x0+dg.tile_size, :3] = (
                                buf[y0:y0+dg.tile_size, x0:x0+dg.tile_size, :3] * (1 - alpha) +
                                tile_img[:, :, :3] * alpha
                            ).astype(np.uint8)
                            buf[y0:y0+dg.tile_size, x0:x0+dg.tile_size, 3] = 255
                        else:
                            # Fallback: fill with background color if tile not found
                            tile = dg.dungeon[wr][wc]
                            if tile.tile_type == DungeonSqr.WALL:
                                buf[y0:y0+dg.tile_size, x0:x0+dg.tile_size, :3] = dg.color_wall_bg
                            elif tile.tile_type == DungeonSqr.FLOOR:
                                buf[y0:y0+dg.tile_size, x0:x0+dg.tile_size, :3] = dg.color_floor_bg
                            elif tile.tile_type == DungeonSqr.DOOR:
                                buf[y0:y0+dg.tile_size, x0:x0+dg.tile_size, :3] = (255, 215, 0)
                            else:
                                buf[y0:y0+dg.tile_size, x0:x0+dg.tile_size, :3] = (10, 10, 10)
                            buf[y0:y0+dg.tile_size, x0:x0+dg.tile_size, 3] = 255

                # Draw player as a white square (or use a small sprite if available)
                player_px = int(dg.player_x - cam_px)
                player_py = int(dg.player_y - cam_py)
                pr = player_py - dg.tile_size // 2
                pc = player_px - dg.tile_size // 2
                # small 10x10 square centered on player position
                ps = max(2, dg.tile_size // 2)
                y0 = pr - ps//2
                x0 = pc - ps//2
                y1 = y0 + ps
                x1 = x0 + ps
                y0c = max(0, y0); x0c = max(0, x0)
                y1c = min(pixel_view_h, y1); x1c = min(pixel_view_w, x1)
                if y1c > y0c and x1c > x0c:
                    buf[y0c:y1c, x0c:x1c, :3] = 255
                    buf[y0c:y1c, x0c:x1c, 3] = 255

                # Draw monsters as red squares
                for monster in dg.monsters:
                    # Use pixel-precise positions if available
                    mpx = int(monster.get('x', (monster.get('col', 0) + 0.5) * dg.tile_size) - cam_px)
                    mpy = int(monster.get('y', (monster.get('row', 0) + 0.5) * dg.tile_size) - cam_py)
                    mr = mpy - dg.tile_size // 2
                    mc = mpx - dg.tile_size // 2
                    # small red square for monsters
                    ms = max(2, dg.tile_size // 3)
                    y0 = mr - ms//2
                    x0 = mc - ms//2
                    y1 = y0 + ms
                    x1 = x0 + ms
                    y0c = max(0, y0); x0c = max(0, x0)
                    y1c = min(pixel_view_h, y1); x1c = min(pixel_view_w, x1)
                    if y1c > y0c and x1c > x0c:
                        buf[y0c:y1c, x0c:x1c, :3] = (255, 0, 0)
                        buf[y0c:y1c, x0c:x1c, 3] = 255
                    # draw small alert marker above monster if alerted
                    if monster.get('alerted'):
                        try:
                            ex_h = max(2, dg.tile_size // 4)
                            ex_w = max(2, dg.tile_size // 8)
                            ex_x0 = mpx - ex_w // 2
                            ex_y0 = mr - ms//2 - ex_h - 2
                            ex_x1 = ex_x0 + ex_w
                            ex_y1 = ex_y0 + ex_h
                            ex_x0c = max(0, ex_x0); ex_y0c = max(0, ex_y0)
                            ex_x1c = min(pixel_view_w, ex_x1); ex_y1c = min(pixel_view_h, ex_y1)
                            if ex_y1c > ex_y0c and ex_x1c > ex_x0c:
                                buf[ex_y0c:ex_y1c, ex_x0c:ex_x1c, :3] = (255, 0, 0)
                                buf[ex_y0c:ex_y1c, ex_x0c:ex_x1c, 3] = 255
                        except Exception:
                            pass

                # Convert buffer to tcod image and present
                try:
                    img = tcod.image.Image(buffer=buf)
                    context.present(img)
                except Exception:
                    # Fallback to console rendering if image present fails
                    use_pixel_render = False

            else:
                # Tile-based console rendering
                console.clear()
                cam_y = int(dg.player_y / dg.tile_size) - view_h // 2
                cam_x = int(dg.player_x / dg.tile_size) - view_w // 2
                if cam_y < 0: cam_y = 0
                if cam_x < 0: cam_x = 0
                if cam_y > dg.height - view_h: cam_y = dg.height - view_h
                if cam_x > dg.width - view_w: cam_x = dg.width - view_w

                for r in range(view_h):
                    wr = cam_y + r
                    for c in range(view_w):
                        wc = cam_x + c
                        if wr < 0 or wr >= dg.height or wc < 0 or wc >= dg.width:
                            continue
                        ch = dg.dungeon[wr][wc].get_ch()
                        tile = dg.dungeon[wr][wc]
                        if tile.tile_type == DungeonSqr.WALL:  # wall
                            fg = dg.color_wall_fg
                            bg = dg.color_wall_bg
                            glyph = ord(ch)
                        elif tile.tile_type == DungeonSqr.FLOOR:  # floor
                            fg = dg.color_floor_fg
                            bg = dg.color_floor_bg
                            glyph = ord(ch)
                        elif tile.tile_type == DungeonSqr.DOOR:  # door
                            fg = (255, 215, 0)
                            bg = (0, 0, 0)
                            glyph = DOOR_GLYPH_INDEX
                        elif tile.tile_type == DungeonSqr.EXIT:  # exit
                            fg = dg.color_floor_fg
                            bg = dg.color_floor_bg
                            glyph = ord(ch)
                        else:
                            fg = (255, 255, 255)
                            bg = (0, 0, 0)
                            glyph = ord(ch)
                        if not dg.explored[wr][wc]:
                            fg = dg.color_fog_fg
                            bg = dg.color_fog_bg
                        console.print(c, r, chr(glyph), fg=fg, bg=bg)

                # Draw the player at sub-tile fractional offset by deciding visual cell and also draw an extra pixel "dot"
                # Compute exact pixel offset inside the cell for visual effect
                exact_px = dg.player_x / dg.tile_size - int(dg.player_x / dg.tile_size)
                exact_py = dg.player_y / dg.tile_size - int(dg.player_y / dg.tile_size)
                # Use rounding so glyph moves when crossing half-cell; draw small dot to indicate sub-cell position
                pr = int(round(dg.player_y / dg.tile_size)) - cam_y
                pc = int(round(dg.player_x / dg.tile_size)) - cam_x
                if 0 <= pr < view_h and 0 <= pc < view_w:
                    console.print(pc, pr, '@', fg=(255, 255, 255))
                    # Draw a small indicator pixel by printing '.' with bright color at one of the four neighbors to show offset
                    ox = 0
                    oy = 0
                    if exact_px > 0.66:
                        ox = 1
                    elif exact_px < 0.33:
                        ox = -1
                    if exact_py > 0.66:
                        oy = 1
                    elif exact_py < 0.33:
                        oy = -1
                    ipr = pr + oy
                    ipc = pc + ox
                    if 0 <= ipr < view_h and 0 <= ipc < view_w:
                        console.print(ipc, ipr, '.', fg=(255, 0, 0))

                # Draw monsters
                for monster in dg.monsters:
                    mr = monster['row'] - cam_y
                    mc = monster['col'] - cam_x
                    if 0 <= mr < view_h and 0 <= mc < view_w:
                        glyph_index = monster['type']['glyph_index']
                        console.print(mc, mr, chr(glyph_index), fg=(255, 0, 0))
                        if monster.get('alerted') and mr - 1 >= 0:
                            console.print(mc, mr - 1, '!', fg=(255, 0, 0))

                context.present(console)

            # Process events (non-blocking)
            for event in tcod.event.get():
                if event.type == "QUIT":
                    return
                if event.type == "KEYDOWN":
                    if event.sym == tcod.event.K_ESCAPE:
                        return
                    elif event.sym == tcod.event.K_LSHIFT or event.sym == tcod.event.K_RSHIFT:
                        shift_held = True
                    else:
                        # Add to held directions for frame-based movement
                        direction = movement_key_map.get(event.sym)
                        if direction is not None:
                            # keep unique entries
                            if direction not in held_directions:
                                held_directions.append(direction)
                if event.type == "KEYUP":
                    if event.sym == tcod.event.K_LSHIFT or event.sym == tcod.event.K_RSHIFT:
                        shift_held = False
                    else:
                        # Remove from held directions
                        direction = movement_key_map.get(event.sym)
                        if direction is not None and direction in held_directions:
                            held_directions.remove(direction)

            # Small sleep to prevent excessive CPU usage
            time.sleep(0.001)


def show_level_selection_menu(screen: 'pygame.Surface', dg: RLDungeonGenerator, clock: 'pygame.time.Clock', font: 'pygame.font.Font') -> int:
    """Display a level selection menu with scrolling and return the selected level index."""
    if not dg.levels:
        return 0
    
    button_height = 40
    padding = 10
    title_height = 70
    scroll_offset = 0
    menu_running = True
    selected_level = 0
    
    while menu_running:
        # Get current screen dimensions
        screen_width, screen_height = screen.get_size()
        
        # Calculate responsive button width (80% of screen width, max 500px)
        button_width = min(int(screen_width * 0.8), 500)
        button_x = (screen_width - button_width) // 2  # Center horizontally
        
        # Calculate available space for buttons
        available_height = screen_height - title_height - padding
        buttons_per_screen = max(1, available_height // (button_height + padding))
        
        # Clear screen
        screen.fill((30, 30, 30))
        
        # Draw title
        title_font = pygame.font.SysFont('consolas', 32, bold=True)
        title_surf = title_font.render('Select Level', True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(screen_width // 2, 35))
        screen.blit(title_surf, title_rect)
        
        # Draw level buttons with scrolling
        button_rects = []
        y_pos = title_height + padding
        start_index = max(0, scroll_offset // (button_height + padding))
        
        for i in range(start_index, len(dg.levels)):
            if y_pos + button_height > screen_height:
                break
            
            level = dg.levels[i]
            level_name = level.get('name', f'Level {i}')
            
            # Create button rect
            button_rect = pygame.Rect(button_x, y_pos, button_width, button_height)
            button_rects.append((button_rect, i))
            
            # Check if mouse is over this button
            mouse_pos = pygame.mouse.get_pos()
            if button_rect.collidepoint(mouse_pos):
                button_color = (100, 150, 255)
            else:
                button_color = (70, 100, 180)
            
            # Draw button
            pygame.draw.rect(screen, button_color, button_rect)
            pygame.draw.rect(screen, (200, 200, 200), button_rect, 2)  # Border
            
            # Draw text (truncate if too long)
            text_surf = font.render(level_name, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=button_rect.center)
            
            # Clip text to button width
            if text_rect.width > button_width - 10:
                # Render truncated text
                truncated_name = level_name[:len(level_name)//2] + '...'
                text_surf = font.render(truncated_name, True, (255, 255, 255))
                text_rect = text_surf.get_rect(center=button_rect.center)
            
            screen.blit(text_surf, text_rect)
            y_pos += button_height + padding
        
        # Draw scroll indicator
        total_height = len(dg.levels) * (button_height + padding)
        if total_height > available_height:
            scroll_bar_height = max(20, int(available_height * available_height / total_height))
            scroll_bar_pos = int(scroll_offset * available_height / total_height)
            scroll_bar_rect = pygame.Rect(screen_width - 15, title_height + scroll_bar_pos, 10, scroll_bar_height)
            pygame.draw.rect(screen, (150, 150, 150), scroll_bar_rect)
        
        pygame.display.flip()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return -1  # Signal to quit
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = event.pos
                    for button_rect, level_idx in button_rects:
                        if button_rect.collidepoint(mouse_pos):
                            selected_level = level_idx
                            menu_running = False
                            break
                elif event.button == 4:  # Mouse wheel up
                    scroll_offset = max(0, scroll_offset - (button_height + padding))
                elif event.button == 5:  # Mouse wheel down
                    max_scroll = max(0, total_height - available_height)
                    scroll_offset = min(max_scroll, scroll_offset + (button_height + padding))
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return -1  # Signal to quit
        
        clock.tick(60)
    
    return selected_level


def parse_start_level(dg: RLDungeonGenerator, start_level: str | None) -> int | None:
    if start_level is None:
        return None

    # Allow numeric level indices or exact level names.
    try:
        idx = int(start_level)
        if 0 <= idx < len(dg.levels):
            return idx
        print(f"Warning: requested level index {idx} is out of range.")
        return None
    except ValueError:
        pass

    for idx, level_def in enumerate(dg.levels):
        if str(level_def.get('name', '')).lower() == start_level.strip().lower():
            return idx

    print(f"Warning: requested level '{start_level}' was not found.")
    return None


def render_with_pygame(dg: RLDungeonGenerator, force_gui: bool = False, force_menu: bool = False, start_level: str | None = None) -> None:
    import os
    
    if pygame is None:
        info = (
            f"pygame is not installed or failed to import.\n"
            f"Python executable: {sys.executable}\n"
            f"Import traceback:\n{_pygame_import_error}\n"
        )
        print(info)
        raise ImportError(info)

    pygame.init()
    
    # Check if we can actually create a display (detect headless environment)
    # Skip headless detection if GUI is forced, or if we're in VS Code (user wants GUI)
    is_vscode = any(k.startswith('VSCODE_') for k in os.environ.keys())
    
    if not force_gui and not is_vscode:
        import platform
        
        is_headless = (
            os.environ.get('CI', '').lower() in ('true', '1') or
            # Only consider missing DISPLAY as headless on Unix-like systems
            (platform.system() != 'Windows' and os.environ.get('DISPLAY', '') == '') or
            not hasattr(sys.stdout, 'isatty') or
            not sys.stdout.isatty()
        )
        
        if is_headless:
            # Headless environment detected, fall back to ASCII output
            print("Headless environment detected. Using ASCII output.")
            if dg.levels:
                dg.apply_level(0)
                dg.generate_map()
            else:
                dg.generate_map()
            dg.print_map()
            return
    
    try:
        test_surface = pygame.display.set_mode((1, 1))
        pygame.display.quit()  # Clean up test surface
        pygame.init()  # Re-init after quit
    except Exception:
        # Headless environment detected, fall back to ASCII output
        print("Headless environment detected. Using ASCII output.")
        if dg.levels:
            dg.apply_level(0)
            dg.generate_map()
        else:
            dg.generate_map()
        dg.print_map()
        return
    
    # Initial viewport in tiles (used to create starting window)
    init_view_w = min(40, dg.width)
    init_view_h = min(25, dg.height)
    pixel_view_w = init_view_w * dg.tile_size
    pixel_view_h = init_view_h * dg.tile_size

    # Create a resizable window so the user can maximize or adjust it.
    screen = pygame.display.set_mode((pixel_view_w, pixel_view_h), pygame.RESIZABLE)
    pygame.display.set_caption(f"RLDungeonGenerator - {dg.get_current_level_name()}")
    clock = pygame.time.Clock()

    # Attempt to load a PNG tilesheet first (same path as tcod renderer)
    tile_surfaces_orig = None
    tile_surfaces = None
    png_tileset_path = os.path.join(os.path.dirname(__file__), 'assets', 'tilesets', 'unicode_tileset.png')
    if os.path.exists(png_tileset_path):
        try:
            sheet = pygame.image.load(png_tileset_path).convert_alpha()
            sheet_w, sheet_h = sheet.get_size()
            cols = sheet_w // dg.tile_size
            rows = sheet_h // dg.tile_size
            tile_surfaces_orig = []
            for ty in range(rows):
                for tx in range(cols):
                    rect = pygame.Rect(tx * dg.tile_size, ty * dg.tile_size, dg.tile_size, dg.tile_size)
                    tile = pygame.Surface((dg.tile_size, dg.tile_size), pygame.SRCALPHA)
                    tile.blit(sheet, (0, 0), rect)
                    tile_surfaces_orig.append(tile)
            # Start with a scaled copy equal to original tile size
            tile_surfaces = list(tile_surfaces_orig)
        except Exception:
            tile_surfaces_orig = None
            tile_surfaces = None

    # Fallback to a pygame font renderer (monospace) and glyph cache
    font = pygame.font.SysFont('consolas', dg.tile_size, bold=False)
    # Smaller popup font for damage numbers
    try:
        popup_font = pygame.font.SysFont('consolas', max(10, dg.tile_size // 2), bold=True)
    except Exception:
        popup_font = pygame.font.SysFont(None, max(10, dg.tile_size // 2))
    glyph_cache = {}
    # Keep initial view size in tiles fixed; tile size will change on window resize
    init_view_w = min(40, dg.width)
    init_view_h = min(25, dg.height)

    movement_key_map = {
        pygame.K_UP: (0.0, -1.0),
        pygame.K_w: (0.0, -1.0),
        pygame.K_DOWN: (0.0, 1.0),
        pygame.K_s: (0.0, 1.0),
        pygame.K_LEFT: (-1.0, 0.0),
        pygame.K_a: (-1.0, 0.0),
        pygame.K_RIGHT: (1.0, 0.0),
        pygame.K_d: (1.0, 0.0),
    }
    held_directions = []
    shift_held = False
    inventory_open = False

    selected_level_idx = None
    if dg.levels:
        selected_level_idx = parse_start_level(dg, start_level)
        if selected_level_idx is None or force_menu:
            selected_level_idx = show_level_selection_menu(screen, dg, clock, font)
            if selected_level_idx == -1:
                pygame.quit()
                return
    
    if selected_level_idx is not None:
        dg.apply_level(selected_level_idx)
    dg.generate_map()
    pygame.display.set_caption(f"RLDungeonGenerator - {dg.get_current_level_name()}")

    running = True
    last_frame_time = time.time()
    while running:
        current_time = time.time()
        delta_time = current_time - last_frame_time
        last_frame_time = current_time
        if delta_time > 0.1:
            delta_time = 0.1

        # Update temporary attack effects (visual only)
        dg._update_attack_effects(current_time)
        # Update damage popups
        dg._update_damage_popups(current_time)

        # Movement updates: use delta-time based movement so speed is tiles/sec independent of tile_size
        # Apply continuous movement from held keys using `update_movement` which uses `player_speed_pixels`.
        if held_directions:
            sum_dx = sum(d[0] for d in held_directions)
            sum_dy = sum(d[1] for d in held_directions)
            def sign(v):
                return 1 if v > 0 else (-1 if v < 0 else 0)
            mdx = sign(sum_dx)
            mdy = sign(sum_dy)
            if mdx != 0 or mdy != 0:
                dg.update_movement(delta_time, (mdx, mdy))
        else:
            dg.update_movement(delta_time, (0.0, 0.0))

        # Update monsters (aggro & movement)
        dg.update_monsters(delta_time)

        # Update viewport to keep tile count fixed and instead adjust tile size
        pixel_view_w, pixel_view_h = screen.get_size()
        view_w = init_view_w
        view_h = init_view_h

        # Compute the largest integer tile size that fits both dimensions
        desired_tile_w = max(1, pixel_view_w // view_w)
        desired_tile_h = max(1, pixel_view_h // view_h)
        new_tile_size = min(desired_tile_w, desired_tile_h)

        # If tile size changed, update dg.tile_size, rescale tiles and font, and clear glyph cache
        if new_tile_size != dg.tile_size:
            old_tile_size = dg.tile_size
            # Preserve player's tile+fractional offset so they don't appear to move on resize
            try:
                if old_tile_size > 0:
                    frac_x = dg.player_x / old_tile_size - dg.player_col
                    frac_y = dg.player_y / old_tile_size - dg.player_row
                else:
                    frac_x = 0.5
                    frac_y = 0.5
            except Exception:
                frac_x = 0.5
                frac_y = 0.5

            dg.tile_size = new_tile_size
            # Keep movement speed consistent in tiles/sec regardless of pixel tile size
            try:
                dg.player_speed_pixels = dg.player_speed_tiles_per_sec * dg.tile_size
                dg.player_radius = dg.tile_size * 0.375
            except Exception:
                pass
            # Rescale tile surfaces if we have originals
            if tile_surfaces_orig is not None:
                try:
                    tile_surfaces = [pygame.transform.smoothscale(s, (dg.tile_size, dg.tile_size)) for s in tile_surfaces_orig]
                except Exception:
                    tile_surfaces = list(tile_surfaces_orig)
            # Recreate font at new size and clear glyph cache
            try:
                font = pygame.font.SysFont('consolas', dg.tile_size, bold=False)
            except Exception:
                font = pygame.font.SysFont(None, dg.tile_size)
            try:
                popup_font = pygame.font.SysFont('consolas', max(10, dg.tile_size // 2), bold=True)
            except Exception:
                popup_font = pygame.font.SysFont(None, max(10, dg.tile_size // 2))
            glyph_cache.clear()

            # Recompute player pixel coordinates to keep the same tile and fractional offset
            try:
                dg.player_x = (dg.player_col + frac_x) * dg.tile_size
                dg.player_y = (dg.player_row + frac_y) * dg.tile_size
            except Exception:
                # Fallback: center player in its tile
                dg.player_x = (dg.player_col + 0.5) * dg.tile_size
                dg.player_y = (dg.player_row + 0.5) * dg.tile_size

            # Rescale monster pixel positions to match new tile size
            for monster in dg.monsters:
                if 'x' in monster and 'y' in monster:
                    try:
                        m_frac_x = monster['x'] / old_tile_size - monster['col']
                        m_frac_y = monster['y'] / old_tile_size - monster['row']
                        monster['x'] = (monster['col'] + m_frac_x) * dg.tile_size
                        monster['y'] = (monster['row'] + m_frac_y) * dg.tile_size
                        monster['col'] = int(monster['x'] / dg.tile_size)
                        monster['row'] = int(monster['y'] / dg.tile_size)
                    except Exception:
                        monster['x'] = (monster['col'] + 0.5) * dg.tile_size
                        monster['y'] = (monster['row'] + 0.5) * dg.tile_size
                        monster['col'] = monster['col']
                        monster['row'] = monster['row']

        # Compute used pixel area for tiles and center it in the window if extra space exists
        used_w = view_w * dg.tile_size
        used_h = view_h * dg.tile_size
        offset_x = (pixel_view_w - used_w) // 2 if pixel_view_w > used_w else 0
        offset_y = (pixel_view_h - used_h) // 2 if pixel_view_h > used_h else 0

        # Draw background (fill entire window)
        screen.fill((10, 10, 10))

        # Camera top-left in tiles (clamped so camera doesn't go out of bounds)
        cam_ty = int(dg.player_y / dg.tile_size) - view_h // 2
        cam_tx = int(dg.player_x / dg.tile_size) - view_w // 2
        if cam_ty < 0: cam_ty = 0
        if cam_tx < 0: cam_tx = 0
        if cam_ty > dg.height - view_h: cam_ty = max(0, dg.height - view_h)
        if cam_tx > dg.width - view_w: cam_tx = max(0, dg.width - view_w)

        for ty in range(view_h):
            wr = cam_ty + ty
            for tx in range(view_w):
                wc = cam_tx + tx
                x = offset_x + tx * dg.tile_size
                y = offset_y + ty * dg.tile_size
                
                # Handle out-of-bounds areas
                if wr < 0 or wr >= dg.height or wc < 0 or wc >= dg.width:
                    pygame.draw.rect(screen, (10, 10, 10), (x, y, dg.tile_size, dg.tile_size))
                    continue
                    
                ch = dg.dungeon[wr][wc].get_ch()
                tile = dg.dungeon[wr][wc]
                # determine colors and glyph from active level
                if tile.tile_type == DungeonSqr.WALL:  # wall
                    fg = dg.color_wall_fg
                    bg = dg.color_wall_bg
                    glyph = ch
                elif tile.tile_type == DungeonSqr.FLOOR:  # floor
                    fg = dg.color_floor_fg
                    bg = dg.color_floor_bg
                    glyph = ch
                elif tile.tile_type == DungeonSqr.DOOR:  # door
                    fg = (255, 215, 0)
                    bg = (0, 0, 0)
                    glyph = '+'
                elif tile.tile_type == DungeonSqr.EXIT:  # exit
                    fg = dg.color_floor_fg
                    bg = dg.color_floor_bg
                    glyph = ch
                else:
                    fg = (255, 255, 255)
                    bg = (0, 0, 0)
                    glyph = ch

                if not dg.explored[wr][wc]:
                    fg = dg.color_fog_fg
                    bg = dg.color_fog_bg

                if tile_surfaces is not None:
                    # Use a shared glyph index from the tileset for walls/floors and a dedicated one for doors.
                    if glyph in (dg.wall_glyph, dg.floor_glyph):
                        idx = ord(glyph)
                    elif glyph == '+':
                        idx = DOOR_GLYPH_INDEX
                    else:
                        idx = ord(glyph)
                    # Draw background color so walls vs floors are distinguishable.
                    pygame.draw.rect(screen, bg, (x, y, dg.tile_size, dg.tile_size))
                    if idx < len(tile_surfaces):
                        screen.blit(tile_surfaces[idx], (x, y))
                    else:
                        # fallback to a filled rect and rendered glyph
                        pygame.draw.rect(screen, bg, (x, y, dg.tile_size, dg.tile_size))
                        surf = glyph_cache.get((glyph, fg))
                        if surf is None:
                            surf = font.render(glyph, True, fg)
                            glyph_cache[(glyph, fg)] = surf
                        screen.blit(surf, (x, y))
                else:
                    pygame.draw.rect(screen, bg, (x, y, dg.tile_size, dg.tile_size))
                    surf = glyph_cache.get((glyph, fg))
                    if surf is None:
                        surf = font.render(glyph, True, fg)
                        glyph_cache[(glyph, fg)] = surf
                    # center glyph inside tile
                    sw, sh = surf.get_size()
                    screen.blit(surf, (x + (dg.tile_size - sw)//2, y + (dg.tile_size - sh)//2))

        # Draw objects
        for obj in dg.objects:
            obj_row = obj['row']
            obj_col = obj['col']
            if (cam_ty <= obj_row < cam_ty + view_h and
                    cam_tx <= obj_col < cam_tx + view_w):
                obj_px = (obj_col + 0.5) * dg.tile_size - cam_tx * dg.tile_size + offset_x
                obj_py = (obj_row + 0.5) * dg.tile_size - cam_ty * dg.tile_size + offset_y
                x = int(obj_px - 0.5 * dg.tile_size)
                y = int(obj_py - 0.5 * dg.tile_size)
                glyph_index = obj['type']['glyph_index']
                if tile_surfaces is not None and glyph_index < len(tile_surfaces):
                    screen.blit(tile_surfaces[glyph_index], (x, y))
                else:
                    pygame.draw.rect(screen, (80, 60, 40), (x, y, dg.tile_size, dg.tile_size))

        # Draw player as a white circle at sub-tile position
        player_px = dg.player_x - cam_tx * dg.tile_size + offset_x
        player_py = dg.player_y - cam_ty * dg.tile_size + offset_y
        pygame.draw.circle(screen, (255, 255, 255), (int(player_px), int(player_py)), max(2, dg.tile_size // 3))

        # Draw monsters
        for monster in dg.monsters:
                    # Compute integer tile coords for visibility check
                    monster_row = monster.get('row', int(monster.get('y', 0) / dg.tile_size))
                    monster_col = monster.get('col', int(monster.get('x', 0) / dg.tile_size))
                    if (cam_ty <= monster_row < cam_ty + view_h and 
                        cam_tx <= monster_col < cam_tx + view_w):
                        # Pixel position for smooth movement
                        monster_px = monster.get('x', (monster_col + 0.5) * dg.tile_size) - cam_tx * dg.tile_size + offset_x
                        monster_py = monster.get('y', (monster_row + 0.5) * dg.tile_size) - cam_ty * dg.tile_size + offset_y
                        x = int(monster_px - 0.5 * dg.tile_size)
                        y = int(monster_py - 0.5 * dg.tile_size)

                        # Use monster glyph from tileset
                        glyph_index = monster['type']['glyph_index']
                        if tile_surfaces is not None and glyph_index < len(tile_surfaces):
                            # Draw monster sprite centered on tile
                            screen.blit(tile_surfaces[glyph_index], (x, y))
                        else:
                            # Fallback: draw red circle
                            pygame.draw.circle(screen, (255, 0, 0), (int(monster_px), int(monster_py)), max(2, dg.tile_size // 4))

                        # Draw alert indicator if alerted
                        if monster.get('alerted'):
                            try:
                                ex_surf = popup_font.render('!', True, (255, 0, 0))
                                ex_rect = ex_surf.get_rect(center=(int(monster_px), int(monster_py - dg.tile_size * 0.5 - 6)))
                                screen.blit(ex_surf, ex_rect)
                            except Exception:
                                # fallback to a small red rectangle
                                rx = int(monster_px) - 2
                                ry = int(monster_py - dg.tile_size * 0.5 - 8)
                                pygame.draw.rect(screen, (255, 0, 0), (rx, ry, 4, 6))

        # Draw damage popups (float up and fade over their lifetime)
        for popup in dg.damage_popups:
            popup_row, popup_col = popup['row'], popup['col']
            if (cam_ty <= popup_row < cam_ty + view_h and 
                cam_tx <= popup_col < cam_tx + view_w):
                popup_px = (popup_col - cam_tx + 0.5) * dg.tile_size + offset_x
                # Base Y (just above the monster)
                base_py = (popup_row - cam_ty + 0.5) * dg.tile_size + offset_y - dg.tile_size // 2
                created = popup.get('created_at', current_time)
                expires = popup.get('expires_at', created + 2.0)
                duration = max(0.0001, expires - created)
                age = current_time - created
                progress = min(max(age / duration, 0.0), 1.0)
                # Float distance in pixels (move up by ~1.5 tiles over lifetime)
                float_pixels = dg.tile_size * 1.5
                y_offset = -int(float_pixels * progress)
                popup_text = str(popup['damage'])
                # White smaller text
                try:
                    popup_surf = popup_font.render(popup_text, True, (255, 255, 255))
                except Exception:
                    popup_surf = font.render(popup_text, True, (255, 255, 255))
                # Fade out as it ages
                try:
                    alpha = int(255 * (1.0 - progress))
                    if alpha < 0: alpha = 0
                    if alpha > 255: alpha = 255
                    popup_surf.set_alpha(alpha)
                except Exception:
                    pass
                popup_rect = popup_surf.get_rect(center=(int(popup_px), int(base_py + y_offset)))
                screen.blit(popup_surf, popup_rect)

        # Draw attack effects overlay (if any)
        if dg.attack_effects:
            overlay = pygame.Surface((dg.tile_size, dg.tile_size), pygame.SRCALPHA)
            overlay.fill((255, 0, 0, 100))
            for effect in dg.attack_effects:
                for (er, ec) in effect['tiles']:
                    if cam_ty <= er < cam_ty + view_h and cam_tx <= ec < cam_tx + view_w:
                        ex = offset_x + (ec - cam_tx) * dg.tile_size
                        ey = offset_y + (er - cam_ty) * dg.tile_size
                        screen.blit(overlay, (ex, ey))

        # Draw health and stamina bars
        bar_tile_size = dg.tile_size
        
        # Health bar (vertical, red, bottom left)
        # Each tile represents 25 health, so 1 full tile
        health_tiles = max(1, (dg.health + 24) // 25)  # Round up
        max_health_tiles = max(1, (dg.max_health + 24) // 25)
        health_bar_x = offset_x + 10
        health_bar_y = offset_y + used_h - (max_health_tiles * bar_tile_size) - 10
        for i in range(max_health_tiles):
            tile_y = health_bar_y + i * bar_tile_size
            if i < health_tiles:
                pygame.draw.rect(screen, (255, 0, 0), (health_bar_x, tile_y, bar_tile_size, bar_tile_size))
            pygame.draw.rect(screen, (100, 100, 100), (health_bar_x, tile_y, bar_tile_size, bar_tile_size), 2)
        
        # Health number (centered in bar)
        health_font = pygame.font.SysFont('consolas', 16, bold=True)
        health_text = health_font.render(f'{dg.health}', True, (255, 255, 255))
        health_text_rect = health_text.get_rect(center=(health_bar_x + bar_tile_size // 2, health_bar_y + (max_health_tiles * bar_tile_size) // 2))
        screen.blit(health_text, health_text_rect)
        
        # Stamina bar (horizontal, yellow, slightly above bottom center)
        # Each tile represents 25 stamina, so 2 full tiles
        stamina_tiles = max(1, (dg.stamina + 24) // 25)  # Round up
        max_stamina_tiles = max(1, (dg.max_stamina + 24) // 25)
        stamina_bar_x = offset_x + (used_w - (max_stamina_tiles * bar_tile_size)) // 2
        stamina_bar_y = offset_y + used_h - (2 * bar_tile_size) - 10
        for i in range(max_stamina_tiles):
            tile_x = stamina_bar_x + i * bar_tile_size
            if i < stamina_tiles:
                pygame.draw.rect(screen, (200, 200, 0), (tile_x, stamina_bar_y, bar_tile_size, bar_tile_size))
            pygame.draw.rect(screen, (100, 100, 100), (tile_x, stamina_bar_y, bar_tile_size, bar_tile_size), 2)
        
        # Stamina number (centered in bar)
        stamina_text = health_font.render(f'{dg.stamina}', True, (255, 255, 255))
        stamina_text_rect = stamina_text.get_rect(center=(stamina_bar_x + (max_stamina_tiles * bar_tile_size) // 2, stamina_bar_y + bar_tile_size // 2))
        screen.blit(stamina_text, stamina_text_rect)

        # Draw inventory (hotbar always; full inventory when inventory_open)
        INV_SLOT_SIZE = 32
        INV_SLOT_PAD = 3
        INV_MARGIN = 8
        INV_COLS = 8
        inv_slot_font = pygame.font.SysFont('consolas', 10)
        inv_rows = 4 if inventory_open else 1
        for row in range(inv_rows):
            for col in range(INV_COLS):
                sx = offset_x + INV_MARGIN + col * (INV_SLOT_SIZE + INV_SLOT_PAD)
                sy = offset_y + INV_MARGIN + row * (INV_SLOT_SIZE + INV_SLOT_PAD)
                pygame.draw.rect(screen, (30, 30, 30), (sx, sy, INV_SLOT_SIZE, INV_SLOT_SIZE))
                pygame.draw.rect(screen, (110, 110, 110), (sx, sy, INV_SLOT_SIZE, INV_SLOT_SIZE), 1)
                if row == 0:
                    num_surf = inv_slot_font.render(str(col + 1), True, (180, 180, 180))
                    screen.blit(num_surf, (sx + INV_SLOT_SIZE - num_surf.get_width() - 2, sy + 2))

        pygame.display.flip()
        # Update window title with current level
        pygame.display.set_caption(f"RLDungeonGenerator - {dg.get_current_level_name()}")

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    target = dg.screen_to_tile(event.pos[0], event.pos[1], cam_tx, cam_ty, offset_x, offset_y, view_w, view_h)
                    if target is not None:
                        tr, tc = target
                        # Trace a line of tiles from player to clicked tile and look
                        # for the first monster on that ray. If found, retarget
                        # the attack to that monster's tile.
                        line_tiles = dg.bresenham_line(dg.player_row, dg.player_col, tr, tc)
                        chosen = None
                        # skip the first tile because it's the player's tile
                        for (lr, lc) in line_tiles[1:]:
                            for m in dg.monsters:
                                if m.get('row') == lr and m.get('col') == lc:
                                    chosen = (lr, lc)
                                    break
                            if chosen:
                                break

                        if chosen is not None:
                            tr, tc = chosen

                        # Draw the line as a short-lived visual effect
                        try:
                            dg._add_attack_effect(set(line_tiles), duration=0.25)
                        except Exception:
                            pass

                        dg.perform_attack(tr, tc)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    shift_held = True
                    dg.player_speed_pixels = 7.0 * dg.tile_size
                elif event.key == pygame.K_TAB:
                    inventory_open = not inventory_open
                else:
                    direction = movement_key_map.get(event.key)
                    if direction is not None and direction not in held_directions:
                        held_directions.append(direction)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    shift_held = False
                    dg.player_speed_pixels = 3.0 * dg.tile_size
                else:
                    direction = movement_key_map.get(event.key)
                    if direction is not None and direction in held_directions:
                        held_directions.remove(direction)
            elif event.type == pygame.VIDEORESIZE:
                # Recreate the window surface to the new size while keeping RESIZABLE
                try:
                    screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                except Exception:
                    pass

        # Cap framerate and allow high-res timers
        clock.tick(60)

    pygame.quit()


def main() -> None:
    parser = argparse.ArgumentParser(description="RLDungeonGenerator with optional tcod rendering")
    parser.add_argument("--width", type=int, default=150, help="Dungeon width in tiles")
    parser.add_argument("--height", type=int, default=80, help="Dungeon height in tiles")
    parser.add_argument("--ascii", action="store_true", help="Print ASCII map to console instead of opening a window")
    parser.add_argument("--gui", action="store_true", help="Force GUI mode even in headless environments")
    parser.add_argument("--menu", action="store_true", help="Always show level selection menu (even in VS Code)")
    parser.add_argument("--level", type=str, help="Select a level by index or name and skip the level menu.")
    args = parser.parse_args()

    dg = RLDungeonGenerator(args.width, args.height)
    
    try:
        if args.ascii:
            # Go straight to a level if available, otherwise generate procedurally
            if dg.levels:
                selected_level_idx = parse_start_level(dg, args.level)
                if selected_level_idx is None:
                    selected_level_idx = 0
                dg.apply_level(selected_level_idx)
                dg.generate_map()
            else:
                dg.generate_map()
            dg.print_map()
        else:
            # Prefer pygame renderer if available
            if pygame is not None:
                render_with_pygame(dg, args.gui, args.menu, args.level)
            else:
                render_with_tcod(dg)
    except Exception:
        traceback.print_exc()
        try:
            input("Press Enter to exit...")
        except Exception:
            pass

if __name__ == "__main__":
    main()
