#!/usr/bin/env python3
"""Compare two PNG screenshots and report mismatch percentages per region.

Makes the figma-design-to-code compare loop measurable: diff the exported
Figma reference against the rendered-app screenshot and gate on a number
instead of eyeballing. Pure stdlib (own PNG decoder) so it runs anywhere the
template runs, with no new dependencies.

Usage:
    <python> .agents/tools/pixel_diff.py REFERENCE.png ACTUAL.png \
        [--threshold 5.0] [--tolerance 24] [--grid 4] [--sample 1]

- threshold: max overall mismatch %% to PASS (default 5.0)
- tolerance: per-channel delta (0-255) below which a pixel still counts as a
  match; absorbs anti-aliasing and font-hinting noise (default 24)
- grid: NxN region breakdown so deviations can be localized (default 4)
- sample: check every Nth pixel in both axes for very large images (default 1)

Sizes may differ (e.g. 1x vs 3x exports): the actual image is sampled at the
reference's coordinate space via nearest neighbor. A large aspect-ratio
difference is reported as an error since the comparison would be meaningless.

Exit codes: 0 = PASS, 1 = FAIL (mismatch above threshold), 2 = usage/decode error.
"""

from __future__ import annotations

import argparse
import struct
import sys
import zlib
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}  # color type -> samples per pixel


class PngError(ValueError):
    pass


def _paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    return b if pb <= pc else c


def read_png(path: Path) -> tuple[int, int, list[bytes]]:
    """Decode a PNG to (width, height, rows of RGB bytes: 3 bytes per pixel)."""
    data = path.read_bytes()
    if data[:8] != PNG_SIGNATURE:
        raise PngError(f"{path.name}: not a PNG file")

    width = height = 0
    bit_depth = color_type = interlace = -1
    palette = b""
    idat = bytearray()
    pos = 8
    while pos + 8 <= len(data):
        length, ctype = struct.unpack(">I4s", data[pos : pos + 8])
        chunk = data[pos + 8 : pos + 8 + length]
        pos += 12 + length  # length + type + data + crc
        if ctype == b"IHDR":
            width, height, bit_depth, color_type, _, _, interlace = struct.unpack(
                ">IIBBBBB", chunk
            )
        elif ctype == b"PLTE":
            palette = chunk
        elif ctype == b"IDAT":
            idat += chunk
        elif ctype == b"IEND":
            break

    if width == 0 or height == 0:
        raise PngError(f"{path.name}: missing IHDR")
    if bit_depth != 8:
        raise PngError(f"{path.name}: unsupported bit depth {bit_depth} (need 8)")
    if interlace != 0:
        raise PngError(f"{path.name}: interlaced PNG unsupported; re-export without interlacing")
    if color_type not in CHANNELS:
        raise PngError(f"{path.name}: unsupported color type {color_type}")

    channels = CHANNELS[color_type]
    stride = width * channels
    raw = zlib.decompress(bytes(idat))
    if len(raw) < (stride + 1) * height:
        raise PngError(f"{path.name}: truncated pixel data")

    rows: list[bytes] = []
    previous = bytearray(stride)
    offset = 0
    for _ in range(height):
        filter_type = raw[offset]
        line = bytearray(raw[offset + 1 : offset + 1 + stride])
        offset += 1 + stride
        if filter_type == 1:  # Sub
            for i in range(channels, stride):
                line[i] = (line[i] + line[i - channels]) & 0xFF
        elif filter_type == 2:  # Up
            for i in range(stride):
                line[i] = (line[i] + previous[i]) & 0xFF
        elif filter_type == 3:  # Average
            for i in range(stride):
                left = line[i - channels] if i >= channels else 0
                line[i] = (line[i] + ((left + previous[i]) >> 1)) & 0xFF
        elif filter_type == 4:  # Paeth
            for i in range(stride):
                left = line[i - channels] if i >= channels else 0
                up_left = previous[i - channels] if i >= channels else 0
                line[i] = (line[i] + _paeth(left, previous[i], up_left)) & 0xFF
        elif filter_type != 0:
            raise PngError(f"{path.name}: unknown scanline filter {filter_type}")
        previous = line

        # Normalize every color type to packed RGB (alpha ignored: screenshots
        # are opaque, and Figma exports composite on white anyway).
        rgb = bytearray(width * 3)
        if color_type == 2:  # RGB
            rgb[:] = line
        elif color_type == 6:  # RGBA
            for x in range(width):
                rgb[x * 3 : x * 3 + 3] = line[x * 4 : x * 4 + 3]
        elif color_type == 0:  # gray
            for x in range(width):
                rgb[x * 3] = rgb[x * 3 + 1] = rgb[x * 3 + 2] = line[x]
        elif color_type == 4:  # gray + alpha
            for x in range(width):
                rgb[x * 3] = rgb[x * 3 + 1] = rgb[x * 3 + 2] = line[x * 2]
        elif color_type == 3:  # palette
            if not palette:
                raise PngError(f"{path.name}: palette image missing PLTE")
            for x in range(width):
                idx = line[x] * 3
                rgb[x * 3 : x * 3 + 3] = palette[idx : idx + 3]
        rows.append(bytes(rgb))
    return width, height, rows


