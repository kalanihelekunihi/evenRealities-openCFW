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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mode_service_4216d4.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mode_service_host.c"
SPECIAL = 0x02DC6C00


class BootloaderModeServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "mode-service.dylib" if sys.platform == "darwin" else "mode-service.so"
        cls.library = Path(cls.temporary.name) / suffix
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                str(FIXTURE),
                *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
                "-o", str(cls.library),
            ], check=True, capture_output=True,
        )
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.service = cls.lib.open_cfw_bootloader_mode_service_4216d4
        cls.service.argtypes = [ctypes.c_size_t, ctypes.POINTER(ctypes.c_uint32)]
        cls.service.restype = ctypes.c_uint32
        cls.lib.open_cfw_mode_fixture_reset.argtypes = []

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def u32(self, name: str) -> ctypes.c_uint32:
        return ctypes.c_uint32.in_dll(self.lib, name)

    def uptr(self, name: str) -> ctypes.c_size_t:
        return ctypes.c_size_t.in_dll(self.lib, name)

    def u8(self, name: str) -> ctypes.c_uint8:
        return ctypes.c_uint8.in_dll(self.lib, name)

    def array(self, name: str) -> ctypes.Array[ctypes.c_uint32]:
        return (ctypes.c_uint32 * 3).in_dll(self.lib, name)

    def setUp(self) -> None:
        self.lib.open_cfw_mode_fixture_reset()

    def test_authenticated_complete_body_literals_calls_and_caller(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x116D4:0x117D2]
        self.assertEqual(len(body), 254)
        self.assertEqual(
            hashlib.sha256(body).hexdigest(),
            "0cd7003be718ce1986083724a97a682e58e6623d4a579da5a272a4c34df85036",
        )
        self.assertEqual(blob[0x12214:0x12220].hex(), "083f4300006cdc027c000020")
        self.assertEqual(blob[0x122B8:0x122BC].hex(), "fff70cfa")
        self.assertEqual(blob[0x117D2:0x117D6].hex(), "2de9ff41")

    def test_rejects_unknown_instance_and_missing_controller(self) -> None:
        self.assertEqual(self.service(1, None), 5)
        self.assertEqual(self.service(SPECIAL, None), 7)
        self.assertEqual(self.u32("open_cfw_mode_fixture_restored_mask").value, 0)

    def test_query_builds_default_configuration_and_publishes_success(self) -> None:
        self.u32("open_cfw_mode_host_controller").value = 0x1234
        self.u32("open_cfw_mode_fixture_query_value").value = 0xABC
        self.assertEqual(self.service(SPECIAL, None), 0)
        self.assertEqual(self.u32("open_cfw_mode_fixture_query_calls").value, 1)
        self.assertEqual(list(self.array("open_cfw_mode_host_fallback")), [0x002ABC00, 0, 0])
        self.assertEqual(self.uptr("open_cfw_mode_host_current").value, SPECIAL)
        self.assertEqual(self.u8("open_cfw_mode_host_ready").value, 1)
        self.assertEqual(self.u32("open_cfw_mode_fixture_bitmap_selector").value, 4)
        self.assertEqual(self.u32("open_cfw_mode_fixture_restored_mask").value, 0xA5)

    def test_query_failure_returns_without_critical_section(self) -> None:
        self.u32("open_cfw_mode_host_controller").value = 1
        self.u32("open_cfw_mode_fixture_query_status").value = 9
        self.assertEqual(self.service(SPECIAL, None), 9)
        self.assertEqual(self.u32("open_cfw_mode_fixture_restored_mask").value, 0)
        self.assertEqual(self.u8("open_cfw_mode_host_ready").value, 0)

    def test_busy_apply_failure_runs_fallback_and_does_not_publish(self) -> None:
        config = (ctypes.c_uint32 * 3)(0xABCDEF01, 2, 3)
        self.u32("open_cfw_mode_host_controller").value = 1
        self.u32("open_cfw_mode_fixture_bitmap_count").value = 2
        self.u32("open_cfw_mode_fixture_apply_status").value = 8
        self.assertEqual(self.service(SPECIAL, config), 8)
        values = (ctypes.c_uint32 * 2).in_dll(self.lib, "open_cfw_mode_fixture_apply_values")
        self.assertEqual(list(values), [0xABCDEF01, 0x11111111])
        self.assertEqual(self.u32("open_cfw_mode_fixture_apply_calls").value, 2)
        self.assertEqual(self.u8("open_cfw_mode_host_ready").value, 0)
        self.assertEqual(self.u32("open_cfw_mode_fixture_restored_mask").value, 0xA5)

    def test_idle_transition_disables_clears_and_publishes_null(self) -> None:
        self.uptr("open_cfw_mode_host_current").value = SPECIAL
        self.assertEqual(self.service(0, None), 0)
        self.assertEqual(self.u32("open_cfw_mode_fixture_disable_calls").value, 1)
        self.assertEqual(self.u8("open_cfw_mode_host_aux_flag").value, 0)
        self.assertEqual(self.u32("open_cfw_mode_host_aux_word").value, 0)
        self.assertEqual(self.uptr("open_cfw_mode_host_current").value, 0)
        self.assertEqual(self.u8("open_cfw_mode_host_ready").value, 1)

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        for compiler in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if not Path(compiler).is_file():
                continue
            output = Path(self.temporary.name) / (Path(compiler).parent.name + "-mode.o")
            subprocess.run(
                [
                    compiler, "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections",
                    "-fdata-sections", "-Wall", "-Wextra", "-Werror",
                    "-c", str(SOURCE), "-o", str(output),
                ], check=True, capture_output=True,
            )
            self.assertTrue(output.is_file())


if __name__ == "__main__":
    unittest.main()
