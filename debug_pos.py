import sys
sys.path.insert(0, '.')
from RLDungeonGenerator import RLDungeonGenerator
dg = RLDungeonGenerator(80, 40)
dg.apply_level(0)
dg.generate_map()
print('Player at', dg.player_row, dg.player_col)
for m in dg.monsters:
    print(f'Monster {m["type"]["name"]} at {m["row"]}, {m["col"]}')