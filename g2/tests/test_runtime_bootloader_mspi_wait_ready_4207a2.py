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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_wait_ready_4207a2.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mspi_wait_ready_host.c"


class MspiWaitReadyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "fixture.dylib" if sys.platform == "darwin" else "fixture.so"
        cls.library_path = Path(cls.temporary.name) / suffix
        subprocess.run(
            [os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2",
             "-Wall", "-Wextra", "-Werror", str(FIXTURE),
             *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
             "-o", str(cls.library_path)], check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(cls.library_path))
        cls.lib.open_cfw_wait_ready_fixture_config.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32]
        cls.lib.open_cfw_wait_ready_fixture_value.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_wait_ready_fixture_value.restype = ctypes.c_uint32
        cls.lib.open_cfw_bootloader_mspi_wait_ready_4207a2.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_bootloader_mspi_wait_ready_4207a2.restype = ctypes.c_uint32
        cls.lib.open_cfw_bootloader_mspi_wait_ready_default_4207f4.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.lib.open_cfw_wait_ready_fixture_reset()

    def value(self, field: int) -> int:
        return self.lib.open_cfw_wait_ready_fixture_value(field)

    def test_authenticated_stock_bodies(self) -> None:
        stock = OFFICIAL.read_bytes()
        wait = stock[0x107A2:0x107F4]
        wrapper = stock[0x107F4:0x10800]
        self.assertEqual((len(wait), hashlib.sha256(wait).hexdigest()),
                         (82, "b5d741edee4dcb847a20256e315ae4304b07a43e02ef189da8c6a36ff0f9e809"))
        self.assertEqual((len(wrapper), hashlib.sha256(wrapper).hexdigest()),
                         (12, "bceeab3a47379a62e78b6b07417c52a86da437468ee68ddb43e56468065e7329"))

    def test_fast_phase_success_and_delay_order(self) -> None:
        self.lib.open_cfw_wait_ready_fixture_config(1, 0)
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_wait_ready_4207a2(5), 0)
        self.assertEqual(tuple(self.value(i) for i in range(5)),
                         (1, 0, 0, 0, 0))

        self.lib.open_cfw_wait_ready_fixture_reset()
        self.lib.open_cfw_wait_ready_fixture_config(200, 0)
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_wait_ready_4207a2(5), 0)
        self.assertEqual((self.value(0), self.value(2)), (200, 199))

    def test_slow_phase_delay_notify_and_timeout_contract(self) -> None:
        self.lib.open_cfw_wait_ready_fixture_config(201, 0)
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_wait_ready_4207a2(1), 0)
        self.assertEqual(tuple(self.value(i) for i in range(5)),
                         (201, 1, 200, 1, 0))

        self.lib.open_cfw_wait_ready_fixture_reset()
        self.lib.open_cfw_wait_ready_fixture_config(201, 2)
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_wait_ready_4207a2(1), 0)
        self.assertEqual(tuple(self.value(i) for i in range(6)),
                         (201, 1, 200, 0, 1, 1))

        self.lib.open_cfw_wait_ready_fixture_reset()
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_wait_ready_4207a2(0), 1)
        self.assertEqual(tuple(self.value(i) for i in range(5)),
                         (200, 0, 200, 0, 0))

    def test_default_wrapper_supplies_500_slow_polls(self) -> None:
        self.lib.open_cfw_wait_ready_fixture_config(0, 2)
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_wait_ready_default_4207f4(), 1)
        self.assertEqual(tuple(self.value(i) for i in range(6)),
                         (700, 500, 200, 0, 500, 1))

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        output = Path(self.temporary.name) / "target.o"
        subprocess.run(
            [os.environ.get("CC", "/usr/bin/clang"), "--target=arm-none-eabi",
             "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding",
             "-fno-builtin", "-Wall", "-Wextra", "-Werror", "-c",
             str(SOURCE), "-o", str(output)], check=True, capture_output=True)
        self.assertTrue(output.is_file())


if __name__ == "__main__":
    unittest.main()
