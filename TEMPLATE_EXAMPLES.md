# Level Template Extension Examples

This document provides examples of how to extend and customize the level template system.

## Adding More Levels

To add additional levels beyond the default 5, insert new dictionaries into the `LEVEL_TEMPLATES` array:

```python
LEVEL_TEMPLATES = [
    # ... existing levels ...
    {
        'name': 'Primordial Void',
        'room_size_min_pct': 15,
        'room_size_max_pct': 50,
        'floor_fg': (80, 80, 100),
        'floor_bg': (3, 3, 10),
        'wall_fg': (30, 30, 50),
        'wall_bg': (5, 5, 15),
        'door_weight': 3.0,
        'monster_count': 75,
        'monster_health': 50,
    },
]
```

## Color Themes

### Forest/Nature Theme
```python
{
    'name': 'Forest Grove',
    'room_size_min_pct': 55,
    'room_size_max_pct': 95,
    'floor_fg': (120, 160, 80),      # Green
    'floor_bg': (40, 60, 30),         # Dark green
    'wall_fg': (100, 140, 60),        # Darker green
    'wall_bg': (30, 50, 20),          # Very dark green
    'door_weight': 0.8,               # Fewer doors
    'monster_count': 25,
    'monster_health': 18,
}
```

### Ice/Frozen Theme
```python
{
    'name': 'Frozen Caverns',
    'room_size_min_pct': 50,
    'room_size_max_pct': 85,
    'floor_fg': (200, 240, 255),      # Light cyan
    'floor_bg': (50, 80, 100),        # Dark blue
    'wall_fg': (150, 200, 220),       # Light blue
    'wall_bg': (30, 60, 80),          # Dark blue
    'door_weight': 1.1,
    'monster_count': 28,
    'monster_health': 22,
}
```

### Fire/Lava Theme
```python
{
    'name': 'Molten Depths',
    'room_size_min_pct': 45,
    'room_size_max_pct': 75,
    'floor_fg': (255, 140, 0),        # Orange
    'floor_bg': (60, 30, 0),          # Dark brown
    'wall_fg': (200, 100, 0),         # Dark orange
    'wall_bg': (40, 20, 0),           # Very dark brown
    'door_weight': 1.4,
    'monster_count': 45,
    'monster_health': 28,
}
```

### Toxic/Poison Theme
```python
{
    'name': 'Toxic Swamp',
    'room_size_min_pct': 50,
    'room_size_max_pct': 80,
    'floor_fg': (100, 200, 100),      # Sickly green
    'floor_bg': (30, 60, 30),         # Dark green
    'wall_fg': (80, 150, 80),         # Darker green
    'wall_bg': (20, 40, 20),          # Very dark green
    'door_weight': 1.3,
    'monster_count': 35,
    'monster_health': 25,
}
```

## Difficulty Progression Curves

### Slow Progression (Beginner)
```python
LEVEL_TEMPLATES = [
    {
        'name': 'Level 1 - Easy',
        'room_size_min_pct': 70,
        'room_size_max_pct': 100,
        'floor_fg': (220, 220, 220),
        'floor_bg': (0, 0, 0),
        'wall_fg': (150, 150, 150),
        'wall_bg': (0, 0, 0),
        'door_weight': 1.0,
        'monster_count': 10,
        'monster_health': 10,
    },
    {
        'name': 'Level 2 - Medium',
        'room_size_min_pct': 60,
        'room_size_max_pct': 90,
        'floor_fg': (200, 200, 200),
        'floor_bg': (0, 0, 0),
        'wall_fg': (120, 120, 120),
        'wall_bg': (0, 0, 0),
        'door_weight': 1.1,
        'monster_count': 20,
        'monster_health': 15,
    },
    {
        'name': 'Level 3 - Hard',
        'room_size_min_pct': 50,
        'room_size_max_pct': 80,
        'floor_fg': (180, 180, 180),
        'floor_bg': (0, 0, 0),
        'wall_fg': (100, 100, 100),
        'wall_bg': (0, 0, 0),
        'door_weight': 1.2,
        'monster_count': 35,
        'monster_health': 25,
    },
]
```

