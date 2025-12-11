# This code is released into the Public Domain.
from math import sqrt
from random import random
from random import randrange
from random import choice
import argparse
import os
import sys

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

        # Monsters: list of dicts {row, col, health}
        self.monsters = []

        for h in range(self.height):
            row = []
            for w in range(self.width):
                row.append(DungeonSqr('#'))

            self.dungeon.append(row)

        # Fog-of-war explored grid (all unexplored initially)
        self.explored = [[False for _ in range(self.width)] for _ in range(self.height)]

        # Player stats
        self.player_health = 25
        self.player_max_health = 25
        self.player_stamina = 50
        self.player_max_stamina = 50
        
        # Hotbar (8 item slots, currently empty)
        #self.hotbar = [None] * 8
        # Add a wooden sword in the first hotbar slot
        #self.hotbar[0] = {"type": "weapon", "name": "Wooden Sword", "damage": 5}
        # Currently equipped hotbar slot (None = unequipped)
        # Start with the wooden sword equipped in the first slot for easier testing
        self.equipped_slot = 0
        # Facing direction as a vector (dr, dc) normalized to {-1, 0, 1}
        self.facing = (0, 1)
        # Last swing tile for one-frame visual feedback
        self.last_swing = None
        # Last known mouse tile in world coords (row, col)
        self.mouse_tile = None

        # Inventory: 4 rows x 8 cols. Top row (row 0) is the hotbar.
        self.inventory = [[None for _ in range(8)] for _ in range(4)]
        # Add a wooden sword in the first hotbar slot
        self.inventory[0][0] = {"type": "weapon", "name": "Wooden Sword", "damage": 5}

    def swing_weapon(self):
        """Swing the currently equipped weapon in the facing direction."""
        if self.equipped_slot is None:
            return
        item = self.inventory[0][self.equipped_slot]
        if item is None or item.get("type") != "weapon":
            return
        
        # Normalize facing to unit vector
        def sign(x):
            return 0 if x == 0 else (1 if x > 0 else -1)
        dr = sign(self.facing[0])
        dc = sign(self.facing[1])
        if dr == 0 and dc == 0:
            return
        
        # Check tile 1 step in facing direction
        tr = self.player_row + dr
        tc = self.player_col + dc
        if tr < 0 or tc < 0 or tr >= self.height or tc >= self.width:
            return
        
        ch = self.dungeon[tr][tc].get_ch()
        # If there is a monster at the target tile, apply damage
        for i, m in enumerate(list(self.monsters)):
            if m['row'] == tr and m['col'] == tc:
                m['health'] -= 5
                # store last swing for one-frame highlight in renderer
                self.last_swing = (tr, tc)
                if m['health'] <= 0:
                    # remove monster and leave a coin on the ground
                    try:
                        self.monsters.pop(i)
                    except Exception:
                        # fallback: remove by identity
                        if m in self.monsters:
                            self.monsters.remove(m)
                    self.dungeon[tr][tc] = DungeonSqr('o')
                    self.explored[tr][tc] = True
                return
        # If it's a door, open it. If tile is non-walkable (e.g. wall), register hit.
        if ch == '+':
            self.dungeon[tr][tc] = DungeonSqr('.')
            self.explored[tr][tc] = True
        # For any non-walkable tile (not '.' or '+'), consider it hit
        if ch not in ('.', '+'): 
            # debug feedback omitted in release
            pass
        # store last swing for one-frame highlight in renderer
        self.last_swing = (tr, tc)

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
        # Scatter monsters after player is placed so we don't spawn on the player
        self.spawn_monsters(20, 20)
        self.reveal_current_area()

    def spawn_monsters(self, count=20, health=20):
        """Place up to `count` monsters on random floor tiles ('.'), each with given health."""
        floor_tiles = []
        for r in range(self.height):
            for c in range(self.width):
                if self.dungeon[r][c].get_ch() == '.':
                    # avoid player's tile
                    if r == self.player_row and c == self.player_col:
                        continue
                    floor_tiles.append((r, c))

        if not floor_tiles:
            return

        if count > len(floor_tiles):
            count = len(floor_tiles)

        for _ in range(count):
            pos = choice(floor_tiles)
            floor_tiles.remove(pos)
            self.monsters.append({"row": pos[0], "col": pos[1], "health": health})
    
    def add_item_to_inventory(self, item_type, count=1):
        """Add items to inventory. Coins stack in a single slot if present; otherwise put into first available slot (rows 1..3 first, then hotbar)."""
        if item_type == 'coin':
            # try to find existing coin stack
            for r in range(4):
                for c in range(8):
                    slot = self.inventory[r][c]
                    if slot is not None and slot.get('type') == 'coin':
                        slot['count'] += count
                        return True
            # find first empty slot: prefer rows 1..3, then hotbar (0)
            for r in range(1, 4):
                for c in range(8):
                    if self.inventory[r][c] is None:
                        self.inventory[r][c] = {'type': 'coin', 'count': count, 'name': 'Coin'}
                        return True
            for c in range(8):
                if self.inventory[0][c] is None:
                    self.inventory[0][c] = {'type': 'coin', 'count': count, 'name': 'Coin'}
                    return True
            # inventory full
            return False
        # future item types
        return False

    def pickup_coins(self):
        """Pick up coins on the player's tile and adjacent tiles. Converts coin tile to floor and adds to inventory."""
        picked = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                r = self.player_row + dr
                c = self.player_col + dc
                if 0 <= r < self.height and 0 <= c < self.width:
                    if self.dungeon[r][c].get_ch() == 'o':
                        # pick up
                        self.dungeon[r][c] = DungeonSqr('.')
                        self.explored[r][c] = True
                        self.add_item_to_inventory('coin', 1)
                        picked += 1
        return picked

    def is_walkable(self, r, c):
        if r < 0 or c < 0 or r >= self.height or c >= self.width:
            return False
        ch = self.dungeon[r][c].get_ch()
        # Walkable if floor, door, or coin
        if ch not in ('.', '+', 'o'):
            return False
        # Check if there's a monster on this tile
        for m in self.monsters:
            if m['row'] == r and m['col'] == c:
                return False
        return True

    def spawn_player(self):
        # Prefer the center of the first room if available, otherwise first walkable tile
        if len(self.rooms) > 0:
            room = self.rooms[0]
            r = room.row + room.height // 2
            c = room.col + room.width // 2
            if self.is_walkable(r, c):
                self.player_row = r
                self.player_col = c
                return
        for r in range(self.height):
            for c in range(self.width):
                if self.is_walkable(r, c):
                    self.player_row = r
                    self.player_col = c
                    return

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
        # Print ASCII map with monsters and player overlaid
        monster_positions = {(m['row'], m['col']) for m in getattr(self, 'monsters', [])}
        for r in range(self.height):
            row = ''
            for c in range(self.width):
                if (r, c) == (self.player_row, self.player_col):
                    row += '@'
                elif (r, c) in monster_positions:
                    row += 'M'
                else:
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

    with tcod.context.new(
        columns=view_w,
        rows=view_h,
        tileset=tileset,
        title="RLDungeonGenerator",
        vsync=True,
    ) as context:
        while True:
            # Draw current dungeon
            console.clear()
            # Compute camera top-left to center on player, clamped to map
            cam_y = dg.player_row - view_h // 2
            cam_x = dg.player_col - view_w // 2
            if cam_y < 0: cam_y = 0
            if cam_x < 0: cam_x = 0
            if cam_y > dg.height - view_h: cam_y = dg.height - view_h
            if cam_x > dg.width - view_w: cam_x = dg.width - view_w

            for r in range(view_h):
                wr = cam_y + r
                for c in range(view_w):
                    wc = cam_x + c
                    ch = dg.dungeon[wr][wc].get_ch()
                    # Determine tile background; highlight mouse tile
                    # Note: mouse_tile is (row, col) in world coordinates, wr/wc are also (row, col)
                    tile_bg = (0, 0, 0)  # default bg
                    if getattr(dg, 'mouse_tile', None) is not None:
                        mouse_row, mouse_col = dg.mouse_tile
                        if mouse_row == wr and mouse_col == wc:
                            tile_bg = (40, 40, 100)  # highlight color

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
                    # If this tile was the last swing, draw a brief highlight marker
                    if getattr(dg, 'last_swing', None) == (wr, wc):
                        console.print(c, r, '*', fg=(255, 100, 50), bg=None)
                    else:
                        console.print(c, r, chr(glyph), fg=fg, bg=tile_bg)

            # Draw player last so it appears on top
            # Draw monsters (if their tile has been explored)
            for m in getattr(dg, 'monsters', []):
                mr = m['row'] - cam_y
                mc = m['col'] - cam_x
                if 0 <= mr < view_h and 0 <= mc < view_w:
                    # only draw monsters on explored tiles for now
                    if dg.explored[m['row']][m['col']]:
                        console.print(mc, mr, 'M', fg=(180, 30, 30), bg=None)

            pr = dg.player_row - cam_y
            pc = dg.player_col - cam_x
            if 0 <= pr < view_h and 0 <= pc < view_w:
                console.print(pc, pr, '@', fg=(255, 255, 255), bg=(0, 0, 0))

            # Draw HUD: Hotbar in top-left (8 slots) - inventory row 0
            for i in range(8):
                x = i
                y = 0
                bg = (50, 50, 50)
                item = dg.inventory[0][i] if i < len(dg.inventory[0]) else None
                if item is None:
                    # empty slot: show slot number
                    console.print(x, y, str(i + 1), fg=(200, 200, 200), bg=bg)
                else:
                    # Draw simple icons per type
                    if item.get('type') == 'weapon':
                        icon = '/'
                    elif item.get('type') == 'coin':
                        # show a small coin glyph and count if >1
                        icon = 'o' if item.get('count', 1) == 1 else str(min(9, item.get('count', 1)))
                    else:
                        icon = '?'
                    # When equipped, use brighter background to indicate selection
                    if dg.equipped_slot == i:
                        console.print(x, y, icon, fg=(255, 230, 150), bg=(140, 90, 20))
                    else:
                        console.print(x, y, icon, fg=(200, 200, 200), bg=bg)

            # --- Health bar (vertical) ---
            # Short vertical bar (2 tiles tall) overlaid on dungeon tiles
            health_pct = max(0.0, min(1.0, dg.player_health / dg.player_max_health))
            bar_height = 2  # much shorter
            # Allow sub-tile precision by scaling to 4 steps per cell (for a smoother look)
            steps = bar_height * 4
            filled_steps = int(round(health_pct * steps))
            bar_x = 0
            bar_top = max(0, view_h - bar_height)
            # Draw from top to bottom; decide per-cell which fraction to draw (use block glyphs)
            for i in range(bar_height):
                y = bar_top + i
                # compute how many steps are filled in this cell (0..4)
                cell_index = bar_height - 1 - i
                cell_filled = max(0, min(4, filled_steps - cell_index * 4))
                # choose glyph: use full block for fully filled, lower shades for partial
                if cell_filled >= 4:
                    ch = '█'
                    fg = (255, 0, 0)
                elif cell_filled >= 3:
                    ch = '▓'
                    fg = (220, 30, 30)
                elif cell_filled >= 2:
                    ch = '▒'
                    fg = (200, 60, 60)
                elif cell_filled >= 1:
                    ch = '░'
                    fg = (150, 40, 40)
                else:
                    ch = '░'
                    fg = (80, 20, 20)
                console.print(bar_x, y, ch, fg=fg, bg=None)
            # Overlay health number to the right of the vertical bar
            health_str = str(dg.player_health)
            health_num_x = bar_x + 1
            health_num_y = bar_top + bar_height // 2
            if health_num_x + len(health_str) > view_w:
                health_num_x = max(0, view_w - len(health_str))
            console.print(health_num_x, health_num_y, health_str, fg=(255, 200, 200), bg=None)

            # --- Stamina bar (horizontal) ---
            # Short horizontal bar (2 tiles wide) overlaid on dungeon tiles, centered
            stamina_pct = max(0.0, min(1.0, dg.player_stamina / dg.player_max_stamina))
            bar_w = 2  # much shorter
            steps_w = bar_w * 4
            filled_steps_w = int(round(stamina_pct * steps_w))
            start_x = max(0, (view_w - bar_w) // 2)
            stamina_y = max(0, bar_top - 1)
            for i in range(bar_w):
                x = start_x + i
                # compute how many steps are filled in this cell (0..4)
                cell_filled = max(0, min(4, filled_steps_w - i * 4))
                if cell_filled >= 4:
                    ch = '█'
                    fg = (255, 215, 0)
                elif cell_filled >= 3:
                    ch = '▓'
                    fg = (240, 200, 30)
                elif cell_filled >= 2:
                    ch = '▒'
                    fg = (220, 180, 20)
                elif cell_filled >= 1:
                    ch = '░'
                    fg = (180, 140, 10)
                else:
                    ch = '░'
                    fg = (100, 80, 0)
                console.print(x, stamina_y, ch, fg=fg, bg=None)
            # Overlay stamina number immediately to the right of the short bar
            stamina_str = str(dg.player_stamina)
            stamina_num_x = start_x + bar_w
            stamina_num_y = stamina_y
            if stamina_num_x + len(stamina_str) > view_w:
                stamina_num_x = max(0, view_w - len(stamina_str))
            console.print(stamina_num_x, stamina_num_y, stamina_str, fg=(255, 255, 200), bg=None)

            context.present(console)
            # clear last_swing so highlight only shows for one frame
            dg.last_swing = None

            for event in tcod.event.wait():
                # Try to convert the event through the context so tile coordinates are initialized when available.
                mouse_coords = None
                try:
                    conv = context.convert_event(event)
                except Exception:
                    conv = None
                # If convert_event returned an event with a tile attribute, use it; otherwise fall back to raw event.tile if present
                if conv is not None and getattr(conv, 'tile', None) is not None:
                    mouse_coords = conv.tile
                else:
                    mouse_coords = getattr(event, 'tile', None)

                if event.type == "QUIT":
                    return
                if event.type == "KEYDOWN":
                    if event.sym == tcod.event.K_ESCAPE:
                        return
                    # Movement: arrows and WASD
                    dr = 0
                    dc = 0
                    if event.sym in (tcod.event.K_UP, tcod.event.K_w, tcod.event.K_KP_8):
                        dr = -1
                    elif event.sym in (tcod.event.K_DOWN, tcod.event.K_s, tcod.event.K_KP_2):
                        dr = 1
                    elif event.sym in (tcod.event.K_LEFT, tcod.event.K_a, tcod.event.K_KP_4):
                        dc = -1
                    elif event.sym in (tcod.event.K_RIGHT, tcod.event.K_d, tcod.event.K_KP_6):
                        dc = 1

                    if dr != 0 or dc != 0:
                        nr = dg.player_row + dr
                        nc = dg.player_col + dc
                        if dg.is_walkable(nr, nc):
                            dg.player_row = nr
                            dg.player_col = nc
                            dg.reveal_current_area()
                            # pick up nearby coins after moving
                            dg.pickup_coins()

                    # Equip/unequip hotbar items (slots 1-8)
                    key_to_slot = {
                        tcod.event.K_1: 0, tcod.event.K_2: 1, tcod.event.K_3: 2, tcod.event.K_4: 3,
                        tcod.event.K_5: 4, tcod.event.K_6: 5, tcod.event.K_7: 6, tcod.event.K_8: 7,
                    }
                    if event.sym in key_to_slot:
                        slot = key_to_slot[event.sym]
                        if dg.inventory[0][slot] is not None:
                            # Toggle: equip if not equipped, unequip if already equipped
                            if dg.equipped_slot == slot:
                                dg.equipped_slot = None
                            else:
                                dg.equipped_slot = slot

                elif event.type == "MOUSEMOTION":
                    # Update facing direction based on mouse position (console tile coords -> world coords)
                    if mouse_coords is None:
                        continue
                    mx, my = mouse_coords
                    world_x = cam_x + mx
                    world_y = cam_y + my
                    dg.facing = (world_y - dg.player_row, world_x - dg.player_col)
                    # store mouse tile in world coords (row, col)
                    dg.mouse_tile = (world_y, world_x)
                elif event.type == "MOUSEBUTTONDOWN":
                     if event.button == 1:  # Left click
                        if mouse_coords is None:
                            continue
                        # Update facing using click position in case no prior motion event
                        mx, my = mouse_coords
                        world_x = cam_x + mx
                        world_y = cam_y + my
                        dg.facing = (world_y - dg.player_row, world_x - dg.player_col)
                        dg.mouse_tile = (world_y, world_x)
                        dg.swing_weapon()

def main():
    parser = argparse.ArgumentParser(description="RL Dungeon Generator")
    parser.add_argument("--ascii", action="store_true", help="Force ASCII output, ignore graphics settings")
    args = parser.parse_args()

    # Temporarily disable Python traceback limit for full traceback on errors
    sys.tracebacklimit = 1000

    w = 80
    h = 45
    dg = RLDungeonGenerator(w, h)
    dg.generate_map()

    if args.ascii:
        dg.print_map()
    else:
        try:
            render_with_tcod(dg)
        except Exception:
            # Print full traceback to console so the user can see what failed
            import traceback
            traceback.print_exc()
            print("render_with_tcod failed; falling back to ASCII output.")
            dg.print_map()

if __name__ == "__main__":
    main()
