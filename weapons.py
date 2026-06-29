# Weapon definitions for RLDungeonGenerator
# Each weapon is a dict with:
# - name: display name
# - damage: numeric damage amount
# - stamina_cost: numeric stamina cost
# - range: maximum distance (in tiles) from the player to the attack centroid
# - area: radius (in tiles) around the attack centroid that can be affected
# - angle: cone angle in degrees (centered on attack direction)
# - glyph: optional glyph/tileset index (not used yet)

WEAPONS = [
    {
        'name': 'Unarmed',
        'damage': 20.0,
        'stamina_cost': 0,
        'range': 99.5,
        'area': 2.0,
        'angle': 360.0,
        'knockback': 10.0,  # tiles of knockback
        'glyph': None,
    },
]
