#!/usr/bin/env python3
# Generate one GLYPH_SIZE x GLYPH_SIZE PNG per tileset cell in the Raw folder.
# Each image is the font rendering of that cell's codepoint, named by its
# position (e.g. r07_c16.png), as a starting point for hand-drawn art.
# compose_raw_glyphs.py pastes the Raw images back into the tileset.
#
# Existing Raw images are kept so edits are never lost; pass --overwrite to
# regenerate them all.

from PIL import Image, ImageDraw, ImageFont
import os
import sys

# Sheet geometry comes from Glyph_Grimoire.py at the repo root.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Glyph_Grimoire import GLYPH_SIZE, TILESET_COLUMNS, glyph_row_col
from generate_unicode_tileset import find_font, tileset_codepoints

RAW_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Raw')

def raw_filename(row, col):
    """Raw image name for the glyph at (row, col); compose_raw_glyphs.py parses it back."""
    return f"r{row:02d}_c{col:02d}.png"

def generate_raw_glyphs(out_dir, font_path, tile_size=16, codepoints=None, fg=(255,255,255), overwrite=False):
    if codepoints is None:
        codepoints = list(range(256))
    try:
        font = ImageFont.truetype(font_path, tile_size)
    except Exception as e:
        raise RuntimeError(f"Failed to load font {font_path}: {e}")
    os.makedirs(out_dir, exist_ok=True)
    written = skipped = 0
    for i, cp in enumerate(codepoints):
        row, col = glyph_row_col(i)
        out_path = os.path.join(out_dir, raw_filename(row, col))
        if os.path.exists(out_path) and not overwrite:
            skipped += 1
            continue
        # Transparent background, glyph at top-left, matching generate_unicode_tileset.
        img = Image.new('RGBA', (tile_size, tile_size), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        try:
            draw.text((0, 0), chr(cp), font=font, fill=fg + (255,))
        except Exception:
            # if glyph can't be drawn, leave blank
            pass
        img.save(out_path, 'PNG')
        written += 1
    print(f"Raw glyphs in {out_dir}: {written} written, {skipped} kept (already existed)")

if __name__ == '__main__':
    overwrite = '--overwrite' in sys.argv[1:]
    generate_raw_glyphs(RAW_DIR, find_font(), tile_size=GLYPH_SIZE,
                        codepoints=tileset_codepoints(), overwrite=overwrite)
