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
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_transfer_41623a_host.c"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_transfer_41623a.c"


class TransferCall(ctypes.Structure):
    _fields_ = [
        ("argument_0", ctypes.c_uint), ("argument_1", ctypes.c_uint),
        ("argument_2", ctypes.c_int), ("argument_3", ctypes.c_uint),
        ("result_present", ctypes.c_uint), ("schedule_present", ctypes.c_uint),
    ]


class BootloaderRuntimeTransfer41623aTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "dylib" if sys.platform == "darwin" else "so"
        cls.library = Path(cls.temporary.name) / f"boot-runtime-transfer.{suffix}"
        command = [os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        command += ["-o", str(cls.library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.lib.open_cfw_test_transfer_reset.argtypes = [ctypes.c_uint, ctypes.c_int, ctypes.c_uint]
        cls.lib.open_cfw_bootloader_runtime_transfer_41623a.argtypes = [ctypes.c_uint, ctypes.c_int]
        cls.lib.open_cfw_bootloader_runtime_transfer_41623a.restype = ctypes.c_int
        cls.lib.open_cfw_test_transfer_call_get.argtypes = [ctypes.c_uint]
        cls.lib.open_cfw_test_transfer_call_get.restype = TransferCall
        for name in ("critical_calls", "normal_calls", "pendsv_calls"):
            getattr(cls.lib, f"open_cfw_test_transfer_{name}_get").restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def counts(self) -> tuple[int, int, int]:
        return (self.lib.open_cfw_test_transfer_critical_calls_get(), self.lib.open_cfw_test_transfer_normal_calls_get(), self.lib.open_cfw_test_transfer_pendsv_calls_get())

    def test_authenticated_complete_stock_entry_and_callers(self) -> None:
        image = OFFICIAL.read_bytes(); body = image[0x623A:0x62C4]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (138, "b30ed83bcec2f4c12f8987b6d05abe0138d2a8791063900e3c7664f45e7b3058"))
        self.assertEqual(image[0x1DD0A:0x1DD0E].hex(), "e8f796fa")
        self.assertEqual(image[0x1E2B0:0x1E2B4].hex(), "e7f7c3ff")

    def test_invalid_arguments_short_circuit_before_context_query(self) -> None:
        for argument_0, argument_1 in ((0, 0), (0, -1), (1, -1)):
            self.lib.open_cfw_test_transfer_reset(1, 7, 1)
            self.assertEqual(self.lib.open_cfw_bootloader_runtime_transfer_41623a(argument_0, argument_1), -4)
            self.assertEqual(self.counts(), (0, 0, 0))

    def assert_calls(self, argument_0: int, argument_1: int, critical: bool) -> None:
        first = self.lib.open_cfw_test_transfer_call_get(0)
        second = self.lib.open_cfw_test_transfer_call_get(1)
        self.assertEqual((first.argument_0, first.argument_1, first.argument_2, first.argument_3, first.result_present, first.schedule_present), (argument_0, 0, argument_1, 1, 0, int(critical)))
        self.assertEqual((second.argument_0, second.argument_1, second.argument_2, second.argument_3, second.result_present, second.schedule_present), (argument_0, 0, 0, 0, 1, 0))

    def test_normal_context_two_call_sequence_and_result(self) -> None:
        self.lib.open_cfw_test_transfer_reset(0, -17, 1)
        self.assertEqual(self.lib.open_cfw_bootloader_runtime_transfer_41623a(0x12345678, 9), -17)
        self.assertEqual(self.counts(), (0, 2, 0))
        self.assert_calls(0x12345678, 9, False)

    def test_critical_context_pendsv_contract(self) -> None:
        for schedule, pendsv in ((0, 0), (1, 1), (0xFFFFFFFF, 1)):
            with self.subTest(schedule=schedule):
                self.lib.open_cfw_test_transfer_reset(1, 23, schedule)
                self.assertEqual(self.lib.open_cfw_bootloader_runtime_transfer_41623a(7, 0), 23)
                self.assertEqual(self.counts(), (2, 0, pendsv))
                self.assert_calls(7, 0, True)

    def test_freestanding_target_compiles(self) -> None:
        output = Path(self.temporary.name) / "runtime-transfer.o"
        subprocess.run(["/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(output)], check=True, capture_output=True, text=True)


if __name__ == "__main__": unittest.main()
