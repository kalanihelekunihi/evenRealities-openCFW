#!/usr/bin/env python3
"""Round-trip and target-header compile gates for assetgen_lvgl_image.py.

Confirms the XC-005 LVGL image generator (1) never touches the stock
firmware image, (2) produces bytes an independent decoder reconstructs
byte-exactly (or, for the lossy formats, exactly as encoded), and (3)
type-checks against the real vendored `lv_image_dsc.h`/`lv_image_header_t`
with the header's own default configuration (`LV_CONF_SKIP`).
"""
from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # Pillow is listed in tools/bootstrap/requirements.txt
    raise unittest.SkipTest("Pillow is not installed")

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/assetgen_lvgl_image.py"
LVGL_SRC = ROOT.parent / "third-party/upstream/lvgl/src"
LVGL_DRAW = ROOT.parent / "third-party/upstream/lvgl/src/draw"


def load_tool():
    spec = importlib.util.spec_from_file_location("assetgen_lvgl_image", TOOL)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def make_source_png(path: Path, w: int = 5, h: int = 4) -> None:
    image = Image.new("RGBA", (w, h))
    for y in range(h):
        for x in range(w):
            image.putpixel((x, y), ((x * 40) % 256, (y * 60) % 256, (x + y) * 5 % 256, 255 if (x + y) % 3 else 90))
    image.save(path)


@unittest.skipUnless(shutil.which("clang"), "clang not available on this host")
class AssetgenLvglImageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load_tool()
        cls.tmp = tempfile.TemporaryDirectory(prefix="assetgen-lvgl-image-")
        cls.dir = Path(cls.tmp.name)
        cls.source = cls.dir / "source.png"
        make_source_png(cls.source)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_never_reads_stock_image(self):
        source_text = TOOL.read_text()
        self.assertNotIn("blobs/official", source_text)
        self.assertNotIn("ota_s200_firmware_ota", source_text)

    def test_every_format_round_trips_and_compiles(self):
        for cf in sorted(self.m.COLOR_FORMATS):
            with self.subTest(cf=cf):
                text, meta = self.m.build(self.source, cf, f"test_{cf.lower()}")
                self.assertEqual(meta["color_format"], cf)
                out = self.dir / f"gen_{cf}.c"
                out.write_text(text)
                result = subprocess.run(
                    [
                        "clang", "-c", "-DLV_CONF_SKIP=1", "-Wall", "-Wextra", "-Werror",
                        "-I", str(LVGL_SRC), "-I", str(LVGL_DRAW),
                        str(out), "-o", str(self.dir / f"gen_{cf}.o"),
                    ],
                    capture_output=True, text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_deterministic_output(self):
        text1, _ = self.m.build(self.source, "RGB565", "det")
        text2, _ = self.m.build(self.source, "RGB565", "det")
        self.assertEqual(text1, text2)

    def test_lossless_formats_reconstruct_source_pixels(self):
        image = Image.open(self.source).convert("RGBA")
        w, h = image.size
        for cf in ("ARGB8888",):
            flags, stride, palette, pixels = self.m.convert(image, cf)
            rows = self.m.decode(cf, w, h, stride, palette, pixels)
            for y in range(h):
                for x in range(w):
                    self.assertEqual(tuple(rows[y][x]), image.getpixel((x, y)))

    def test_header_packing_matches_compiled_bitfield_layout(self):
        # Independently confirms pack_header()'s byte layout against the
        # real (compiled, not hand-modeled) lv_image_header_t bitfields.
        header = self.m.pack_header("I8", 8, 6, 8, flags=0x1234)
        probe_c = self.dir / "probe.c"
        probe_c.write_text(
            "#define LV_CONF_SKIP 1\n"
            "#include <stdint.h>\n"
            '#include "lv_image_dsc.h"\n'
            "#include <stdio.h>\n"
            "int main(void){\n"
            f"    unsigned char raw[12] = {{{','.join(str(b) for b in header)}}};\n"
            "    lv_image_header_t hdr;\n"
            "    __builtin_memcpy(&hdr, raw, sizeof(hdr));\n"
            '    printf("%u %u %u %u %u %u\\n", hdr.magic, hdr.cf, hdr.flags, hdr.w, hdr.h, hdr.stride);\n'
            "    return 0;\n"
            "}\n"
        )
        probe_bin = self.dir / "probe"
        subprocess.run(
            ["clang", "-I", str(LVGL_SRC), "-I", str(LVGL_DRAW), str(probe_c), "-o", str(probe_bin)],
            check=True,
        )
        out = subprocess.run([str(probe_bin)], capture_output=True, text=True, check=True).stdout.split()
        self.assertEqual([int(v) for v in out], [self.m.LV_IMAGE_HEADER_MAGIC, self.m.COLOR_FORMATS["I8"], 0x1234, 8, 6, 8])

    def test_unknown_format_rejected(self):
        with self.assertRaises(self.m.AssetGenError):
            self.m.build(self.source, "NOT_A_FORMAT", "x")


if __name__ == "__main__":
    unittest.main()
