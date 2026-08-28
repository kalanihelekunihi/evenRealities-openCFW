from __future__ import annotations

import ctypes
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_quad_enable_420c5c.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mspi_quad_enable_host.c"


class MspiQuadEnableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "quad.dylib" if sys.platform == "darwin" else "quad.so"
        cls.library = Path(cls.temporary.name) / suffix
        subprocess.run(
            [os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2",
             "-Wall", "-Wextra", "-Werror", str(FIXTURE),
             *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
             "-o", str(cls.library)], check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.lib.open_cfw_quad_fixture_config.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.lib.open_cfw_quad_fixture_value.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_quad_fixture_value.restype = ctypes.c_uint32
        cls.lib.open_cfw_bootloader_mspi_quad_enable_420c5c.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_bootloader_mspi_quad_enable_420c5c.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.lib.open_cfw_quad_fixture_reset()

    def config(self, field: int, value: int) -> None:
        self.lib.open_cfw_quad_fixture_config(field, value)

    def value(self, field: int) -> int:
        return self.lib.open_cfw_quad_fixture_value(field)

    def events(self) -> tuple[int, ...]:
        return tuple(self.value(64 + index) for index in range(self.value(32)))

    def test_authenticated_stock_body_pool_calls_and_caller(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x10C5C:0x10DFA]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()),
                         (414, "ba6c3ac9d495b2fa232fbf70349bd0f4c588eb1699c69c92e5079fc6b03ec463"))
        pool = blob[0x10DFA:0x10E08]
        self.assertEqual((len(pool), hashlib.sha256(pool).hexdigest()),
                         (14, "8b41f058c64229c00d3a505f11715874ac3dcada1086d696f408e9365a2b3b6f"))
        calls = {
            0x10C70: "fff7c0fd", 0x10C80: "fff7b8fc",
            0x10CFA: "fff743fe", 0x10D5C: "fff79ffc",
            0x10D82: "fff737fd", 0x10D92: "fff72ffc",
        }
        for offset, encoded in calls.items():
            self.assertEqual(blob[offset:offset + 4].hex(), encoded)
        self.assertEqual(blob[0x10518:0x1051C].hex(), "00f0a0fb")

    def test_null_handle_short_circuits(self) -> None:
        self.config(0, 0)
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_quad_enable_420c5c(1), 2)
        self.assertEqual(self.events(), ())

    def test_already_desired_requires_clear_protection_bits(self) -> None:
        self.config(1, 99)
        self.config(2, 0x40)
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_quad_enable_420c5c(1), 0)
        self.assertEqual(self.events(), (1, 2, 5))
        self.assertEqual((self.value(13), self.value(14)), (0x52A, 0x00432D9C))
        self.assertEqual((self.value(8), self.value(9)), (0x05, 1))

        self.setUp()
        self.config(2, 0x00)
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_quad_enable_420c5c(0), 0)
        self.assertEqual(self.events(), (1, 2, 5))

    def test_rewrite_sets_or_clears_qe_and_protection_bits(self) -> None:
        for requested, initial, verified, expected in (
            (1, 0x3C, 0x40, 0x40),
            (0, 0x7C, 0x00, 0x00),
        ):
            with self.subTest(requested=requested):
                self.setUp()
                self.config(1, 17)
                self.config(2, initial)
                self.config(3, verified)
                self.assertEqual(
                    self.lib.open_cfw_bootloader_mspi_quad_enable_420c5c(requested), 0)
                self.assertEqual(self.events(), (1, 2, 3, 4, 1, 2))
                self.assertEqual((self.value(8), self.value(9)), (0x05, 1))
                self.assertEqual((self.value(10), self.value(11), self.value(12)),
                                 (0x01, 1, expected))
                self.assertEqual((self.value(16), self.value(17)), (2, 2))

    def test_raw_failures_and_verification_mismatch(self) -> None:
        cases = (
            (4, 7, (1, 2, 5), 0x521, 0x00432D78),
            (5, 8, (1, 2, 3, 5), 0x531, 0x00432A9C),
            (6, 9, (1, 2, 3, 4, 5), 0x540, 0x00432DC0),
            (7, 10, (1, 2, 3, 4, 1, 2, 5), 0x54A, 0x0043355C),
        )
        for field, raw, expected_events, line, format_address in cases:
            with self.subTest(field=field):
                self.setUp()
                self.config(2, 0)
                self.config(3, 0x40)
                self.config(field, raw)
                self.assertEqual(
                    self.lib.open_cfw_bootloader_mspi_quad_enable_420c5c(1), raw)
                self.assertEqual(self.events(), expected_events)
                self.assertEqual((self.value(13), self.value(14)),
                                 (line, format_address))

        self.setUp()
        self.config(2, 0)
        self.config(3, 0)
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_quad_enable_420c5c(1), 1)
        self.assertEqual(self.events(), (1, 2, 3, 4, 1, 2, 5))
        self.assertEqual((self.value(13), self.value(14), self.value(15)),
                         (0x550, 0x0043385C, 1))

    def test_non_boolean_request_preserves_stock_mismatch_quirk(self) -> None:
        self.config(2, 0)
        self.config(3, 0x40)
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_quad_enable_420c5c(2), 1)
        self.assertEqual(self.value(12), 0x40)
        self.assertEqual(self.value(15), 1)

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        output = Path(self.temporary.name) / "quad-target.o"
        subprocess.run(
            [os.environ.get("CC", "/usr/bin/clang"), "--target=arm-none-eabi",
             "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding",
             "-fno-builtin", "-Wall", "-Wextra", "-Werror", "-c",
             str(SOURCE), "-o", str(output)], check=True, capture_output=True)
        self.assertTrue(output.is_file())


if __name__ == "__main__":
    unittest.main()
