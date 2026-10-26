import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"

ARUS = "#0B7A64"
ARANG = "#1C2624"
WHITE = "#FFFFFF"
BLACK = "#000000"

TILE = 256
TILE_RADIUS = 56
U = TILE / 4
MARK_SCALE_IN_TILE = 0.8

WORD_CAP_HEIGHT_FONT_UNITS = 745
WORD_INK_LEFT_FONT_UNITS = 11
WORD_INK_RIGHT_FONT_UNITS = 2827
WORD_INK_BOTTOM_FONT_UNITS = 12

HORIZONTAL_CAP_HEIGHT = TILE * 2 / 3
STACKED_CAP_HEIGHT = TILE / 3

MARK = (BUILD / "mark.txt").read_text().strip()
WORD = (BUILD / "wordmark.txt").read_text().strip()

COLORWAYS = {
    "": {"tile": ARUS, "mark": WHITE, "word": ARANG},
    "-dark": {"tile": ARUS, "mark": WHITE, "word": WHITE},
    "-inverse": {"tile": WHITE, "mark": ARUS, "word": WHITE},
    "-black": {"one_ink": BLACK},
    "-white": {"one_ink": WHITE},
}


def num(value):
    text = f"{value:.3f}".rstrip("0").rstrip(".")
    if text == "-0":
        return "0"
    return text


def scale_mark_path(path, scale, center):
    tokens = re.findall(r"[MLAZ]|-?\d+(?:\.\d+)?", path)
    out = []
    index = 0
    while index < len(tokens):
        command = tokens[index]
        index += 1
        if command in ("M", "L"):
            x = float(tokens[index])
            y = float(tokens[index + 1])
            index += 2
            out.append(f"{command}{num(center + (x - center) * scale)} {num(center + (y - center) * scale)}")
        elif command == "A":
            rx, ry, rotation, large, sweep, x, y = tokens[index:index + 7]
            index += 7
            x = center + (float(x) - center) * scale
            y = center + (float(y) - center) * scale
            out.append(f"A{num(float(rx) * scale)} {num(float(ry) * scale)} {rotation} {large} {sweep} {num(x)} {num(y)}")
        elif command == "Z":
            out.append("Z")
    return " ".join(out)


def rounded_square_path(x, y, size, radius):
    r = radius
    return (
        f"M{num(x + r)} {num(y)} H{num(x + size - r)} "
        f"A{num(r)} {num(r)} 0 0 1 {num(x + size)} {num(y + r)} V{num(y + size - r)} "
        f"A{num(r)} {num(r)} 0 0 1 {num(x + size - r)} {num(y + size)} H{num(x + r)} "
        f"A{num(r)} {num(r)} 0 0 1 {num(x)} {num(y + size - r)} V{num(y + r)} "
        f"A{num(r)} {num(r)} 0 0 1 {num(x + r)} {num(y)} Z"
    )


def svg(width, height, title, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {num(width)} {num(height)}" '
        f'width="{num(width)}" height="{num(height)}" role="img" aria-labelledby="title">'
        f'<title id="title">{title}</title>{body}</svg>\n'
    )


def tile_body(x, y, colors):
    in_tile = scale_mark_path(MARK, MARK_SCALE_IN_TILE, TILE / 2)
    if "one_ink" in colors:
        knockout = rounded_square_path(0, 0, TILE, TILE_RADIUS) + " " + in_tile
        return f'<path transform="translate({num(x)} {num(y)})" fill="{colors["one_ink"]}" fill-rule="evenodd" d="{knockout}"/>'
    return (
        f'<g transform="translate({num(x)} {num(y)})">'
        f'<rect width="{TILE}" height="{TILE}" rx="{TILE_RADIUS}" fill="{colors["tile"]}"/>'
        f'<path fill="{colors["mark"]}" fill-rule="evenodd" d="{in_tile}"/>'
        f"</g>"
    )


def word_body(ink_left_x, baseline_y, cap_height, color):
    scale = cap_height / WORD_CAP_HEIGHT_FONT_UNITS
    x = ink_left_x - WORD_INK_LEFT_FONT_UNITS * scale
    return f'<path transform="translate({num(x)} {num(baseline_y)}) scale({scale:.6f})" fill="{color}" d="{WORD}"/>'


def word_width(cap_height):
    scale = cap_height / WORD_CAP_HEIGHT_FONT_UNITS
    return (WORD_INK_RIGHT_FONT_UNITS - WORD_INK_LEFT_FONT_UNITS) * scale


def word_color(colors):
    if "one_ink" in colors:
        return colors["one_ink"]
    return colors["word"]


def horizontal(colors):
    cap = HORIZONTAL_CAP_HEIGHT
    baseline = TILE / 2 + cap / 2
    word_left = TILE + U
    width = word_left + word_width(cap)
    body = tile_body(0, 0, colors) + word_body(word_left, baseline, cap, word_color(colors))
    return svg(width, TILE, "Zekaa", body)


def stacked(colors):
    cap = STACKED_CAP_HEIGHT
    width = max(TILE, word_width(cap))
    baseline = TILE + U + cap
    scale = cap / WORD_CAP_HEIGHT_FONT_UNITS
    height = baseline + WORD_INK_BOTTOM_FONT_UNITS * scale
    tile_x = (width - TILE) / 2
    word_left = (width - word_width(cap)) / 2
    body = tile_body(tile_x, 0, colors) + word_body(word_left, baseline, cap, word_color(colors))
    return svg(width, height, "Zekaa", body)


def tile(colors):
    return svg(TILE, TILE, "Zekaa", tile_body(0, 0, colors))


def tile_square():
    in_tile = scale_mark_path(MARK, MARK_SCALE_IN_TILE, TILE / 2)
    body = f'<rect width="{TILE}" height="{TILE}" fill="{ARUS}"/><path fill="{WHITE}" fill-rule="evenodd" d="{in_tile}"/>'
    return svg(TILE, TILE, "Zekaa", body)


def mark(color):
    return svg(TILE, TILE, "Zekaa", f'<path fill="{color}" fill-rule="evenodd" d="{MARK}"/>')


def manifest():
    data = {
        "name": "Zekaa",
        "icons": [
            {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "/maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
        "theme_color": ARUS,
        "background_color": ARUS,
        "display": "standalone",
    }
    return json.dumps(data, indent=2) + "\n"


HEAD_SNIPPET = """<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#0B7A64">
"""


def write(relative, text):
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    print(relative)


def main():
    for suffix, colors in COLORWAYS.items():
        write(f"logo/horizontal/zekaa-logo-horizontal{suffix}.svg", horizontal(colors))
        write(f"logo/stacked/zekaa-logo-stacked{suffix}.svg", stacked(colors))
    write("tile/zekaa-tile.svg", tile(COLORWAYS[""]))
    write("tile/zekaa-tile-inverse.svg", tile(COLORWAYS["-inverse"]))
    write("tile/zekaa-tile-black.svg", tile(COLORWAYS["-black"]))
    write("tile/zekaa-tile-white.svg", tile(COLORWAYS["-white"]))
    write("tile/zekaa-tile-square.svg", tile_square())
    write("mark/zekaa-mark-arus.svg", mark(ARUS))
    write("mark/zekaa-mark-black.svg", mark(BLACK))
    write("mark/zekaa-mark-white.svg", mark(WHITE))
    write("web/favicon.svg", tile(COLORWAYS[""]))
    write("web/site.webmanifest", manifest())
    write("web/head-snippet.html", HEAD_SNIPPET)


if __name__ == "__main__":
    main()
