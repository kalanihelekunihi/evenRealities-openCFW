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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mode0_enable_421bd2.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mode0_enable_host.c"


class BootloaderMode0EnableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "mode0.dylib" if sys.platform == "darwin" else "mode0.so"
        cls.library = Path(cls.temporary.name) / suffix
        subprocess.run([
            os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2", "-Wall",
            "-Wextra", "-Werror", str(FIXTURE),
            *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
            "-o", str(cls.library),
        ], check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.enable = cls.lib.open_cfw_bootloader_mode0_enable_421bd2
        cls.enable.argtypes = [ctypes.c_uint32]
        cls.enable.restype = ctypes.c_uint32
        cls.lib.open_cfw_mode0_fixture_reset.argtypes = []

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def u32(self, name: str) -> ctypes.c_uint32:
        return ctypes.c_uint32.in_dll(self.lib, name)

    def uptr(self, name: str) -> ctypes.c_size_t:
        return ctypes.c_size_t.in_dll(self.lib, name)

    def u8(self, name: str) -> ctypes.c_uint8:
        return ctypes.c_uint8.in_dll(self.lib, name)

    def bitmap(self) -> ctypes.Array[ctypes.c_uint32]:
        return (ctypes.c_uint32 * 2).in_dll(self.lib, "open_cfw_mode0_fixture_bitmap")

    def setUp(self) -> None:
        self.lib.open_cfw_mode0_fixture_reset()

    def test_authenticated_body_calls_literals_and_successor(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x11BD2:0x11CCE]
        self.assertEqual(len(body), 252)
        self.assertEqual(hashlib.sha256(body).hexdigest(),
                         "beaa4d231ad6eca158c9b2aac09a55b69258e213980ac1ce2cd704a33d1344f5")
        self.assertEqual(blob[0x11CCE:0x11CD0].hex(), "1cb5")

    def test_missing_controller_returns_seven_without_side_effects(self) -> None:
        self.assertEqual(self.enable(4), 7)
        self.assertEqual(self.u32("open_cfw_mode0_fixture_query_calls").value, 0)

    def test_existing_client_refreshes_timeout_and_cleans_up(self) -> None:
        prior = ctypes.c_uint32(77)
        self.uptr("open_cfw_mode0_host_controller").value = 1
        self.bitmap()[0] = 1 << 5
        self.u8("open_cfw_mode0_host_active").value = 1
        self.uptr("open_cfw_mode0_host_state_pointer").value = ctypes.addressof(prior)
        self.assertEqual(self.enable(5), 0)
        self.assertEqual(self.u32("open_cfw_mode0_fixture_cleanup_value").value, 77)
        self.assertEqual(self.u32("open_cfw_mode0_fixture_query_calls").value, 0)

    def test_idle_state_controls_and_publishes_client(self) -> None:
        self.uptr("open_cfw_mode0_host_controller").value = 1
        self.u8("open_cfw_mode0_host_table_mode").value = 1
        self.assertEqual(self.enable(0x106), 0)
        self.assertEqual((self.u32("open_cfw_mode0_fixture_control_request").value,
                          self.u32("open_cfw_mode0_fixture_control_argument").value), (3, 1))
        self.assertEqual(self.u32("open_cfw_mode0_fixture_update_bit").value, 6)
        self.assertEqual(self.u32("open_cfw_mode0_fixture_cleanup_value").value, 150)

    def test_incompatible_state_returns_three_without_bitmap_update(self) -> None:
        self.uptr("open_cfw_mode0_host_controller").value = 1
        self.u8("open_cfw_mode0_fixture_query_state").value = 2
        self.u8("open_cfw_mode0_host_table_mode").value = 0
        self.assertEqual(self.enable(9), 3)
        self.assertEqual(self.u32("open_cfw_mode0_fixture_update_calls").value, 0)
        self.assertEqual(self.u32("open_cfw_mode0_fixture_restore_calls").value, 1)

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        for compiler in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if not Path(compiler).exists():
                continue
            output = Path(self.temporary.name) / (Path(compiler).parent.name + "-mode0.o")
            subprocess.run([
                compiler, "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections",
                "-fdata-sections", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables",
                "-Wall", "-Wextra", "-Werror", "-fno-ident", "-c", str(SOURCE),
                "-o", str(output),
            ], check=True, capture_output=True)


if __name__ == "__main__":
    unittest.main()
