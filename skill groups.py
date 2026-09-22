# Skill group definitions for RLDungeonGenerator.
#
# A skill group is one tree in the skill menu: the buttons down the left side of
# the menu are these groups, and clicking one shows its skills in the center.
# Each group is a dict with:
# - 'name': the group's display name, shown on its button in the skill menu
# - 'skills': the names of the skills in the group, top to bottom. Every name
#   must match a skill in skills.py; a name with no matching skill is skipped.
#
# Groups are display only. A skill's own 'level_requirement' is what gates it,
# so a group can freely mix tiers, and one skill could appear in two groups.
#
# Skills within a group run cheapest to most expensive, which is also lowest to
# highest level requirement: 1, 5, 10, then 15.
#
# NOTE: this file's name has a space in it, so RLDungeonGenerator imports it
# through importlib rather than a plain import, the same way it loads
# `player levels.py`.

SKILL_GROUPS = [
    {
        'name': 'Fire Blast',
        'skills': ['Fire Bolt', 'Scorch', 'Fireball', 'Immolate'],
    },
    {
        'name': 'Ice Blast',
        'skills': ['Frost Bolt', 'Ice Shard', 'Frigid Blast', 'Ice Bolt'],
    },
    {
        'name': 'Electricity Blast',
        'skills': ['Zap', 'Shocking Bolt', 'Static Discharge', 'Lightning Bolt'],
    },
]
