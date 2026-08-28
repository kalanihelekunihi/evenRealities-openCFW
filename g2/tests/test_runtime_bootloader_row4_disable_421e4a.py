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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_row4_disable_421e4a.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_row4_disable_host.c"
FUNCTIONS = ((0x421E4A, 0x421E8C, "f4f21abad8199cfea2524c7335d809b7f624100c1e34b693c08025ae1fb40a2a"), (0x421E8C, 0x421EBA, "113121d1847a984448cf18c516a0fbab330809872367ea03a787d3ba61b95985"))


class BootloaderRow4DisableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory(); suffix = "row4-disable.dylib" if sys.platform == "darwin" else "row4-disable.so"; cls.library = Path(cls.temporary.name) / suffix
        subprocess.run([os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE), *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]), "-o", str(cls.library)], check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(cls.library)); cls.disable = cls.lib.open_cfw_bootloader_row4_disable_421e4a; cls.cleanup = cls.lib.open_cfw_bootloader_row4_poll_cleanup_421e8c
        cls.disable.argtypes = [ctypes.c_uint32]; cls.disable.restype = ctypes.c_uint32; cls.cleanup.argtypes = [ctypes.POINTER(ctypes.c_uint32)]; cls.lib.open_cfw_row4_disable_fixture_reset.argtypes = []

    @classmethod
    def tearDownClass(cls) -> None: cls.temporary.cleanup()
    def u32(self, name: str) -> ctypes.c_uint32: return ctypes.c_uint32.in_dll(self.lib, name)
    def uptr(self, name: str) -> ctypes.c_size_t: return ctypes.c_size_t.in_dll(self.lib, name)
    def u8(self, name: str) -> ctypes.c_uint8: return ctypes.c_uint8.in_dll(self.lib, name)
    def bitmap(self) -> ctypes.Array[ctypes.c_uint32]: return (ctypes.c_uint32 * 2).in_dll(self.lib, "open_cfw_row4_disable_fixture_bitmap")
    def setUp(self) -> None: self.lib.open_cfw_row4_disable_fixture_reset()

    def test_authenticated_bodies_literals_and_successor(self) -> None:
        blob = OFFICIAL.read_bytes()
        for start, end, digest in FUNCTIONS: self.assertEqual(hashlib.sha256(blob[start - 0x410000:end - 0x410000]).hexdigest(), digest)
        self.assertEqual(blob[0x12450:0x12458].hex(), "9d71022048700220")
        self.assertEqual(blob[0x11EBA:0x11EBC].hex(), "feb5")

    def test_absent_and_nonfinal_disable_are_idempotent(self) -> None:
        self.assertEqual(self.disable(3), 0); self.assertEqual(self.u32("open_cfw_row4_disable_fixture_restore_calls").value, 0)
        self.bitmap()[0] = (1 << 3) | (1 << 4); self.assertEqual(self.disable(3), 0); self.assertEqual(self.u32("open_cfw_row4_disable_fixture_switch_calls").value, 0)

    def test_last_client_disables_switch(self) -> None:
        self.bitmap()[0] = 1 << 7; self.assertEqual(self.disable(7), 0); self.assertEqual(self.u32("open_cfw_row4_disable_fixture_switch_calls").value, 1); self.assertEqual(self.u32("open_cfw_row4_disable_fixture_restore_calls").value, 1)

    def test_cleanup_short_circuit_and_active_clear(self) -> None:
        remaining = ctypes.c_uint32(8); self.cleanup(ctypes.byref(remaining)); self.assertEqual(self.u32("open_cfw_row4_disable_fixture_poll_calls").value, 0)
        self.u8("open_cfw_row4_disable_host_active").value = 1; self.uptr("open_cfw_row4_disable_host_state_pointer").value = ctypes.addressof(remaining); self.cleanup(ctypes.byref(remaining))
        self.assertEqual(self.u32("open_cfw_row4_disable_fixture_poll_calls").value, 1); self.assertEqual(self.u8("open_cfw_row4_disable_host_active").value, 0); self.assertEqual(self.uptr("open_cfw_row4_disable_host_state_pointer").value, 0)

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        for compiler in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if not Path(compiler).exists(): continue
            output = Path(self.temporary.name) / (Path(compiler).parent.name + "-row4-disable.o")
            subprocess.run([compiler, "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror", "-fno-ident", "-c", str(SOURCE), "-o", str(output)], check=True, capture_output=True)


if __name__ == "__main__": unittest.main()
