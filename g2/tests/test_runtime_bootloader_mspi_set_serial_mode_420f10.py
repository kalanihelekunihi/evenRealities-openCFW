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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_set_serial_mode_420f10.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mspi_set_serial_mode_host.c"


class MspiSetSerialModeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "serial-mode.dylib" if sys.platform == "darwin" else "serial-mode.so"
        cls.library = Path(cls.temporary.name) / suffix
        subprocess.run(
            [os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2",
             "-Wall", "-Wextra", "-Werror", str(FIXTURE),
             *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
             "-o", str(cls.library)], check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.lib.open_cfw_serial_fixture_config.argtypes = [ctypes.c_uint32,
                                                            ctypes.c_uint32]
        cls.lib.open_cfw_serial_fixture_value.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_serial_fixture_value.restype = ctypes.c_uint32
        cls.lib.open_cfw_bootloader_mspi_set_serial_mode_420f10.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.lib.open_cfw_serial_fixture_reset()

    def value(self, field: int) -> int:
        return self.lib.open_cfw_serial_fixture_value(field)

    def events(self) -> tuple[int, ...]:
        return tuple(self.value(64 + i) for i in range(self.value(32)))

    def test_authenticated_stock_body_callers_and_successor_gap(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x10F10:0x10F6A]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()),
                         (90, "b73005fad7b0cae8e2f2273bae21ab2877963d2d14534b5afc2918c515c26a13"))
        self.assertEqual(blob[0x10F6A:0x10F70].hex(), "000073657400")
        calls = {0x104B6: "00f02bfd", 0x104BE: "00f027fd",
                 0x10A4C: "00f060fa", 0x10B58: "00f0daf9"}
        for offset, encoded in calls.items():
            self.assertEqual(blob[offset:offset + 4].hex(), encoded)
        self.assertEqual(blob[0x110B4:0x110B8],
                         (0x2000020C).to_bytes(4, "little"))

    def test_success_uses_template_disables_xip_and_controls_zero_mode(self) -> None:
        self.lib.open_cfw_bootloader_mspi_set_serial_mode_420f10()
        self.assertEqual(self.events(), (1, 2, 3))
        self.assertEqual((self.value(3), self.value(4), self.value(5)),
                         (1, 8, 0))
        self.assertEqual((self.value(6), self.value(7), self.value(8),
                          self.value(9)), (0, 0x12345678, 0x18, 0))

    def test_reconfigure_failure_logs_and_short_circuits(self) -> None:
        self.lib.open_cfw_serial_fixture_config(1, 7)
        self.lib.open_cfw_bootloader_mspi_set_serial_mode_420f10()
        self.assertEqual(self.events(), (1, 4))
        self.assertEqual((self.value(10), self.value(11)),
                         (0x5C0, 0x00432E74))

    def test_control_failure_logs_after_xip(self) -> None:
        self.lib.open_cfw_serial_fixture_config(2, 9)
        self.lib.open_cfw_bootloader_mspi_set_serial_mode_420f10()
        self.assertEqual(self.events(), (1, 2, 3, 4))
        self.assertEqual((self.value(10), self.value(11)),
                         (0x5C7, 0x00433260))

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        output = Path(self.temporary.name) / "serial-mode-target.o"
        subprocess.run(
            [os.environ.get("CC", "/usr/bin/clang"), "--target=arm-none-eabi",
             "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding",
             "-fno-builtin", "-Wall", "-Wextra", "-Werror", "-c",
             str(SOURCE), "-o", str(output)], check=True, capture_output=True)
        self.assertTrue(output.is_file())


if __name__ == "__main__":
    unittest.main()
