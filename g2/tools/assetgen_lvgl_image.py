#!/usr/bin/env python3
"""Generate an LVGL v9 `lv_image_dsc_t` C source file from a source image.

This is XC-005 host tooling: the maintainable *source* representation for an
Apollo LVGL image data region is the original artwork (a PNG under a
documented license) plus this generator, not a byte array copied out of the
stock firmware. An AD-* item that reconstructs an image region places its
source asset under `g2/assets/<component>/...`, records its license and
SHA-256 in that asset's own provenance note, runs this tool to produce the
`.c` file, and registers the result exactly as any other reviewed source file
(overlay entry, manifest pin, EVIDENCE update). This tool never reads the
stock firmware image; the differential comparison against the stock bytes (if
any) is the AD-* item's job, using the stock image strictly as an oracle.

Output format
--------------
The emitted `lv_image_dsc_t`/`lv_image_header_t` layout matches
`third_party/lvgl/src/draw/lv_image_dsc.h` at the pinned openCFW LVGL
snapshot (commit 344c7c318047b7348e1be8572a9fd4260c251cfa, see
`third_party/lvgl/README.openCFW.md`). Supported `lv_color_format_t` values
mirror `third_party/lvgl/src/misc/lv_color.h`:

  L8        1 byte/px, grayscale (matches the recovered G2 LV_COLOR_DEPTH=8)
  A8        1 byte/px, alpha-only mask (no color channel)
  I8        1 byte/px index + 256-entry BGRA8888 palette prefix
  RGB565    2 bytes/px, little-endian 5-6-5
  RGB888    3 bytes/px, B,G,R
  XRGB8888  4 bytes/px, B,G,R,X (X = 0xFF)
  ARGB8888  4 bytes/px, B,G,R,A

Every row is padded to `stride` bytes (LVGL v9 images carry an explicit
stride field, so no implicit alignment rule is assumed).

This tool is openCFW-authored and offered under the repository's MIT License
(see CONTRIBUTING.md); it is independent of, and does not embed, any LVGL
source.
"""
from __future__ import annotations

import argparse
import hashlib
import struct
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover - environment guard, not a design fallback
    Image = None

LV_IMAGE_HEADER_MAGIC = 0x19

COLOR_FORMATS = {
    "L8": 0x06,
    "I8": 0x0A,
    "A8": 0x0E,
    "RGB888": 0x0F,
    "ARGB8888": 0x10,
    "XRGB8888": 0x11,
    "RGB565": 0x12,
}

BYTES_PER_PIXEL = {
    "L8": 1, "A8": 1, "RGB565": 2, "RGB888": 3, "XRGB8888": 4, "ARGB8888": 4,
}


class AssetGenError(Exception):
    pass


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pack_header(cf: str, w: int, h: int, stride: int, flags: int = 0) -> bytes:
    """Pack an `lv_image_header_t` (little-endian target, the only ABI the
    recovered G2 configuration establishes; see lv_conf_recovered.h)."""
    if not (0 <= w <= 0xFFFF and 0 <= h <= 0xFFFF and 0 <= stride <= 0xFFFF):
        raise AssetGenError("width/height/stride must fit in 16 bits")
    word0 = (LV_IMAGE_HEADER_MAGIC & 0xFF) | ((COLOR_FORMATS[cf] & 0xFF) << 8) | ((flags & 0xFFFF) << 16)
    word1 = (w & 0xFFFF) | ((h & 0xFFFF) << 16)
    word2 = (stride & 0xFFFF)  # reserved_2 (upper 16 bits) stays zero
    return struct.pack("<III", word0, word1, word2)


def _row_bytes_indexed(pixels, w: int, bpp_pack: int) -> bytes:
    assert bpp_pack == 8
    return bytes(pixels)


def build_palette(image) -> list[tuple[int, int, int, int]]:
    """Return the up-to-256-entry RGBA palette in index order."""
    pal = image.getpalette(rawmode="RGBA")
    if pal is None:
        pal = image.getpalette() or []
        # getpalette() without rawmode returns flat RGB triples.
        entries = [tuple(pal[i:i + 3]) + (255,) for i in range(0, len(pal), 3)]
    else:
        entries = [tuple(pal[i:i + 4]) for i in range(0, len(pal), 4)]
    return entries