### Steep Progression (Hardcore)
```python
LEVEL_TEMPLATES = [
    {
        'name': 'Extreme Level 1',
        'room_size_min_pct': 40,
        'room_size_max_pct': 70,
        'floor_fg': (180, 180, 200),
        'floor_bg': (0, 0, 0),
        'wall_fg': (100, 100, 120),
        'wall_bg': (0, 0, 0),
        'door_weight': 1.5,
        'monster_count': 40,
        'monster_health': 30,
    },
    {
        'name': 'Extreme Level 2',
        'room_size_min_pct': 25,
        'room_size_max_pct': 60,
        'floor_fg': (160, 160, 180),
        'floor_bg': (0, 0, 0),
        'wall_fg': (80, 80, 100),
        'wall_bg': (0, 0, 0),
        'door_weight': 2.0,
        'monster_count': 60,
        'monster_health': 50,
    },
]
```

## Dynamic Level Properties

You can also use Python to generate level templates programmatically:

```python
def generate_levels(num_levels=5):
    """Generate levels with smooth progression."""
    templates = []
    for i in range(num_levels):
        # Scale from 0 to 1
        progress = i / max(1, num_levels - 1)
        
        # Room size decreases with level
        min_pct = int(70 - progress * 50)  # 70 to 20
        max_pct = int(100 - progress * 40)  # 100 to 60
        
        # Colors darken with level
        brightness = int(255 * (1 - progress * 0.3))
        
        # Monsters increase with level
        monster_count = int(15 + progress * 50)
        monster_health = int(12 + progress * 40)
        
        templates.append({
            'name': f'Level {i + 1}',
            'room_size_min_pct': min_pct,
            'room_size_max_pct': max_pct,
            'floor_fg': (brightness, brightness, brightness),
            'floor_bg': (0, 0, 0),
            'wall_fg': (brightness // 2, brightness // 2, brightness // 2),
            'wall_bg': (0, 0, 0),
            'door_weight': 1.0 + progress,
            'monster_count': monster_count,
            'monster_health': monster_health,
        })
    
    return templates

# Use it:
# LEVEL_TEMPLATES = generate_levels(10)  # Generate 10 levels
```

## Themed Dungeon Series

### Dungeon of Seasons
```python
LEVEL_TEMPLATES = [
    {
        'name': 'Spring Meadows',
        'room_size_min_pct': 65,
        'room_size_max_pct': 95,
        'floor_fg': (150, 220, 100),
        'floor_bg': (20, 40, 10),
        'wall_fg': (120, 180, 80),
        'wall_bg': (15, 30, 5),
        'door_weight': 1.0,
        'monster_count': 15,
        'monster_health': 12,
    },
    {
        'name': 'Summer Heat',
        'room_size_min_pct': 55,
        'room_size_max_pct': 85,
        'floor_fg': (255, 200, 100),
        'floor_bg': (60, 40, 0),
        'wall_fg': (200, 160, 80),
        'wall_bg': (40, 30, 0),
        'door_weight': 1.1,
        'monster_count': 25,
        'monster_health': 18,
    },
    {
        'name': 'Autumn Decay',
        'room_size_min_pct': 50,
        'room_size_max_pct': 80,
        'floor_fg': (200, 140, 80),
        'floor_bg': (40, 20, 0),
        'wall_fg': (160, 110, 60),
        'wall_bg': (30, 15, 0),
        'door_weight': 1.2,
        'monster_count': 35,
        'monster_health': 22,
    },
    {
        'name': 'Winter Frost',
        'room_size_min_pct': 45,
        'room_size_max_pct': 75,
        'floor_fg': (180, 220, 255),
        'floor_bg': (30, 50, 70),
        'wall_fg': (140, 180, 220),
        'wall_bg': (20, 40, 60),
        'door_weight': 1.3,
        'monster_count': 40,
        'monster_health': 25,
    },
]
```

## Testing Your Templates

To test custom templates, temporarily modify `LEVEL_TEMPLATES` at the top of `RLDungeonGenerator.py`, then run:

```bash
python RLDungeonGenerator.py --level 0
```

You can quickly test different levels:
```bash
python RLDungeonGenerator.py --level 1
python RLDungeonGenerator.py --level 2
```
