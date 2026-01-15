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

# Level template progression
# Each level defines parameters for dungeon generation
LEVEL_TEMPLATES = [
    {
        'name': 'Caverns',
        'room_size_min_pct': 60,
        'room_size_max_pct': 100,
        'floor_fg': (200, 210, 235),
        'floor_bg': (20, 20, 40),
        'wall_fg': (125, 125, 125),
        'wall_bg': (40, 40, 50),
        'door_weight': 1.0,
        'monster_count': 20,
        'monster_health': 15,
    },
    {
        'name': 'Underground Halls',
        'room_size_min_pct': 50,
        'room_size_max_pct': 90,
        'floor_fg': (180, 180, 200),
        'floor_bg': (30, 30, 50),
        'wall_fg': (100, 100, 120),
        'wall_bg': (50, 50, 70),
        'door_weight': 1.2,
        'monster_count': 30,
        'monster_health': 20,
    },
    {
        'name': 'Dark Dungeons',
        'room_size_min_pct': 40,
        'room_size_max_pct': 80,
        'floor_fg': (160, 160, 180),
        'floor_bg': (20, 20, 30),
        'wall_fg': (80, 80, 100),
        'wall_bg': (30, 30, 40),
        'door_weight': 1.5,
        'monster_count': 40,
        'monster_health': 25,
    },
    {
        'name': 'Obsidian Depths',
        'room_size_min_pct': 30,
        'room_size_max_pct': 70,
        'floor_fg': (140, 140, 160),
        'floor_bg': (10, 10, 20),
        'wall_fg': (60, 60, 80),
        'wall_bg': (20, 20, 30),
        'door_weight': 2.0,
        'monster_count': 50,
        'monster_health': 30,
    },
    {
        'name': 'Abyss',
        'room_size_min_pct': 20,
        'room_size_max_pct': 60,
        'floor_fg': (100, 100, 120),
        'floor_bg': (5, 5, 15),
        'wall_fg': (40, 40, 60),
        'wall_bg': (10, 10, 20),
        'door_weight': 2.5,
        'monster_count': 60,
        'monster_health': 40,
        'generation': 'open_space',  # Specify open space generation
    },
]

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
    def __init__(self, w, h, level=0):
        self.MAX = 15 # Cutoff for when we want to stop dividing sections
        self.width = w
        self.height = h
        self.leaves = []
        self.dungeon = []
        self.rooms = []
        self.player_row = 0
        self.player_col = 0

        # Level progression
        self.current_level = level
        # Level card timing (show when entering a level)
        self.level_card_duration = 1.5
        self.level_card_until = 0.0
        self.set_level_template(level)

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
        self.stamina_regen_rate = 10.0  # stamina per second
        self.stamina_cooldown_seconds = 1.0  # seconds without regen after attack
        self.stamina_cooldown_until = 0.0
        self.last_stamina_update = time.time()

    def set_level_template(self, level):
        """Set the current level template based on level number."""
        if level >= len(LEVEL_TEMPLATES):
            level = len(LEVEL_TEMPLATES) - 1
        self.level_template = LEVEL_TEMPLATES[level]
        self.current_level = level
        # Start level card display timer
        try:
            self.level_card_until = time.time() + self.level_card_duration
        except Exception:
            self.level_card_until = time.time() + 1.5

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
            min_pct = self.level_template.get('room_size_min_pct', 60) / 100
            max_pct = self.level_template.get('room_size_max_pct', 100) / 100
            room_width = round(randrange(int(min_pct * 100), int(max_pct * 100) + 1) / 100 * section_width)
            room_height = round(randrange(int(min_pct * 100), int(max_pct * 100) + 1) / 100 * section_height)
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

    def generate_open_space(self):
        """Generate a huge open area: floors everywhere and walls only on the outer border.
        Also create a single large Room representing the interior so room-based logic still works."""
        # Fill borders with walls and interior with floor
        for r in range(self.height):
            for c in range(self.width):
                if r == 0 or c == 0 or r == self.height - 1 or c == self.width - 1:
                    self.dungeon[r][c] = DungeonSqr('#')
                else:
                    self.dungeon[r][c] = DungeonSqr('.')
        # Treat the interior as a single room (exclude the border)
        inner_r = 1
        inner_c = 1
        inner_h = max(1, self.height - 2)
        inner_w = max(1, self.width - 2)
        self.rooms = [Room(inner_r, inner_c, inner_h, inner_w)]
        # Place player near center
        self.player_row = self.height // 2
        self.player_col = self.width // 2
        # Reset explored for new map
        self.explored = [[False for _ in range(self.width)] for _ in range(self.height)]

    def generate_map(self):
        # reset and generate
        self.leaves = []
        self.rooms = []
        self.monsters = []
        self.exit_row = None
        self.exit_col = None
        self.dungeon = [[DungeonSqr('#') for _ in range(self.width)] for _ in range(self.height)]
        self.explored = [[False for _ in range(self.width)] for _ in range(self.height)]

        # If the template specifies a custom generation method, use it
        generation_method = self.level_template.get('generation')
        if generation_method == 'open_space':
            self.generate_open_space()
        else:
            self.random_split(1, 1, self.height - 1, self.width - 1)
            self.carve_rooms()
            self.connect_rooms()
            self.spawn_player()

        monster_count = self.level_template.get('monster_count', 20)
        monster_health = self.level_template.get('monster_health', 20)
        self.spawn_monsters(monster_count, monster_health)
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
            # Progress to next level
            next_level = self.current_level + 1
            if next_level >= len(LEVEL_TEMPLATES):
                # Loop back to first level or handle endgame
                next_level = 0
            self.set_level_template(next_level)
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
    # Helper: try different signatures for load_tilesheet
    def try_load_tilesheet(path, tw, th, charmaps=(), cols=None, rows=None):
        # Inspect signature to determine parameter semantics
        try:
            import inspect
            sig = inspect.signature(tcod.tileset.load_tilesheet)
            params = list(sig.parameters.keys())
        except Exception:
            params = []
        # If function expects columns/rows (grid counts), use cols/rows when provided
        use_counts = False
        if len(params) >= 3:
            p1 = params[1].lower()
            p2 = params[2].lower()
            if 'col' in p1 or 'count' in p1 or 'cols' in p1 or 'columns' in p1:
                use_counts = True
            if 'tile' in p1 or 'width' in p1:
                use_counts = False
        # Try explicit charmaps first with appropriate args
        attempts = []
        if use_counts:
            a_args = (path, cols if cols is not None else tw, rows if rows is not None else th)
        else:
            a_args = (path, tw, th)
        for ch in charmaps:
            if ch is None:
                continue
            try:
                return tcod.tileset.load_tilesheet(*a_args, ch)
            except Exception:
                pass
        # Try the 3-arg form (either tile size or cols/rows)
        try:
            return tcod.tileset.load_tilesheet(*a_args)
        except Exception:
            pass
        # Try keyword form if supported
        for ch in charmaps:
            try:
                if use_counts:
                    return tcod.tileset.load_tilesheet(path, a_args[1], a_args[2], charmap=ch)
                else:
                    return tcod.tileset.load_tilesheet(path, a_args[1], a_args[2], charmap=ch)
            except Exception:
                pass
        return None

    # Helper: try different signatures for load_truetype_font
    def try_load_truetype(path, ts, charmaps=()):
        for ch in charmaps:
            if ch is None:
                continue
            try:
                return tcod.tileset.load_truetype_font(path, ts, ch)
            except Exception:
                pass
        # Try without explicit charmap
        try:
            return tcod.tileset.load_truetype_font(path, ts)
        except Exception:
            pass
        for ch in charmaps:
            try:
                return tcod.tileset.load_truetype_font(path, ts, charmap=ch)
            except Exception:
                pass
        return None

    # Detect available charmap constants in tcod (may be in different modules)
    charmap_candidates = []
    charmap_unicode = None
    charmap_cp437 = None
    used_charmap = 'unknown'  # Track which charmap was actually used
    try:
        for src in (getattr(tcod, 'tileset', None), tcod, getattr(tcod, 'constants', None)):
            if src is None:
                continue
            for name in ('CHARMAP_UNICODE', 'CHARMAP_CP437', 'CHARMAP_TCOD', 'CHARMAP_DEFAULT'):
                if hasattr(src, name):
                    try:
                        ch = getattr(src, name)
                        charmap_candidates.append(ch)
                        if name == 'CHARMAP_UNICODE':
                            charmap_unicode = ch
                        elif name == 'CHARMAP_CP437':
                            charmap_cp437 = ch
                    except Exception:
                        pass
    except Exception:
        pass

    # Try a dedicated Unicode tileset image first (if provided)
    unicode_tileset_path = os.path.join(os.path.dirname(__file__), 'assets', 'tilesets', 'unicode_tileset.png')
    if os.path.exists(unicode_tileset_path):
        try:
            # Try to inspect the PNG to determine tile pixel size and grid dimensions
            tile_w = 16
            tile_h = 16
            img_cols = 32
            img_rows = None
            try:
                from PIL import Image
                img = Image.open(unicode_tileset_path)
                img_w, img_h = img.size
                # Prefer the known generator's tile_size=16 if it divides image
                if img_w % 16 == 0 and img_h % 16 == 0:
                    tile_w = tile_h = 16
                    img_cols = img_w // tile_w
                    img_rows = img_h // tile_h
                else:
                    # Fallback: use gcd of dimensions to guess tile size
                    from math import gcd
                    guess = gcd(img_w, img_h)
                    if guess > 0 and guess <= 64:
                        tile_w = tile_h = guess
                        img_cols = img_w // tile_w
                        img_rows = img_h // tile_h
                    else:
                        tile_w = tile_h = 16
                        img_cols = img_w // tile_w if img_w % tile_w == 0 else img_cols
                        img_rows = img_h // tile_h if img_h % tile_h == 0 else img_rows
            except Exception:
                # PIL not available or failed to read; assume generator defaults (16px tiles, 32 cols)
                tile_w = tile_h = 16
                img_cols = 32
                img_rows = None

            # When calling try_load_tilesheet, prefer passing grid counts (cols, rows) which tcod.load_tilesheet expects
            # Prefer a Unicode charmap constant first so codepoints in the image map as intended
            local_charmaps = list(charmap_candidates)
            try:
                # prefer CHARMAP_UNICODE if available in tcod or constants
                ch_unicode = None
                for src in (getattr(tcod, 'tileset', None), tcod, getattr(tcod, 'constants', None)):
                    if src is None:
                        continue
                    if hasattr(src, 'CHARMAP_UNICODE'):
                        ch_unicode = getattr(src, 'CHARMAP_UNICODE')
                        break
                if ch_unicode is not None:
                    # move to front if present
                    if ch_unicode in local_charmaps:
                        local_charmaps.remove(ch_unicode)
                    local_charmaps.insert(0, ch_unicode)
            except Exception:
                pass
            # Try Unicode charmap first explicitly, since our tileset uses Unicode codepoints
            # CP437 only supports 0-255, but our tileset has Unicode codepoints beyond that range
            tileset = None
            if charmap_unicode is not None:
                try:
                    tileset = try_load_tilesheet(unicode_tileset_path, tile_w, tile_h, (charmap_unicode,), cols=img_cols, rows=img_rows)
                    if tileset is not None:
                        used_charmap = 'unicode'
                        print(f"Loaded Unicode tileset image: {unicode_tileset_path} (tile {tile_w}x{tile_h}, cols={img_cols}, rows={img_rows}, charmap=unicode)")
                except Exception as e:
                    print(f"Failed to load with Unicode charmap: {e}")
                    tileset = None
            
            # If Unicode loading succeeded, wrap it
            if tileset is not None:
                class TilesetWrapper:
                    def __init__(self, inner, tw, th, rows=None, cols=None):
                        self._inner = inner
                        self.tile_width = tw
                        self.tile_height = th
                        # Expose shape as (rows, cols) when available or when provided
                        try:
                            if hasattr(inner, 'shape') and getattr(inner, 'shape'):
                                self.shape = getattr(inner, 'shape')
                            else:
                                # use provided rows/cols if available
                                if rows is not None and cols is not None:
                                    self.shape = (int(rows), int(cols))
                                else:
                                    self.shape = None
                        except Exception:
                            self.shape = None
                    def __getattr__(self, name):
                        return getattr(self._inner, name)

                # Pass img_rows/img_cols to wrapper so shape is accurate
                tileset = TilesetWrapper(tileset, tile_w, tile_h, rows=img_rows, cols=img_cols)
                print(f"Wrapped tileset: tile_width={tileset.tile_width}, tile_height={tileset.tile_height}, shape={getattr(tileset, 'shape', None)}")
            else:
                # Unicode charmap not available or failed - don't fall back to CP437 for Unicode tileset
                print(f"WARNING: Could not load {unicode_tileset_path} with CHARMAP_UNICODE. Unicode tileset requires Unicode charmap support in tcod.")
        except Exception as e:
            print(f"Failed to load unicode tileset image: {e}")
            tileset = None

    # Try the project's PNG tileset (keep compatibility with older CP437 mapping)
    if tileset is None:
        png_tileset_path = os.path.join(os.path.dirname(__file__), 'assets', 'tilesets', 'Redjack17ex.png')
        if os.path.exists(png_tileset_path):
            try:
                # attempt to detect grid size via PIL
                try:
                    from PIL import Image
                    pimg = Image.open(png_tileset_path)
                    p_w, p_h = pimg.size
                    # assume tile size 16 unless divisible differently
                    if p_w % 16 == 0 and p_h % 16 == 0:
                        p_cols = p_w // 16
                        p_rows = p_h // 16
                    else:
                        p_cols = None
                        p_rows = None
                except Exception:
                    p_cols = None
                    p_rows = None
                tileset = try_load_tilesheet(png_tileset_path, 16, 16, charmap_candidates, cols=p_cols, rows=p_rows)
                if tileset is not None:
                    print(f"Loaded tilesheet: {png_tileset_path}")
            except Exception as e:
                print(f"Failed to load tilesheet image: {e}")
                tileset = None

    # Fallback: try a set of common system TrueType fonts (prefer Unicode charmap)
    if tileset is None:
        unicode_ttf_paths = [
            os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'consola.ttf'),
            os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'consolab.ttf'),
            '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
            '/usr/share/fonts/truetype/noto/NotoSansMono-Regular.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf',
            '/System/Library/Fonts/Monaco.ttf',
            '/System/Library/Fonts/Menlo.ttc',
        ]
        for path in unicode_ttf_paths:
            if path and os.path.exists(path):
                try:
                    tileset = try_load_truetype(path, 16, charmap_candidates)
                    if tileset is not None:
                        print(f"Loaded TrueType font as tileset: {path}")
                        break
                except Exception:
                    tileset = None
                    continue

    if tileset is None:
        print("Could not load a tileset or TrueType font from system. Falling back to ASCII output. Run with --ascii to skip this attempt.")
        dg.print_map()
        return

    # Print tileset information
    print(f"Tileset loaded: {tileset}")
    print(f"Tileset shape: {getattr(tileset, 'shape', 'unknown')}")
    print(f"Tileset tile_width: {getattr(tileset, 'tile_width', 'unknown')}")
    print(f"Tileset tile_height: {getattr(tileset, 'tile_height', 'unknown')}")
    if hasattr(tileset, 'shape'):
        total_tiles = tileset.shape[0] * tileset.shape[1] if len(tileset.shape) >= 2 else tileset.shape[0]
        print(f"Total tiles available (Unicode/CP437): {total_tiles}")

    # Determine view size: base defaults but don't exceed dungeon size or tileset grid
    default_w = 40
    default_h = 25
    view_w = min(default_w, dg.width)
    view_h = min(default_h, dg.height)
    try:
        # tileset.shape is typically (rows, cols)
        shape = getattr(tileset, 'shape', None)
        if shape:
            if isinstance(shape, (list, tuple)) and len(shape) >= 2:
                max_rows, max_cols = int(shape[0]), int(shape[1])
                # tileset.shape is number of tile rows and cols in the sheet; ensure view doesn't exceed it
                view_w = min(view_w, max_cols)
                view_h = min(view_h, max_rows)
            elif isinstance(shape, int):
                # some implementations expose a single-dimension shape (total tiles)
                total = int(shape)
                max_cols = min(total, default_w)
                view_w = min(view_w, max_cols)
    except Exception:
        # ignore and use defaults
        pass

    # Determine tileset columns/rows (prefer image-detected img_cols/img_rows if available)
    try:
        if 'img_cols' in locals() and img_cols is not None:
            tileset_cols = int(img_cols)
        else:
            _shape = getattr(tileset, 'shape', None)
            if isinstance(_shape, (list, tuple)) and len(_shape) >= 2:
                tileset_rows, tileset_cols = int(_shape[0]), int(_shape[1])
            else:
                tileset_cols = 32
        if 'img_rows' in locals() and img_rows is not None:
            tileset_rows = int(img_rows)
    except Exception:
        tileset_cols = 32
        tileset_rows = None

    base_offset = 32  # generator placed codepoints starting at U+0020

    # Allow small row offset adjustment if tilesheet glyphs are shifted (set to -1 or 1 to tweak)
    tilesheet_row_offset = 0

    # Build tilesheet codepoints mapping matching generate_unicode_tileset.py
    tilesheet_codepoints = None
    try:
        codepoints = list(range(32, 127))
        codepoints += list(range(0x2500, 0x2580))
        codepoints += list(range(0x2580, 0x25A0))
        codepoints += list(range(0x25A0, 0x25FF))
        codepoints += list(range(0x2600, 0x26FF))
        codepoints += list(range(0x2700, 0x27BF))
        codepoints += [0x2588, 0x00B7, 0x2193]
        tilesheet_codepoints = codepoints
    except Exception:
        tilesheet_codepoints = None

    def get_tile_index(row_1based, col_1based_from_left=None, col_1based_from_right=None):
        """Return the tile index (0-based) for the tile at (row, col) in the tilesheet.
        Rows/cols are 1-based. This returns the raw tile index that can be used directly
        with CP437 or TCOD charmaps where tile index N maps to character at position N.
        """
        # convert to 0-based and apply optional offset
        row0 = (row_1based - 1) + tilesheet_row_offset
        if col_1based_from_right is not None:
            col0 = tileset_cols - col_1based_from_right
        elif col_1based_from_left is not None:
            col0 = col_1based_from_left - 1
        else:
            raise ValueError("Must specify a column")
        idx0 = row0 * tileset_cols + col0
        return idx0
    
    def get_char_from_tile_index(tile_idx, use_unicode_charmap=False):
        """Convert a tile index to a character for rendering.
        If use_unicode_charmap is True, use the codepoint from tilesheet_codepoints.
        Otherwise, for CP437/TCOD, tile index N maps directly to character at codepoint N (if < 256).
        For indices >= 256 with CP437/TCOD, fall back to using codepoint from tilesheet_codepoints.
        """
        if use_unicode_charmap:
            # With Unicode charmap, use the codepoint that's actually at this tile index
            if tilesheet_codepoints is not None and 0 <= tile_idx < len(tilesheet_codepoints):
                return chr(tilesheet_codepoints[tile_idx])
            # Fallback: assume codepoint = base_offset + tile_idx
            try:
                return chr(base_offset + tile_idx)
            except:
                return '?'
        else:
            # With CP437/TCOD charmap, tile index N maps to character at codepoint N
            # But CP437 only supports 0-255, so for indices >= 256, use Unicode approach
            if tile_idx < 256:
                try:
                    return chr(tile_idx)
                except:
                    return '?'
            # For indices >= 256, use the codepoint from tilesheet_codepoints (like Unicode)
            if tilesheet_codepoints is not None and 0 <= tile_idx < len(tilesheet_codepoints):
                try:
                    return chr(tilesheet_codepoints[tile_idx])
                except:
                    return '?'
            # Last resort: use base_offset + index
            try:
                return chr(base_offset + tile_idx)
            except:
                return '?'

    def tilesheet_char_for_unicode(cp: int) -> str:
        """Map a Unicode codepoint (logical) to the character code that will display the matching glyph
        from the tilesheet. If a direct mapping exists in tilesheet_codepoints, return that; otherwise
        attempt index-based fallback, then finally return the original character.
        Returns a single-character string.
        """
        try:
            if tilesheet_codepoints is not None:
                # If the requested codepoint is present in the tilesheet, return it directly
                if cp in tilesheet_codepoints:
                    return chr(cp)
                # Otherwise, try to treat cp as an index offset from base_offset
                idx0 = cp - base_offset
                if 0 <= idx0 < len(tilesheet_codepoints):
                    return chr(tilesheet_codepoints[idx0])
                # As a last resort, if cp is within image range, map by raw index
            # Fallback: return original character if nothing else
            return chr(cp)
        except Exception:
            try:
                return chr(cp)
            except Exception:
                return '?'

    # Debugging: print tileset mapping details and computed tile indices for key glyphs
    try:
        print("DEBUG: tileset_cols=", tileset_cols, "tileset_rows=", locals().get('tileset_rows', None))
        print("DEBUG: img_cols=", locals().get('img_cols', None), "img_rows=", locals().get('img_rows', None))
        print("DEBUG: base_offset=", base_offset, "tilesheet_row_offset=", tilesheet_row_offset)
        print("DEBUG: used_charmap=", used_charmap)
        def _dbg_tile(r, c, name):
            tile_idx = get_tile_index(r, col_1based_from_left=c)
            if tilesheet_codepoints is not None and 0 <= tile_idx < len(tilesheet_codepoints):
                cp = tilesheet_codepoints[tile_idx]
            else:
                cp = base_offset + tile_idx
            ch_unicode = get_char_from_tile_index(tile_idx, use_unicode_charmap=True)
            ch_direct = get_char_from_tile_index(tile_idx, use_unicode_charmap=False)
            try:
                ch_display = ch_unicode if use_unicode else ch_direct
            except:
                ch_display = '?'
            print(f"DEBUG: {name} row={r} col={c} -> tile_idx={tile_idx} cp={cp} chr_unicode={ch_unicode} chr_direct={ch_direct} chr_used={ch_display}")
        # Expected generator placements (example positions)
        # Check both column 3 and column 5 for diamond suit
        _dbg_tile(15, 3, 'player_char_col3')
        _dbg_tile(15, 5, 'player_char_col5')
        # Also check what codepoint U+2666 maps to
        if tilesheet_codepoints is not None and 0x2666 in tilesheet_codepoints:
            idx_2666 = tilesheet_codepoints.index(0x2666)
            row_2666 = idx_2666 // tileset_cols + 1
            col_2666 = idx_2666 % tileset_cols + 1
            print(f"DEBUG: Diamond suit U+2666 at tile_idx={idx_2666}, row={row_2666}, col={col_2666}")
        _dbg_tile(8, 8, 'floor_char')
        _dbg_tile(10, 10, 'coin_char')
        _dbg_tile(4, 2, 'monster_char')
        _dbg_tile(9, 1, 'exit_char')
    except Exception as _e:
        print('DEBUG: failed to print tileset debug info:', _e)

    # Calculate tile indices for game entities using specified positions
    # Then convert to characters based on the charmap being used
    # Player character: diamond suit symbol (♦) U+2666
    # With Unicode charmap, we can use the codepoint directly - tcod will find the tile
    player_codepoint = 0x2666  # Diamond suit (♦)
    if tilesheet_codepoints is not None and player_codepoint in tilesheet_codepoints:
        # Find the tile index where this codepoint is located
        player_tile_idx = tilesheet_codepoints.index(player_codepoint)
    else:
        # Fallback: calculate based on row/col if codepoint not found
        # Row 15, column 5 based on tilesheet layout
        player_tile_idx = get_tile_index(15, col_1based_from_left=5)
    attack_tile_idx = get_tile_index(21, col_1based_from_left=20)
    monster_tile_idx = get_tile_index(4, col_1based_from_left=2)
    floor_tile_idx = get_tile_index(8, col_1based_from_left=8)
    coin_tile_idx = get_tile_index(10, col_1based_from_left=10)
    exit_tile_idx = get_tile_index(9, col_1based_from_left=1)
    
    # Determine if we're using Unicode charmap (tile index -> codepoint from tilesheet_codepoints)
    # or CP437/TCOD charmap (tile index -> character at codepoint = tile index)
    use_unicode = (used_charmap == 'unicode')
    
    # Convert tile indices to characters for rendering
    # IMPORTANT: The charmap affects how tcod interprets the tilesheet, but we always need to
    # pass the actual Unicode codepoint that exists in the tilesheet at that tile index.
    # With Unicode charmap: codepoint N maps to tile containing codepoint N
    # With CP437 charmap: codepoint N (0-255) maps to tile index N, but for Unicode codepoints
    # we still need to pass them - tcod should handle it if the tileset supports it
    
    def get_char_from_tile_idx(tile_idx):
        """Get the character for a tile index by using its codepoint from tilesheet_codepoints."""
        if tilesheet_codepoints is not None and 0 <= tile_idx < len(tilesheet_codepoints):
            cp = tilesheet_codepoints[tile_idx]
            return chr(cp)
        # Fallback
        try:
            return chr(base_offset + tile_idx)
        except:
            return '?'
    
    # For player, use the diamond suit codepoint (U+2666) directly
    # NOTE: With CP437 charmap, Unicode codepoints > 255 may not work correctly.
    # The tileset should be loaded with Unicode charmap for best results.
    if tilesheet_codepoints is not None and player_codepoint in tilesheet_codepoints:
        player_char = chr(player_codepoint)  # Use codepoint directly - tcod will find the tile
        print(f"DEBUG: Player character set to U+{player_codepoint:04X} ({player_char})")
    else:
        player_char = get_char_from_tile_idx(player_tile_idx)
        print(f"DEBUG: Player character from tile index {player_tile_idx}: {player_char} (U+{ord(player_char):04X})")
    attack_char = get_char_from_tile_idx(attack_tile_idx)
    monster_char = get_char_from_tile_idx(monster_tile_idx)
    floor_char = get_char_from_tile_idx(floor_tile_idx)
    coin_char = get_char_from_tile_idx(coin_tile_idx)
    exit_char = get_char_from_tile_idx(exit_tile_idx)

    # Print what we computed for debugging
    print(f"DEBUG: Computed characters:")
    print(f"  player_char = U+{ord(player_char):04X} ({player_char})")
    print(f"  attack_char = U+{ord(attack_char):04X} ({attack_char})")
    print(f"  monster_char = U+{ord(monster_char):04X} ({monster_char})")
    print(f"  floor_char = U+{ord(floor_char):04X} ({floor_char})")
    print(f"  coin_char = U+{ord(coin_char):04X} ({coin_char})")
    print(f"  exit_char = U+{ord(exit_char):04X} ({exit_char})")

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

            # If level card is active, show black screen with centered level name
            if getattr(dg, 'level_card_until', 0) > now:
                # fill console with black background
                console.clear(bg=(0,0,0))
                level_name = dg.level_template.get('name', 'Unknown')
                level_str = f"Level {dg.current_level + 1}: {level_name}"
                # draw a simple box with text centered
                box_w = min(view_w - 4, len(level_str) + 4)
                box_h = 3
                box_x = max(0, (view_w - box_w) // 2)
                box_y = max(0, (view_h - box_h) // 2)
                # draw background for box
                for by in range(box_y, box_y + box_h):
                    for bx in range(box_x, box_x + box_w):
                        console.print(bx, by, ' ', fg=(255,255,255), bg=(0,0,0))
                text_x = box_x + (box_w - len(level_str)) // 2
                text_y = box_y + box_h // 2
                console.print(text_x, text_y, level_str, fg=(255,255,255), bg=(0,0,0))
                context.present(console)
                # process a reduced event loop so we can still quit or accept input
                for event in tcod.event.wait(0.05):
                    if event.type == 'QUIT':
                        return
                    if event.type == 'KEYDOWN' and event.sym == tcod.event.K_ESCAPE:
                        return
                continue

            cam_y = dg.player_row - view_h // 2
            cam_x = dg.player_col - view_w // 2
            if cam_y < 0: cam_y = 0
            if cam_x < 0: cam_x = 0
            if cam_y > dg.height - view_h: cam_y = dg.height - view_h
            if cam_x > dg.width - view_w: cam_x = dg.width - view_w

            # Get level template colors
            template = dg.level_template
            floor_fg = template.get('floor_fg', (200, 210, 235))
            floor_bg = template.get('floor_bg', (0, 0, 0))
            wall_fg = template.get('wall_fg', (125, 125, 125))
            wall_bg = template.get('wall_bg', (0, 0, 0))

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
                    # Map logical tile characters to display glyphs
                    if ch == '#':
                        fg = wall_fg
                        disp = '█'  # solid wall
                    elif ch == '.':
                        fg = floor_fg
                        disp = floor_char  # floor symbol from tileset
                    elif ch == '+':
                        fg = (255, 215, 0)
                        disp = '┼'  # door-esque
                    elif ch == 'o':
                        fg = (255, 215, 0)
                        disp = coin_char  # coin symbol from tileset
                    elif ch == dg.exit_char:
                        fg = (50, 200, 50)
                        disp = exit_char  # exit symbol from tileset
                    else:
                        # If underlying map contains letters (e.g. older code), render a safe non-alphanumeric fallback
                        fg = (255, 255, 255)
                        # keep displayed char non-alphanumeric if possible
                        if ch.isalnum():
                            disp = '•'
                        else:
                            disp = ch
                    if not dg.explored[wr][wc]:
                        fg = (int(fg[0] * 0.15), int(fg[1] * 0.15), int(fg[2] * 0.15))
                    if getattr(dg, 'last_swing', None) == (wr, wc):
                        console.print(c, r, attack_char, fg=(255, 100, 50), bg=None)
                    else:
                        console.print(c, r, disp, fg=fg, bg=tile_bg)

            dg.update_monster_alerts()
            for m in getattr(dg, 'monsters', []):
                 mr = m['row'] - cam_y
                 mc = m['col'] - cam_x
                 if 0 <= mr < view_h and 0 <= mc < view_w:
                     if dg.explored[m['row']][m['col']]:
                         # Use tileset symbol for monsters
                         gdisp = monster_char
                         if m.get('alerted', False):
                             console.print(mc, mr, gdisp, fg=(255, 0, 0), bg=(0,0,0))
                         else:
                             console.print(mc, mr, gdisp, fg=(180, 30, 30), bg=(0,0,0))

            pr = dg.player_row - cam_y
            pc = dg.player_col - cam_x
            if 0 <= pr < view_h and 0 <= pc < view_w:
                # Use tileset symbol for the player
                console.print(pc, pr, player_char, fg=(255, 255, 255), bg=(0, 0, 0))

            # HUD hotbar
            for i in range(8):
                x = i
                y = 0
                bg = (50, 50, 50)
                item = dg.inventory[0][i] if i < len(dg.inventory[0]) else None
                if item is None:
                    # show slot number using correct tileset mapping
                    # Digits '0'-'9' are at codepoints 48-57, which in the tileset are at:
                    # index = codepoint - base_offset, row = index // tileset_cols + 1, col = index % tileset_cols + 1
                    digit = i + 1  # 1-8
                    digit_cp = ord('0') + digit  # codepoint for '1'-'8'
                    digit_idx = digit_cp - base_offset
                    digit_row = digit_idx // tileset_cols + 1
                    digit_col = digit_idx % tileset_cols + 1
                    digit_tile_idx = get_tile_index(digit_row, col_1based_from_left=digit_col)
                    digit_char = get_char_from_tile_index(digit_tile_idx, use_unicode_charmap=use_unicode)
                    console.print(x, y, digit_char, fg=(200, 200, 200), bg=bg)
                else:
                    # Use tileset symbols for items
                    if item.get('type') == 'weapon':
                        icon = '⚔'
                    elif item.get('type') == 'coin':
                        # Use coin symbol from tileset, show count if > 1
                        if item.get('count', 1) == 1:
                            icon = coin_char
                        else:
                            icon = tilesheet_char_for_unicode(ord(str(min(9, item.get('count', 1)))[0]))
                    else:
                        icon = '•'
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
                            # show a tilesheet '.' glyph if available
                            console.print(x, y, tilesheet_char_for_unicode(ord('.')), fg=(100, 100, 100), bg=bg)
                        else:
                            if item.get('type') == 'weapon':
                                icon = '⚔'
                            elif item.get('type') == 'coin':
                                if item.get('count', 1) == 1:
                                    icon = coin_char
                                else:
                                    icon = tilesheet_char_for_unicode(ord(str(min(9, item.get('count', 1)))[0]))
                            else:
                                icon = '•'
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
                    icon = '⚔'
                elif itype == 'coin':
                    icon = coin_char
                else:
                    icon = '•'
                count_str = str(count).rjust(3)
                inv_str = f"{count_str} {icon}"
                console.print(inv_x, inv_y + inv_index, inv_str, fg=(200, 200, 200), bg=None)
                inv_index += 1

            # Health bar (uses digits instead of alpha 'H')
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
                # show a digit for filled amount (0-4)
                ch = str(cell_filled)
                if cell_filled >= 4:
                    fg_col = (255, 0, 0)
                elif cell_filled >= 3:
                    fg_col = (220, 30, 30)
                elif cell_filled >= 2:
                    fg_col = (200, 60, 60)
                elif cell_filled >= 1:
                    fg_col = (150, 40, 40)
                else:
                    fg_col = (80, 20, 20)
                console.print(bar_x, y, ch, fg=fg_col, bg=(0,0,0))
            health_str = str(dg.player_health)
            health_num_x = bar_x + 1
            health_num_y = bar_top + bar_height // 2
            if health_num_x + len(health_str) > view_w:
                health_num_x = max(0, view_w - len(health_str))
            console.print(health_num_x, health_num_y, health_str, fg=(255, 200, 200), bg=(0,0,0))

            # Stamina bar (use digits for icons)
            stamina_val = max(0.0, min(dg.player_max_stamina, dg.player_stamina))
            stamina_pct = stamina_val / dg.player_max_stamina
            bar_w = 2
            start_x = max(0, (view_w - bar_w) // 2)
            stamina_y = max(0, bar_top - 1)
            if stamina_pct >= 1.0:
                icons = [('9', (255, 215, 0)), ('9', (255, 215, 0))]
            elif stamina_pct >= 0.5:
                icons = [('9', (255, 215, 0)), ('5', (220, 180, 20))]
            else:
                icons = [('3', (180, 140, 10)), ('1', (100, 80, 0))]
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

            # No level indicator on map — level name shown during fullscreen card only

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
    parser.add_argument("--level", type=int, default=0, help="Starting level (0-4)")
    args = parser.parse_args()
    sys.tracebacklimit = 1000
    w = 80
    h = 45
    dg = RLDungeonGenerator(w, h, level=args.level)
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