def decode(cf: str, w: int, h: int, stride: int, palette: bytes, pixels: bytes):
    """Independent reference decoder for the formats this tool emits.

    Returns a list of `h` rows, each a list of `w` RGBA 4-tuples, using only
    the packed bytes (mirrors what `lv_bin_decoder.c` would reconstruct).
    Used to round-trip-verify every generated file before it is written.
    """
    rows = []
    if cf == "L8":
        for y in range(h):
            row = pixels[y * stride: y * stride + w]
            rows.append([(v, v, v, 255) for v in row])
    elif cf == "A8":
        for y in range(h):
            row = pixels[y * stride: y * stride + w]
            rows.append([(0, 0, 0, v) for v in row])
    elif cf == "I8":
        entries = [struct.unpack_from("<BBBB", palette, i * 4) for i in range(256)]
        for y in range(h):
            row = pixels[y * stride: y * stride + w]
            out_row = []
            for idx in row:
                b, g, r, a = entries[idx]
                out_row.append((r, g, b, a))
            rows.append(out_row)
    elif cf == "RGB565":
        for y in range(h):
            row = pixels[y * stride: y * stride + w * 2]
            out_row = []
            for i in range(w):
                value = struct.unpack_from("<H", row, i * 2)[0]
                r5 = (value >> 11) & 0x1F
                g6 = (value >> 5) & 0x3F
                b5 = value & 0x1F
                out_row.append(((r5 << 3) | (r5 >> 2), (g6 << 2) | (g6 >> 4), (b5 << 3) | (b5 >> 2), 255))
            rows.append(out_row)
    elif cf == "RGB888":
        for y in range(h):
            row = pixels[y * stride: y * stride + w * 3]
            out_row = [(row[i * 3 + 2], row[i * 3 + 1], row[i * 3 + 0], 255) for i in range(w)]
            rows.append(out_row)
    elif cf in ("XRGB8888", "ARGB8888"):
        for y in range(h):
            row = pixels[y * stride: y * stride + w * 4]
            out_row = [(row[i * 4 + 2], row[i * 4 + 1], row[i * 4 + 0], row[i * 4 + 3]) for i in range(w)]
            rows.append(out_row)
    else:
        raise AssetGenError(f"unsupported color format {cf!r}")
    return rows


def convert(image, cf: str):
    """Return (header_flags, stride, palette_bgra_bytes, pixel_bytes), after
    round-trip-verifying the packed bytes against an independent decoder."""
    w, h = image.size
    expected = None
    if cf == "L8":
        gray = image.convert("L")
        stride = w
        rows = [bytes(gray.crop((0, y, w, y + 1)).getdata()) for y in range(h)]
        flags, palette, pixels = 0, b"", b"".join(rows)
        expected = [[(v, v, v, 255) for v in row] for row in rows]
    elif cf == "A8":
        rgba = image.convert("RGBA")
        alpha = rgba.getchannel("A")
        stride = w
        rows = [bytes(alpha.crop((0, y, w, y + 1)).getdata()) for y in range(h)]
        flags, palette, pixels = 0, b"", b"".join(rows)
        expected = [[(0, 0, 0, v) for v in row] for row in rows]
    elif cf == "I8":
        indexed = image.convert("RGBA").convert("P", palette=Image.ADAPTIVE, colors=256)
        entries = build_palette(indexed)
        entries = (entries + [(0, 0, 0, 0)] * 256)[:256]
        # This format's palette carries one alpha value per index (not per
        # source pixel): a fully faithful per-pixel alpha channel requires a
        # format with a separate alpha plane (e.g. ARGB8888) instead.
        palette_bgra = b"".join(struct.pack("<BBBB", b, g, r, a) for (r, g, b, a) in entries)
        stride = w
        rows = [bytes(indexed.crop((0, y, w, y + 1)).getdata()) for y in range(h)]
        flags, palette, pixels = 0, palette_bgra, b"".join(rows)
        expected = [[(entries[i][0], entries[i][1], entries[i][2], entries[i][3]) for i in row] for row in rows]
    elif cf == "RGB565":
        rgb = image.convert("RGB")
        stride = w * 2
        out = bytearray()
        expected = []
        for y in range(h):
            out_row = []
            exp_row = []
            for r, g, b in rgb.crop((0, y, w, y + 1)).getdata():
                r5, g6, b5 = r >> 3, g >> 2, b >> 3
                value = (r5 << 11) | (g6 << 5) | b5
                out_row.append(struct.pack("<H", value))
                exp_row.append(((r5 << 3) | (r5 >> 2), (g6 << 2) | (g6 >> 4), (b5 << 3) | (b5 >> 2), 255))
            out += b"".join(out_row)
            expected.append(exp_row)
        flags, palette, pixels = 0, b"", bytes(out)
    elif cf == "RGB888":
        rgb = image.convert("RGB")
        stride = w * 3
        out = bytearray()
        expected = []
        for y in range(h):
            exp_row = []
            for r, g, b in rgb.crop((0, y, w, y + 1)).getdata():
                out += bytes((b, g, r))
                exp_row.append((r, g, b, 255))
            expected.append(exp_row)
        flags, palette, pixels = 0, b"", bytes(out)
    elif cf in ("XRGB8888", "ARGB8888"):
        rgba = image.convert("RGBA")
        stride = w * 4
        out = bytearray()
        expected = []
        for y in range(h):
            exp_row = []
            for r, g, b, a in rgba.crop((0, y, w, y + 1)).getdata():
                a_out = 0xFF if cf == "XRGB8888" else a
                out += bytes((b, g, r, a_out))
                exp_row.append((r, g, b, a_out))
            expected.append(exp_row)
        flags, palette, pixels = 0, b"", bytes(out)
    else:
        raise AssetGenError(f"unsupported color format {cf!r}")

    actual = decode(cf, w, h, stride, palette, pixels)
    if actual != expected:
        raise AssetGenError(f"{cf} round-trip mismatch: generated bytes do not decode back to the encoded pixels")
    return flags, stride, palette, pixels


