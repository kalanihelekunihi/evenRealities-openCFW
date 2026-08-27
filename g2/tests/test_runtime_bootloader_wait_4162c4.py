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
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_wait_4162c4_host.c"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_wait_4162c4.c"


class WaitCall(ctypes.Structure):
    _fields_ = [("clear_mask", ctypes.c_uint), ("timeout", ctypes.c_uint)]


class BootloaderRuntimeWait4162c4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "dylib" if sys.platform == "darwin" else "so"
        cls.library = Path(cls.temporary.name) / f"boot-runtime-wait.{suffix}"
        command = [os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        command += ["-o", str(cls.library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.lib.open_cfw_test_wait_reset.argtypes = [ctypes.c_uint]
        cls.lib.open_cfw_test_wait_tick_add.argtypes = [ctypes.c_uint]
        cls.lib.open_cfw_test_wait_response_add.argtypes = [ctypes.c_int, ctypes.c_uint]
        cls.lib.open_cfw_test_wait_call_get.argtypes = [ctypes.c_uint]
        cls.lib.open_cfw_test_wait_call_get.restype = WaitCall
        cls.lib.open_cfw_bootloader_runtime_wait_4162c4.argtypes = [ctypes.c_uint, ctypes.c_uint, ctypes.c_uint]
        cls.lib.open_cfw_bootloader_runtime_wait_4162c4.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_authenticated_complete_stock_entry_and_callers(self) -> None:
        image = OFFICIAL.read_bytes(); body = image[0x62C4:0x6378]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (180, "48f58a21c85b21ba530c63f1bc88a6bc17c080da9f2c370f6c2cfc3a3430f42d"))
        self.assertEqual(image[0x1DD3A:0x1DD3E].hex(), "e8f7c3fa")
        self.assertEqual(image[0x1E37C:0x1E380].hex(), "e7f7a2ff")
        self.assertEqual(image[0x1E3EE:0x1E3F2].hex(), "e7f769ff")

    def test_guards_short_circuit(self) -> None:
        self.lib.open_cfw_test_wait_reset(1)
        self.assertEqual(self.lib.open_cfw_bootloader_runtime_wait_4162c4(1, 0, 0), -6)
        self.lib.open_cfw_test_wait_reset(0)
        self.assertEqual(self.lib.open_cfw_bootloader_runtime_wait_4162c4(0x80000000, 0, 0), -4)
        self.assertEqual(self.lib.open_cfw_test_wait_call_count(), 0)

    def test_wait_any_and_clear_mask_option(self) -> None:
        for options, clear_mask in ((0, 0x0C), (2, 0)):
            with self.subTest(options=options):
                self.lib.open_cfw_test_wait_reset(0)
                self.lib.open_cfw_test_wait_tick_add(10)
                self.lib.open_cfw_test_wait_response_add(1, 4)
                self.assertEqual(self.lib.open_cfw_bootloader_runtime_wait_4162c4(0x0C, options, 20), 4)
                call = self.lib.open_cfw_test_wait_call_get(0)
                self.assertEqual((call.clear_mask, call.timeout), (clear_mask, 20))

    def test_wait_all_accumulates_and_recomputes_timeout(self) -> None:
        self.lib.open_cfw_test_wait_reset(0)
        for tick in (100, 103, 107): self.lib.open_cfw_test_wait_tick_add(tick)
        self.lib.open_cfw_test_wait_response_add(1, 1)
        self.lib.open_cfw_test_wait_response_add(1, 4)
        self.lib.open_cfw_test_wait_response_add(1, 2)
        self.assertEqual(self.lib.open_cfw_bootloader_runtime_wait_4162c4(7, 1, 10), 7)
        self.assertEqual([self.lib.open_cfw_test_wait_call_get(i).timeout for i in range(3)], [10, 7, 3])

    def test_timeout_status_mapping_and_final_zero_timeout_probe(self) -> None:
        self.lib.open_cfw_test_wait_reset(0)
        self.lib.open_cfw_test_wait_tick_add(5)
        self.lib.open_cfw_test_wait_response_add(0, 0)
        self.assertEqual(self.lib.open_cfw_bootloader_runtime_wait_4162c4(1, 0, 0), -3)
        self.lib.open_cfw_test_wait_reset(0)
        self.lib.open_cfw_test_wait_tick_add(10)
        self.lib.open_cfw_test_wait_tick_add(25)
        self.lib.open_cfw_test_wait_response_add(1, 0)
        self.lib.open_cfw_test_wait_response_add(0, 0)
        self.assertEqual(self.lib.open_cfw_bootloader_runtime_wait_4162c4(1, 0, 7), -2)
        self.assertEqual([self.lib.open_cfw_test_wait_call_get(i).timeout for i in range(2)], [7, 0])

    def test_freestanding_target_compiles(self) -> None:
        output = Path(self.temporary.name) / "runtime-wait.o"
        subprocess.run(["/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(output)], check=True, capture_output=True, text=True)


if __name__ == "__main__": unittest.main()
