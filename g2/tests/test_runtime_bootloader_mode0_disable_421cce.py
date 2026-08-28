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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mode0_disable_421cce.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mode0_disable_host.c"
FUNCTIONS = (
    (0x421CCE, 0x421D28, "3dac14d8bed9201a8c8e9147d2216bb399ccb35b33642840d4ad49ad3a691c6e"),
    (0x421D28, 0x421D5E, "4b8c76a46e4a846d4c3320718698134d79310d3b4c6a4dc3cb5b0602ab00ba20"),
)


class BootloaderMode0DisableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "mode0-disable.dylib" if sys.platform == "darwin" else "mode0-disable.so"
        cls.library = Path(cls.temporary.name) / suffix
        subprocess.run([
            os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2", "-Wall",
            "-Wextra", "-Werror", str(FIXTURE),
            *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
            "-o", str(cls.library),
        ], check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.disable = cls.lib.open_cfw_bootloader_mode0_disable_421cce
        cls.cleanup = cls.lib.open_cfw_bootloader_mode0_poll_cleanup_421d28
        cls.disable.argtypes = [ctypes.c_uint32]
        cls.disable.restype = ctypes.c_uint32
        cls.cleanup.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
        cls.lib.open_cfw_mode0_disable_fixture_reset.argtypes = []

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
        return (ctypes.c_uint32 * 2).in_dll(self.lib, "open_cfw_mode0_disable_fixture_bitmap")

    def setUp(self) -> None:
        self.lib.open_cfw_mode0_disable_fixture_reset()

    def test_authenticated_bodies_literals_and_successor(self) -> None:
        blob = OFFICIAL.read_bytes()
        for start, end, digest in FUNCTIONS:
            body = blob[start - 0x410000:end - 0x410000]
            self.assertEqual(hashlib.sha256(body).hexdigest(), digest)
        self.assertEqual(blob[0x12298:0x122A0].hex(), "9c71022044700220")
        self.assertEqual(blob[0x12444:0x12450].hex(), "9b710220407002209e710220")
        self.assertEqual(blob[0x11D5E:0x11D60].hex(), "7cb5")

    def test_absent_client_is_idempotent(self) -> None:
        self.assertEqual(self.disable(7), 0)
        self.assertEqual(self.u32("open_cfw_mode0_disable_fixture_restore_calls").value, 0)
        self.assertEqual(self.u32("open_cfw_mode0_disable_fixture_control_calls").value, 0)

    def test_disable_controls_only_after_last_client(self) -> None:
        self.bitmap()[0] = (1 << 5) | (1 << 6)
        self.u8("open_cfw_mode0_disable_host_active").value = 1
        state = ctypes.c_uint32(19)
        self.uptr("open_cfw_mode0_disable_host_state_pointer").value = ctypes.addressof(state)
        self.assertEqual(self.disable(5), 0)
        self.assertEqual(self.u32("open_cfw_mode0_disable_fixture_control_calls").value, 0)
        self.assertEqual(self.disable(6), 0)
        self.assertEqual((self.u32("open_cfw_mode0_disable_fixture_control_request").value,
                          self.u32("open_cfw_mode0_disable_fixture_control_argument").value), (4, 1))
        self.assertEqual(self.u8("open_cfw_mode0_disable_host_active").value, 0)
        self.assertEqual(self.uptr("open_cfw_mode0_disable_host_state_pointer").value, 0)

    def test_cleanup_short_circuit_and_active_completion(self) -> None:
        remaining = ctypes.c_uint32(9)
        self.cleanup(ctypes.byref(remaining))
        self.assertEqual(self.u32("open_cfw_mode0_disable_fixture_poll_calls").value, 0)
        self.u8("open_cfw_mode0_disable_host_active").value = 1
        self.uptr("open_cfw_mode0_disable_host_state_pointer").value = ctypes.addressof(remaining)
        self.cleanup(ctypes.byref(remaining))
        self.assertEqual(self.u32("open_cfw_mode0_disable_fixture_poll_calls").value, 1)
        self.assertEqual(self.u8("open_cfw_mode0_disable_host_complete").value, 1)
        self.assertEqual(self.u8("open_cfw_mode0_disable_host_active").value, 0)
        self.assertEqual(self.uptr("open_cfw_mode0_disable_host_state_pointer").value, 0)
        self.assertEqual(self.u32("open_cfw_mode0_disable_fixture_restore_calls").value, 1)

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        for compiler in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if not Path(compiler).exists():
                continue
            output = Path(self.temporary.name) / (Path(compiler).parent.name + "-mode0-disable.o")
            subprocess.run([
                compiler, "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections",
                "-fdata-sections", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables",
                "-Wall", "-Wextra", "-Werror", "-fno-ident", "-c", str(SOURCE),
                "-o", str(output),
            ], check=True, capture_output=True)


if __name__ == "__main__":
    unittest.main()
