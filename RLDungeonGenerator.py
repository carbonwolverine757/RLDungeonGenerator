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

try:
    import tcod
    import tcod.tileset
    import tcod.image
    _tcod_import_error = None
except Exception as e:
    tcod = None
    import traceback as _tb
    _tcod_import_error = _tb.format_exc()

# Prefer pygame for rendering when available
try:
    import pygame
    _pygame_import_error = None
except Exception:
    pygame = None
    import traceback as _tb2
    _pygame_import_error = _tb2.format_exc()

# numpy is optional only required for pixel rendering path
try:
    import numpy as np
except Exception:
    np = None

class DungeonSqr:
    def __init__(self, sqr):
        self.sqr = sqr

    def get_ch(self):
        return self.sqr

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
        self.player_speed_pixels = 120.0  # pixels per second
        self.player_radius = 6.0
        self.last_revealed_tile = (-1, -1)

        for h in range(self.height):
            row = []
            for w in range(self.width):
                row.append(DungeonSqr('\u2588'))  # FULL BLOCK for walls

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
                    self.dungeon[r][c] = DungeonSqr('\u00B7')  # MIDDLE DOT for floors

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
                self.dungeon[row][c] = DungeonSqr('\u00B7')  # MIDDLE DOT for floors

            if end_col - start_col >= 4:
                self.dungeon[row][start_col] = DungeonSqr('+')
                self.dungeon[row][end_col - 1] = DungeonSqr('+')
            elif start_col == end_col - 1:
                self.dungeon[row][start_col] = DungeonSqr('+')
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
                self.dungeon[r][col] = DungeonSqr('\u00B7')  # MIDDLE DOT for floors

            if end_row - start_row >= 4:
                self.dungeon[start_row][col] = DungeonSqr('+')
                self.dungeon[end_row - 1][col] = DungeonSqr('+')
            elif start_row == end_row - 1:
                self.dungeon[start_row][col] = DungeonSqr('+')

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
        self.random_split(1, 1, self.height - 1, self.width - 1)
        self.carve_rooms()
        self.connect_rooms()
        self.spawn_player()
        self.reveal_current_area()

    def is_walkable(self, r, c):
        if r < 0 or c < 0 or r >= self.height or c >= self.width:
            return False
        ch = self.dungeon[r][c].get_ch()
        return ch in ('\u00B7', '+')  # MIDDLE DOT (floor) or door

    def spawn_player(self):
        # Prefer the center of the first room if available, otherwise first walkable tile
        if len(self.rooms) > 0:
            room = self.rooms[0]
            r = room.row + room.height // 2
            c = room.col + room.width // 2
            if self.is_walkable(r, c):
                self.set_player_position(r, c)
                return
        for r in range(self.height):
            for c in range(self.width):
                if self.is_walkable(r, c):
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
        if move_x != 0.0:
            nx = self.player_x + move_x
            if self._can_move_to(nx, self.player_y):
                self.player_x = nx
        if move_y != 0.0:
            ny = self.player_y + move_y
            if self._can_move_to(self.player_x, ny):
                self.player_y = ny
        self._update_tile_position()

    def move_by_pixels(self, dx, dy, pixels=1):
        """
        Nudge the player by a given number of pixels in integer direction (dx,dy should be -1/0/1).
        Movement is attempted axis-by-axis with collision checks.
        """
        if pixels == 0:
            return
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

    def _update_tile_position(self):
        # Use float division to preserve sub-tile positions when converting to tile indices
        new_col = int(self.player_x / self.tile_size)
        new_row = int(self.player_y / self.tile_size)
        if new_row != self.player_row or new_col != self.player_col:
            self.player_row = new_row
            self.player_col = new_col
            if (new_row, new_col) != self.last_revealed_tile:
                self.last_revealed_tile = (new_row, new_col)
                self.reveal_current_area()

    def _can_move_to(self, px, py):
        radius = self.player_radius
        # Use precise division instead of floor-division so small pixel moves are detected correctly
        min_col = int((px - radius) / self.tile_size)
        max_col = int((px + radius) / self.tile_size)
        min_row = int((py - radius) / self.tile_size)
        max_row = int((py + radius) / self.tile_size)
        for r in range(min_row, max_row + 1):
            for c in range(min_col, max_col + 1):
                if not self.is_walkable(r, c):
                    return False
        return True

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
            radius = 2
            rr = self.player_row
            cc = self.player_col
            for dr in range(-radius, radius + 1):
                for dc in range(-radius, radius + 1):
                    r = rr + dr
                    c = cc + dc
                    if 0 <= r < self.height and 0 <= c < self.width:
                        if dr*dr + dc*dc <= radius*radius:
                            self.explored[r][c] = True

    def print_map(self):
        for r in range(self.height):
            row = ''
            for c in range(self.width):
                row += self.dungeon[r][c].get_ch()
            print(row)


