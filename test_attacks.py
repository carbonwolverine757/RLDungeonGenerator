"""Headless exercise of time-of-flight attacks (update_attacks).

Builds an open walled arena, then drives the attack clock at 60fps without
opening a window, checking that each attack type deals damage only after its
attack delay and only when its effect reaches a hitbox, that projectiles stop
on what they hit, and that monster attacks can be dodged. Run: python test_attacks.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import RLDungeonGenerator as M
from RLDungeonGenerator import RLDungeonGenerator as DG, DungeonSqr

FRAME = 1.0 / 60.0
WEAPONS = {w['name']: w for w in M.WEAPONS}
SKILLS = {s['name']: s for s in M.SKILLS}
MONSTERS = {m['name']: m for m in M.MONSTER_TYPES}
fails = []

def check(cond, msg):
    print(("  OK   " if cond else "  FAIL ") + msg)
    if not cond:
        fails.append(msg)

def arena(size=40):
    """An empty floor surrounded by walls, player at (20, 10)."""
    dg = DG(size, size)
    dg.generate_map()
    for r in range(size):
        for c in range(size):
            edge = r in (0, size - 1) or c in (0, size - 1)
            dg.dungeon[r][c] = DungeonSqr(dg.wall_glyph if edge else dg.floor_glyph,
                                          DungeonSqr.WALL if edge else DungeonSqr.FLOOR)
    dg.objects = []
    dg._object_tiles = set()
    dg.monsters = []
    dg.active_attacks = []
    dg._static_blocked = None
    dg._begin_monster_frame()
    dg.set_player_position(20, 10)
    return dg

def tough(name='Boar', hp=1000):
    """A monster type that survives a few hits and doesn't fight back."""
    mt = dict(MONSTERS[name])
    mt['health'] = hp
    return mt

def step(dg, seconds, monsters=False):
    for _ in range(int(round(seconds / FRAME))):
        if monsters:
            dg.update_monsters(FRAME)
        dg.update_attacks(FRAME)

def center(dg, m):
    cx, cy = dg._monster_center(m)
    return cy / dg.tile_size, cx / dg.tile_size

print("Melee Swing (Iron Sword)")
dg = arena()
sword = WEAPONS['Iron Sword']
m = dg._spawn_monster(tough(), 20, 11)
m['type'] = dict(m['type'], knockback_resistance=0.0)  # keep it in place
stamina0 = dg.stamina
check(dg.perform_attack(*center(dg, m), weapon=sword), "attack starts")
check(dg.stamina == stamina0 - sword['stamina_cost'], "stamina spent when the attack starts")
check(not dg.perform_attack(*center(dg, m), weapon=sword), "second click during the delay is refused")
step(dg, sword['attack_delay'] - 2 * FRAME)
check(m['health'] == 1000, "no damage during the attack delay")
step(dg, 0.5)
check(m['health'] == 1000 - sword['damage'], "damage lands once after the delay (health %s)" % m['health'])
step(dg, 1.0)
check(m['health'] == 1000 - sword['damage'], "no second hit from the same swing")
check(not dg.active_attacks, "finished attack removed after its fade")

print("Melee AOE (Flint Spear): damage when the wave reaches the hitbox")
dg = arena()
spear = WEAPONS['Flint Spear']
m = dg._spawn_monster(tough(), 20, 13)  # hitbox edge 2.5 tiles from the player's center
m['type'] = dict(m['type'], knockback_resistance=0.0)
dg.perform_attack(*center(dg, m), weapon=spear)
reach_time = 2.5 / spear['effect_speed']
step(dg, spear['attack_delay'] + reach_time * 0.5)
check(m['health'] == 1000, "wave released but not yet at the monster")
step(dg, reach_time + 3 * FRAME)
check(m['health'] == 1000 - spear['damage'], "wave reached the monster and hit it")

print("Ranged Arrow (Crude Bow)")
dg = arena()
bow = WEAPONS['Crude Bow']
near = dg._spawn_monster(tough(), 20, 15)
far = dg._spawn_monster(tough(), 20, 18)
dg.perform_attack(*center(dg, far), weapon=bow)
flight_time = (15 - 10.5) / bow['projectile_speed']
step(dg, bow['attack_delay'] + flight_time * 0.5)
check(near['health'] == 1000, "arrow still in flight: no damage yet")
check(dg.active_attacks and dg.active_attacks[0]['phase'] == 'flight', "attack is in its flight phase")
step(dg, 1.0)
check(near['health'] == 1000 - bow['damage'], "arrow hit the first monster in line")
check(far['health'] == 1000, "monster behind it was not hit")

