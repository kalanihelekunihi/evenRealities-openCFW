#!/usr/bin/env python3
"""Generate an LVGL bitmap-font C source file from a source font, via the
official `lv_font_conv` tool.

XC-005 host tooling: an Apollo LVGL font data region (an `lv_font_t` /
`lv_font_fmt_txt_dsc_t` glyph table) should be reconstructed as a documented
source font file (an open/licensed TTF or OTF, chosen and provenance-recorded
by the AD-* item that needs it) plus a real font-rasterizing tool, not as an
opaque byte array. Hand-rolling a TrueType/OpenType shaper and rasterizer
from scratch would itself be an unreviewable reimplementation risk; instead
this wraps LVGL's own official converter (`lv_font_conv`, MIT license,
https://github.com/lvgl/lv_font_conv), which already emits exactly the
`lv_font_fmt_txt_dsc_t` layout vendored at `third_party/lvgl/src/font`.

`lv_font_conv` is an *external* host build tool (Node.js/npm), deliberately
not vendored into this repository -- vendoring its full npm dependency tree
(opentype.js, pngjs, yargs, ...) would defeat the point of a small, reviewable
diff. It is pinned by exact published version and by the npm registry's own
content-integrity hash, verified before every run; a version drift or a
missing `npx`/network path fails closed rather than silently falling back to
any retained bytes.

Because resolving/fetching the pinned npm package needs network access, this
tool (unlike assetgen_lvgl_image.py, assetgen_string_pool.py, and
assetgen_nanopb_descriptor.py, which are fully offline once their inputs
exist) requires it at generation time. That is a real, documented limitation
of this representation -- see g2/docs/research/g2-apollo-asset-generator-tooling.md.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

REQUIRED_LV_FONT_CONV_VERSION = "1.5.3"
REQUIRED_LV_FONT_CONV_INTEGRITY = (
    "sha512-0xJQThBOw2iptFccSXrKDIUTQAwr/2zhKjCI1lATIRgZo8uvYRTmenKafW9yTw6G0y5AyW00tqGpUtYuTuBIbQ=="
)
PACKAGE_SPEC = f"lv_font_conv@{REQUIRED_LV_FONT_CONV_VERSION}"


class AssetGenError(Exception):
    pass


def _require_npx() -> str:
    npx = shutil.which("npx")
    if npx is None:
        raise AssetGenError("npx (Node.js) not found on PATH; install Node.js to run lv_font_conv")
    return npx


def _verify_pinned_integrity() -> None:
    """Fail closed if the npm registry's resolved package no longer matches
    the pinned version's recorded integrity hash (supply-chain drift)."""
    npm = shutil.which("npm")
    if npm is None:
        raise AssetGenError("npm not found on PATH; cannot verify the lv_font_conv package pin")
    result = subprocess.run(
        [npm, "view", PACKAGE_SPEC, "dist.integrity"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise AssetGenError(f"npm view {PACKAGE_SPEC} failed:\n{result.stderr}")
    resolved = result.stdout.strip()
    if resolved != REQUIRED_LV_FONT_CONV_INTEGRITY:
        raise AssetGenError(
            f"lv_font_conv@{REQUIRED_LV_FONT_CONV_VERSION} integrity changed: "
            f"expected {REQUIRED_LV_FONT_CONV_INTEGRITY!r}, registry reports {resolved!r}"
        )


def generate(font_path: Path, output_path: Path, symbol: str, size_px: int,
             ranges: list, bpp: int = 4, compress: bool = False) -> dict:
    npx = _require_npx()
    _verify_pinned_integrity()
    if not font_path.is_file():
        raise AssetGenError(f"source font not found: {font_path}")
    if output_path.stem != symbol:
        # lv_font_conv has no --symbol flag; it derives the emitted C
        # identifier from the output file's stem. Enforce the match up
        # front instead of discovering it after a subprocess round trip.
        raise AssetGenError(
            f"lv_font_conv names the generated font after the output file "
            f"stem; expected --output stem {symbol!r}, got {output_path.stem!r}"
        )

    args = [
        npx, "--yes", PACKAGE_SPEC,
        "--font", str(font_path),
        "--size", str(size_px),
        "--bpp", str(bpp),
        "--format", "lvgl",
        "-o", str(output_path),
    ]
    for r in ranges:
        args += ["-r", r]
    if not compress:
        args.append("--no-compress")

    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        raise AssetGenError(f"lv_font_conv failed:\n{result.stderr}")
    if not output_path.is_file() or output_path.stat().st_size == 0:
        raise AssetGenError(f"lv_font_conv produced no output at {output_path}")

    generated = output_path.read_text()
    if symbol not in generated:
        raise AssetGenError(f"expected font symbol {symbol!r} not found in generated output")

    banner = (
        "/* SPDX-License-Identifier: MIT\n"
        " * Rasterized by g2/tools/assetgen_lvgl_font.py (openCFW asset generator\n"
        " * tool, XC-005) using the official lv_font_conv "
        f"{REQUIRED_LV_FONT_CONV_VERSION} (MIT, lvgl/lv_font_conv).\n"
        f" * Source font: {font_path}\n"
        " * This file is derived from the source font above, not from any Even\n"
        " * Realities firmware image.\n"
        " */\n"
    )
    output_path.write_text(banner + generated)

    return {
        "output": str(output_path), "bytes": output_path.stat().st_size,
        "lv_font_conv_version": REQUIRED_LV_FONT_CONV_VERSION,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("font", type=Path, help="source TTF/OTF file")
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("--symbol", required=True, help="C symbol lv_font_conv should emit (its --lvgl-name)")
    parser.add_argument("--size", type=int, required=True)
    parser.add_argument("--bpp", type=int, default=4, choices=(1, 2, 4, 8))
    parser.add_argument("-r", "--range", dest="ranges", action="append", default=[], help="codepoint range, e.g. 0x20-0x7e")
    args = parser.parse_args(argv)
    try:
        report = generate(args.font, args.output, args.symbol, args.size, args.ranges, args.bpp)
    except AssetGenError as exc:
        print(f"assetgen_lvgl_font: {exc}", file=sys.stderr)
        return 1
    print(f"wrote {report['output']} ({report['bytes']} bytes, lv_font_conv {report['lv_font_conv_version']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
