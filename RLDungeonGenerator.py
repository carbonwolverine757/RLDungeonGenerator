# This code is released into the Public Domain.
from math import sqrt
from random import random
from random import randrange
from random import choice
import argparse
import os
import sys
import time

try:
    import tcod
    import tcod.tileset
except Exception:
    tcod = None

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
                row.append(DungeonSqr('#'))

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
                    self.dungeon[r][c] = DungeonSqr('.')

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
                self.dungeon[row][c] = DungeonSqr('.')

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
                self.dungeon[r][col] = DungeonSqr('.')

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
        return ch in ('.', '+')

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
        print("tcod is not installed. Install requirements and try again.")
        sys.exit(1)

    # Prefer a project-local bitmap tileset first
    tileset = None
    png_tileset_path = os.path.join(os.path.dirname(__file__), 'assets', 'tilesets', 'Redjack17.png')
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

    # Viewport size (camera window). Smaller than full map = zoomed-in view.
    view_w = min(40, dg.width)
    view_h = min(25, dg.height)
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
    held_directions = []

    with tcod.context.new(
        columns=view_w,
        rows=view_h,
        tileset=tileset,
        title="RLDungeonGenerator",
        vsync=True,
    ) as context:
        last_frame_time = time.time()
        
        while True:
            current_time = time.time()
            delta_time = current_time - last_frame_time
            last_frame_time = current_time
            # Cap delta_time to prevent large jumps
            if delta_time > 0.1:
                delta_time = 0.1
            
            # Determine desired movement direction from input
            input_dx = 0.0
            input_dy = 0.0
            for direction in held_directions:
                input_dx += direction[0]
                input_dy += direction[1]
            dg.update_movement(delta_time, (input_dx, input_dy))
            
            # Draw current dungeon
            console.clear()
            # Camera uses logical tile position (not visual) to prevent jiggling
            # This keeps the map stable while only the player moves smoothly
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
                    if ch == '#':
                        fg = (125, 125, 125)
                        bg = (10, 10, 10)
                        glyph = ord('#')
                    elif ch == '.':
                        # Brighter, slightly bluish floor with lighter background
                        fg = (200, 210, 235)
                        bg = (35, 40, 55)
                        glyph = ord('.')
                    elif ch == '+':
                        fg = (255, 215, 0)
                        bg = (0, 0, 0)
                        glyph = ord('+')
                    else:
                        fg = (255, 255, 255)
                        bg = (0, 0, 0)
                        glyph = ord(ch)
                    # Apply fog-of-war dimming to unexplored tiles
                    if not dg.explored[wr][wc]:
                        fg = (int(fg[0] * 0.15), int(fg[1] * 0.15), int(fg[2] * 0.15))
                        bg = (0, 0, 0)
                    console.print(c, r, chr(glyph), fg=fg, bg=bg)

            # Draw the player as a sprite-like glyph on top of non-wall tiles.
            # Position is derived from pixel coords to allow sub-tile movement feel.
            pr = int(round(dg.player_y / dg.tile_size)) - cam_y
            pc = int(round(dg.player_x / dg.tile_size)) - cam_x
            if 0 <= pr < view_h and 0 <= pc < view_w:
                console.print(pc, pr, '@', fg=(255, 255, 255))
            context.present(console)

            # Process events (non-blocking to allow smooth movement)
            for event in tcod.event.get():
                if event.type == "QUIT":
                    return
                if event.type == "KEYDOWN":
                    if event.sym == tcod.event.K_ESCAPE:
                        return
                    # Track held movement keys for continuous travel
                    direction = movement_key_map.get(event.sym)
                    if direction is not None:
                        if direction in held_directions:
                            held_directions.remove(direction)
                        held_directions.insert(0, direction)
                if event.type == "KEYUP":
                    direction = movement_key_map.get(event.sym)
                    if direction is not None and direction in held_directions:
                        held_directions.remove(direction)

            # Remove directions that are blocked by walls
            for direction in list(held_directions):
                check_dx = direction[0]
                check_dy = direction[1]
                if check_dx == 0 and check_dy == 0:
                    continue
                test_x = dg.player_x + check_dx * dg.player_radius
                test_y = dg.player_y + check_dy * dg.player_radius
                if not dg._can_move_to(test_x, test_y):
                    held_directions.remove(direction)
            
            # Small sleep to prevent excessive CPU usage
            time.sleep(0.001)


def main() -> None:
    parser = argparse.ArgumentParser(description="RLDungeonGenerator with optional tcod rendering")
    parser.add_argument("--width", type=int, default=75, help="Dungeon width in tiles")
    parser.add_argument("--height", type=int, default=40, help="Dungeon height in tiles")
    parser.add_argument("--ascii", action="store_true", help="Print ASCII map to console instead of opening a window")
    args = parser.parse_args()

    dg = RLDungeonGenerator(args.width, args.height)
    dg.generate_map()

    if args.ascii:
        dg.print_map()
    else:
        render_with_tcod(dg)

if __name__ == "__main__":
    main()
