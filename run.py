import argparse
from RLDungeonGenerator import RLDungeonGenerator, render_with_tcod


def main() -> None:
    parser = argparse.ArgumentParser(description="RLDungeonGenerator runner")
    parser.add_argument("--width", type=int, default=75, help="Dungeon width in tiles")
    parser.add_argument("--height", type=int, default=40, help="Dungeon height in tiles")
    parser.add_argument("--ascii", action="store_true", help="Print ASCII map to console instead of opening a window")
    args = parser.parse_args()

    dg = RLDungeonGenerator(args.width, args.height)
    dg.generate_map()

    if args.ascii:
        dg.print_map()
    else:
        render_with_tcod(dg)


if __name__ == "__main__":
    main()
