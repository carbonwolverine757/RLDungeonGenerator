#!/usr/bin/env python3
# Generate a Unicode tilesheet PNG from a TrueType font.
# Produces a grid of tile_size x tile_size cells containing codepoints you choose.

from PIL import Image, ImageDraw, ImageFont
import os

def generate_tilesheet(out_path, font_path, tile_size=16, cols=16, codepoints=None, bg=(0,0,0), fg=(255,255,255)):
    if codepoints is None:
        # default: first 256 codepoints (simple ASCII + control area)
        codepoints = list(range(256))
    rows = (len(codepoints) + cols - 1) // cols
    img_w = cols * tile_size
    img_h = rows * tile_size
    # Use a fully transparent background (alpha = 0) so the tilesheet
    # has no solid black behind glyphs. The RGB portion of `bg` is kept
    # only as a fallback tint and is not visible due to alpha=0.
    img = Image.new('RGBA', (img_w, img_h), color=bg + (0,))
    draw = ImageDraw.Draw(img)
    try:
        # Use full tile_size for the font to allow glyphs to fill cells and align with grid boundaries
        font = ImageFont.truetype(font_path, tile_size)
    except Exception as e:
        raise RuntimeError(f"Failed to load font {font_path}: {e}")
    for i, cp in enumerate(codepoints):
        row = i // cols
        col = i % cols
        x = col * tile_size
        y = row * tile_size
        ch = chr(cp)
        # Render glyphs at top-left of cells (no centering) so they align with tcod's grid slicing
        tx = x
        ty = y
        try:
            draw.text((tx, ty), ch, font=font, fill=fg + (255,))
        except Exception:
            # if glyph can't be drawn, leave blank
            pass
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, 'PNG')
    print(f"Saved tilesheet: {out_path} ({cols}×{rows} tiles = {cols*rows})")

if __name__ == '__main__':
    # Example usage:
    # - tile_size 16
    # - 16 columns → 16×16 grid = 256 tiles
    # - To get more tiles increase cols or include more codepoints (rows increase automatically)
    font_candidates = [
        r"C:\Windows\Fonts\consola.ttf",
        r"/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        r"/usr/share/fonts/truetype/noto/NotoSansMono-Regular.ttf",
        r"/System/Library/Fonts/Monaco.ttf",
    ]
    font_path = None
    tile_size = 64
    for p in font_candidates:
        if os.path.exists(p):
            font_path = p
            break
    if font_path is None:
        raise SystemExit("No font found - install DejaVu/Noto or update font path in script.")
    out = os.path.join('assets', 'tilesets', f'unicode_tileset_{tile_size}.png')
    # Example: create tilesheet for Unicode block U+2500..U+257F plus ASCII and extended characters.
    codepoints = list(range(32, 127))  # printable ASCII
    codepoints += list(range(0x2500, 0x2580))  # box drawing block (128 chars)
    # Additional Unicode blocks:
    codepoints += list(range(0x2580, 0x25A0))  # block elements
    codepoints += list(range(0x25A0, 0x25FF))  # geometric shapes
    codepoints += list(range(0x2600, 0x26FF))  # miscellaneous symbols
    codepoints += list(range(0x2700, 0x27BF))  # dingbats
    # You can append any other codepoints you need:
    codepoints += [0x2588, 0x00B7, 0x2193]  # '█', '·', '↓' (duplicates okay, they'll just appear twice)
    generate_tilesheet(out, font_path, tile_size=tile_size, cols=32, codepoints=codepoints)