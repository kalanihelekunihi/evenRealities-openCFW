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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mode1_services_421b08.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mode1_services_host.c"
FUNCTIONS = (
    (0x421B08, 0x421B5C, "891c88359e96db91d98fd0b159621ca6da87bc784c0e3280f4a625dcc1aad579"),
    (0x421B5C, 0x421BA4, "0ec002b261917a95a5afe815494a62f850408c5de5b3a911e81fe3b1df23d06d"),
    (0x421BA4, 0x421BD2, "7bce9267762f0c94865d13a566fd4c0476bf127b1f1781e659016de79124461b"),
)


class BootloaderMode1ServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "mode1.dylib" if sys.platform == "darwin" else "mode1.so"
        cls.library = Path(cls.temporary.name) / suffix
        subprocess.run([
            os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2", "-Wall",
            "-Wextra", "-Werror", str(FIXTURE),
            *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
            "-o", str(cls.library),
        ], check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.enable = cls.lib.open_cfw_bootloader_mode1_enable_421b08
        cls.disable = cls.lib.open_cfw_bootloader_mode1_disable_421b5c
        cls.cleanup = cls.lib.open_cfw_bootloader_mode1_poll_cleanup_421ba4
        cls.enable.argtypes = cls.disable.argtypes = [ctypes.c_uint32]
        cls.enable.restype = cls.disable.restype = ctypes.c_uint32
        cls.cleanup.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
        cls.lib.open_cfw_mode1_fixture_reset.argtypes = []

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
        return (ctypes.c_uint32 * 2).in_dll(self.lib, "open_cfw_mode1_fixture_bitmap")

    def setUp(self) -> None:
        self.lib.open_cfw_mode1_fixture_reset()

    def test_authenticated_bodies_literals_and_successor(self) -> None:
        blob = OFFICIAL.read_bytes()
        for start, end, digest in FUNCTIONS:
            body = blob[start - 0x410000:end - 0x410000]
            self.assertEqual(hashlib.sha256(body).hexdigest(), digest)
        self.assertEqual(blob[0x1243C:0x1244C].hex(), "4c414300504143009b71022040700220")
        self.assertEqual(blob[0x11BD2:0x11BD4].hex(), "feb5")

    def test_enable_requires_controller_and_is_idempotent(self) -> None:
        self.assertEqual(self.enable(5), 7)
        self.uptr("open_cfw_mode1_host_controller").value = 1
        self.assertEqual(self.enable(0x105), 0)
        self.assertEqual((self.u32("open_cfw_mode1_fixture_control_request").value,
                          self.u32("open_cfw_mode1_fixture_control_value").value),
                         (15, 0x1234567A))
        self.assertEqual(self.u32("open_cfw_mode1_fixture_update_bit").value, 5)
        self.assertEqual(self.enable(5), 0)
        self.assertEqual(self.u32("open_cfw_mode1_fixture_control_calls").value, 1)

    def test_disable_controls_only_after_last_client(self) -> None:
        bits = self.bitmap()
        bits[0] = (1 << 5) | (1 << 6)
        self.assertEqual(self.disable(5), 0)
        self.assertEqual(self.u32("open_cfw_mode1_fixture_control_calls").value, 0)
        self.assertEqual(self.disable(6), 0)
        self.assertEqual(self.u32("open_cfw_mode1_fixture_control_value").value, 0x89ABCDEF)
        self.assertEqual(self.disable(6), 0)
        self.assertEqual(self.u32("open_cfw_mode1_fixture_control_calls").value, 1)

    def test_cleanup_short_circuit_and_active_state_clear(self) -> None:
        remaining = ctypes.c_uint32(4)
        self.cleanup(ctypes.byref(remaining))
        self.assertEqual(self.u32("open_cfw_mode1_fixture_poll_calls").value, 0)
        self.u8("open_cfw_mode1_host_active").value = 1
        self.u32("open_cfw_mode1_host_state").value = 0x1234
        self.cleanup(ctypes.byref(remaining))
        self.assertEqual(remaining.value, 3)
        self.assertEqual(self.u8("open_cfw_mode1_host_active").value, 0)
        self.assertEqual(self.u32("open_cfw_mode1_host_state").value, 0)
        self.assertEqual(self.u32("open_cfw_mode1_fixture_restore_calls").value, 1)

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        for compiler in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if not Path(compiler).exists():
                continue
            output = Path(self.temporary.name) / (Path(compiler).parent.name + "-mode1.o")
            subprocess.run([
                compiler, "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections",
                "-fdata-sections", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables",
                "-Wall", "-Wextra", "-Werror", "-fno-ident", "-c", str(SOURCE),
                "-o", str(output),
            ], check=True, capture_output=True)


if __name__ == "__main__":
    unittest.main()
