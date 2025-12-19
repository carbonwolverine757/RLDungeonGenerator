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

        # Exit tile (row/col) and character
        self.exit_row = None
        self.exit_col = None
        self.exit_char = '>'

        # Monsters: list of dicts {row, col, health}
        self.monsters = []

        for _ in range(self.height):
            row = []
            for _ in range(self.width):
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
        self.equipped_slot = 0
        self.facing = (0, 1)
        self.last_swing = None
        self.mouse_tile = None

        # Inventory UI state
        self.inventory_open = False

        # Inventory: 4 rows x 8 cols. Top row (row 0) is the hotbar.
        self.inventory = [[None for _ in range(8)] for _ in range(4)]
        # Add a wooden sword in the first hotbar slot
        self.inventory[0][0] = {"type": "weapon", "name": "Wooden Sword", "damage": 5}

        # Stamina fields: regen and cooldown
        self.stamina_regen_rate = 1.0  # stamina per second
        self.stamina_cooldown_seconds = 1.5  # seconds without regen after attack
        self.stamina_cooldown_until = 0.0
        self.last_stamina_update = time.time()

    def swing_weapon(self):
        """Swing the currently equipped weapon in the facing direction."""
        if self.equipped_slot is None:
            return
        item = self.inventory[0][self.equipped_slot]
        if item is None or item.get("type") != "weapon":
            return
        def sign(x):
            return 0 if x == 0 else (1 if x > 0 else -1)
        dr = sign(self.facing[0])
        dc = sign(self.facing[1])
        if dr == 0 and dc == 0:
            return
        now = time.time()
        if getattr(self, 'player_stamina', 0) < 3:
            return
        self.player_stamina = max(0, self.player_stamina - 3)
        self.stamina_cooldown_until = now + self.stamina_cooldown_seconds
        tr = self.player_row + dr
        tc = self.player_col + dc
        if tr < 0 or tc < 0 or tr >= self.height or tc >= self.width:
            return
        ch = self.dungeon[tr][tc].get_ch()
        for i, m in enumerate(list(self.monsters)):
            if m['row'] == tr and m['col'] == tc:
                m['health'] -= 5
                self.last_swing = (tr, tc)
                if m['health'] <= 0:
                    try:
                        self.monsters.pop(i)
                    except Exception:
                        if m in self.monsters:
                            self.monsters.remove(m)
                    self.dungeon[tr][tc] = DungeonSqr('o')
                    self.explored[tr][tc] = True
                return
        if ch == '+':
            self.dungeon[tr][tc] = DungeonSqr('.')
            self.explored[tr][tc] = True
        if ch not in ('.', '+'):
            pass
        self.last_swing = (tr, tc)

    def random_split(self, min_row, min_col, max_row, max_col):
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
            if random() > 0.80: continue
            section_width = leaf[3] - leaf[1]
            section_height = leaf[2] - leaf[0]
            room_width = round(randrange(60, 100) / 100 * section_width)
            room_height = round(randrange(60, 100) / 100 * section_height)
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
        other_group = None
        for group in groups:
            if nearest[0] in group:
                other_group = group
                break
        start_group += other_group
        groups.remove(other_group)

    def connect_rooms(self):
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
        # reset and generate
        self.leaves = []
        self.rooms = []
        self.monsters = []
        self.exit_row = None
        self.exit_col = None
        self.dungeon = [[DungeonSqr('#') for _ in range(self.width)] for _ in range(self.height)]
        self.explored = [[False for _ in range(self.width)] for _ in range(self.height)]
        self.random_split(1, 1, self.height - 1, self.width - 1)
        self.carve_rooms()
        self.connect_rooms()
        self.spawn_player()
        self.spawn_monsters(40, 20)
        self.reveal_current_area()
        self.place_exit()

    def spawn_monsters(self, count=20, health=20):
        floor_tiles = []
        for r in range(self.height):
            for c in range(self.width):
                if self.dungeon[r][c].get_ch() == '.':
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
            self.monsters.append({"row": pos[0], "col": pos[1], "health": health, "state": 'calm', 'alerted': False})

    def add_item_to_inventory(self, item_type, count=1):
        if item_type == 'coin':
            max_stack = 9
            remaining = count
            for r in range(4):
                for c in range(8):
                    slot = self.inventory[r][c]
                    if slot is not None and slot.get('type') == 'coin':
                        space = max_stack - slot.get('count', 0)
                        if space > 0:
                            add = min(space, remaining)
                            slot['count'] = slot.get('count', 0) + add
                            remaining -= add
                            if remaining <= 0:
                                return True
            for r in range(1, 4):
                for c in range(8):
                    if remaining <= 0:
                        return True
                    if self.inventory[r][c] is None:
                        put = min(max_stack, remaining)
                        self.inventory[r][c] = {'type': 'coin', 'count': put, 'name': 'Coin'}
                        remaining -= put
            for c in range(8):
                if remaining <= 0:
                    return True
                if self.inventory[0][c] is None:
                    put = min(max_stack, remaining)
                    self.inventory[0][c] = {'type': 'coin', 'count': put, 'name': 'Coin'}
                    remaining -= put
            return remaining < count
        return False

    def pickup_coins(self):
        picked = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                r = self.player_row + dr
                c = self.player_col + dc
                if 0 <= r < self.height and 0 <= c < self.width:
                    if self.dungeon[r][c].get_ch() == 'o':
                        self.dungeon[r][c] = DungeonSqr('.')
                        self.explored[r][c] = True
                        self.add_item_to_inventory('coin', 1)
                        picked += 1
        return picked

    def is_walkable(self, r, c):
        if r < 0 or c < 0 or r >= self.height or c >= self.width:
            return False
        ch = self.dungeon[r][c].get_ch()
        if ch not in ('.', '+', 'o', self.exit_char):
            return False
        for m in self.monsters:
            if m['row'] == r and m['col'] == c:
                return False
        return True

    def spawn_player(self):
        if len(self.rooms) > 0:
            room = self.rooms[0]
            r = room.row + room.height // 2
            c = room.col + room.width // 2
            if self.is_walkable(r, c) and self.dungeon[r][c].get_ch() != self.exit_char:
                self.player_row = r
                self.player_col = c
                return
        for r in range(self.height):
            for c in range(self.width):
                if self.is_walkable(r, c) and self.dungeon[r][c].get_ch() != self.exit_char:
                    self.player_row = r
                    self.player_col = c
                    return

    def place_exit(self):
        candidates = []
        for r in range(self.height):
            for c in range(self.width):
                if self.dungeon[r][c].get_ch() != '#':
                    continue
                for dr, dc in ((-1,0),(1,0),(0,-1),(0,1)):
                    rr = r + dr
                    cc = c + dc
                    if 0 <= rr < self.height and 0 <= cc < self.width:
                        if self.dungeon[rr][cc].get_ch() == '.':
                            candidates.append((r,c))
                            break
        if not candidates:
            floor_tiles = [(r,c) for r in range(self.height) for c in range(self.width) if self.dungeon[r][c].get_ch() == '.']
            if floor_tiles:
                er, ec = choice(floor_tiles)
                self.dungeon[er][ec] = DungeonSqr(self.exit_char)
                self.exit_row, self.exit_col = er, ec
                return
            er = randrange(0, self.height)
            ec = randrange(0, self.width)
            self.dungeon[er][ec] = DungeonSqr(self.exit_char)
            self.exit_row, self.exit_col = er, ec
            return
        er, ec = choice(candidates)
        self.dungeon[er][ec] = DungeonSqr(self.exit_char)
        self.exit_row, self.exit_col = er, ec

    def reveal_current_area(self):
        current_room = None
        for room in self.rooms:
            if (self.player_row >= room.row and self.player_row < room.row + room.height and
                self.player_col >= room.col and self.player_col < room.col + room.width):
                current_room = room
                break
        if current_room is not None:
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

    def find_room_containing(self, r, c):
        for room in self.rooms:
            if r >= room.row and r < room.row + room.height and c >= room.col and c < room.col + room.width:
                return room
        return None

    def bresenham_los(self, r0, c0, r1, c1):
        dr = abs(r1 - r0)
        dc = abs(c1 - c0)
        sr = 1 if r1 > r0 else -1
        sc = 1 if c1 > c0 else -1
        err = (dr - dc) if dr > dc else (dc - dr)
        r = r0
        c = c0
        while True:
            if r == r1 and c == c1:
                return True
            if dr > dc:
                r += sr
                err -= dc
                if err < 0:
                    c += sc
                    err += dr
            else:
                c += sc
                err -= dr
                if err < 0:
                    r += sr
                    err += dc
            if r == r1 and c == c1:
                return True
            if 0 <= r < self.height and 0 <= c < self.width:
                if self.dungeon[r][c].get_ch() == '#':
                    return False
            else:
                return False

    def update_monster_alerts(self):
        # Find player's room
        player_room = None
        for room in self.rooms:
            if (self.player_row >= room.row and self.player_row < room.row + room.height and
                self.player_col >= room.col and self.player_col < room.col + room.width):
                player_room = room
                break

        target_rooms = set()
        if player_room is not None:
            target_rooms.add(player_room)
            # include adjacent rooms (shared rows or cols)
            for room in self.rooms:
                if room is player_room:
                    continue
                adj = self.are_rooms_adjacent(player_room, room)
                if len(adj[0]) > 0 or len(adj[1]) > 0:
                    target_rooms.add(room)
        else:
            # if player not in a room, consider none
            return

        alert_range = 8.0
        for m in self.monsters:
            # default not alerted
            m['alerted'] = False
            # check if monster is in one of target rooms
            m_room = self.find_room_containing(m['row'], m['col'])
            if m_room not in target_rooms:
                continue
            # line of sight check
            if not self.bresenham_los(self.player_row, self.player_col, m['row'], m['col']):
                continue
            # range check
            dist = sqrt((self.player_row - m['row'])**2 + (self.player_col - m['col'])**2)
            if dist <= alert_range:
                m['alerted'] = True
                m['state'] = 'alerted'
            else:
                m['alerted'] = False
                m['state'] = 'calm'

    def check_exit(self):
        if self.exit_row is not None and self.player_row == self.exit_row and self.player_col == self.exit_col:
            # regenerate map
            self.generate_map()

    def update_stamina(self, dt, now):
        """Update stamina regeneration, respecting cooldown periods."""
        # If we're not in cooldown, regenerate stamina
        if now >= self.stamina_cooldown_until:
            stamina_gain = self.stamina_regen_rate * dt
            self.player_stamina = min(self.player_max_stamina, self.player_stamina + stamina_gain)

    def print_map(self):
        monster_positions = {(m['row'], m['col']) for m in getattr(self, 'monsters', [])}
        for r in range(self.height):
            row = ''
            for c in range(self.width):
                if (r, c) == (self.player_row, self.player_col):
                    row += '@'
                elif (r, c) in monster_positions:
                    row += 'G'
                else:
                    row += self.dungeon[r][c].get_ch()
            print(row)


