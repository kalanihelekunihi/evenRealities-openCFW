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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_bitmap_clients_421978.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_bitmap_clients_host.c"
FUNCTIONS = (
    (0x421978, 0x421A30, "14c0af33cbe710b3f3272f9ce0731f82c27f5ddf4c7586f8169264621335eb57"),
    (0x421A30, 0x421A62, "55df16968e7cebea48cb197fa9e91b0534c3420fd587d2e362ee3f14e5f2ad12"),
    (0x421A62, 0x421A94, "61afcf0355e0f2fdc9095ff5311cea9e3e52749acc277a981788ccd6f0833473"),
    (0x421A94, 0x421AD6, "0b01e6b1f407cd164536ca7c894b0cb48dcf7c2497814eb3187860633f189a4c"),
    (0x421AD6, 0x421B08, "9aea3a0a0c095098f5c43b3cb3b34fb1565983cda5769771928650d440ef58d5"),
)


class BootloaderBitmapClientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "bitmap-clients.dylib" if sys.platform == "darwin" else "bitmap-clients.so"
        cls.library = Path(cls.temporary.name) / suffix
        subprocess.run([
            os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2",
            "-Wall", "-Wextra", "-Werror", str(FIXTURE),
            *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
            "-o", str(cls.library),
        ], check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.service = cls.lib.open_cfw_bootloader_bitmap_client_service_421978
        cls.service.argtypes = [ctypes.c_size_t, ctypes.POINTER(ctypes.c_uint32)]
        cls.service.restype = ctypes.c_uint32
        cls.helpers = [
            cls.lib.open_cfw_bootloader_bitmap_row0_set_421a30,
            cls.lib.open_cfw_bootloader_bitmap_row0_clear_421a62,
            cls.lib.open_cfw_bootloader_bitmap_row1_set_421a94,
            cls.lib.open_cfw_bootloader_bitmap_row1_clear_421ad6,
        ]
        for helper in cls.helpers:
            helper.argtypes = [ctypes.c_uint32]
            helper.restype = ctypes.c_uint32
        cls.lib.open_cfw_clients_fixture_reset.argtypes = []

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def u32(self, name: str) -> ctypes.c_uint32:
        return ctypes.c_uint32.in_dll(self.lib, name)

    def uptr(self, name: str) -> ctypes.c_size_t:
        return ctypes.c_size_t.in_dll(self.lib, name)

    def u8(self, name: str) -> ctypes.c_uint8:
        return ctypes.c_uint8.in_dll(self.lib, name)

    def array(self, name: str, length: int) -> ctypes.Array[ctypes.c_uint32]:
        return (ctypes.c_uint32 * length).in_dll(self.lib, name)

    def setUp(self) -> None:
        self.lib.open_cfw_clients_fixture_reset()

    def test_authenticated_cluster_literals_and_successor(self) -> None:
        blob = OFFICIAL.read_bytes()
        for start, end, digest in FUNCTIONS:
            body = blob[start - 0x410000:end - 0x410000]
            self.assertEqual(hashlib.sha256(body).hexdigest(), digest)
        self.assertEqual(blob[0x1221C:0x12220].hex(), "7c000020")
        self.assertEqual(blob[0x12430:0x1243C].hex(), "04700220387002209a710220")
        self.assertEqual(blob[0x11B08:0x11B0A].hex(), "38b5")

    def test_service_validates_controllers_and_query_routes(self) -> None:
        self.assertEqual(self.service(0x1234, None), 7)
        self.uptr("open_cfw_clients_host_controller0").value = 0x10
        self.assertEqual(self.service(0x1234, None), 0)
        self.assertEqual(self.uptr("open_cfw_clients_fixture_query_controller").value, 0x10)
        self.assertEqual(self.uptr("open_cfw_clients_fixture_query_instance").value, 0x1234)
        self.assertEqual(list(self.array("open_cfw_clients_host_configuration", 3)),
                         [0x11111111, 0x22222222, 0x33333333])
        self.lib.open_cfw_clients_fixture_reset()
        self.uptr("open_cfw_clients_host_controller1").value = 0x20
        self.assertEqual(self.service(0x5678, None), 0)
        self.assertEqual(self.uptr("open_cfw_clients_fixture_query_controller").value, 0x20)

    def test_service_query_failure_and_busy_state_do_not_publish(self) -> None:
        self.uptr("open_cfw_clients_host_controller0").value = 1
        self.u32("open_cfw_clients_fixture_query_status").value = 9
        self.assertEqual(self.service(4, None), 9)
        self.assertEqual(self.u32("open_cfw_clients_fixture_save_calls").value, 0)
        config = (ctypes.c_uint32 * 3)(2, 3, 4)
        self.u32("open_cfw_clients_fixture_query_status").value = 0
        self.u32("open_cfw_clients_fixture_count6").value = 1
        self.assertEqual(self.service(4, config), 3)
        self.assertEqual(self.u32("open_cfw_clients_fixture_copy_calls").value, 0)
        self.assertEqual(self.u32("open_cfw_clients_fixture_restored_mask").value, 0xA5)

    def test_service_configuration_validation_and_publication(self) -> None:
        config0 = (ctypes.c_uint32 * 3)(0, 7, 8)
        config1 = (ctypes.c_uint32 * 3)(1, 7, 8)
        self.assertEqual(self.service(1, config0), 7)
        self.assertEqual(self.service(1, config1), 7)
        self.uptr("open_cfw_clients_host_controller0").value = 1
        self.assertEqual(self.service(0xABC, config0), 0)
        self.assertEqual(list(self.array("open_cfw_clients_host_configuration", 3)), [0, 7, 8])
        self.assertEqual(self.uptr("open_cfw_clients_host_current").value, 0xABC)
        self.assertEqual(self.u8("open_cfw_clients_host_ready").value, 1)

    def test_row0_helpers_are_idempotent_and_narrow_bit(self) -> None:
        self.assertEqual(self.helpers[0](0x105), 0)
        self.assertEqual((self.u32("open_cfw_clients_fixture_update_row").value,
                          self.u32("open_cfw_clients_fixture_update_bit").value,
                          self.u32("open_cfw_clients_fixture_update_enabled").value), (0, 5, 1))
        self.assertEqual(self.helpers[0](5), 0)
        self.assertEqual(self.u32("open_cfw_clients_fixture_update_calls").value, 1)
        self.assertEqual(self.helpers[1](5), 0)
        self.assertEqual(self.u32("open_cfw_clients_fixture_update_enabled").value, 0)

    def test_row1_set_requires_controller_but_clear_does_not(self) -> None:
        self.assertEqual(self.helpers[2](7), 7)
        self.uptr("open_cfw_clients_host_controller_required").value = 1
        self.assertEqual(self.helpers[2](7), 0)
        self.assertEqual(self.u32("open_cfw_clients_fixture_update_row").value, 1)
        self.uptr("open_cfw_clients_host_controller_required").value = 0
        self.assertEqual(self.helpers[3](7), 0)
        self.assertEqual(self.u32("open_cfw_clients_fixture_update_enabled").value, 0)

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        for compiler in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if not Path(compiler).exists():
                continue
            output = Path(self.temporary.name) / (Path(compiler).parent.name + ".o")
            subprocess.run([
                compiler, "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections",
                "-fdata-sections", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables",
                "-Wall", "-Wextra", "-Werror", "-fno-ident", "-c", str(SOURCE),
                "-o", str(output),
            ], check=True, capture_output=True)


if __name__ == "__main__":
    unittest.main()
