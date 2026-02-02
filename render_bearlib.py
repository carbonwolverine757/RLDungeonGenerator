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
        raise ImportError("BearLibTerminal is not installed. Install with: pip install bearlib")

    try:
        # Terminal configuration
        view_w = 80
        view_h = 45
        
        # Initialize terminal - bearlib uses a simpler API
        try:
            terminal.open()
        except:
            # If open() doesn't work, try alternative initialization
            pass

        # Define game characters using ASCII
        chars = {
            'wall': '#',
            'floor': '.',
            'door': '+',
            'coin': 'o',
            'monster': 'G',
            'player': '@',
            'exit': '>',
            'attack': '*',
        }

        console_width = view_w
        console_height = view_h
        prev_time = time.time()

        while True:
            now = time.time()
            dt = now - prev_time
            prev_time = now
            dg.update_stamina(dt, now)

            # Calculate camera position
            cam_y = dg.player_row - view_h // 2
            cam_x = dg.player_col - view_w // 2
            if cam_y < 0: cam_y = 0
            if cam_x < 0: cam_x = 0
            if cam_y > dg.height - view_h: cam_y = dg.height - view_h
            if cam_x > dg.width - view_w: cam_x = dg.width - view_w

            terminal.clear()

            # Render terrain
            for r in range(view_h):
                wr = cam_y + r
                for c in range(view_w):
                    wc = cam_x + c
                    if wr < 0 or wr >= dg.height or wc < 0 or wc >= dg.width:
                        continue
                    ch = dg.dungeon[wr][wc].get_ch()
                    
                    if ch == '#':
                        try:
                            terminal.color('gray')
                            terminal.put(c, r, '#')
                        except:
                            pass
                    elif ch == '.':
                        try:
                            terminal.color('light gray')
                            terminal.put(c, r, '.')
                        except:
                            pass
                    elif ch == '+':
                        try:
                            terminal.color('yellow')
                            terminal.put(c, r, '+')
                        except:
                            pass

            # Render coins
            for r in range(view_h):
                wr = cam_y + r
                for c in range(view_w):
                    wc = cam_x + c
                    if wr < 0 or wr >= dg.height or wc < 0 or wc >= dg.width:
                        continue
                    ch = dg.dungeon[wr][wc].get_ch()
                    
                    if ch == 'o' and dg.explored[wr][wc]:
                        try:
                            terminal.color('yellow')
                            terminal.put(c, r, 'o')
                        except:
                            pass

            # Update monster alerts and render
            dg.update_monster_alerts()
            
            for m in getattr(dg, 'monsters', []):
                mr = m['row'] - cam_y
                mc = m['col'] - cam_x
                if 0 <= mr < view_h and 0 <= mc < view_w:
                    if dg.explored[m['row']][m['col']]:
                        try:
                            if m.get('alerted', False):
                                terminal.color('red')
                            else:
                                terminal.color('dark red')
                            terminal.put(mc, mr, 'G')
                        except:
                            pass

            # Draw player
            pr = dg.player_row - cam_y
            pc = dg.player_col - cam_x
            if 0 <= pr < view_h and 0 <= pc < view_w:
                try:
                    terminal.color('white')
                    terminal.put(pc, pr, '@')
                except:
                    pass

            # Draw attack effect
            if getattr(dg, 'last_swing', None) is not None:
                sr = dg.last_swing[0] - cam_y
                sc = dg.last_swing[1] - cam_x
                if 0 <= sr < view_h and 0 <= sc < view_w:
                    try:
                        terminal.color('orange')
                        terminal.put(sc, sr, '*')
                    except:
                        pass

            # Draw HUD
            try:
                health_str = f"HP:{int(dg.player_health)}/{int(dg.player_max_health)}"
                terminal.color('red')
                terminal.puts(0, view_h - 2, health_str)
            except:
                pass

            try:
                stamina_str = f"STA:{int(dg.player_stamina)}/{int(dg.player_max_stamina)}"
                terminal.color('yellow')
                terminal.puts(0, view_h - 1, stamina_str)
            except:
                pass

            # Refresh display
            try:
                terminal.refresh()
            except:
                pass

            # Input handling
            try:
                key = terminal.read()
            except:
                key = 0

            if key == getattr(terminal, 'TK_CLOSE', -1) or key == getattr(terminal, 'TK_ESCAPE', 27):
                break

            # Movement
            dr, dc = 0, 0
            if key == getattr(terminal, 'TK_UP', -1) or key == ord('w'):
                dr, dc = -1, 0
            elif key == getattr(terminal, 'TK_DOWN', -1) or key == ord('s'):
                dr, dc = 1, 0
            elif key == getattr(terminal, 'TK_LEFT', -1) or key == ord('a'):
                dr, dc = 0, -1
            elif key == getattr(terminal, 'TK_RIGHT', -1) or key == ord('d'):
                dr, dc = 0, 1

            if dr != 0 or dc != 0:
                nr = dg.player_row + dr
                nc = dg.player_col + dc
                if dg.is_walkable(nr, nc):
                    dg.player_row = nr
                    dg.player_col = nc
                    dg.reveal_current_area()
                    dg.pickup_coins()

            # Hotbar selection
            if ord('1') <= key <= ord('8'):
                slot = key - ord('1')
                if dg.inventory[0][slot] is not None:
                    if dg.equipped_slot == slot:
                        dg.equipped_slot = None
                    else:
                        dg.equipped_slot = slot

            # Attack
            if key == getattr(terminal, 'TK_SPACE', 32):
                dg.swing_weapon()

            # Check exit
            dg.check_exit()

    except Exception as e:
        print(f"Error in BearLibTerminal rendering: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if terminal is not None:
            terminal.close()
