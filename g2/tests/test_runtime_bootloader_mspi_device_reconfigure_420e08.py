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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_device_reconfigure_420e08.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mspi_device_reconfigure_host.c"


class MspiDeviceReconfigureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "reconfigure.dylib" if sys.platform == "darwin" else "reconfigure.so"
        cls.library = Path(cls.temporary.name) / suffix
        subprocess.run(
            [os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2",
             "-Wall", "-Wextra", "-Werror", str(FIXTURE),
             *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
             "-o", str(cls.library)], check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.lib.open_cfw_reconfigure_fixture_config.argtypes = [ctypes.c_uint32,
                                                                 ctypes.c_uint32]
        cls.lib.open_cfw_reconfigure_fixture_value.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_reconfigure_fixture_value.restype = ctypes.c_uint32
        cls.lib.open_cfw_bootloader_mspi_device_reconfigure_420e08.argtypes = [
            ctypes.POINTER(ctypes.c_uint8)]
        cls.lib.open_cfw_bootloader_mspi_device_reconfigure_420e08.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.lib.open_cfw_reconfigure_fixture_reset()
        self.config_blob = (ctypes.c_uint8 * 24)()
        self.config_blob[8] = 16

    def config(self, field: int, value: int) -> None:
        self.lib.open_cfw_reconfigure_fixture_config(field, value)

    def value(self, field: int) -> int:
        return self.lib.open_cfw_reconfigure_fixture_value(field)

    def events(self) -> tuple[int, ...]:
        return tuple(self.value(64 + index) for index in range(self.value(32)))

    def call(self) -> int:
        return self.lib.open_cfw_bootloader_mspi_device_reconfigure_420e08(
            self.config_blob)

    def test_authenticated_stock_body_calls_callers_and_successor(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x10E08:0x10E8C]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()),
                         (132, "575026ee48ade40393f0bf4f6bcaaf005966b05d97246e9170ae8201f15ec61c"))
        self.assertEqual(blob[0x10DFA:0x10E08].hex(),
                         "000050264300ec3a4300fc374300")
        calls = {
            0x10E10: "04f06ef9", 0x10E2A: "f6f750fc",
            0x10E36: "03f0d5fe", 0x10E50: "f6f73dfc",
            0x10E5A: "04f004f9", 0x10E74: "f6f72bfc",
            0x10E84: "fef72afe", 0x10EB4: "fff7a8ff",
            0x10F14: "fff778ff",
        }
        for offset, encoded in calls.items():
            self.assertEqual(blob[offset:offset + 4].hex(), encoded)
        self.assertEqual(blob[0x11010:0x11014], (0x200270DC).to_bytes(4, "little"))
        self.assertEqual(blob[0x110A0:0x110A4], (0x200270D8).to_bytes(4, "little"))

    def test_success_orders_disable_configure_enable_and_pin_group(self) -> None:
        self.config(31, 7)
        self.config_blob[8] = 23
        self.assertEqual(self.call(), 0)
        self.assertEqual(self.events(), (1, 2, 3, 4))
        self.assertEqual((self.value(8), self.value(9), self.value(10)),
                         (0x12345678,) * 3)
        self.assertEqual(self.value(11), 1)
        self.assertEqual((self.value(12), self.value(13)), (7, 23))

    def test_each_hal_failure_is_logged_and_collapsed_to_one(self) -> None:
        cases = (
            (1, 17, (1, 5), 0x58A, 0x00432E08),
            (2, 18, (1, 2, 5), 0x592, 0x00432E2C),
            (3, 19, (1, 2, 3, 5), 0x59A, 0x00432E2C),
        )
        for field, raw, expected_events, line, format_address in cases:
            with self.subTest(field=field):
                self.setUp()
                self.config(field, raw)
                self.assertEqual(self.call(), 1)
                self.assertEqual(self.events(), expected_events)
                self.assertEqual((self.value(14), self.value(15)),
                                 (line, format_address))
                self.assertEqual(self.value(19), 0)

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        output = Path(self.temporary.name) / "reconfigure-target.o"
        subprocess.run(
            [os.environ.get("CC", "/usr/bin/clang"), "--target=arm-none-eabi",
             "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding",
             "-fno-builtin", "-Wall", "-Wextra", "-Werror", "-c",
             str(SOURCE), "-o", str(output)], check=True, capture_output=True)
        self.assertTrue(output.is_file())


if __name__ == "__main__":
    unittest.main()
