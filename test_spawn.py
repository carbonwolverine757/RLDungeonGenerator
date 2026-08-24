"""Headless exercise of the runtime monster spawner (update_spawning).

Drives the spawn tick directly at 60fps without opening a window, so cadence, caps,
the player exclusion ring, boss respawn and level-change resets can all be checked
without playing the game. Run: python test_spawn.py
"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import RLDungeonGenerator as M
from RLDungeonGenerator import RLDungeonGenerator as DG
from levels import LEVELS

FRAME = 1.0 / 60.0
LEVEL_IDX = {lv['name']: i for i, lv in enumerate(LEVELS)}
fails = []

def check(cond, msg):
    print(("  OK   " if cond else "  FAIL ") + msg)
    if not cond:
        fails.append(msg)

def make(level_name, w=150, h=80):
    dg = DG(w, h)
    dg.apply_level(LEVEL_IDX[level_name])
    dg.generate_map()
    return dg

def run(dg, seconds, move_player=None):
    """Advance `seconds` of gameplay at 60fps, recording each spawn."""
    seen = []
    n = 0
    for _ in range(int(seconds / FRAME)):
        before = len(dg.monsters)
        dg.update_spawning(FRAME)
        if len(dg.monsters) > before:
            for m in dg.monsters[before:]:
                seen.append((round(dg._spawn_clock, 2), m['type']['name'], m['row'], m['col']))
        n += 1
        if move_player is not None and n % 60 == 0:
            move_player(dg)
    return seen

print("=== 1. Map generates empty ===")
dg = make('Meadows')
check(len(dg.monsters) == 0, f"0 monsters at generation (got {len(dg.monsters)})")
check(dg._spawn_chunk_tiles is None, "chunk cache not built until first use")

print("\n=== 2. First tick fires on the first frame ===")
dg.update_spawning(FRAME)
check(dg._spawn_clock > 0, "spawn clock advanced")
check(dg._spawn_tick_accumulator < dg._SPAWN_TICK_INTERVAL,
      "primed accumulator consumed by a tick on frame 1")
# The cache is built only when an attempt actually needs a location, so a tick where
# every type fails its chance roll correctly leaves it unbuilt. Run until one spawns.
run(dg, 60)
check(len(dg.monsters) > 0, f"spawns within 60s (got {len(dg.monsters)})")
check(dg._spawn_chunk_tiles is not None, "chunk cache built lazily once a location is needed")
nchunks = len(dg._spawn_chunk_tiles)
ntiles = sum(len(v) for v in dg._spawn_chunk_tiles.values())
print(f"       chunk cache: {nchunks} chunks, {ntiles} anchor tiles")
check(nchunks == 15 * 8, f"15x8=120 chunks on a 150x80 map (got {nchunks})")

print("\n=== 3. Exclusion ring: nothing spawns near the player ===")
dg = make('Meadows')
spawns = run(dg, 400)
pr, pc = dg.player_row // 10, dg.player_col // 10
worst = min((max(abs(r // 10 - pr), abs(c // 10 - pc)) for _, _, r, c in spawns), default=99)
check(worst >= 2, f"min chunk distance from player >= 2 (got {worst}, {len(spawns)} spawns)")
mind = min((max(abs(r - dg.player_row), abs(c - dg.player_col)) for _, _, r, c in spawns), default=99)
check(mind >= 11, f"min tile distance >= 11, clears the 20x12 viewport (got {mind})")

print("\n=== 4. Cadence and caps (Meadows, 400s) ===")
boar = [t for t, n, r, c in spawns if n == 'Boar']
grey = [t for t, n, r, c in spawns if n == 'Greyling']
print(f"       Boar spawn times:     {[round(t) for t in boar]}")
print(f"       Greyling spawn times: {[round(t) for t in grey]}")
gaps = [round(b - a, 1) for a, b in zip(boar, boar[1:])]
print(f"       Boar gaps: {gaps}")
check(all(g >= 12.0 for g in gaps), f"every Boar gap >= 12.0s interval (got min {min(gaps) if gaps else 'n/a'})")
check(all(abs((g - 12.0) % 4.0) < 0.15 or abs((g - 12.0) % 4.0 - 4.0) < 0.15 for g in gaps),
      "Boar gaps quantized to 12 + 4k seconds")
counts = {}
for m in dg.monsters:
    counts[m['type']['name']] = counts.get(m['type']['name'], 0) + 1
print(f"       final live counts: {counts}")
check(counts.get('Boar', 0) == 12, f"Boar reached max_count 12 (got {counts.get('Boar', 0)})")
check(counts.get('Greyling', 0) == 8, f"Greyling reached max_count 8 (got {counts.get('Greyling', 0)})")
check(len(boar) == 12 and len(grey) == 8, "no over-spawning past the cap")

print("\n=== 5. Killing one frees a slot ===")
victim = next(m for m in dg.monsters if m['type']['name'] == 'Boar')
victim['health'] = 0
dg._cleanup_dead_monsters()
live = sum(1 for m in dg.monsters if m['type']['name'] == 'Boar')
check(live == 11, f"11 boars after a kill (got {live})")
after = run(dg, 30)
live = sum(1 for m in dg.monsters if m['type']['name'] == 'Boar')
check(live == 12, f"replacement spawned within 30s (got {live})")
check(any(n == 'Boar' for _, n, _, _ in after), "replacement was a Boar")

print("\n=== 6. No overlaps: every monster sits on legal, unshared ground ===")
occupied = {}
overlap = 0
offmap = 0
onwall = 0
instruct = 0
for m in dg.monsters:
    size = dg._monster_size(m)
    for i in range(size):
        for j in range(size):
            r, c = m['row'] + i, m['col'] + j
            if not (0 <= r < dg.height and 0 <= c < dg.width):
                offmap += 1
                continue
            if dg.dungeon[r][c].tile_type not in ('floor', 'door', 'exit'):
                onwall += 1
            if dg._in_structure(r, c):
                instruct += 1
            if (r, c) in occupied:
                overlap += 1
            occupied[(r, c)] = m
check(offmap == 0, f"no monster off-map ({offmap})")
check(onwall == 0, f"no monster on a wall ({onwall})")
check(instruct == 0, f"no monster inside the base structure ({instruct})")
check(overlap == 0, f"no two monsters share a tile ({overlap})")
objtiles = {(o['row'], o['col']) for o in dg.objects}
check(not (set(occupied) & objtiles), f"no monster on an object ({len(set(occupied) & objtiles)})")

print("\n=== 7. Boss: spawns at once, stays dead ===")
dg = make('Eikthyr Bossfight')
check(len(dg.monsters) == 0, "arena empty at generation")
dg.update_spawning(FRAME)
names = [m['type']['name'] for m in dg.monsters]
check(names == ['Eikthyr'], f"Eikthyr present on the very first tick (got {names})")
boss = dg.monsters[0]
check(dg._monster_size(boss) == 4, "boss is 4x4")
run(dg, 60)
check(len([m for m in dg.monsters if m['type']['name'] == 'Eikthyr']) == 1,
      "only one Eikthyr after 60s")
boss['health'] = 0
dg._cleanup_dead_monsters()
check(len(dg.monsters) == 0, "boss removed on death")
run(dg, 120)
check(len(dg.monsters) == 0, f"boss does not respawn after 120s (got {len(dg.monsters)})")

print("\n=== 8. Level change resets timers and per-level rosters ===")
dg = make('Meadows')
run(dg, 100)
check(any(m['type']['name'] == 'Boar' for m in dg.monsters), "boars on Meadows")
old_clock = dg._spawn_clock
dg.apply_level(LEVEL_IDX['Black Forest'])
dg.generate_map()
check(dg._spawn_clock == 0.0, f"spawn clock reset (was {old_clock:.1f})")
check(dg._spawn_last_time == {}, "per-type timers cleared")
check(dg._spawn_chunk_tiles is None, "chunk cache invalidated for the new map")
check(len(dg.monsters) == 0, "new map starts empty")
bf = run(dg, 450)  # measured mean time-to-cap is ~260s, max ~292s over 12 trials
bfnames = {n for _, n, _, _ in bf}
check(bfnames == {'Greyling'}, f"only Greylings in Black Forest (got {bfnames})")
live = sum(1 for m in dg.monsters if m['type']['name'] == 'Greyling')
check(live == 24, f"Black Forest Greyling cap 24 reached (got {live})")
objtiles = {(o['row'], o['col']) for o in dg.objects}
on_obj = [m for m in dg.monsters if (m['row'], m['col']) in objtiles]
check(not on_obj, f"no monster spawned on a Black Forest tree ({len(on_obj)}) [stale _object_tiles regression]")

print("\n=== 9. Exclusion ring follows a moving player ===")
dg = make('Meadows')
def walk(d):
    d.player_col = min(d.width - 2, d.player_col + 7)
    d.player_row = max(1, d.player_row - 3)
sp = run(dg, 300, move_player=walk)
check(len(sp) > 0, f"spawns happened while walking ({len(sp)})")

print("\n=== 10. Degenerate small map warns and does not crash ===")
dg = DG(30, 20)
dg.apply_level(LEVEL_IDX['Meadows'])
dg.generate_map()
sp = run(dg, 60)
check(len(sp) == 0, f"nothing spawns when the ring covers the map (got {len(sp)})")
check(dg._spawn_warned_no_chunks, "warned exactly once")

print("\n=== 11. Perf: worst-case tick cost ===")
dg = make('Meadows')
run(dg, 400)  # fill to cap
t0 = time.perf_counter()
for _ in range(200):
    dg._spawn_tick_accumulator = dg._SPAWN_TICK_INTERVAL
    dg.update_spawning(FRAME)
per = (time.perf_counter() - t0) / 200 * 1000
print(f"       {per:.2f} ms per tick at cap")
check(per < 5.0, f"tick under 5ms at cap ({per:.2f} ms)")

dg = make('Eikthyr Bossfight')
dg.update_spawning(FRAME)
t0 = time.perf_counter()
for _ in range(50):
    dg._spawn_tick_accumulator = dg._SPAWN_TICK_INTERVAL
    dg._spawn_totals = {}          # force it past the respawns gate
    dg._spawn_last_time = {}
    dg.update_spawning(FRAME)
per = (time.perf_counter() - t0) / 50 * 1000
print(f"       {per:.2f} ms per tick searching for 4x4 boss slots")
check(per < 30.0, f"size-4 search bounded by _SPAWN_MAX_LOCATION_TESTS ({per:.2f} ms)")

print("\n" + "=" * 50)
if fails:
    print(f"{len(fails)} FAILURE(S):")
    for f in fails:
        print("  - " + f)
    sys.exit(1)
print("ALL CHECKS PASSED")
