# This code is released into the Public Domain.
from math import sqrt
from random import random
from random import randrange
from random import choice
import argparse
import os
import sys
import time
import atexit
import math

# If a debugger is attached (e.g. Visual Studio), pause on exit so console window stays open
def _pause_on_exit_if_debugger():
    try:
        if sys.gettrace() is not None:
            try:
                print("\nDebugger detected. Press Enter to exit...")
                input()
            except Exception:
                pass
    except Exception:
        pass

atexit.register(_pause_on_exit_if_debugger)

try:
    import tcod
    import tcod.tileset
except Exception:
    tcod = None

from weapons_data import get_weapon_by_name, get_all_weapons

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
        self.equipped_slot = None  # No weapon equipped initially
        self.facing = (0, 1)
        self.last_swing = None
        self.mouse_tile = None

        # Inventory UI state
        self.inventory_open = False
        self.hovered_item = None  # Track hovered item for tooltip display
        self.hovered_ground_item = None  # Track hovered ground item
        self.dragged_item = None  # Item being dragged
        self.dragged_from_slot = None  # (row, col) of the item being dragged

        # Inventory: 4 rows x 8 cols. Top row (row 0) is the hotbar.
        self.inventory = [[None for _ in range(8)] for _ in range(4)]
        # Add a wooden sword in the first hotbar slot (copy from weapons data)
        wooden_sword = get_weapon_by_name("Wooden Sword")
        if wooden_sword:
            wooden_sword['type'] = 'weapon'
            self.inventory[0][0] = wooden_sword
            self.equipped_slot = 0  # Auto-equip the wooden sword

        # Stamina fields: regen and cooldown
        self.stamina_regen_rate = 10.0  # stamina per second
        self.stamina_cooldown_seconds = 1.0  # seconds without regen after attack
        self.stamina_cooldown_until = 0.0
        self.last_stamina_update = time.time()
        
        # Track the last attack time for attack speed limiting
        self.last_attack_time = 0.0
        
        # Ground items (weapons and coins lying on the ground)
        self.ground_items = {}

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
        """Swing the currently equipped weapon at the mouse tile if in range, 
        or at the farthest tile in that direction within range."""
        if self.equipped_slot is None:
            return
        item = self.inventory[0][self.equipped_slot]
        if item is None or item.get("type") != "weapon":
            return
        
        # Get weapon stats
        damage = item.get('damage', 5)
        stamina_cost = item.get('stamina_use', 3)
        attack_speed = item.get('attack_speed', 1.0)
        weapon_range = item.get('range', 0)
        
        now = time.time()
        
        # Check if enough stamina
        if getattr(self, 'player_stamina', 0) < stamina_cost:
            return
        
        # Check if attack is on cooldown
        if now - self.last_attack_time < attack_speed:
            return
        
        # Determine target tile
        if self.mouse_tile is None:
            return
        
        mouse_row, mouse_col = self.mouse_tile
        
        # Calculate distance to mouse tile
        dr_mouse = mouse_row - self.player_row
        dc_mouse = mouse_col - self.player_col
        distance_to_mouse = max(abs(dr_mouse), abs(dc_mouse))  # Chebyshev distance (diagonal)
        
        # Determine direction
        def sign(x):
            return 0 if x == 0 else (1 if x > 0 else -1)
        
        dr = sign(dr_mouse)
        dc = sign(dc_mouse)
        
        if dr == 0 and dc == 0:
            return
        
        # Consume stamina and update cooldown
        self.player_stamina = max(0, self.player_stamina - stamina_cost)
        self.stamina_cooldown_until = now + self.stamina_cooldown_seconds
        self.last_attack_time = now
        
        # Determine max distance to attack
        # For melee weapons (range=0), always attack at least 1 tile
        # For ranged weapons, attack to mouse if in range, otherwise to max range
        if weapon_range == 0:
            # Melee: always attack at least 1 tile (adjacent)
            max_dist = max(1, distance_to_mouse)
        elif distance_to_mouse <= weapon_range:
            # Ranged: mouse is in range, attack to mouse
            max_dist = distance_to_mouse
        else:
            # Ranged: mouse is out of range, attack to weapon range
            max_dist = weapon_range
        
        # Process attacks on all tiles from player toward target
        # This creates a line attack effect
        for dist in range(1, max_dist + 1):
            tr = self.player_row + dr * dist
            tc = self.player_col + dc * dist
            
            # Stop if out of bounds
            if tr < 0 or tc < 0 or tr >= self.height or tc >= self.width:
                break
            
            ch = self.dungeon[tr][tc].get_ch()
            
            # Stop at walls
            if ch == '#':
                break
            
            # Mark swing location for visual feedback
            self.last_swing = (tr, tc)
            
            # Check for monsters at this location
            hit = False
            for i, m in enumerate(list(self.monsters)):
                if m['row'] == tr and m['col'] == tc:
                    m['health'] -= damage
                    hit = True
                    if m['health'] <= 0:
                        try:
                            self.monsters.pop(i)
                        except Exception:
                            if m in self.monsters:
                                self.monsters.remove(m)
                        self.dungeon[tr][tc] = DungeonSqr('o')
                        self.explored[tr][tc] = True
                    break
            
            if hit:
                break  # Stop after hitting first target
            
            # Open doors
            if ch == '+':
                self.dungeon[tr][tc] = DungeonSqr('.')
                self.explored[tr][tc] = True

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
        # spawn weapon items after map and exit placed
        try:
            self.spawn_weapon_items()
        except Exception:
            pass

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

    def add_weapon_to_inventory(self, weapon):
        """Try to add a weapon dict to the first available inventory slot. Returns True if added."""
        if weapon is None:
            return False
        # ensure it's a copy and marked as weapon
        w = weapon.copy()
        w['type'] = 'weapon'
        # Search for first empty slot (hotbar preferred: row 0 then rows 1-3)
        for r in range(4):
            for c in range(8):
                if self.inventory[r][c] is None:
                    self.inventory[r][c] = w
                    return True
        # Inventory full
        return False

    def spawn_weapon_items(self):
        """Randomly place one of each weapon on floor tiles as pickable ground items."""
        try:
            weapons = get_all_weapons()
        except Exception:
            return
        # Prepare ground_items mapping if not present
        if not hasattr(self, 'ground_items') or self.ground_items is None:
            self.ground_items = {}

        floor_tiles = [(r, c) for r in range(self.height) for c in range(self.width) if self.dungeon[r][c].get_ch() == '.']
        # Remove player position and exit and monster positions from candidates
        floor_tiles = [p for p in floor_tiles if p != (self.player_row, self.player_col) and p != (self.exit_row, self.exit_col)]
        # Remove tiles occupied by monsters
        monster_positions = {(m['row'], m['col']) for m in self.monsters}
        floor_tiles = [p for p in floor_tiles if p not in monster_positions]
        if not floor_tiles:
            return
        import random as _rand
        _rand.shuffle(floor_tiles)
        idx = 0
        for w in weapons:
            # find next available tile
            while idx < len(floor_tiles) and floor_tiles[idx] in self.ground_items:
                idx += 1
            if idx >= len(floor_tiles):
                break
            pos = floor_tiles[idx]
            idx += 1
            item = w.copy()
            item['type'] = 'weapon'
            # store by world coords
            self.ground_items[(pos[0], pos[1])] = item

    def pickup_coins(self):
        picked = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                r = self.player_row + dr
                c = self.player_col + dc
                if 0 <= r < self.height and 0 <= c < self.width:
                    # pick up coins
                    if self.dungeon[r][c].get_ch() == 'o':
                        self.dungeon[r][c] = DungeonSqr('.')
                        self.explored[r][c] = True
                        self.add_item_to_inventory('coin', 1)
                        picked += 1
                    # pick up weapons on ground_items mapping
                    if hasattr(self, 'ground_items') and (r, c) in self.ground_items:
                        item = self.ground_items.pop((r, c))
                        # try to add to inventory
                        if self.add_weapon_to_inventory(item):
                            picked += 1
                        else:
                            # inventory full, put it back
                            self.ground_items[(r, c)] = item
        return picked

    def drop_item_in_direction(self, item, direction_row, direction_col):
        """Drop an item in the world in a direction from the player.
        Returns True if dropped successfully, False otherwise."""
        if not hasattr(self, 'ground_items'):
            self.ground_items = {}
        
        # Find a walkable tile in the given direction
        dr = 1 if direction_row > 0 else (-1 if direction_row < 0 else 0)
        dc = 1 if direction_col > 0 else (-1 if direction_col < 0 else 0)
        
        for distance in range(1, 4):  # Try up to 3 tiles away
            drop_r = self.player_row + dr * distance
            drop_c = self.player_col + dc * distance
            
            if 0 <= drop_r < self.height and 0 <= drop_c < self.width:
                ch = self.dungeon[drop_r][drop_c].get_ch()
                # Check if tile is walkable and not occupied
                if ch in ('.', '+', 'o') and (drop_r, drop_c) not in self.ground_items:
                    # Check if no monsters are there
                    occupied = False
                    for m in self.monsters:
                        if m['row'] == drop_r and m['col'] == drop_c:
                            occupied = True
                            break
                    if not occupied:
                        item_copy = item.copy()
                        self.ground_items[(drop_r, drop_c)] = item_copy
                        return True
        return False


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
    """On BearLib_Terminal branch, delegate to BearLibTerminal renderer."""
    try:
        from render_bearlib import render_with_bearlib
        render_with_bearlib(dg)
        return
    except ImportError:
        raise ImportError("BearLibTerminal is not installed. Install with: pip install bearlib")
    except Exception as e:
        print(f"Error loading render_bearlib: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise


def main():
    """Start the game always using BearLibTerminal renderer (no CLI required)."""
    sys.tracebacklimit = 1000
    try:
        print("=" * 60)
        print("RLDungeonGenerator - Initializing (BearLibTerminal mode)")
        print("=" * 60)

        w = 80
        h = 45
        print(f"Creating dungeon generator (size: {w}x{h})...")
        dg = RLDungeonGenerator(w, h, level=0)

        print("Generating map...")
        dg.generate_map()
        print(f"Map generated successfully. Level: {dg.level_template.get('name', 'Unknown')}")
        print()

        # Always use BearLibTerminal renderer
        try:
            from render_bearlib import render_with_bearlib
            print("Starting BearLibTerminal renderer...")
            render_with_bearlib(dg)
            print("Game ended (BearLibTerminal renderer).")
            return
        except ImportError:
            print("✗ BearLibTerminal is not installed")
            print("Install with: pip install bearlib")
            print("\nFalling back to ASCII output...")
            dg.print_map()
            print("\nGame ended (ASCII fallback).")
            return
        except Exception as e:
            print(f"✗ BearLibTerminal renderer error: {type(e).__name__}: {e}")
            print("Falling back to ASCII output...")
            dg.print_map()
            print("\nGame ended (ASCII fallback).")
            return

    except KeyboardInterrupt:
        print("\n\nGame interrupted by user (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        print(f"\n{'='*60}")
        print("FATAL ERROR - Initialization Failed")
        print(f"{'='*60}")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        print()
        import traceback
        print("Technical details:")
        print("-" * 60)
        traceback.print_exc()
        sys.exit(1)

# Ensure main() is called when the script is executed directly
if __name__ == '__main__':
    main()
