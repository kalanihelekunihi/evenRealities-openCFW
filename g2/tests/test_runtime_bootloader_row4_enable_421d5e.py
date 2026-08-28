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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_row4_enable_421d5e.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_row4_enable_host.c"


class BootloaderRow4EnableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "row4.dylib" if sys.platform == "darwin" else "row4.so"
        cls.library = Path(cls.temporary.name) / suffix
        subprocess.run([os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE), *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]), "-o", str(cls.library)], check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.enable = cls.lib.open_cfw_bootloader_row4_enable_421d5e
        cls.enable.argtypes = [ctypes.c_uint32]; cls.enable.restype = ctypes.c_uint32
        cls.lib.open_cfw_row4_fixture_reset.argtypes = []

    @classmethod
    def tearDownClass(cls) -> None: cls.temporary.cleanup()

    def u32(self, name: str) -> ctypes.c_uint32: return ctypes.c_uint32.in_dll(self.lib, name)
    def uptr(self, name: str) -> ctypes.c_size_t: return ctypes.c_size_t.in_dll(self.lib, name)
    def u8(self, name: str) -> ctypes.c_uint8: return ctypes.c_uint8.in_dll(self.lib, name)
    def bitmap(self) -> ctypes.Array[ctypes.c_uint32]: return (ctypes.c_uint32 * 2).in_dll(self.lib, "open_cfw_row4_fixture_bitmap")
    def setUp(self) -> None: self.lib.open_cfw_row4_fixture_reset()

    def test_authenticated_body_literals_calls_and_successor(self) -> None:
        blob = OFFICIAL.read_bytes(); body = blob[0x11D5E:0x11E4A]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (236, "680cf0628b0c3ed785836da7faeb3fcecf7ab51a02c90ed91c2c5b18442ef899"))
        self.assertEqual(blob[0x12290:0x122A0].hex(), "30700220ec6f02209c71022044700220")
        self.assertEqual(blob[0x11E4A:0x11E4C].hex(), "1cb5")

    def test_existing_client_refreshes_timeout(self) -> None:
        prior = ctypes.c_uint32(77); self.bitmap()[0] = 1 << 3
        self.u8("open_cfw_row4_host_active").value = 1
        self.uptr("open_cfw_row4_host_state_pointer").value = ctypes.addressof(prior)
        self.assertEqual(self.enable(3), 0)
        self.assertEqual(self.u32("open_cfw_row4_fixture_cleanup_value").value, 77)
        self.assertEqual(self.u32("open_cfw_row4_fixture_apply_calls").value, 0)

    def test_not_ready_returns_one_without_bitmap_update(self) -> None:
        self.u8("open_cfw_row4_host_ready").value = 0
        self.assertEqual(self.enable(5), 1)
        self.assertEqual(self.u32("open_cfw_row4_fixture_update_calls").value, 0)
        self.assertEqual(self.u32("open_cfw_row4_fixture_restore_calls").value, 1)

    def test_first_client_switches_applies_and_activates(self) -> None:
        self.assertEqual(self.enable(0x106), 0)
        self.assertEqual((self.u32("open_cfw_row4_fixture_switch_calls").value, self.u32("open_cfw_row4_fixture_switch_value").value), (1, 1))
        self.assertEqual(self.u32("open_cfw_row4_fixture_apply_calls").value, 1)
        self.assertEqual(self.u8("open_cfw_row4_host_active").value, 1)
        self.assertEqual(self.bitmap()[0], 1 << 6)
        self.assertEqual(self.u32("open_cfw_row4_fixture_cleanup_value").value, 1000)

    def test_apply_failure_rolls_back_switch_and_skips_bitmap(self) -> None:
        self.u32("open_cfw_row4_fixture_apply_status").value = 9
        self.assertEqual(self.enable(2), 9)
        self.assertEqual((self.u32("open_cfw_row4_fixture_switch_calls").value, self.u32("open_cfw_row4_fixture_switch_value").value), (2, 0))
        self.assertEqual(self.u32("open_cfw_row4_fixture_update_calls").value, 0)

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        for compiler in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if not Path(compiler).exists(): continue
            output = Path(self.temporary.name) / (Path(compiler).parent.name + "-row4.o")
            subprocess.run([compiler, "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror", "-fno-ident", "-c", str(SOURCE), "-o", str(output)], check=True, capture_output=True)


if __name__ == "__main__": unittest.main()