def generate_c_source(symbol: str, cf: str, w: int, h: int, stride: int,
                       flags: int, palette: bytes, pixels: bytes,
                       source_path: str, source_sha256: str, tool_version: str) -> str:
    header = pack_header(cf, w, h, stride, flags)
    data = palette + pixels
    lines = []
    lines.append("/* SPDX-License-Identifier: MIT")
    lines.append(" * Generated by g2/tools/assetgen_lvgl_image.py (openCFW asset generator tool, XC-005).")
    lines.append(f" * Generator version: {tool_version}")
    lines.append(f" * Source asset: {source_path}")
    lines.append(f" * Source asset SHA-256: {source_sha256}")
    lines.append(f" * Color format: {cf} ({w}x{h}, stride {stride})")
    lines.append(" * This file is derived from the source asset above, not from any Even")
    lines.append(" * Realities firmware image. Re-running the generator against the same")
    lines.append(" * asset reproduces this file byte-for-byte.")
    lines.append(" */")
    lines.append("#include <stdint.h>")
    lines.append('#include "lv_image_dsc.h"')
    lines.append("")
    lines.append(f"static const uint8_t {symbol}_map[] = {{")
    for i in range(0, len(data), 16):
        chunk = data[i:i + 16]
        lines.append("    " + ", ".join(f"0x{b:02x}" for b in chunk) + ",")
    lines.append("};")
    lines.append("")
    lines.append(f"const lv_image_dsc_t {symbol} = {{")
    lines.append("    .header = {")
    lines.append(f"        .magic = {LV_IMAGE_HEADER_MAGIC},")
    lines.append(f"        .cf = {COLOR_FORMATS[cf]},")
    lines.append(f"        .flags = {flags},")
    lines.append(f"        .w = {w},")
    lines.append(f"        .h = {h},")
    lines.append(f"        .stride = {stride},")
    lines.append("        .reserved_2 = 0,")
    lines.append("    },")
    lines.append(f"    .data_size = sizeof({symbol}_map),")
    lines.append(f"    .data = {symbol}_map,")
    lines.append("    .reserved = 0,")
    lines.append("    .reserved_2 = 0,")
    lines.append("};")
    lines.append("")
    return "\n".join(lines)


def build(source: Path, cf: str, symbol: str, tool_version: str = "1"):
    if Image is None:
        raise AssetGenError("Pillow (PIL) is required to run assetgen_lvgl_image.py")
    if cf not in COLOR_FORMATS:
        raise AssetGenError(f"unknown --format {cf!r}; choose one of {sorted(COLOR_FORMATS)}")
    raw = source.read_bytes()
    image = Image.open(source)
    image.load()
    flags, stride, palette, pixels = convert(image, cf)
    w, h = image.size
    text = generate_c_source(symbol, cf, w, h, stride, flags, palette, pixels,
                              str(source), sha256_hex(raw), tool_version)
    return text, {
        "width": w, "height": h, "stride": stride, "color_format": cf,
        "data_size": len(palette) + len(pixels), "source_sha256": sha256_hex(raw),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="source image (PNG or any Pillow-readable format)")
    parser.add_argument("--format", required=True, choices=sorted(COLOR_FORMATS), help="lv_color_format_t to emit")
    parser.add_argument("--symbol", required=True, help="C symbol name for the generated lv_image_dsc_t")
    parser.add_argument("-o", "--output", type=Path, required=True, help="output .c path")
    args = parser.parse_args(argv)
    try:
        text, meta = build(args.source, args.format, args.symbol)
    except AssetGenError as exc:
        print(f"assetgen_lvgl_image: {exc}", file=sys.stderr)
        return 1
    args.output.write_text(text)
    print(f"wrote {args.output} ({meta['data_size']} data bytes, {meta['color_format']} {meta['width']}x{meta['height']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
