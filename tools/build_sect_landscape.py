"""Package the sect landscape PNG as a native-size CK3 DDS texture."""
import argparse
from pathlib import Path
import struct

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'AuraClash/gfx/interface/window_domiciles/ac_sect_landscape.dds'


def render():
    with Image.open(ROOT / 'assets/sect-domicile/landscape.png') as source:
        native = source.convert('RGBA').resize((2412, 1112), Image.Resampling.LANCZOS)
    width, height = native.size
    header = struct.pack('<4s31I', b'DDS ',
                         124, 0x100F, height, width, width * 4, 0, 0,
                         *([0] * 11), 32, 0x41, 0, 32,
                         0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000,
                         0x1000, 0, 0, 0, 0)
    return header + native.tobytes('raw', 'BGRA')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    data = render()
    if args.check:
        if not TARGET.exists() or TARGET.read_bytes() != data:
            raise SystemExit('Sect landscape DDS is stale.')
    else:
        TARGET.parent.mkdir(parents=True, exist_ok=True)
        TARGET.write_bytes(data)
    print('Verified sect landscape.' if args.check else 'Built sect landscape.')


if __name__ == '__main__':
    main()
