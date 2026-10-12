#!/usr/bin/env python3
# Paste the images in the Raw folder into the tileset (TILESET_PATH).
# Each Raw image is resized to GLYPH_SIZE x GLYPH_SIZE and replaces the cell
# named by its row and column (r<row>_c<col>, e.g. r07_c16.png or
# "r07_c16 grass.jpg"). Files without a row and column in the name are skipped.
#
# Usage:
#   python compose_raw_glyphs.py                 # every image in Raw
#   python compose_raw_glyphs.py r07_c16.png ... # only the named Raw images
#
# Before writing, the previous tileset is copied to
# Backups/<name>.<timestamp>.png, so every run keeps its own backup and never
# overwrites an earlier one.

from PIL import Image
from datetime import datetime
import os
import re
import shutil
import sys

# Sheet geometry comes from Glyph_Grimoire.py at the repo root.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Glyph_Grimoire import GLYPH_SIZE, TILESET_COLUMNS, TILESET_ROWS, TILESET_PATH

RAW_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Raw')
RAW_NAME = re.compile(r'r(\d+)_c(\d+)', re.IGNORECASE)
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')

def raw_row_col(filename):
    """Return the (row, col) named in a Raw filename, or None if it names none."""
    m = RAW_NAME.search(filename)
    return (int(m.group(1)), int(m.group(2))) if m else None

def compose_raw_glyphs(raw_dir, tileset_path, tile_size=16, filenames=None):
    if filenames is None:
        filenames = sorted(f for f in os.listdir(raw_dir) if f.lower().endswith(IMAGE_EXTENSIONS))
    sheet = Image.open(tileset_path).convert('RGBA')
    expected = (TILESET_COLUMNS * tile_size, TILESET_ROWS * tile_size)
    if sheet.size != expected:
        raise SystemExit(f"{tileset_path} is {sheet.size}, expected {expected} from Glyph_Grimoire.py")
    blank = Image.new('RGBA', (tile_size, tile_size), color=(0, 0, 0, 0))
    placed = 0
    for name in filenames:
        pos = raw_row_col(name)
        if pos is None:
            print(f"Skipped {name}: no r<row>_c<col> in the name")
            continue
        row, col = pos
        if not (0 <= row < TILESET_ROWS and 0 <= col < TILESET_COLUMNS):
            print(f"Skipped {name}: ({row}, {col}) is off the tileset")
            continue
        img = Image.open(os.path.join(raw_dir, name)).convert('RGBA')
        if img.size != (tile_size, tile_size):
            img = img.resize((tile_size, tile_size), Image.LANCZOS)
        x = col * tile_size
        y = row * tile_size
        # Clear the cell first so transparent parts of the Raw image stay transparent.
        sheet.paste(blank, (x, y))
        sheet.paste(img, (x, y))
        placed += 1
    if placed == 0:
        print("Nothing to place; tileset unchanged.")
        return
    backup_dir = os.path.join(os.path.dirname(tileset_path), 'Backups')
    stem = os.path.splitext(os.path.basename(tileset_path))[0]
    backup = os.path.join(backup_dir, f"{stem}.{datetime.now():%Y%m%d-%H%M%S}.png")
    try:
        os.makedirs(backup_dir, exist_ok=True)
        shutil.copyfile(tileset_path, backup)
    except OSError as e:
        raise SystemExit(f"Could not back up the tileset to {backup} ({e}); tileset unchanged.")
    try:
        sheet.save(tileset_path, 'PNG')
    except OSError as e:
        # Windows refuses to write a file another program (image viewer, editor preview) has open.
        raise SystemExit(f"Could not write {tileset_path} ({e}). Close any program showing it and rerun.")
    print(f"Placed {placed} glyphs into {tileset_path} (previous version: {backup})")

if __name__ == '__main__':
    names = [os.path.basename(a) for a in sys.argv[1:]] or None
    compose_raw_glyphs(RAW_DIR, TILESET_PATH, tile_size=GLYPH_SIZE, filenames=names)