def render_with_tcod(dg: RLDungeonGenerator) -> None:
    if tcod is None:
        print("tcod is not installed. Install requirements and try again.")
        sys.exit(1)

    tileset = None
    png_tileset_path = os.path.join(os.path.dirname(__file__), 'assets', 'tilesets', 'Redjack17ex.png')
    if os.path.exists(png_tileset_path):
        try:
            tileset = tcod.tileset.load_tilesheet(png_tileset_path, 16, 16, tcod.tileset.CHARMAP_CP437)
        except Exception:
            tileset = None

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

    # Print tileset information
    print(f"Tileset loaded: {tileset}")
    print(f"Tileset shape: {getattr(tileset, 'shape', 'unknown')}")
    print(f"Tileset tile_width: {getattr(tileset, 'tile_width', 'unknown')}")
    print(f"Tileset tile_height: {getattr(tileset, 'tile_height', 'unknown')}")
    if hasattr(tileset, 'shape'):
        total_tiles = tileset.shape[0] * tileset.shape[1] if len(tileset.shape) >= 2 else tileset.shape[0]
        print(f"Total tiles available (CP437): {total_tiles}")

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
        prev_time = time.time()
        while True:
            now = time.time()
            dt = now - prev_time
            prev_time = now
            dg.update_stamina(dt, now)
            console.clear()
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
                    tile_bg = (0, 0, 0)
                    if getattr(dg, 'mouse_tile', None) is not None:
                        mouse_row, mouse_col = dg.mouse_tile
                        if mouse_row == wr and mouse_col == wc:
                            tile_bg = (40, 40, 100)
                    if ch == '#':
                        fg = (125, 125, 125)
                        glyph = ord('#')
                    elif ch == '.':
                        fg = (200, 210, 235)
                        glyph = ord('.')
                    elif ch == '+':
                        fg = (255, 215, 0)
                        glyph = ord('+')
                    elif ch == dg.exit_char:
                        fg = (50, 200, 50)
                        glyph = ord(dg.exit_char)
                    else:
                        fg = (255, 255, 255)
                        glyph = ord(ch)
                    if not dg.explored[wr][wc]:
                        fg = (int(fg[0] * 0.15), int(fg[1] * 0.15), int(fg[2] * 0.15))
                    if getattr(dg, 'last_swing', None) == (wr, wc):
                        console.print(c, r, '*', fg=(255, 100, 50), bg=None)
                    else:
                        console.print(c, r, chr(glyph), fg=fg, bg=tile_bg)

            dg.update_monster_alerts()
            for m in getattr(dg, 'monsters', []):
                 mr = m['row'] - cam_y
                 mc = m['col'] - cam_x
                 if 0 <= mr < view_h and 0 <= mc < view_w:
                     if dg.explored[m['row']][m['col']]:
                         if m.get('alerted', False):
                             console.print(mc, mr, 'G', fg=(255, 0, 0), bg=(0,0,0))
                         else:
                             console.print(mc, mr, 'G', fg=(180, 30, 30), bg=(0,0,0))

            pr = dg.player_row - cam_y
            pc = dg.player_col - cam_x
            if 0 <= pr < view_h and 0 <= pc < view_w:
                console.print(pc, pr, '@', fg=(255, 255, 255), bg=(0, 0, 0))

            # HUD hotbar
            for i in range(8):
                x = i
                y = 0
                bg = (50, 50, 50)
                item = dg.inventory[0][i] if i < len(dg.inventory[0]) else None
                if item is None:
                    console.print(x, y, str(i + 1), fg=(200, 200, 200), bg=bg)
                else:
                    if item.get('type') == 'weapon':
                        icon = 'B'
                    elif item.get('type') == 'coin':
                        icon = 'o' if item.get('count', 1) == 1 else str(min(9, item.get('count', 1)))
                    else:
                        icon = '?'
                    if dg.equipped_slot == i:
                        console.print(x, y, icon, fg=(255, 230, 150), bg=(140, 90, 20))
                    else:
                        console.print(x, y, icon, fg=(200, 200, 200), bg=bg)

            if dg.inventory_open:
                for row in range(1, 4):
                    for col in range(8):
                        x = col
                        y = row
                        bg = (40, 40, 40)
                        item = dg.inventory[row][col]
                        if item is None:
                            console.print(x, y, '.', fg=(100, 100, 100), bg=bg)
                        else:
                            if item.get('type') == 'weapon':
                                icon = 'B'
                            elif item.get('type') == 'coin':
                                icon = 'o' if item.get('count', 1) == 1 else str(min(9, item.get('count', 1)))
                            else:
                                icon = '?'
                            console.print(x, y, icon, fg=(200, 200, 200), bg=bg)

            # Inventory summary
            summary = {}
            for row in range(4):
                for col in range(8):
                    item = dg.inventory[row][col]
                    if item is None:
                        continue
                    key = (item.get('type'), item.get('name'))
                    if key not in summary:
                        summary[key] = {'type': item.get('type'), 'name': item.get('name'), 'count': 0}
                    if item.get('type') == 'coin':
                        summary[key]['count'] += item.get('count', 1)
                    else:
                        summary[key]['count'] += 1
            entry_width = 5
            inv_x = max(0, view_w - entry_width)
            inv_y = 0
            inv_index = 0
            max_inv_rows = view_h
            for (itype, iname), data in summary.items():
                if inv_index >= max_inv_rows:
                    break
                count = data['count']
                if itype == 'weapon':
                    icon = 'B'
                elif itype == 'coin':
                    icon = 'o'
                else:
                    icon = '?'
                count_str = str(count).rjust(3)
                inv_str = f"{count_str} {icon}"
                console.print(inv_x, inv_y + inv_index, inv_str, fg=(200, 200, 200), bg=None)
                inv_index += 1

            # Health bar (uses 'H')
            health_pct = max(0.0, min(1.0, dg.player_health / dg.player_max_health))
            bar_height = 2
            steps = bar_height * 4
            filled_steps = int(round(health_pct * steps))
            bar_x = 0
            bar_top = max(0, view_h - bar_height)
            for i in range(bar_height):
                y = bar_top + i
                cell_index = bar_height - 1 - i
                cell_filled = max(0, min(4, filled_steps - cell_index * 4))
                if cell_filled >= 4:
                    ch = 'H'; fg = (255, 0, 0)
                elif cell_filled >= 3:
                    ch = 'H'; fg = (220, 30, 30)
                elif cell_filled >= 2:
                    ch = 'H'; fg = (200, 60, 60)
                elif cell_filled >= 1:
                    ch = 'H'; fg = (150, 40, 40)
                else:
                    ch = 'H'; fg = (80, 20, 20)
                console.print(bar_x, y, ch, fg=fg, bg=(0,0,0))
            health_str = str(dg.player_health)
            health_num_x = bar_x + 1
            health_num_y = bar_top + bar_height // 2
            if health_num_x + len(health_str) > view_w:
                health_num_x = max(0, view_w - len(health_str))
            console.print(health_num_x, health_num_y, health_str, fg=(255, 200, 200), bg=(0,0,0))

            # Stamina bar (uses 'S')
            stamina_val = max(0.0, min(dg.player_max_stamina, dg.player_stamina))
            stamina_pct = stamina_val / dg.player_max_stamina
            bar_w = 2
            start_x = max(0, (view_w - bar_w) // 2)
            stamina_y = max(0, bar_top - 1)
            if stamina_pct >= 1.0:
                icons = [('S', (255, 215, 0)), ('S', (255, 215, 0))]
            elif stamina_pct >= 0.5:
                icons = [('S', (255, 215, 0)), ('S', (220, 180, 20))]
            else:
                icons = [('S', (180, 140, 10)), ('S', (100, 80, 0))]
            for i in range(bar_w):
                x = start_x + i
                ch, fg = icons[i]
                console.print(x, stamina_y, ch, fg=fg, bg=(0,0,0))
            stamina_str = str(int(max(0, round(dg.player_stamina))))
            stamina_num_x = start_x + bar_w
            stamina_num_y = stamina_y
            if stamina_num_x + len(stamina_str) > view_w:
                stamina_num_x = max(0, view_w - len(stamina_str))
            console.print(stamina_num_x, stamina_num_y, stamina_str, fg=(255, 255, 200), bg=(0,0,0))

            context.present(console)
            dg.last_swing = None

            for event in tcod.event.wait():
                mouse_coords = None
                try:
                    conv = context.convert_event(event)
                except Exception:
                    conv = None
                if conv is not None and getattr(conv, 'tile', None) is not None:
                    mouse_coords = conv.tile
                else:
                    mouse_coords = getattr(event, 'tile', None)

                if event.type == "QUIT":
                    return
                if event.type == "KEYDOWN":
                    if event.sym == tcod.event.K_ESCAPE:
                        return
                    if event.sym == tcod.event.K_TAB:
                        dg.inventory_open = not dg.inventory_open
                    dr = 0; dc = 0
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
                            dg.pickup_coins()

                    key_to_slot = {
                        tcod.event.K_1: 0, tcod.event.K_2: 1, tcod.event.K_3: 2, tcod.event.K_4: 3,
                        tcod.event.K_5: 4, tcod.event.K_6: 5, tcod.event.K_7: 6, tcod.event.K_8: 7,
                    }
                    if event.sym in key_to_slot:
                        slot = key_to_slot[event.sym]
                        if dg.inventory[0][slot] is not None:
                            if dg.equipped_slot == slot:
                                dg.equipped_slot = None
                            else:
                                dg.equipped_slot = slot

                elif event.type == "MOUSEMOTION":
                    if mouse_coords is None:
                        continue
                    mx, my = mouse_coords
                    world_x = cam_x + mx
                    world_y = cam_y + my
                    dg.facing = (world_y - dg.player_row, world_x - dg.player_col)
                    dg.mouse_tile = (world_y, world_x)
                elif event.type == "MOUSEBUTTONDOWN":
                     if event.button == 1:
                        if mouse_coords is None:
                            continue
                        mx, my = mouse_coords
                        world_x = cam_x + mx
                        world_y = cam_y + my
                        dg.facing = (world_y - dg.player_row, world_x - dg.player_col)
                        dg.mouse_tile = (world_y, world_x)
                        dg.swing_weapon()

            dg.check_exit()


def main():
    parser = argparse.ArgumentParser(description="RL Dungeon Generator")
    parser.add_argument("--ascii", action="store_true", help="Force ASCII output, ignore graphics settings")
    args = parser.parse_args()
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
            import traceback
            traceback.print_exc()
            print("render_with_tcod failed; falling back to ASCII output.")
            dg.print_map()

if __name__ == "__main__":
    main()
