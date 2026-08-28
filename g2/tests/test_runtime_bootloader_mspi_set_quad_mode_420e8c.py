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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_set_quad_mode_420e8c.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mspi_set_quad_mode_host.c"


class MspiSetQuadModeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "quad-mode.dylib" if sys.platform == "darwin" else "quad-mode.so"
        cls.library = Path(cls.temporary.name) / suffix
        subprocess.run(
            [os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2",
             "-Wall", "-Wextra", "-Werror", str(FIXTURE),
             *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
             "-o", str(cls.library)], check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.lib.open_cfw_quad_fixture_config.argtypes = [ctypes.c_uint32,
                                                          ctypes.c_uint32]
        cls.lib.open_cfw_quad_fixture_value.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_quad_fixture_value.restype = ctypes.c_uint32
        cls.lib.open_cfw_bootloader_mspi_set_quad_mode_420e8c.restype = None

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

    def call(self) -> None:
        self.lib.open_cfw_bootloader_mspi_set_quad_mode_420e8c()

    def test_authenticated_stock_body_calls_and_successor_pool(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x10E8C:0x10F0C]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()),
                         (128, "d3eeee3b649bcab6d485d604bb94fe739a753064b80b6918a4d5a9db616b86ef"))
        self.assertEqual(blob[0x10F0C:0x10F10].hex(), "40420f00")
        calls = {
            0x10ACE: "00f0ddf9", 0x10C08: "00f040f9", 0x10F9C: "fff776ff",
            0x10E96: "f4f709fc", 0x10EB4: "fff7a8ff",
            0x10ECE: "f6f7fefb", 0x10ED6: "fff72df8",
            0x10EE8: "04f06af9", 0x10F02: "f6f7e4fb",
        }
        for offset, encoded in calls.items():
            self.assertEqual(blob[offset:offset + 4].hex(), encoded)
        self.assertEqual(blob[0x110A4:0x110A8],
                         (0x20000224).to_bytes(4, "little"))

    def test_success_clones_mutates_reconfigures_and_enables_quad_xip(self) -> None:
        self.call()
        self.assertEqual(self.events(), (1, 2, 3, 4))
        self.assertEqual(self.value(3), 24)
        expected = bytes.fromhex(
            "080300006c00020010000014000101010000000000000000")
        self.assertEqual(bytes(self.value(100 + index) for index in range(24)),
                         expected)
        self.assertEqual((self.value(4), self.value(5), self.value(6),
                          self.value(7)), (1, 0x12345678, 0x18, 0x10))
        self.assertEqual(self.value(10), 0)

    def test_reconfigure_failure_logs_and_short_circuits_xip_and_control(self) -> None:
        self.config(1, 7)
        self.call()
        self.assertEqual(self.events(), (1, 2, 5))
        self.assertEqual((self.value(8), self.value(9)),
                         (0x5AE, 0x00432E50))
        self.assertEqual((self.value(4), self.value(6)), (0, 0))

    def test_control_failure_logs_after_xip_and_preserves_void_completion(self) -> None:
        self.config(2, 9)
        self.call()
        self.assertEqual(self.events(), (1, 2, 3, 4, 5))
        self.assertEqual((self.value(8), self.value(9), self.value(10)),
                         (0x5B5, 0x00433240, 1))

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        output = Path(self.temporary.name) / "quad-mode-target.o"
        subprocess.run(
            [os.environ.get("CC", "/usr/bin/clang"), "--target=arm-none-eabi",
             "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding",
             "-fno-builtin", "-Wall", "-Wextra", "-Werror", "-c",
             str(SOURCE), "-o", str(output)], check=True, capture_output=True)
        self.assertTrue(output.is_file())


if __name__ == "__main__":
    unittest.main()
