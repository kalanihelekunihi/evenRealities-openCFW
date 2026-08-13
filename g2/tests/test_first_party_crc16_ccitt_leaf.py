"""Guard the source-replaced first-party CRC-16/CCITT overlay leaves.

The core overlay appends two source-owned CRC-16/CCITT (poly 0x1021, MSB-first)
update leaves (runtime_crc16_ccitt.c) and redirects the stock bodies at run
0x0059D350 (seed 0x0000, XMODEM) and 0x0049ACD4 (seed *ptr/0xFFFF,
CCITT-FALSE) with B.W tail-branches, gated to the linux-clang profile so the
canonical apple-clang overlay stays byte-identical. This test verifies the
profile gating and proves the leaf source computes the canonical CRC-16 values
when compiled against the firmware's own pinned tables. The full firmware
reproduction (with the live redirects) is covered by `make source verify`.

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
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
import apollo_overlay  # noqa: E402

CORE_CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
LEAF_SOURCE = ROOT / "components/apollo_main/core_overlay/runtime_crc16_ccitt.c"
MAIN_PACKAGE = ROOT / "blobs" / "official" / "g2-2.2.6.10" / "ota_s200_firmware_ota.bin"
LOAD_BASE = 0x00437FE0
MAIN_PACKAGE_SHA256 = (
    "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
)
TABLE_SHA256 = (
    "ea5f177f22d32b7e80c132b498ee4b92882484f891f43f1897075f28bb3da4d9"
)

# (function, patch name, stock run, stock size, stock body sha256, table run)
XMODEM = (
    "open_cfw_crc16_ccitt_xmodem",
    "replace_crc16_ccitt_xmodem",
    0x0059D350,
    44,
    "e6140b25efec9859630cd8a79079243322694e7d7a632ad9e6a4a82457cee999",
    0x006C0350,
)
CCITT = (
    "open_cfw_crc16_ccitt",
    "replace_crc16_ccitt",
    0x0049ACD4,
    52,
    "52c3def4c908a312e9ea66015188a2cc93d3dc23254a8fa8836d3e1bf0caaee1",
    0x006C0B50,
)


def crc16_ref(data: bytes, seed: int) -> int:
    crc = seed
    for byte in data:
        crc = ((crc << 8) ^ (POLY_TABLE[((crc >> 8) ^ byte) & 0xFF])) & 0xFFFF
    return crc


POLY_TABLE = []
for _i in range(256):
    _c = _i << 8
    for _ in range(8):
        _c = ((_c << 1) ^ 0x1021) if (_c & 0x8000) else (_c << 1)
    POLY_TABLE.append(_c & 0xFFFF)


class FirstPartyCrc16CcittLeafTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = json.loads(CORE_CONFIG.read_text(encoding="utf-8"))
        cls.image = MAIN_PACKAGE.read_bytes()
        cls.lib = cls._build_leaf()

    @classmethod
    def _build_leaf(cls):
        table_words = struct.unpack(
            "<256H", cls.image[0x006C0350 - LOAD_BASE : 0x006C0350 - LOAD_BASE + 512]
        )
        cls._raw = tempfile.TemporaryDirectory()
        raw = Path(cls._raw.name)
        decl = raw / "tables.h"
        decl.write_text(
            "#include <stdint.h>\n"
            "extern const uint16_t open_cfw_crc16_test_table[256];\n",
            encoding="utf-8",
        )
        table_c = raw / "tables.c"
        table_c.write_text(
            "#include <stdint.h>\n"
            "const uint16_t open_cfw_crc16_test_table[256] = {"
            + ",".join("0x%04xu" % w for w in table_words)
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
            "-DOPEN_CFW_CRC16_CCITT_XMODEM_TABLE=open_cfw_crc16_test_table",
            "-DOPEN_CFW_CRC16_CCITT_TABLE=open_cfw_crc16_test_table",
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
        dll = ctypes.CDLL(str(lib))
        dll.open_cfw_crc16_ccitt_xmodem.argtypes = [
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.c_int,
        ]
        dll.open_cfw_crc16_ccitt_xmodem.restype = ctypes.c_uint16
        dll.open_cfw_crc16_ccitt.argtypes = [
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint16),
        ]
        dll.open_cfw_crc16_ccitt.restype = ctypes.c_uint16
        return dll

    @classmethod
    def tearDownClass(cls) -> None:
        cls._raw.cleanup()

    def _leaf(self, function):
        return next(
            (l for l in self.config["relocated_leaves"] if l["function"] == function),
            None,
        )

    def _patch(self, name):
        return next(
            (s for s in self.config["patch_sites"] if s.get("name") == name), None
        )

    def test_leaves_and_patches_are_linux_clang_gated(self) -> None:
        for function, name, run, size, digest, _table in (XMODEM, CCITT):
            leaf, patch = self._leaf(function), self._patch(name)
            self.assertIsNotNone(leaf, f"{function} leaf missing")
            self.assertIsNotNone(patch, f"{name} patch missing")
            self.assertEqual(leaf["profiles"], ["linux-clang"])
            self.assertEqual(leaf["relocations"], [])
            self.assertEqual(patch["profiles"], ["linux-clang"])
            self.assertEqual(patch["runtime_address"], run)
            self.assertEqual(patch["expected_size"], size)
            self.assertEqual(patch["expected_sha256"], digest)
            self.assertEqual(patch["branch"], "b_w")
            self.assertEqual(patch["target_function"], function)

    def test_apple_profile_excludes_the_leaves(self) -> None:
        apple = apollo_overlay.filter_config_for_profile(self.config, "apple-clang")
        for function, name, *_ in (XMODEM, CCITT):
            self.assertFalse(
                any(l["function"] == function for l in apple["relocated_leaves"])
            )
            self.assertFalse(any(s.get("name") == name for s in apple["patch_sites"]))
            self.assertNotIn(function, apple["functions"])

    def test_linux_profile_includes_the_leaves(self) -> None:
        linux = apollo_overlay.filter_config_for_profile(self.config, "linux-clang")
        for function, name, *_ in (XMODEM, CCITT):
            self.assertTrue(
                any(l["function"] == function for l in linux["relocated_leaves"])
            )
            self.assertTrue(any(s.get("name") == name for s in linux["patch_sites"]))
            self.assertIn(function, linux["functions"])

    def test_stock_bodies_and_tables_are_pinned(self) -> None:
        self.assertEqual(hashlib.sha256(self.image).hexdigest(), MAIN_PACKAGE_SHA256)
        for _function, _name, run, size, digest, table in (XMODEM, CCITT):
            body = self.image[run - LOAD_BASE : run - LOAD_BASE + size]
            self.assertEqual(hashlib.sha256(body).hexdigest(), digest)
            tbl = self.image[table - LOAD_BASE : table - LOAD_BASE + 512]
            self.assertEqual(hashlib.sha256(tbl).hexdigest(), TABLE_SHA256)

    def _xmodem(self, data: bytes) -> int:
        buf = (ctypes.c_uint8 * (len(data) or 1)).from_buffer_copy(data or b"\x00")
        return self.lib.open_cfw_crc16_ccitt_xmodem(buf, len(data))

    def _ccitt(self, data: bytes, seed=None) -> int:
        buf = (ctypes.c_uint8 * (len(data) or 1)).from_buffer_copy(data or b"\x00")
        seed_ptr = ctypes.byref(ctypes.c_uint16(seed)) if seed is not None else None
        return self.lib.open_cfw_crc16_ccitt(buf, len(data), seed_ptr)

    def test_xmodem_leaf_computes_canonical_crc16(self) -> None:
        self.assertEqual(self._xmodem(b"123456789"), 0x31C3)
        for vector in (b"", b"\x00", b"openCFW", bytes(range(256))):
            with self.subTest(vector=vector[:16]):
                self.assertEqual(self._xmodem(vector), crc16_ref(vector, 0x0000))

    def test_ccitt_leaf_computes_canonical_crc16(self) -> None:
        # Null seed => 0xFFFF (CRC-16/CCITT-FALSE check value).
        self.assertEqual(self._ccitt(b"123456789"), 0x29B1)
        for vector in (b"", b"\x00", b"openCFW", bytes(range(256))):
            with self.subTest(vector=vector[:16]):
                self.assertEqual(self._ccitt(vector), crc16_ref(vector, 0xFFFF))

    def test_ccitt_leaf_resumes_from_seed_pointer(self) -> None:
        # A running seed reproduces a single pass over the concatenation.
        whole = b"openCFW-transport"
        split = 7
        first = self._ccitt(whole[:split])
        second = self._ccitt(whole[split:], seed=first)
        self.assertEqual(second, self._ccitt(whole))


if __name__ == "__main__":
    unittest.main()
