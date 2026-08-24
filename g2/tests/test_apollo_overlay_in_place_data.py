#!/usr/bin/env python3
"""Unit contracts for C-compiled scattered in-place data replacement."""

from __future__ import annotations

import hashlib
import importlib.util
import struct
import tempfile
import unittest
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/apollo_overlay.py"


def load_module():
    spec = importlib.util.spec_from_file_location("apollo_overlay_data_test", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ApolloOverlayInPlaceDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()

    def test_compiled_const_object_is_pinned_and_installed(self) -> None:
        build_root = ROOT / "build"
        build_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=build_root) as directory:
            temporary = Path(directory)
            source = temporary / "data.c"
            source.write_text(
                '__attribute__((used,section(".rodata.test_blob")))\n'
                "const unsigned char test_blob[4] = {1, 2, 3, 4};\n",
                encoding="utf-8",
            )
            source_bytes = source.read_bytes()
            old = b"WXYZ"
            group = {
                "symbol": "test_blob",
                "section": ".rodata.test_blob",
                "source": {
                    "path": source.relative_to(ROOT).as_posix(),
                    "size": len(source_bytes),
                    "sha256": hashlib.sha256(source_bytes).hexdigest(),
                },
                "toolchain": {
                    "target": "thumbv7em-none-eabi",
                    "reviewed_version_prefix": "Apple clang version 21.0.0",
                    "flags": [
                        "-mthumb",
                        "-mcpu=cortex-m55",
                        "-ffreestanding",
                        "-fdata-sections",
                        "-Wall",
                        "-Wextra",
                        "-Werror",
                    ],
                },
                "expected": {
                    "size": 4,
                    "sha256": hashlib.sha256(bytes((1, 2, 3, 4))).hexdigest(),
                    "alignment": 1,
                },
                "placements": [
                    {
                        "name": "test_data",
                        "runtime_address": 0x1020,
                        "source_offset": 0,
                        "size": 4,
                        "stock_sha256": hashlib.sha256(old).hexdigest(),
                    }
                ],
            }
            payload, report = self.module.compile_in_place_data_group(
                root=ROOT,
                clang="/usr/bin/clang",
                group_config=group,
                object_path=temporary / "data.o",
            )
            self.assertEqual(payload, bytes((1, 2, 3, 4)))
            self.assertEqual(report["extraction"]["relocation_count"], 0)

            base = bytearray(128)
            struct.pack_into("<I", base, 0, len(base))
            struct.pack_into("<I", base, 0x10, 0xCB)
            struct.pack_into("<I", base, 0x14, 0x1000)
            base[0x40:0x44] = old
            struct.pack_into("<I", base, 4, zlib.crc32(base[8:]) & 0xFFFFFFFF)
            component, details = self.module.patch_component(
                base=bytes(base),
                overlay=b"\0\0",
                functions={},
                config={
                    "run_base": 0x1000,
                    "preamble_bytes": 32,
                    "alignment": 4,
                    "patch_sites": [],
                },
                in_place_data=[(payload, report)],
            )
            self.assertEqual(component[0x40:0x44], payload)
            self.assertEqual(len(details["patched_in_place_data"]), 1)

if __name__ == "__main__":
    unittest.main()
