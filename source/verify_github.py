"""Check that upload canvases retain the exact canonical SVGs and recorded PNGs."""
from pathlib import Path
import base64
import hashlib
import json
import struct
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parent.parent
ns = '{http://www.w3.org/2000/svg}'
receipt = json.loads((root / 'github/derivation.json').read_text())
assert {item['upload'] for item in receipt} == {'loamcommons-avatar.png', 'loam-social-preview.png'}
for item in receipt:
    source = (root / item['canonical_source']).read_bytes()
    assert hashlib.sha256(source).hexdigest() == item['canonical_sha256']
    png = root / 'github' / item['upload']
    data = png.read_bytes()
    assert hashlib.sha256(data).hexdigest() == item['sha256']
    assert len(data) == item['bytes'] < 1_000_000
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    assert list(struct.unpack('>II', data[16:24])) == item['size']
    svg = ET.fromstring(png.with_suffix('.svg').read_bytes())
    width, height = item['size']
    assert svg.attrib == {'width': str(width), 'height': str(height), 'viewBox': f'0 0 {width} {height}'}
    assert [node.tag for node in svg] == [ns + 'rect', ns + 'image']
    background, image = list(svg)
    assert background.attrib == {'width': str(width), 'height': str(height), 'fill': '#FFFFFF'}
    prefix = 'data:image/svg+xml;base64,'
    assert image.attrib['href'].startswith(prefix)
    assert base64.b64decode(image.attrib['href'][len(prefix):], validate=True) == source
    assert [float(image.attrib[key]) for key in ['x', 'y', 'width', 'height']] == item['placement']
    assert image.attrib['preserveAspectRatio'] == 'xMidYMid meet'
print('PASS: both GitHub upload canvases preserve canonical SVG geometry and recorded PNG bytes')
