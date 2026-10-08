# Skill definitions for RLDungeonGenerator
#
# A skill is a weapon the player casts instead of swinging. Every combat key
# here is spelled exactly as it is in weapons.py, so a skill dict can be handed
# straight to perform_attack(row, col, weapon=skill) with no adapter:
# - name: display name, and the key skill groups.py refers to
# - damage: numeric damage amount, before the proficiency bonus
# - stamina_cost: numeric stamina cost; an attack the player cannot afford fizzles
# - range: maximum distance (in tiles) from the player to the attack centroid.
#   NOTE: a range of 0 disables clamping entirely (see _resolve_attack_target),
#   so the attack lands wherever the player clicked, at any distance. No skill
#   uses 0. The 0.1 on Frigid Blast and Ice Bolt pins the centroid to the
#   player's own tile, which is what makes those two self-centered cones.
# - area: radius (in tiles) around the attack centroid that can be affected
# - angle: cone angle in degrees (centered on attack direction). 360 or more
#   short-circuits to a full disc, ignoring direction.
# - knockback: tiles of knockback, before the target's knockback resistance
# - glyph: tileset index (declared by row and column in Glyph_Grimoire.py),
#   drawn in the skill menu and the tray
#
# Plus three fields weapons do not have:
# - background: RGB fill drawn behind the glyph, so a skill's tree reads at a
#   glance from its color. Skills in the same group share one.
# - level_requirement: the player level needed before a point can be spent here
# - cooldown: seconds the skill is unusable after it is cast
#
# Points are spent in the skill menu (H). Spending one raises that skill's
# proficiency by 1; proficiency 1 unlocks the skill and each point past the
# first adds 10% damage. See skill groups.py for how these are grouped.

try:
    from .Glyph_Grimoire import SKILL_BOLT, SKILL_LANCE, SKILL_BALL, SKILL_BURST, SKILL_CONE, SKILL_SPEAR, SKILL_ARC
except ImportError:
    from Glyph_Grimoire import SKILL_BOLT, SKILL_LANCE, SKILL_BALL, SKILL_BURST, SKILL_CONE, SKILL_SPEAR, SKILL_ARC

# Skill art lives on row 23 of the tileset. Art is shared across trees — the
# background color is what distinguishes a fire bolt from a frost one.
BOLT_GLYPH = SKILL_BOLT
LANCE_GLYPH = SKILL_LANCE
BALL_GLYPH = SKILL_BALL
BURST_GLYPH = SKILL_BURST
CONE_GLYPH = SKILL_CONE
SPEAR_GLYPH = SKILL_SPEAR
ARC_GLYPH = SKILL_ARC

# One background per tree. RGB tuples, like every other color in the codebase.
FIRE_BG = (255, 141, 10)    # #ff8d0a
ICE_BG = (144, 238, 255)    # #90eeff
SHOCK_BG = (94, 109, 240)   # #5e6df0