dg = arena()
dg.dungeon[20][14] = DungeonSqr(dg.wall_glyph, DungeonSqr.WALL)
dg._static_blocked = None
behind = dg._spawn_monster(tough(), 20, 18)
dg.perform_attack(*center(dg, behind), weapon=bow)
attack = dg.active_attacks[-1]
step(dg, 1.0)
check(behind['health'] == 1000, "arrow stopped by a wall in front of the monster")
check(abs(attack['arc']['col'] - 14.0) < 1e-6, "arrow burst at the wall face (col %.3f)" % attack['arc']['col'])

dg = arena()
dg.perform_attack(20.5, 12.5, weapon=bow)  # aim at empty floor
attack = dg.active_attacks[-1]
step(dg, 3.0)
check(abs(attack['arc']['col'] - (dg.width - 1)) < 1e-6,
      "arrow flew past the aim point to the far wall (col %.3f)" % attack['arc']['col'])

print("Ranged AOE (Fireball)")
dg = arena()
fireball = SKILLS['Fireball']
side = dg._spawn_monster(tough(), 23, 20)  # off the flight line, within the blast
dg.perform_attack(20.5, 20.5, weapon=fireball)
attack = dg.active_attacks[-1]
step(dg, fireball['attack_delay'] + 0.3)
check(side['health'] == 1000, "no damage before the fireball lands")
step(dg, 1.0)
check(abs(attack['arc']['row'] - 20.5) < 1e-6 and abs(attack['arc']['col'] - 20.5) < 1e-6,
      "fireball burst on the aim point")
check(side['health'] == 1000 - fireball['damage'], "blast caught a monster beside the aim point")

print("Skill: cooldown and stamina at the click")
dg = arena()
dg.skill_proficiency['Fire Bolt'] = 1
dg.active_skill_name = 'Fire Bolt'
stamina0 = dg.stamina
check(dg.perform_player_attack(20.5, 15.5), "skill cast starts")
check(dg.skill_cooldown_remaining('Fire Bolt') > 0, "cooldown started at the click")
check(dg.active_skill_name is None, "skill disarmed")
check(dg.stamina == stamina0 - SKILLS['Fire Bolt']['stamina_cost'], "skill stamina spent at the click")

print("Monster attacks: telegraphed, dodgeable")
gore = M.MONSTER_ATTACKS_BY_NAME['Gore']
dg = arena()
boar = dg._spawn_monster(dict(MONSTERS['Boar']), 20, 11)
hp0 = dg.health
dg.update_monsters(FRAME)
check(boar.get('_winding_up') and dg.active_attacks, "boar started an attack and is winding up")
pos = (boar['x'], boar['y'])
step(dg, gore['attack_delay'] - 3 * FRAME, monsters=True)
check(dg.health == hp0, "no damage during the boar's attack delay")
check((boar['x'], boar['y']) == pos, "boar stands still while winding up")
step(dg, 0.5, monsters=True)
gore_damage = MONSTERS['Boar']['attacks'][0]['damage']
check(dg.health == hp0 - gore_damage, "standing still: the gore lands (health %s)" % dg.health)

dg = arena()
boar = dg._spawn_monster(dict(MONSTERS['Boar']), 20, 11)
hp0 = dg.health
dg.update_monsters(FRAME)
dg.set_player_position(20, 3)  # step well out of the outline before it goes off
step(dg, gore['attack_delay'] + 0.4, monsters=True)
check(dg.health == hp0, "stepping away dodges the gore")
check(not boar.get('_winding_up'), "boar free to move once the attack went off")

dg = arena()
boar = dg._spawn_monster(dict(MONSTERS['Boar']), 20, 11)
hp0 = dg.health
dg.update_monsters(FRAME)
dg.monsters.remove(boar)  # killed during its windup
step(dg, 1.0)
check(dg.health == hp0 and not dg.active_attacks, "a dead monster's windup is cancelled")

print()
if fails:
    print("%d check(s) FAILED" % len(fails))
    sys.exit(1)
print("All checks passed")
