"""Guard the source-replaced first-party transport CRC-32 overlay leaf.

The core overlay appends a source-owned standard reflected CRC-32 finaliser
(runtime_transport_crc32.c) and redirects the stock update at run 0x0058FCF0 to
it with a B.W tail-branch, gated to the linux-clang profile so the canonical
apple-clang overlay stays byte-identical. This test verifies the profile gating
and the leaf's behavioural equivalence to the canonical CRC-32 when compiled
against the firmware's own pinned table. The full firmware reproduction
(including the live redirect) is covered end-to-end by `make source verify`.

Host equivalence only; no target overlay, signing, flashing, or hardware.
"""

from __future__ import annotations

import ctypes
import hashlib
import json
import os
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import apollo_overlay  # noqa: E402

CORE_CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
LEAF_SOURCE = ROOT / "components/apollo_main/core_overlay/runtime_transport_crc32.c"
MAIN_PACKAGE = ROOT / "blobs" / "official" / "g2-2.2.6.10" / "ota_s200_firmware_ota.bin"
FUNCTION = "open_cfw_transport_crc32_update"
PATCH_NAME = "replace_transport_crc32_update"
STOCK_ENTRY = 0x0058FCF0
STOCK_BODY_SIZE = 40
STOCK_BODY_SHA256 = (
    "232e226bd1ece2ee0d8a14abc3461651743ef4c987b46406fc2995154ed59a29"
)

LOAD_BASE = 0x00437FE0
CRC_TABLE_RUN = 0x006987A8
CRC_TABLE_FILE = CRC_TABLE_RUN - LOAD_BASE
CRC_TABLE_BYTES = 1024
FIRMWARE_TABLE_SHA256 = (
    "12f3e0576d447eb37b36d82ba0c1c5481b8f0d12fdc70347ce4a076b229d4c86"
)
MAIN_PACKAGE_SHA256 = (
    "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
)


def crc32_reference(data: bytes) -> int:
    crc = 0xFFFFFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0xEDB88320 if (crc & 1) else (crc >> 1)
    return crc ^ 0xFFFFFFFF


class FirstPartyTransportCrc32LeafTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = json.loads(CORE_CONFIG.read_text(encoding="utf-8"))
        cls.image = MAIN_PACKAGE.read_bytes()

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
                if site.get("name") == PATCH_NAME
            ),
            None,
        )

    def test_leaf_and_patch_are_linux_clang_gated(self) -> None:
        leaf, patch = self._leaf(), self._patch()
        self.assertIsNotNone(leaf, "transport crc32 leaf missing")
        self.assertIsNotNone(patch, "transport crc32 patch site missing")
        self.assertEqual(leaf["profiles"], ["linux-clang"])
        self.assertEqual(patch["profiles"], ["linux-clang"])
        self.assertEqual(patch["runtime_address"], STOCK_ENTRY)
        self.assertEqual(patch["expected_size"], STOCK_BODY_SIZE)
        self.assertEqual(patch["expected_sha256"], STOCK_BODY_SHA256)
        self.assertEqual(patch["branch"], "b_w")
        self.assertEqual(patch["target_function"], FUNCTION)
        pin = leaf["toolchain_profiles"]["linux-clang"]["expected"]
        self.assertGreater(pin["size"], 0)
        self.assertEqual(leaf["relocations"], [])

    def test_apple_profile_excludes_the_leaf(self) -> None:
        apple = apollo_overlay.filter_config_for_profile(self.config, "apple-clang")
        self.assertFalse(
            any(l["function"] == FUNCTION for l in apple["relocated_leaves"])
        )
        self.assertFalse(
            any(s.get("name") == PATCH_NAME for s in apple["patch_sites"])
        )
        self.assertNotIn(FUNCTION, apple["functions"])

    def test_linux_profile_includes_the_leaf(self) -> None:
        linux = apollo_overlay.filter_config_for_profile(self.config, "linux-clang")
        self.assertTrue(
            any(l["function"] == FUNCTION for l in linux["relocated_leaves"])
        )
        self.assertTrue(
            any(s.get("name") == PATCH_NAME for s in linux["patch_sites"])
        )
        self.assertIn(FUNCTION, linux["functions"])

    def test_stock_body_and_table_are_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(self.image).hexdigest(), MAIN_PACKAGE_SHA256
        )
        body = self.image[
            STOCK_ENTRY - LOAD_BASE : STOCK_ENTRY - LOAD_BASE + STOCK_BODY_SIZE
        ]
        self.assertEqual(hashlib.sha256(body).hexdigest(), STOCK_BODY_SHA256)
        table = self.image[CRC_TABLE_FILE : CRC_TABLE_FILE + CRC_TABLE_BYTES]
        self.assertEqual(hashlib.sha256(table).hexdigest(), FIRMWARE_TABLE_SHA256)

    def test_leaf_source_computes_canonical_crc32(self) -> None:
        """Compile the exact target leaf source, but point its table at the
        firmware's own pinned table, and prove it computes the canonical
        reflected CRC-32 the stock body did."""
        table_words = struct.unpack(
            "<256I", self.image[CRC_TABLE_FILE : CRC_TABLE_FILE + CRC_TABLE_BYTES]
        )
        with tempfile.TemporaryDirectory() as raw:
            raw = Path(raw)
            decl = raw / "table_decl.h"
            decl.write_text(
                "#include <stdint.h>\n"
                "extern const uint32_t open_cfw_transport_crc32_test_table[256];\n",
                encoding="utf-8",
            )
            table_c = raw / "table.c"
            table_c.write_text(
                "#include <stdint.h>\n"
                "const uint32_t open_cfw_transport_crc32_test_table[256] = {"
                + ",".join("0x%08xu" % w for w in table_words)
                + "};\n",
                encoding="utf-8",
            )
            lib = raw / ("leaf.dylib" if sys.platform == "darwin" else "leaf.so")
            clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
            command = [
                clang,
                "-O2",
                "-Wall",
                "-Wextra",
                "-Werror",
                "-DOPEN_CFW_TRANSPORT_CRC32_TABLE=open_cfw_transport_crc32_test_table",
                "-include",
                str(decl),
                str(LEAF_SOURCE),
                str(table_c),
            ]
            command.extend(
                ["-dynamiclib", "-o", str(lib)]
                if sys.platform == "darwin"
                else ["-shared", "-fPIC", "-o", str(lib)]
            )
            subprocess.run(command, check=True, capture_output=True, text=True)
            fn = ctypes.CDLL(str(lib)).open_cfw_transport_crc32_update
            fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint8)]
            fn.restype = ctypes.c_uint32

            def crc(data: bytes) -> int:
                buf = (ctypes.c_uint8 * (len(data) or 1)).from_buffer_copy(
                    data or b"\x00"
                )
                # The stock ABI: caller seeds 0xFFFFFFFF; length then data.
                return fn(0xFFFFFFFF, len(data), buf)

            self.assertEqual(crc(b"123456789"), 0xCBF43926)
            for vector in (b"", b"\x00", b"openCFW", bytes(range(256))):
                with self.subTest(vector=vector[:16]):
                    self.assertEqual(crc(vector), crc32_reference(vector))


if __name__ == "__main__":
    unittest.main()
