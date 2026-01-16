# BearLibTerminal Renderer for RLDungeonGenerator
# Provides native layer support for multi-layer tile rendering
# This code is released into the Public Domain.

import time
import os
import sys

try:
    from bearlib import terminal
except ImportError:
    terminal = None


def render_with_bearlib(dg) -> None:
    """Render dungeon using BearLibTerminal with native layering support."""
    if terminal is None:
        print("BearLibTerminal is not installed. Install requirements and try again.")
        sys.exit(1)

    # Terminal configuration
    view_w = 80
    view_h = 45
    
    # Try to load custom tileset
    tileset_path = os.path.join(os.path.dirname(__file__), 'assets', 'tilesets', 'unicode_tileset.png')
    
    # Initialize terminal with tileset or fallback to default font
    if os.path.exists(tileset_path):
        terminal_config = f"window: size={view_w}x{view_h}, cellsize=16x16, title='RLDungeonGenerator'; font: {tileset_path}"
        print(f"Loading tileset from: {tileset_path}")
    else:
        # Fallback: use default monospace font
        terminal_config = f"window: size={view_w}x{view_h}, cellsize=8x16, title='RLDungeonGenerator'; font: default"
        print("Using default font (tileset not found)")

    terminal.open(terminal_config)

    # Define tile characters and their layer assignments
    # Layer 0 = terrain (floors, walls)
    # Layer 1 = objects (coins, items)
    # Layer 2 = entities (monsters, player)
    # Layer 3 = effects (attack highlights)

    def char_code(ch):
        """Return character code for rendering."""
        return ord(ch) if isinstance(ch, str) else ch

    # Define game characters using Unicode
    chars = {
        'wall': '?',        # Solid block
        'floor': '·',       # Middle dot
        'door': '?',        # Plus/cross
        'coin': '¤',        # Currency sign
        'monster': 'G',     # Ghoul
        'player': '?',      # Diamond suit
        'exit': '>',        # Greater than
        'attack': '*',      # Asterisk
    }

    console_width = view_w
    console_height = view_h
    prev_time = time.time()

    try:
        while True:
            now = time.time()
            dt = now - prev_time
            prev_time = now
            dg.update_stamina(dt, now)

            # Level card overlay (full screen transition)
            if getattr(dg, 'level_card_until', 0) > now:
                terminal.clear()
                level_name = dg.level_template.get('name', 'Unknown')
                level_str = f"Level {dg.current_level + 1}: {level_name}"
                
                # Center text
                x = (console_width - len(level_str)) // 2
                y = console_height // 2
                
                # Semi-transparent background
                for row in range(console_height):
                    for col in range(console_width):
                        terminal.color(terminal.color_from_argb(100, 0, 0, 0))
                        terminal.put(col, row, ' ')
                
                # Draw text
                terminal.color('white')
                terminal.put(x, y, level_str)
                terminal.refresh()
                
                # Process minimal input
                key = terminal.read()
                if key == terminal.TK_ESCAPE or key == terminal.TK_CLOSE:
                    break
                continue

            # Calculate camera position
            cam_y = dg.player_row - view_h // 2
            cam_x = dg.player_col - view_w // 2
            if cam_y < 0: cam_y = 0
            if cam_x < 0: cam_x = 0
            if cam_y > dg.height - view_h: cam_y = dg.height - view_h
            if cam_x > dg.width - view_w: cam_x = dg.width - view_w

            terminal.clear()

            # Get level template colors (RGB tuples)
            template = dg.level_template
            floor_fg = template.get('floor_fg', (200, 210, 235))
            floor_bg = template.get('floor_bg', (20, 20, 40))
            wall_fg = template.get('wall_fg', (125, 125, 125))
            wall_bg = template.get('wall_bg', (40, 40, 50))

            # ===== LAYER 0: Terrain =====
            for r in range(view_h):
                wr = cam_y + r
                for c in range(view_w):
                    wc = cam_x + c
                    ch = dg.dungeon[wr][wc].get_ch()
                    
                    # Determine display character and color
                    if ch == '#':
                        disp = chars['wall']
                        fg = wall_fg
                        bg = wall_bg
                    elif ch == '.':
                        disp = chars['floor']
                        fg = floor_fg
                        bg = floor_bg
                    elif ch == '+':
                        disp = chars['door']
                        fg = (255, 215, 0)
                        bg = floor_bg
                    else:
                        # Fallback for unknown tiles
                        disp = ch if not ch.isalnum() else '·'
                        fg = (200, 200, 200)
                        bg = (0, 0, 0)

                    # Fog of war darkening
                    if not dg.explored[wr][wc]:
                        fg = (int(fg[0] * 0.15), int(fg[1] * 0.15), int(fg[2] * 0.15))

                    # Mouse highlight
                    if getattr(dg, 'mouse_tile', None) == (wr, wc):
                        bg = (40, 40, 100)

                    # Render on layer 0
                    terminal.color(terminal.color_from_argb(255, *bg))
                    terminal.put(c, r, ' ')  # Background
                    terminal.color(terminal.color_from_argb(255, *fg))
                    terminal.put(c, r, disp)  # Foreground character

            # ===== LAYER 1: Objects (coins) =====
            for r in range(view_h):
                wr = cam_y + r
                for c in range(view_w):
                    wc = cam_x + c
                    ch = dg.dungeon[wr][wc].get_ch()
                    
                    if ch == 'o' and dg.explored[wr][wc]:
                        terminal.color(terminal.color_from_argb(255, 255, 215, 0))
                        terminal.put(c, r, chars['coin'])

            # ===== LAYER 2: Entities (monsters, player) =====
            dg.update_monster_alerts()
            
            # Draw monsters
            for m in getattr(dg, 'monsters', []):
                mr = m['row'] - cam_y
                mc = m['col'] - cam_x
                if 0 <= mr < view_h and 0 <= mc < view_w:
                    if dg.explored[m['row']][m['col']]:
                        if m.get('alerted', False):
                            terminal.color(terminal.color_from_argb(255, 255, 0, 0))  # Red
                        else:
                            terminal.color(terminal.color_from_argb(255, 180, 30, 30))  # Dark red
                        terminal.put(mc, mr, chars['monster'])

            # Draw player
            pr = dg.player_row - cam_y
            pc = dg.player_col - cam_x
            if 0 <= pr < view_h and 0 <= pc < view_w:
                terminal.color(terminal.color_from_argb(255, 255, 255, 255))  # White
                terminal.put(pc, pr, chars['player'])

            # ===== LAYER 3: Effects (attack highlights) =====
            if getattr(dg, 'last_swing', None) is not None:
                sr = dg.last_swing[0] - cam_y
                sc = dg.last_swing[1] - cam_x
                if 0 <= sr < view_h and 0 <= sc < view_w:
                    terminal.color(terminal.color_from_argb(255, 255, 100, 50))  # Orange
                    terminal.put(sc, sr, chars['attack'])

            # ===== HUD: Hotbar =====
            for i in range(8):
                x = i
                y = 0
                bg = (50, 50, 50)
                item = dg.inventory[0][i] if i < len(dg.inventory[0]) else None
                
                terminal.color(terminal.color_from_argb(255, *bg))
                terminal.put(x, y, ' ')  # Background
                
                if item is None:
                    # Show slot number
                    terminal.color(terminal.color_from_argb(255, 200, 200, 200))
                    terminal.put(x, y, str(i + 1))
                else:
                    # Show item icon
                    if item.get('type') == 'weapon':
                        icon = '?'
                    elif item.get('type') == 'coin':
                        icon = chars['coin']
                    else:
                        icon = '•'
                    
                    if dg.equipped_slot == i:
                        terminal.color(terminal.color_from_argb(255, 255, 230, 150))  # Gold
                    else:
                        terminal.color(terminal.color_from_argb(255, 200, 200, 200))
                    
                    terminal.put(x, y, icon)

            # ===== HUD: Health Bar =====
            health_pct = max(0.0, min(1.0, dg.player_health / dg.player_max_health))
            bar_height = 2
            bar_x = 0
            bar_top = view_h - bar_height
            
            for i in range(bar_height):
                y = bar_top + i
                cell_index = bar_height - 1 - i
                cell_filled = max(0, min(4, int(round(health_pct * 8)) - cell_index * 4))
                
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
                
                terminal.color(terminal.color_from_argb(255, *fg_col))
                terminal.put(bar_x, y, '?')

            # Health text
            health_str = str(int(dg.player_health))
            terminal.color(terminal.color_from_argb(255, 255, 200, 200))
            terminal.put(bar_x + 2, bar_top + bar_height // 2, health_str)

            # ===== HUD: Stamina Bar =====
            stamina_pct = max(0.0, min(1.0, dg.player_stamina / dg.player_max_stamina))
            bar_w = 2
            start_x = (view_w - bar_w) // 2
            stamina_y = bar_top - 1
            
            for i in range(bar_w):
                x = start_x + i
                if stamina_pct >= 1.0:
                    terminal.color(terminal.color_from_argb(255, 255, 215, 0))
                    ch = '?'
                elif stamina_pct >= 0.5:
                    terminal.color(terminal.color_from_argb(255, 220, 180, 20))
                    ch = '?'
                else:
                    terminal.color(terminal.color_from_argb(255, 100, 80, 0))
                    ch = '?'
                
                terminal.put(x, stamina_y, ch)

            # Stamina text
            stamina_str = str(int(dg.player_stamina))
            terminal.color(terminal.color_from_argb(255, 255, 255, 200))
            terminal.put(start_x + bar_w, stamina_y, stamina_str)

            # Refresh display
            terminal.refresh()

            # ===== Input Handling =====
            key = terminal.read()

            if key == terminal.TK_CLOSE or key == terminal.TK_ESCAPE:
                break

            # Arrow keys and WASD movement
            if key == terminal.TK_UP or key == ord('w'):
                dr, dc = -1, 0
            elif key == terminal.TK_DOWN or key == ord('s'):
                dr, dc = 1, 0
            elif key == terminal.TK_LEFT or key == ord('a'):
                dr, dc = 0, -1
            elif key == terminal.TK_RIGHT or key == ord('d'):
                dr, dc = 0, 1
            else:
                dr, dc = 0, 0

            if dr != 0 or dc != 0:
                nr = dg.player_row + dr
                nc = dg.player_col + dc
                if dg.is_walkable(nr, nc):
                    dg.player_row = nr
                    dg.player_col = nc
                    dg.reveal_current_area()
                    dg.pickup_coins()

            # Hotbar selection (1-8)
            if ord('1') <= key <= ord('8'):
                slot = key - ord('1')
                if dg.inventory[0][slot] is not None:
                    if dg.equipped_slot == slot:
                        dg.equipped_slot = None
                    else:
                        dg.equipped_slot = slot

            # Inventory toggle
            if key == ord('i') or key == ord('I'):
                dg.inventory_open = not dg.inventory_open

            # Attack/swing (spacebar)
            if key == terminal.TK_SPACE:
                dg.swing_weapon()

            # Check level exit
            dg.check_exit()

    finally:
        terminal.close()
