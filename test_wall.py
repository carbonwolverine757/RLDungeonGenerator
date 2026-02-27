from RLDungeonGenerator import RLDungeonGenerator, DungeonSqr

dg=RLDungeonGenerator(20,20)
level=dg.levels[0]
# Set both wall and floor to use the same glyph '.'
level['wall_glyph']=ord('.')
level['floor_glyph']=ord('.')
dg.apply_level(0)
try:
    dg.generate_map()
    print('map generated successfully')
except Exception as e:
    print('generate_map raised', type(e), e)
    import traceback
    traceback.print_exc()

print('wall glyph', repr(dg.wall_glyph), 'floor glyph', repr(dg.floor_glyph))

# Verify that tiles are correctly typed despite sharing same glyph
tile_types = set()
wall_tiles = 0
floor_tiles = 0
door_tiles = 0
exit_tiles = 0

for r in range(dg.height):
    for c in range(dg.width):
        tile = dg.dungeon[r][c]
        tile_types.add(tile.tile_type)
        if tile.tile_type == DungeonSqr.WALL:
            wall_tiles += 1
        elif tile.tile_type == DungeonSqr.FLOOR:
            floor_tiles += 1
        elif tile.tile_type == DungeonSqr.DOOR:
            door_tiles += 1
        elif tile.tile_type == DungeonSqr.EXIT:
            exit_tiles += 1

print('tile types found:', tile_types)
print('wall tiles:', wall_tiles)
print('floor tiles:', floor_tiles)
print('door tiles:', door_tiles)
print('exit tiles:', exit_tiles)

# Test is_walkable
wall_walkable = 0
floor_walkable = 0
for r in range(dg.height):
    for c in range(dg.width):
        if dg.is_walkable(r, c):
            floor_walkable += 1
        else:
            wall_walkable += 1

print('is_walkable() says: wall_walkable=', wall_walkable, 'floor_walkable=', floor_walkable)

# Show a small section
print('\nMap section (same glyph . for both wall and floor):')
for r in range(5):
    print(''.join(dg.dungeon[r][c].get_ch() for c in range(15)))


