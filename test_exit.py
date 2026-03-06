from RLDungeonGenerator import RLDungeonGenerator

rg = RLDungeonGenerator(width=40, height=20)
rg.generate_map()
print('player', rg.player_row, rg.player_col)
print('exit', rg.exit_pos)
for r in range(rg.height):
    row = ''
    for c in range(rg.width):
        if (r, c) == rg.exit_pos:
            row += 'E'
        elif (r, c) == (rg.player_row, rg.player_col):
            row += 'P'
        else:
            row += rg.dungeon[r][c].get_ch()
    print(row)