def render_with_tcod(dg: RLDungeonGenerator) -> None:
    if tcod is None:
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
                        # Handle unexplored areas with dark background
                        if not dg.explored[wr][wc]:
                            y0 = ty * dg.tile_size
                            x0 = tx * dg.tile_size
                            buf[y0:y0+dg.tile_size, x0:x0+dg.tile_size, :3] = (0, 0, 0)
                            buf[y0:y0+dg.tile_size, x0:x0+dg.tile_size, 3] = 255
                            continue
                        if ch == '\u2588':  # FULL BLOCK (wall)
                            idx = ord('\u2588')
                        elif ch == '\u00B7':  # MIDDLE DOT (floor)
                            idx = ord('\u00B7')
                        elif ch == '+':
                            idx = ord('+')
                        else:
                            idx = ord(ch)
                        # Map CP437 indices to tilesheet index - assumes tilesheet arranged by codepoint
                        if idx < len(tile_bitmaps):
                            tile_img = tile_bitmaps[idx]
                            y0 = ty * dg.tile_size
                            x0 = tx * dg.tile_size
                            # Simple alpha blit
                            alpha = tile_img[:, :, 3:4] / 255.0
                            buf[y0:y0+dg.tile_size, x0:x0+dg.tile_size, :3] = (
                                buf[y0:y0+dg.tile_size, x0:x0+dg.tile_size, :3] * (1 - alpha) +
                                tile_img[:, :, :3] * alpha
                            ).astype(np.uint8)
                            buf[y0:y0+dg.tile_size, x0:x0+dg.tile_size, 3] = 255
                        else:
                            # Fallback: fill with background color if tile not found
                            y0 = ty * dg.tile_size
                            x0 = tx * dg.tile_size
                            if ch == '\u2588':  # FULL BLOCK (wall)
                                buf[y0:y0+dg.tile_size, x0:x0+dg.tile_size, :3] = (125, 125, 125)
                            elif ch == '\u00B7':  # MIDDLE DOT (floor)
                                buf[y0:y0+dg.tile_size, x0:x0+dg.tile_size, :3] = (180, 180, 180)
                            elif ch == '+':
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
                        if ch == '\u2588':  # FULL BLOCK (wall)
                            fg = (125, 125, 125)
                            bg = (10, 10, 10)
                            glyph = ord('\u2588')
                        elif ch == '\u00B7':  # MIDDLE DOT (floor)
                            fg = (180, 180, 180)
                            bg = (30, 30, 30)
                            glyph = ord('\u00B7')
                        elif ch == '+':
                            fg = (255, 215, 0)
                            bg = (0, 0, 0)
                            glyph = ord('+')
                        else:
                            fg = (255, 255, 255)
                            bg = (0, 0, 0)
                            glyph = ord(ch)
                        if not dg.explored[wr][wc]:
                            fg = (int(fg[0] * 0.15), int(fg[1] * 0.15), int(fg[2] * 0.15))
                            bg = (0, 0, 0)
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
                context.present(console)

            # Process events (non-blocking)
            for event in tcod.event.get():
                if event.type == "QUIT":
                    return
                if event.type == "KEYDOWN":
                    if event.sym == tcod.event.K_ESCAPE:
                        return
                    # Add to held directions for frame-based movement
                    direction = movement_key_map.get(event.sym)
                    if direction is not None:
                        # keep unique entries
                        if direction not in held_directions:
                            held_directions.append(direction)
                if event.type == "KEYUP":
                    # Remove from held directions
                    direction = movement_key_map.get(event.sym)
                    if direction is not None and direction in held_directions:
                        held_directions.remove(direction)

            # Small sleep to prevent excessive CPU usage
            time.sleep(0.001)


