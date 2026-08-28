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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_row5_services_421eba.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_row5_services_host.c"


class BootloaderRow5ServicesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.library = Path(cls.temporary.name) / ("row5.dylib" if sys.platform == "darwin" else "row5.so")
        subprocess.run([os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE), *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]), "-o", str(cls.library)], check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.enable = cls.lib.open_cfw_bootloader_row5_enable_421eba; cls.enable.argtypes = [ctypes.c_uint32]; cls.enable.restype = ctypes.c_uint32
        cls.disable = cls.lib.open_cfw_bootloader_row5_disable_422040; cls.disable.argtypes = [ctypes.c_uint32]; cls.disable.restype = ctypes.c_uint32
        cls.lib.open_cfw_row5_fixture_reset.argtypes = []

    @classmethod
    def tearDownClass(cls) -> None: cls.temporary.cleanup()
    def u32(self, name: str) -> ctypes.c_uint32: return ctypes.c_uint32.in_dll(self.lib, name)
    def u8(self, name: str) -> ctypes.c_uint8: return ctypes.c_uint8.in_dll(self.lib, name)
    def uptr(self, name: str) -> ctypes.c_size_t: return ctypes.c_size_t.in_dll(self.lib, name)
    def bitmap(self) -> ctypes.Array[ctypes.c_uint32]: return (ctypes.c_uint32 * 2).in_dll(self.lib, "open_cfw_row5_fixture_bitmap")
    def disables(self) -> ctypes.Array[ctypes.c_uint32]: return (ctypes.c_uint32 * 2).in_dll(self.lib, "open_cfw_row5_fixture_disable_calls")
    def setUp(self) -> None: self.lib.open_cfw_row5_fixture_reset()

    def test_authenticated_bodies_literals_and_successor(self) -> None:
        blob = OFFICIAL.read_bytes(); enable = blob[0x11EBA:0x12040]; disable = blob[0x12040:0x120B2]
        self.assertEqual((len(enable), hashlib.sha256(enable).hexdigest()), (390, "5d5e8bce49145dfddb318e0aff9baf61150e00e95f6fc7c804fde126dd11f68c"))
        self.assertEqual((len(disable), hashlib.sha256(disable).hexdigest()), (114, "fa335e0a8bf71ef86975470840768672bd90ad0eaac982abfc68e8c84de0bd17"))
        self.assertEqual(blob[0x122DC:0x122F0].hex(), "34700220143f43000000b80bf86f022051050020")
        self.assertEqual(blob[0x12450:0x1245C].hex(), "9d710220487002209f710220")
        self.assertEqual(blob[0x120B2:0x120B6].hex(), "2de9fc41")

    def test_existing_client_inherits_timeout(self) -> None:
        prior = ctypes.c_uint32(19); self.bitmap()[0] = 1 << 3; self.u8("open_cfw_row5_host_active").value = 1; self.uptr("open_cfw_row5_host_state_pointer").value = ctypes.addressof(prior)
        self.assertEqual(self.enable(3), 0); self.assertEqual(self.u32("open_cfw_row5_fixture_cleanup_value").value, 19); self.assertEqual(self.u32("open_cfw_row5_fixture_enable_calls").value, 0)

    def test_first_client_enables_commits_and_activates(self) -> None:
        self.u8("open_cfw_row5_host_selector").value = 1
        self.assertEqual(self.enable(0x106), 0); self.assertEqual(self.bitmap()[0], 1 << 6)
        self.assertEqual((self.u32("open_cfw_row5_fixture_enable_calls").value, self.u32("open_cfw_row5_fixture_commit_calls").value), (1, 1))
        self.assertEqual((self.u8("open_cfw_row5_host_active").value, self.u8("open_cfw_row5_host_pending").value), (1, 0))
        self.assertEqual(self.u32("open_cfw_row5_fixture_cleanup_value").value, 50)

    def test_mode_enable_failure_rolls_back_bitmap_and_selector(self) -> None:
        self.u32("open_cfw_row5_fixture_enable_status").value = 7; self.assertEqual(self.enable(2), 0)
        self.assertEqual(self.bitmap()[0], 0); self.assertEqual(self.disables()[0], 1); self.assertEqual(self.u32("open_cfw_row5_fixture_commit_calls").value, 0)

    def test_commit_failure_rolls_back_switch_bitmap_and_selector(self) -> None:
        self.u32("open_cfw_row5_fixture_commit_status").value = 9; self.assertEqual(self.enable(4), 0)
        self.assertEqual(self.bitmap()[0], 0); self.assertEqual((self.u32("open_cfw_row5_fixture_switch_calls").value, self.u32("open_cfw_row5_fixture_switch_value").value), (2, 0)); self.assertEqual(self.disables()[0], 1)

    def test_disable_absent_nonfinal_and_final_cleanup(self) -> None:
        self.assertEqual(self.disable(1), 0); self.assertEqual(self.u32("open_cfw_row5_fixture_restore_calls").value, 0)
        self.bitmap()[0] = (1 << 1) | (1 << 2); self.disable(1); self.assertEqual(self.u32("open_cfw_row5_fixture_null_commit_calls").value, 0)
        self.u8("open_cfw_row5_host_active").value = 1; self.u8("open_cfw_row5_host_pending").value = 1; prior = ctypes.c_uint32(4); self.uptr("open_cfw_row5_host_state_pointer").value = ctypes.addressof(prior)
        self.disable(2); self.assertEqual(self.u32("open_cfw_row5_fixture_null_commit_calls").value, 1); self.assertEqual(tuple(self.disables()), (1, 1)); self.assertEqual(self.u8("open_cfw_row5_host_active").value, 0); self.assertEqual(self.uptr("open_cfw_row5_host_state_pointer").value, 0)

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        for compiler in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if not Path(compiler).exists(): continue
            output = Path(self.temporary.name) / (Path(compiler).parent.name + "-row5.o")
            subprocess.run([compiler, "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror", "-fno-ident", "-c", str(SOURCE), "-o", str(output)], check=True, capture_output=True)


if __name__ == "__main__": unittest.main()
