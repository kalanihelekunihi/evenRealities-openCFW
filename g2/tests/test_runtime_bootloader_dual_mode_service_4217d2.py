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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_dual_mode_service_4217d2.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_dual_mode_service_host.c"
SPECIAL_A = 0x0EE6B280
SPECIAL_B = 0x0BB80000


class BootloaderDualModeServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "dual-mode.dylib" if sys.platform == "darwin" else "dual-mode.so"
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
        cls.service = cls.lib.open_cfw_bootloader_dual_mode_service_4217d2
        cls.service.argtypes = [ctypes.c_size_t, ctypes.POINTER(ctypes.c_uint32)]
        cls.service.restype = ctypes.c_uint32
        cls.lib.open_cfw_dual_fixture_reset.argtypes = []

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def u32(self, name: str) -> ctypes.c_uint32:
        return ctypes.c_uint32.in_dll(self.lib, name)

    def uptr(self, name: str) -> ctypes.c_size_t:
        return ctypes.c_size_t.in_dll(self.lib, name)

    def u8(self, name: str) -> ctypes.c_uint8:
        return ctypes.c_uint8.in_dll(self.lib, name)

    def array(self, name: str, length: int = 3) -> ctypes.Array[ctypes.c_uint32]:
        return (ctypes.c_uint32 * length).in_dll(self.lib, name)

    def setUp(self) -> None:
        self.lib.open_cfw_dual_fixture_reset()

    def test_authenticated_body_literals_calls_dispatcher_and_successor(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x117D2:0x11978]
        self.assertEqual(len(body), 422)
        self.assertEqual(
            hashlib.sha256(body).hexdigest(),
            "05c24e9854dcc0df94616fd1bbfd81f540add09f4e915b0ebfd998b2052e12f7",
        )
        self.assertEqual(blob[0x122D8:0x122F0].hex(), "80b2e60e34700220143f43000000b80bf86f022051050020")
        self.assertEqual(blob[0x122C0:0x122C4].hex(), "fff787fa")
        self.assertEqual(blob[0x11978:0x1197A].hex(), "f8b5")

    def test_rejects_unknown_instance_and_missing_mode_controller(self) -> None:
        self.assertEqual(self.service(1, None), 5)
        self.assertEqual(self.service(SPECIAL_A, None), 7)
        config0 = (ctypes.c_uint32 * 3)(0, 0, 0)
        config1 = (ctypes.c_uint32 * 3)(1, 0, 0)
        self.assertEqual(self.service(SPECIAL_B, config0), 7)
        self.assertEqual(self.service(SPECIAL_B, config1), 7)
        self.assertEqual(self.u32("open_cfw_dual_fixture_save_calls").value, 0)

    def test_query_selects_first_or_second_controller_and_publishes(self) -> None:
        self.u32("open_cfw_dual_host_controller0").value = 0x10
        self.assertEqual(self.service(SPECIAL_B, None), 0)
        self.assertEqual(self.u32("open_cfw_dual_fixture_query_controller").value, 0x10)
        self.assertEqual(list(self.array("open_cfw_dual_host_configuration")), [0x00020000, 0xAABBCCDD, 0])
        self.assertEqual(self.uptr("open_cfw_dual_host_current").value, SPECIAL_B)
        self.assertEqual(self.u8("open_cfw_dual_host_ready").value, 1)
        self.assertEqual(self.u32("open_cfw_dual_fixture_bitmap_selector").value, 5)
        self.lib.open_cfw_dual_fixture_reset()
        self.u32("open_cfw_dual_host_controller1").value = 0x20
        self.assertEqual(self.service(SPECIAL_B, None), 0)
        self.assertEqual(self.u32("open_cfw_dual_fixture_query_controller").value, 0x20)
        self.assertEqual(bytes(self.array("open_cfw_dual_host_configuration"))[:1], b"\x01")

    def test_query_failure_returns_before_critical_section(self) -> None:
        self.u32("open_cfw_dual_host_controller0").value = 1
        self.u32("open_cfw_dual_fixture_query_status").value = 9
        self.assertEqual(self.service(SPECIAL_A, None), 9)
        self.assertEqual(self.u32("open_cfw_dual_fixture_save_calls").value, 0)
        self.assertEqual(self.u8("open_cfw_dual_host_ready").value, 0)

    def test_busy_incompatible_transition_returns_three_without_publication(self) -> None:
        config = (ctypes.c_uint32 * 3)(0, 2, 3)
        self.u32("open_cfw_dual_host_controller0").value = 1
        self.u32("open_cfw_dual_fixture_bitmap_values").value = 1
        self.uptr("open_cfw_dual_host_current").value = SPECIAL_B
        self.assertEqual(self.service(SPECIAL_B, config), 3)
        self.assertEqual(self.u32("open_cfw_dual_fixture_copy_calls").value, 0)
        self.assertEqual(self.u32("open_cfw_dual_fixture_restore_calls").value, 1)

    def test_mode0_transition_commits_and_disables_other_mode(self) -> None:
        config = (ctypes.c_uint32 * 3)(0, 2, 3)
        self.u32("open_cfw_dual_host_controller0").value = 1
        values = self.array("open_cfw_dual_fixture_bitmap_values", 2)
        values[0] = 1
        values[1] = 1
        self.assertEqual(self.service(SPECIAL_A, config), 0)
        self.assertEqual(self.u32("open_cfw_dual_fixture_mode0_enable_calls").value, 1)
        self.assertEqual(self.u32("open_cfw_dual_fixture_commit_calls").value, 1)
        self.assertEqual(self.u32("open_cfw_dual_fixture_mode1_disable_calls").value, 1)
        self.assertEqual(self.u32("open_cfw_dual_fixture_mode0_disable_calls").value, 0)
        self.assertEqual(self.u32("open_cfw_dual_fixture_last_argument").value, 0x36)
        self.assertEqual(list(self.array("open_cfw_dual_fixture_restored_masks", 2)), [0x11, 0x22])

    def test_commit_failure_runs_both_disable_paths(self) -> None:
        config = (ctypes.c_uint32 * 3)(1, 2, 3)
        self.u32("open_cfw_dual_host_controller1").value = 1
        values = self.array("open_cfw_dual_fixture_bitmap_values", 2)
        values[0] = 1
        values[1] = 1
        self.u32("open_cfw_dual_fixture_commit_status").value = 8
        self.assertEqual(self.service(SPECIAL_A, config), 8)
        self.assertEqual(self.u32("open_cfw_dual_fixture_mode1_enable_calls").value, 1)
        self.assertEqual(self.u32("open_cfw_dual_fixture_mode1_disable_calls").value, 1)
        self.assertEqual(self.u32("open_cfw_dual_fixture_mode0_disable_calls").value, 1)

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        for compiler in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if not Path(compiler).is_file():
                continue
            output = Path(self.temporary.name) / (Path(compiler).parent.name + "-dual-mode.o")
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