def render_with_pygame(dg: RLDungeonGenerator) -> None:
    if pygame is None:
        info = (
            f"pygame is not installed or failed to import.\n"
            f"Python executable: {sys.executable}\n"
            f"Import traceback:\n{_pygame_import_error}\n"
        )
        print(info)
        raise ImportError(info)

    pygame.init()
    # Viewport size in tiles (match tcod defaults used earlier)
    view_w = min(40, dg.width)
    view_h = min(25, dg.height)
    pixel_view_w = view_w * dg.tile_size
    pixel_view_h = view_h * dg.tile_size

    screen = pygame.display.set_mode((pixel_view_w, pixel_view_h))
    pygame.display.set_caption("RLDungeonGenerator")
    clock = pygame.time.Clock()

    # Attempt to load a PNG tilesheet first (same path as tcod renderer)
    tile_surfaces = None
    png_tileset_path = os.path.join(os.path.dirname(__file__), 'assets', 'tilesets', 'unicode_tileset.png')
    if os.path.exists(png_tileset_path):
        try:
            sheet = pygame.image.load(png_tileset_path).convert_alpha()
            sheet_w, sheet_h = sheet.get_size()
            cols = sheet_w // dg.tile_size
            rows = sheet_h // dg.tile_size
            tile_surfaces = []
            for ty in range(rows):
                for tx in range(cols):
                    rect = pygame.Rect(tx * dg.tile_size, ty * dg.tile_size, dg.tile_size, dg.tile_size)
                    tile = pygame.Surface((dg.tile_size, dg.tile_size), pygame.SRCALPHA)
                    tile.blit(sheet, (0, 0), rect)
                    tile_surfaces.append(tile)
        except Exception:
            tile_surfaces = None

    # Fallback to a pygame font renderer (monospace) and glyph cache
    font = pygame.font.SysFont('consolas', dg.tile_size, bold=False)
    glyph_cache = {}

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

    running = True
    last_frame_time = time.time()
    while running:
        current_time = time.time()
        delta_time = current_time - last_frame_time
        last_frame_time = current_time
        if delta_time > 0.1:
            delta_time = 0.1

        # Movement updates
        dg.update_movement(delta_time, (0.0, 0.0))
        if held_directions:
            sum_dx = sum(d[0] for d in held_directions)
            sum_dy = sum(d[1] for d in held_directions)
            def sign(v):
                return 1 if v > 0 else (-1 if v < 0 else 0)
            mdx = sign(sum_dx)
            mdy = sign(sum_dy)
            if mdx != 0 or mdy != 0:
                dg.move_by_pixels(int(mdx), int(mdy), pixels=1)

        # Draw background
        screen.fill((10, 10, 10))

        # Camera top-left in tiles
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
                x = tx * dg.tile_size
                y = ty * dg.tile_size
                
                # Handle out-of-bounds areas
                if wr < 0 or wr >= dg.height or wc < 0 or wc >= dg.width:
                    pygame.draw.rect(screen, (10, 10, 10), (x, y, dg.tile_size, dg.tile_size))
                    continue
                    
                ch = dg.dungeon[wr][wc].get_ch()
                # determine colors and glyph
                if ch == '\u2588':  # FULL BLOCK (wall)
                    fg = (125, 125, 125)
                    bg = (10, 10, 10)
                    glyph = '\u2588'
                elif ch == '\u00B7':  # MIDDLE DOT (floor)
                    fg = (180, 180, 180)
                    bg = (30, 30, 30)
                    glyph = '\u00B7'
                elif ch == '+':
                    fg = (255, 215, 0)
                    bg = (0, 0, 0)
                    glyph = '+'
                else:
                    fg = (255, 255, 255)
                    bg = (0, 0, 0)
                    glyph = ch

                if not dg.explored[wr][wc]:
                    fg = (int(fg[0] * 0.15), int(fg[1] * 0.15), int(fg[2] * 0.15))
                    bg = (0, 0, 0)

                if tile_surfaces is not None:
                    idx = ord(glyph)
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

        # Draw player as a white circle at sub-tile position
        player_px = dg.player_x - cam_tx * dg.tile_size
        player_py = dg.player_y - cam_ty * dg.tile_size
        pygame.draw.circle(screen, (255, 255, 255), (int(player_px), int(player_py)), max(2, dg.tile_size // 3))

        pygame.display.flip()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                direction = movement_key_map.get(event.key)
                if direction is not None and direction not in held_directions:
                    held_directions.append(direction)
            elif event.type == pygame.KEYUP:
                direction = movement_key_map.get(event.key)
                if direction is not None and direction in held_directions:
                    held_directions.remove(direction)

        # Cap framerate and allow high-res timers
        clock.tick(60)

    pygame.quit()


def main() -> None:
    parser = argparse.ArgumentParser(description="RLDungeonGenerator with optional tcod rendering")
    parser.add_argument("--width", type=int, default=75, help="Dungeon width in tiles")
    parser.add_argument("--height", type=int, default=40, help="Dungeon height in tiles")
    parser.add_argument("--ascii", action="store_true", help="Print ASCII map to console instead of opening a window")
    args = parser.parse_args()

    dg = RLDungeonGenerator(args.width, args.height)
    dg.generate_map()

    try:
        if args.ascii:
            dg.print_map()
        else:
            # Prefer pygame renderer if available
            if pygame is not None:
                render_with_pygame(dg)
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