def compare(
    ref: tuple[int, int, list[bytes]],
    act: tuple[int, int, list[bytes]],
    tolerance: int,
    grid: int,
    sample: int,
) -> tuple[float, list[list[float]]]:
    """Return (overall mismatch %, grid of per-cell mismatch %)."""
    rw, rh, ref_rows = ref
    aw, ah, act_rows = act

    checked = [[0] * grid for _ in range(grid)]
    mismatched = [[0] * grid for _ in range(grid)]
    for y in range(0, rh, sample):
        ref_row = ref_rows[y]
        act_row = act_rows[min(y * ah // rh, ah - 1)]
        gy = min(y * grid // rh, grid - 1)
        row_checked = checked[gy]
        row_bad = mismatched[gy]
        for x in range(0, rw, sample):
            ax = min(x * aw // rw, aw - 1)
            gx = min(x * grid // rw, grid - 1)
            row_checked[gx] += 1
            r = x * 3
            a = ax * 3
            if (
                abs(ref_row[r] - act_row[a]) > tolerance
                or abs(ref_row[r + 1] - act_row[a + 1]) > tolerance
                or abs(ref_row[r + 2] - act_row[a + 2]) > tolerance
            ):
                row_bad[gx] += 1

    total = sum(sum(row) for row in checked)
    bad = sum(sum(row) for row in mismatched)
    cells = [
        [100.0 * mismatched[gy][gx] / checked[gy][gx] if checked[gy][gx] else 0.0 for gx in range(grid)]
        for gy in range(grid)
    ]
    return (100.0 * bad / total if total else 0.0), cells


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("reference", type=Path, help="Figma export (ground truth)")
    parser.add_argument("actual", type=Path, help="rendered-app screenshot")
    parser.add_argument("--threshold", type=float, default=5.0)
    parser.add_argument("--tolerance", type=int, default=24)
    parser.add_argument("--grid", type=int, default=4)
    parser.add_argument("--sample", type=int, default=1)
    args = parser.parse_args()

    try:
        ref = read_png(args.reference)
        act = read_png(args.actual)
    except (OSError, PngError, zlib.error) as error:
        print(f"error: {error}")
        return 2

    rw, rh, _ = ref
    aw, ah, _ = act
    if abs((rw / rh) - (aw / ah)) / (rw / rh) > 0.02:
        print(
            f"error: aspect ratios differ too much ({rw}x{rh} vs {aw}x{ah}); "
            "capture the app at the design frame's dimensions first"
        )
        return 2

    overall, cells = compare(ref, act, args.tolerance, max(1, args.grid), max(1, args.sample))
    print(f"reference {rw}x{rh}, actual {aw}x{ah} (sampled at reference size)")
    print(f"overall mismatch: {overall:.2f}% (tolerance {args.tolerance}/255)")
    print("regions (top row first):")
    for row in cells:
        print("  " + "  ".join(f"{cell:6.2f}%" for cell in row))
    verdict = overall <= args.threshold
    print(f"{'PASS' if verdict else 'FAIL'} (threshold {args.threshold}%)")
    return 0 if verdict else 1


if __name__ == "__main__":
    raise SystemExit(main())
