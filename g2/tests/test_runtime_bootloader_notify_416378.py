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
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_notify_416378_host.c"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_notify_416378.c"


class BootloaderRuntimeNotify416378Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "dylib" if sys.platform == "darwin" else "so"
        cls.library = Path(cls.temporary.name) / f"boot-runtime-notify.{suffix}"
        command = [os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        command += ["-o", str(cls.library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.lib.open_cfw_test_notify_reset.argtypes = [ctypes.c_uint]
        cls.lib.open_cfw_bootloader_runtime_notify_416378.argtypes = [ctypes.c_uint]
        cls.lib.open_cfw_bootloader_runtime_notify_416378.restype = ctypes.c_int
        cls.lib.open_cfw_test_notify_call_count.restype = ctypes.c_uint
        cls.lib.open_cfw_test_notify_last_argument.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_authenticated_complete_stock_entry_and_callers(self) -> None:
        image = OFFICIAL.read_bytes(); body = image[0x6378:0x639A]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (34, "8a3050543e3c959ae1b5ef53792a3aa9a192000c0c82567df806bc1cdc7e51be"))
        self.assertEqual(image[0x107D6:0x107DA].hex(), "f5f7cffd")
        self.assertEqual(image[0x1E1E6:0x1E1EA].hex(), "e8f7c7f8")

    def test_critical_context_short_circuits(self) -> None:
        self.lib.open_cfw_test_notify_reset(1)
        self.assertEqual(self.lib.open_cfw_bootloader_runtime_notify_416378(7), -6)
        self.assertEqual(self.lib.open_cfw_test_notify_call_count(), 0)

    def test_null_is_successful_noop_and_nonnull_forwards(self) -> None:
        self.lib.open_cfw_test_notify_reset(0)
        self.assertEqual(self.lib.open_cfw_bootloader_runtime_notify_416378(0), 0)
        self.assertEqual(self.lib.open_cfw_test_notify_call_count(), 0)
        self.assertEqual(self.lib.open_cfw_bootloader_runtime_notify_416378(0x12345678), 0)
        self.assertEqual(self.lib.open_cfw_test_notify_call_count(), 1)
        self.assertEqual(self.lib.open_cfw_test_notify_last_argument(), 0x12345678)

    def test_freestanding_target_compiles(self) -> None:
        output = Path(self.temporary.name) / "runtime-notify.o"
        subprocess.run(["/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(output)], check=True, capture_output=True, text=True)


if __name__ == "__main__": unittest.main()
