# Level Template System

## Overview
The dungeon generator now includes a progressive level template system that provides increasing difficulty through 5 levels. Each level has customized parameters that affect gameplay and visual appearance.

## Level Templates

The `LEVEL_TEMPLATES` array defines 5 levels of progression:

### Level 0: Caverns
- **Room Size**: 60-100% of section size
- **Colors**: Light blue floor, dark navy walls
- **Monster Count**: 20
- **Monster Health**: 15
- **Door Weight**: 1.0

### Level 1: Underground Halls
- **Room Size**: 50-90% of section size  
- **Colors**: Grayish floor, dark slate walls
- **Monster Count**: 30
- **Monster Health**: 20
- **Door Weight**: 1.2

### Level 2: Dark Dungeons
- **Room Size**: 40-80% of section size
- **Colors**: Darker grayish floor, darker walls
- **Monster Count**: 40
- **Monster Health**: 25
- **Door Weight**: 1.5

### Level 3: Obsidian Depths
- **Room Size**: 30-70% of section size
- **Colors**: Very dark floor and walls
- **Monster Count**: 50
- **Monster Health**: 30
- **Door Weight**: 2.0

### Level 4: Abyss
- **Room Size**: 20-60% of section size
- **Colors**: Nearly black floor and walls
- **Monster Count**: 60
- **Monster Health**: 40
- **Door Weight**: 2.5

## Template Properties

Each template is a dictionary with the following properties:

- **name** (str): Display name of the level
- **room_size_min_pct** (int): Minimum room size as percentage of section (20-100)
- **room_size_max_pct** (int): Maximum room size as percentage of section (20-100)
- **floor_fg** (tuple): RGB color tuple for floor foreground
- **floor_bg** (tuple): RGB color tuple for floor background
- **wall_fg** (tuple): RGB color tuple for wall foreground
- **wall_bg** (tuple): RGB color tuple for wall background
- **door_weight** (float): Multiplier for door frequency (future use)
- **monster_count** (int): Number of monsters to spawn
- **monster_health** (int): Health value for each monster

## Usage

### Creating a Dungeon with a Specific Level

```python
# Start at level 2 (Dark Dungeons)
dg = RLDungeonGenerator(width=80, height=45, level=2)
dg.generate_map()
```

### Command Line

```bash
# Start at level 0 (default)
python RLDungeonGenerator.py

# Start at level 3
python RLDungeonGenerator.py --level 3

# Use ASCII output at level 2
python RLDungeonGenerator.py --ascii --level 2
```

## Level Progression

When the player reaches the exit tile ('>'), the game automatically:
1. Advances to the next level
2. Resets the dungeon with the new level's template
3. Keeps the player's inventory and stats
4. Loops back to level 0 after level 4

The current level and name are displayed at the bottom of the HUD.

## Customization

To add more levels or modify existing ones, simply edit the `LEVEL_TEMPLATES` array. The system automatically supports any number of levels.

Example - Adding a custom level:
```python
{
    'name': 'My Custom Level',
    'room_size_min_pct': 45,
    'room_size_max_pct': 85,
    'floor_fg': (150, 200, 100),  # Greenish
    'floor_bg': (20, 40, 20),
    'wall_fg': (100, 150, 80),
    'wall_bg': (30, 50, 30),
    'door_weight': 1.3,
    'monster_count': 35,
    'monster_health': 22,
}
```

## Technical Details

### Room Size Scaling
Room sizes are calculated using the template's min/max percentages:
```
room_size = randrange(min_pct%, max_pct%) * section_size
```

### Color Application
Colors from templates are applied in the render function:
- Floor tiles use `floor_fg` and `floor_bg`
- Wall tiles use `wall_fg` and `wall_bg`
- Unexplored tiles are dimmed to 15% brightness

### Level Display
The current level is shown at the bottom-left corner of the screen in light blue:
```
Level 1: Underground Halls
```
