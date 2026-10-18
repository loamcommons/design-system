"""GitHub upload canvases composed from canonical SVGs without geometry changes."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "source"))
from imagemagick import command

root = Path(__file__).resolve().parent
identity = root.parent
placements = [
    ('loamcommons-avatar', 'loamcommons-mark-square.svg', 512, 512, 0, 0, 512, 512),
    ('loam-social-preview', 'loam-wordmark.svg', 1280, 640, 80, 0, 1120, 640),
]
receipt = []
for name, source, width, height, x, y, art_width, art_height in placements:
    source_path = identity / 'svg' / source
    original = source_path.read_bytes()
    data = base64.b64encode(original).decode()
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><rect width="{width}" height="{height}" fill="#FFFFFF"/><image x="{x}" y="{y}" width="{art_width}" height="{art_height}" preserveAspectRatio="xMidYMid meet" href="data:image/svg+xml;base64,{data}"/></svg>'
    svg_path = root / f'{name}.svg'
    png_path = root / f'{name}.png'
    svg_path.write_text(svg)
    subprocess.run(['rsvg-convert', str(svg_path), '-o', str(png_path)], check=True)
    actual = subprocess.check_output(command('identify', '-format', '%w %h', str(png_path))).decode()
    assert actual == f'{width} {height}'
    assert png_path.stat().st_size < 1_000_000
    receipt.append({'upload': png_path.name, 'size': [width, height], 'bytes': png_path.stat().st_size, 'sha256': hashlib.sha256(png_path.read_bytes()).hexdigest(), 'canonical_source': str(source_path.relative_to(identity)), 'canonical_sha256': hashlib.sha256(original).hexdigest(), 'placement': [x, y, art_width, art_height], 'scaling': 'uniform, centered; white background; original clear space retained'})
(root / 'derivation.json').write_text(json.dumps(receipt, indent=2)+'\n')
print(json.dumps(receipt, indent=2))
