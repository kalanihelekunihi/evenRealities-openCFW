"""Guard the source-replaced TinyFrame TF_CksumAdd overlay leaf.

The core overlay appends a source-owned CRC-16/ARC leaf
(runtime_tinyframe_cksum_add.c) and redirects the stock TF_CksumAdd at
0x00491730 to it, gated to the linux-clang profile so the canonical apple-clang
overlay stays byte-identical. This test verifies the profile gating and the
leaf's behavioural equivalence to the recovered checksum. The full firmware
reproduction (including the live B.W redirect) is covered end-to-end by
tests/test_toolchain_profiles.py's source-package rebuild.
"""

from __future__ import annotations

import ctypes
import os
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import apollo_overlay  # noqa: E402

CORE_CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
LEAF_SOURCE = ROOT / "components/apollo_main/core_overlay/runtime_tinyframe_cksum_add.c"
FUNCTION = "open_cfw_tinyframe_cksum_add"
STOCK_TF_CKSUM_ADD = 0x00491730


def crc16_arc_step(crc: int, byte: int) -> int:
    crc ^= byte
    for _ in range(8):
        crc = (crc >> 1) ^ 0xA001 if (crc & 1) else (crc >> 1)
    return crc & 0xFFFF


class TinyFrameCksumLeafIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = json.loads(CORE_CONFIG.read_text(encoding="utf-8"))

    def _leaf(self):
        return next(
            (
                leaf
                for leaf in self.config["relocated_leaves"]
                if leaf["function"] == FUNCTION
            ),
            None,
        )

    def _patch(self):
        return next(
            (
                site
                for site in self.config["patch_sites"]
                if site.get("name") == "replace_tinyframe_cksum_add"
            ),
            None,
        )

    def test_leaf_and_patch_are_linux_clang_gated(self) -> None:
        leaf, patch = self._leaf(), self._patch()
        self.assertIsNotNone(leaf, "tinyframe cksum leaf missing")
        self.assertIsNotNone(patch, "tinyframe cksum patch site missing")
        self.assertEqual(leaf["profiles"], ["linux-clang"])
        self.assertEqual(patch["profiles"], ["linux-clang"])
        self.assertEqual(patch["runtime_address"], STOCK_TF_CKSUM_ADD)
        self.assertEqual(patch["branch"], "b_w")
        self.assertEqual(patch["target_function"], FUNCTION)
        # Its linux-clang pin is recorded; relocations are empty (self-contained).
        pin = leaf["toolchain_profiles"]["linux-clang"]["expected"]
        self.assertGreater(pin["size"], 0)

    def test_apple_profile_excludes_the_leaf(self) -> None:
        apple = apollo_overlay.filter_config_for_profile(self.config, "apple-clang")
        self.assertFalse(
            any(l["function"] == FUNCTION for l in apple["relocated_leaves"])
        )
        self.assertFalse(
            any(s.get("name") == "replace_tinyframe_cksum_add" for s in apple["patch_sites"])
        )
        self.assertNotIn(FUNCTION, apple["functions"])

    def test_linux_profile_includes_the_leaf(self) -> None:
        linux = apollo_overlay.filter_config_for_profile(self.config, "linux-clang")
        self.assertTrue(
            any(l["function"] == FUNCTION for l in linux["relocated_leaves"])
        )
        self.assertTrue(
            any(s.get("name") == "replace_tinyframe_cksum_add" for s in linux["patch_sites"])
        )
        self.assertIn(FUNCTION, linux["functions"])

    def test_leaf_source_computes_crc16_arc(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            lib = Path(raw) / (
                "leaf.dylib" if sys.platform == "darwin" else "leaf.so"
            )
            clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
            command = [clang, "-O2", "-Wall", "-Wextra", str(LEAF_SOURCE)]
            command.extend(
                ["-dynamiclib", "-o", str(lib)]
                if sys.platform == "darwin"
                else ["-shared", "-fPIC", "-o", str(lib)]
            )
            subprocess.run(command, check=True, capture_output=True, text=True)
            fn = ctypes.CDLL(str(lib)).open_cfw_tinyframe_cksum_add
            fn.argtypes = [ctypes.c_uint16, ctypes.c_uint8]
            fn.restype = ctypes.c_uint16
            for crc in (0x0000, 0x1234, 0xFFFF, 0xABCD, 0x00FF):
                for byte in range(256):
                    self.assertEqual(fn(crc, byte), crc16_arc_step(crc, byte))


if __name__ == "__main__":
    unittest.main()