SKILLS = [
    # Fire Blast: ranged single-target damage that climbs steeply with tier.
    {
        'name': 'Fire Bolt',
        'damage': 10.0,
        'stamina_cost': 5,
        'range': 12.0,
        'area': 0.5,
        'angle': 360.0,
        'knockback': 0.5,  # tiles of knockback
        'glyph': BOLT_GLYPH,
        'background': FIRE_BG,
        'level_requirement': 1,
        'cooldown': 3.0,  # seconds
    },
    {
        'name': 'Scorch',
        'damage': 20.0,
        'stamina_cost': 8,
        'range': 18.0,
        'area': 0.5,
        'angle': 360.0,
        'knockback': 1.0,  # tiles of knockback
        'glyph': LANCE_GLYPH,
        'background': FIRE_BG,
        'level_requirement': 5,
        'cooldown': 5.0,  # seconds
    },
    {
        'name': 'Fireball',
        'damage': 10.0,
        'stamina_cost': 10,
        'range': 15.0,
        'area': 3.0,
        'angle': 360.0,
        'knockback': 0.5,  # tiles of knockback
        'glyph': BALL_GLYPH,
        'background': FIRE_BG,
        'level_requirement': 10,
        'cooldown': 8.0,  # seconds
    },
    {
        'name': 'Immolate',
        'damage': 40.0,
        'stamina_cost': 12,
        'range': 15.0,
        'area': 0.5,
        'angle': 360.0,
        'knockback': 0.2,  # tiles of knockback
        'glyph': BURST_GLYPH,
        'background': FIRE_BG,
        'level_requirement': 15,
        'cooldown': 12.0,  # seconds
    },
    # Ice Blast: opens like Fire Blast, then turns into short self-centered cones.
    {
        'name': 'Frost Bolt',
        'damage': 10.0,
        'stamina_cost': 5,
        'range': 12.0,
        'area': 0.5,
        'angle': 360.0,
        'knockback': 0.5,  # tiles of knockback
        'glyph': BOLT_GLYPH,
        'background': ICE_BG,
        'level_requirement': 1,
        'cooldown': 3.0,  # seconds
    },
    {
        'name': 'Ice Shard',
        'damage': 20.0,
        'stamina_cost': 8,
        'range': 18.0,
        'area': 0.5,
        'angle': 360.0,
        'knockback': 1.0,  # tiles of knockback
        'glyph': LANCE_GLYPH,
        'background': ICE_BG,
        'level_requirement': 5,
        'cooldown': 5.0,  # seconds
    },
    {
        'name': 'Frigid Blast',
        'damage': 10.0,
        'stamina_cost': 10,
        'range': 0.1,
        'area': 9.0,
        'angle': 50.0,
        'knockback': 0.5,  # tiles of knockback
        'glyph': CONE_GLYPH,
        'background': ICE_BG,
        'level_requirement': 10,
        'cooldown': 8.0,  # seconds
    },
    {
        'name': 'Ice Bolt',
        'damage': 20.0,
        'stamina_cost': 12,
        'range': 0.1,
        'area': 12.0,
        'angle': 30.0,
        'knockback': 2.0,  # tiles of knockback
        'glyph': SPEAR_GLYPH,
        'background': ICE_BG,
        'level_requirement': 15,
        'cooldown': 12.0,  # seconds
    },
    # Electricity Blast: the least knockback, the longest reach.
    {
        'name': 'Zap',
        'damage': 10.0,
        'stamina_cost': 5,
        'range': 12.0,
        'area': 0.5,
        'angle': 360.0,
        'knockback': 0.2,  # tiles of knockback
        'glyph': BOLT_GLYPH,
        'background': SHOCK_BG,
        'level_requirement': 1,
        'cooldown': 3.0,  # seconds
    },
    {
        'name': 'Shocking Bolt',
        'damage': 20.0,
        'stamina_cost': 8,
        'range': 18.0,
        'area': 0.5,
        'angle': 360.0,
        'knockback': 0.2,  # tiles of knockback
        'glyph': LANCE_GLYPH,
        'background': SHOCK_BG,
        'level_requirement': 5,
        'cooldown': 5.0,  # seconds
    },
    {
        'name': 'Static Discharge',
        'damage': 10.0,
        'stamina_cost': 10,
        'range': 12.0,
        'area': 30.0,
        'angle': 30.0,
        'knockback': 0.2,  # tiles of knockback
        'glyph': CONE_GLYPH,
        'background': SHOCK_BG,
        'level_requirement': 10,
        'cooldown': 8.0,  # seconds
    },
    {
        'name': 'Lightning Bolt',
        'damage': 20.0,
        'stamina_cost': 12,
        'range': 45.0,
        'area': 1.5,
        'angle': 360.0,
        'knockback': 0.5,  # tiles of knockback
        'glyph': ARC_GLYPH,
        'background': SHOCK_BG,
        'level_requirement': 15,
        'cooldown': 12.0,  # seconds
    },
]
