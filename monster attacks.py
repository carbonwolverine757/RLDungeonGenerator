# Monster attack definitions for RLDungeonGenerator
#
# Each monster attack is a dict describing the *shape* of an attack. How hard it
# hits and how often it can be used are set per monster, in that monster's
# 'attacks' list in monsters.py, so one attack shape can be shared by several
# monsters at different strengths.
#
# The geometry keys are spelled and behave exactly as they do in weapons.py and
# skills.py, with the monster's footprint center standing in for the player:
# - name: display name, and the key monsters.py refers to
# - range: maximum distance (in tiles) from the monster's center to the attack
#   centroid. The attack is always aimed at the player, so the centroid sits on
#   the player when they are closer than this, and on the line toward them
#   otherwise.
#   NOTE: a range of 0 disables clamping entirely, so the centroid lands on the
#   player at any distance. Small values like 0.1 pin the centroid to the
#   monster itself, making a melee cone that reaches 'area' tiles.
# - area: radius (in tiles) of the attack arc drawn from the centroid. The
#   player is hit if the arc touches their hitbox, even partly.
# - angle: arc spread in degrees (centered on the direction to the player).
#   360 or more is a full disc, ignoring direction.
#
# A monster only uses an attack whose arc would actually reach the player (see
# RLDungeonGenerator._monster_try_attack), so range + area is the real reach.
# Areas are measured from the monster's *center*: a 1x1 monster's center is half
# a tile from its edge, a 4x4 monster's is two tiles.

MONSTER_ATTACKS = [
    # Meadows
    {
        'name': 'Gore',
        'range': 0.1,
        'area': 1.5,
        'angle': 60.0,
    },
    {
        'name': 'Bite',
        'range': 0.1,
        'area': 1.2,
        'angle': 45.0,
    },
    {
        'name': 'Claw',
        'range': 0.1,
        'area': 1.5,
        'angle': 90.0,
    },
    {
        # A thrown stone: lands on the player from up to 8 tiles away.
        'name': 'Rock Throw',
        'range': 8.0,
        'area': 0.5,
        'angle': 360.0,
    },
    # Black Forest
    {
        'name': 'Bone Slash',
        'range': 0.1,
        'area': 1.8,
        'angle': 90.0,
    },
    # Swamps
    {
        'name': 'Heavy Slash',
        'range': 0.1,
        'area': 2.0,
        'angle': 120.0,
    },
    {
        'name': 'Slash',
        'range': 0.1,
        'area': 1.8,
        'angle': 90.0,
    },
    # Eikthyr (4x4: his center is 2 tiles from his edge)
    {
        'name': 'Lightning Stomp',
        'range': 0.1,
        'area': 5.0,
        'angle': 360.0,
    },
    {
        'name': 'Antler Sweep',
        'range': 0.1,
        'area': 4.0,
        'angle': 120.0,
    },
    {
        'name': 'Lightning Bolt',
        'range': 15.0,
        'area': 1.5,
        'angle': 360.0,
    },
]
