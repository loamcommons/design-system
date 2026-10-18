"""Compose a presentation preview from the canonical SVGs without altering them."""
from pathlib import Path
import base64
import subprocess

root = Path(__file__).resolve().parent.parent


def asset(name, x, y, width, height):
    encoded = base64.b64encode((root / 'svg' / name).read_bytes()).decode()
    return f'<image x="{x}" y="{y}" width="{width}" height="{height}" href="data:image/svg+xml;base64,{encoded}"/>'


svg = '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="650" viewBox="0 0 1200 650"><rect width="1200" height="650" fill="white"/>'
svg += asset('loam-wordmark.svg', 185, 35, 830, 257)
svg += '<path d="M90 335H1110" stroke="#dedede"/>'
svg += asset('loamcommons-wordmark.svg', 70, 405, 1060, 226)
svg += '</svg>'
path = root / 'evidence/selected-family.svg'
path.write_text(svg)
subprocess.run(['rsvg-convert', str(path), '-o', str(path.with_suffix('.png'))], check=True)
