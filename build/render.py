import base64
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome",
    "chromium",
    "chromium-browser",
]

RASTERS = [
    ("web/favicon.svg", "web/favicon-16.png", 16, 16),
    ("web/favicon.svg", "web/favicon-32.png", 32, 32),
    ("web/favicon.svg", "web/favicon-48.png", 48, 48),
    ("tile/zekaa-tile-square.svg", "web/apple-touch-icon.png", 180, 180),
    ("tile/zekaa-tile.svg", "web/icon-192.png", 192, 192),
    ("tile/zekaa-tile.svg", "web/icon-512.png", 512, 512),
    ("tile/zekaa-tile-square.svg", "web/maskable-512.png", 512, 512),
    ("tile/zekaa-tile.svg", "png/zekaa-tile-512.png", 512, 512),
    ("tile/zekaa-tile.svg", "png/zekaa-tile-1024.png", 1024, 1024),
    ("tile/zekaa-tile-square.svg", "png/zekaa-avatar-1024.png", 1024, 1024),
    ("mark/zekaa-mark-arus.svg", "png/zekaa-mark-arus-1024.png", 1024, 1024),
    ("logo/horizontal/zekaa-logo-horizontal.svg", "png/zekaa-logo-horizontal-2400.png", 2400, None),
    ("logo/horizontal/zekaa-logo-horizontal-dark.svg", "png/zekaa-logo-horizontal-dark-2400.png", 2400, None),
    ("logo/horizontal/zekaa-logo-horizontal-inverse.svg", "png/zekaa-logo-horizontal-inverse-2400.png", 2400, None),
    ("logo/stacked/zekaa-logo-stacked.svg", "png/zekaa-logo-stacked-1200.png", 1200, None),
    ("logo/stacked/zekaa-logo-stacked-dark.svg", "png/zekaa-logo-stacked-dark-1200.png", 1200, None),
]

ICO_SOURCES = ["web/favicon-16.png", "web/favicon-32.png", "web/favicon-48.png"]


def find_chrome():
    for candidate in CHROME_CANDIDATES:
        if Path(candidate).is_absolute() and Path(candidate).exists():
            return candidate
        found = shutil.which(candidate)
        if found:
            return found
    raise SystemExit("Chrome or Chromium not found")


def viewbox_size(svg_text):
    start = svg_text.index('viewBox="') + len('viewBox="')
    end = svg_text.index('"', start)
    _, _, width, height = svg_text[start:end].split()
    return float(width), float(height)


def render(chrome, source, target, width, height):
    svg_text = (ROOT / source).read_text()
    if height is None:
        box_width, box_height = viewbox_size(svg_text)
        height = round(width * box_height / box_width)
    data = base64.b64encode(svg_text.encode()).decode()
    page = (
        "<!doctype html><html><head><style>"
        f"html,body{{margin:0;background:transparent;width:{width}px;height:{height}px;overflow:hidden}}"
        f"img{{display:block;width:{width}px;height:{height}px}}"
        "</style></head><body>"
        f"<img src='data:image/svg+xml;base64,{data}'>"
        "</body></html>"
    )
    out = ROOT / target
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        html = Path(tmp) / "page.html"
        html.write_text(page)
        subprocess.run(
            [
                chrome,
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                "--force-device-scale-factor=1",
                "--default-background-color=00000000",
                f"--user-data-dir={tmp}/profile",
                f"--window-size={width},{height}",
                f"--screenshot={out}",
                html.as_uri(),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    print(target, f"{width}x{height}")


def png_size(path):
    head = path.read_bytes()[:24]
    return struct.unpack(">II", head[16:24])


def write_ico(sources, target):
    blobs = [(ROOT / source).read_bytes() for source in sources]
    sizes = [png_size(ROOT / source) for source in sources]
    offset = 6 + 16 * len(blobs)
    header = struct.pack("<HHH", 0, 1, len(blobs))
    entries = b""
    for (width, height), blob in zip(sizes, blobs):
        entries += struct.pack("<BBBBHHII", width, height, 0, 0, 1, 32, len(blob), offset)
        offset += len(blob)
    (ROOT / target).write_bytes(header + entries + b"".join(blobs))
    print(target)


def main():
    chrome = find_chrome()
    for source, target, width, height in RASTERS:
        render(chrome, source, target, width, height)
    write_ico(ICO_SOURCES, "web/favicon.ico")


if __name__ == "__main__":
    main()
