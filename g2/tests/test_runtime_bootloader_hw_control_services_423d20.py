from __future__ import annotations

import ctypes
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_control_services_423d20.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_hw_control_services_host.c"


class BootloaderHwControlServicesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        output = Path(cls.tmp.name) / ("hwcs.dylib" if sys.platform == "darwin" else "hwcs.so")
        subprocess.run(
            [os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE), *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]), "-o", str(output)],
            check=True, capture_output=True,
        )
        cls.lib = ctypes.CDLL(str(output))
        cls.reset = cls.lib.open_cfw_hwcs_host_reset
        cls.global_service = cls.lib.open_cfw_bootloader_hw_global_service_423d20
        cls.initialize = cls.lib.open_cfw_bootloader_hw_control_initialize_423d58
        cls.query = cls.lib.open_cfw_bootloader_hw_control_query_423d7a
        cls.test = cls.lib.open_cfw_bootloader_hw_control_test_423da0
        cls.test_zero = cls.lib.open_cfw_bootloader_hw_control_test_zero_423dc4
        cls.critical = cls.lib.open_cfw_bootloader_hw_control_critical_423dd0
        for function in (cls.global_service, cls.initialize, cls.query, cls.test, cls.test_zero, cls.critical):
            function.restype = ctypes.c_uint32
        cls.test.argtypes = [ctypes.c_uint32]
        cls.u32 = staticmethod(lambda name: ctypes.c_uint32.in_dll(cls.lib, name))
        cls.u8 = staticmethod(lambda name: ctypes.c_uint8.in_dll(cls.lib, name))
        cls.results = (ctypes.c_uint32 * 8).in_dll(cls.lib, "open_cfw_hwcs_host_register_results")
        cls.calls = ((ctypes.c_uint32 * 4) * 8).in_dll(cls.lib, "open_cfw_hwcs_host_register_calls")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def setUp(self) -> None:
        self.reset()

    def set_results(self, *values: int) -> None:
        self.u32("open_cfw_hwcs_host_register_result_count").value = len(values)
        for index, value in enumerate(values):
            self.results[index] = value

    def test_authenticated_bodies_gaps_and_successor(self) -> None:
        blob = OFFICIAL.read_bytes()
        spans = (
            (0x13D20, 0x13D58, "e4c5106b0aba4050c24d6e8afc548516c92c295bec52ed0397c029a4bad40850"),
            (0x13D58, 0x13D7A, "147c53dc0c6246332d50080fbb99095103cdf73f3c89014027bdaa261ab30e68"),
            (0x13D7A, 0x13D9A, "43b8c7f2aeaba4ddf52365d8bb3eefb7391bdd57169fe64c618552989a536824"),
            (0x13D9A, 0x13DA0, "7cf4979cad48b6ce2b499300c3c3b8ed96387be1abbadcd932aba625b082f975"),
            (0x13DA0, 0x13DC4, "c5f33fc0af91c57d50e522764587e3d6aa5a7bd031187567023c6d825b333c36"),
            (0x13DC4, 0x13DCE, "721f0a9d955a564fa40b09a08980d999ef5cddfb5c55598a28093affa4ef86a6"),
            (0x13DCE, 0x13DD0, "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7"),
            (0x13DD0, 0x13E0C, "946b697419fa8bb2a0eb8988766eaacf053308752bd1ea57f7bbfc353e744002"),
            (0x13E0C, 0x13E14, "eb9eccfa0c7b87835a778c7ab67a2f4201b14d38a0d6b02bbb85a110f172d963"),
        )
        for start, end, expected in spans:
            self.assertEqual(hashlib.sha256(blob[start:end]).hexdigest(), expected)

    def test_query_and_indexed_test_bind_exact_register_arguments(self) -> None:
        self.set_results(0, 9)
        self.assertEqual(self.query(), 1)
        self.assertEqual(self.test(7), 0)
        self.assertEqual(tuple(self.calls[0]), (1000, 0xE0000E80, 0x00800000, 0))
        self.assertEqual(tuple(self.calls[1]), (1000, 0xE000001C, 3, 1))

    def test_initialize_success_and_failures(self) -> None:
        self.set_results(0, 0)
        self.assertEqual(self.initialize(), 0)
        self.assertEqual(self.u32("open_cfw_hwcs_host_delay_value").value, 500)
        self.assertEqual(self.u32("open_cfw_hwcs_host_register_result_index").value, 2)

        self.reset()
        self.set_results(5)
        self.assertEqual(self.initialize(), 4)
        self.assertEqual(self.u32("open_cfw_hwcs_host_register_result_index").value, 1)
        self.assertEqual(self.u32("open_cfw_hwcs_host_delay_value").value, 0)

        self.reset()
        self.set_results(0, 5)
        self.assertEqual(self.initialize(), 4)
        self.assertEqual(self.u32("open_cfw_hwcs_host_register_result_index").value, 2)

    def test_global_service_clears_control_bits_and_routes_status(self) -> None:
        self.u32("open_cfw_hwcs_host_control_register").value = 0xFFFFFFFF
        self.set_results(0, 0, 7)
        self.assertEqual(self.global_service(), 7)
        self.assertEqual(self.u32("open_cfw_hwcs_host_control_register").value, 0xFFFFFFEE)
        self.assertEqual(self.u32("open_cfw_hwcs_host_debug_calls").value, 0)

        self.reset()
        self.set_results(0, 0, 0)
        self.u32("open_cfw_hwcs_host_debug_result").value = 3
        self.assertEqual(self.global_service(), 0)
        self.assertEqual(self.u32("open_cfw_hwcs_host_debug_calls").value, 1)

    def test_critical_countdown_latch_and_primask_restore(self) -> None:
        self.u32("open_cfw_hwcs_host_primask_token").value = 0xA5
        self.u8("open_cfw_hwcs_host_countdown").value = 2
        self.u8("open_cfw_hwcs_host_latch").value = 1
        self.assertEqual(self.critical(), 3)
        self.assertEqual(self.u8("open_cfw_hwcs_host_countdown").value, 1)
        self.assertEqual(self.u8("open_cfw_hwcs_host_latch").value, 1)
        self.assertEqual(self.u32("open_cfw_hwcs_host_debug_calls").value, 0)
        self.assertEqual(self.u32("open_cfw_hwcs_host_restored_token").value, 0xA5)

        self.u32("open_cfw_hwcs_host_debug_result").value = 3
        self.assertEqual(self.critical(), 0)
        self.assertEqual(self.u8("open_cfw_hwcs_host_countdown").value, 0)
        self.assertEqual(self.u8("open_cfw_hwcs_host_latch").value, 0)
        self.assertEqual(self.u32("open_cfw_hwcs_host_debug_calls").value, 1)

    def test_source_cross_compiles(self) -> None:
        for compiler in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if Path(compiler).exists():
                subprocess.run(
                    [compiler, "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror", "-fno-ident", "-c", str(SOURCE), "-o", str(Path(self.tmp.name) / (Path(compiler).parent.name + "-hwcs.o"))],
                    check=True, capture_output=True,
                )


if __name__ == "__main__":
    unittest.main()
