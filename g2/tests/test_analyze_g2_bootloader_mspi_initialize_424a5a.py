from __future__ import annotations

import ctypes
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_initialize_424a5a.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mspi_initialize_host.c"
sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_bootloader_mspi_initialize_424a5a as analyzer


class BootloaderMspiInitializeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory(prefix="open-cfw-mspi-initialize-host-")
        output = Path(cls.tmp.name) / ("initialize.dylib" if sys.platform == "darwin" else "initialize.so")
        command = ["/usr/bin/clang", "-std=c11", "-O2", "-Wall", "-Wextra",
                   "-Werror", str(FIXTURE)]
        command += ["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]
        subprocess.run([*command, "-o", str(output)], check=True,
                       capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(output))
        cls.loaded.open_cfw_test_mspi_initialize_reset.argtypes = [
            ctypes.c_uint8, ctypes.c_uint32, ctypes.c_uint32]
        cls.loaded.open_cfw_test_mspi_initialize_run.argtypes = [ctypes.c_uint32,
                                                                 ctypes.c_uint32]
        cls.loaded.open_cfw_test_mspi_initialize_run.restype = ctypes.c_uint32
        cls.loaded.open_cfw_test_mspi_initialize_read.argtypes = [ctypes.c_uint32,
                                                                  ctypes.c_uint32,
                                                                  ctypes.c_uint32]
        cls.loaded.open_cfw_test_mspi_initialize_read.restype = ctypes.c_uint32
        cls.loaded.open_cfw_test_mspi_initialize_handle_module.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def read(self, module: int, offset: int, width: int = 4) -> int:
        return self.loaded.open_cfw_test_mspi_initialize_read(module, offset, width)

    def test_audit_is_structured_source_and_fail_closed(self) -> None:
        report = analyzer.audit()
        self.assertEqual(report["stock"]["sha256"], analyzer.STOCK_SHA)
        self.assertEqual(report["callers"], [0x0042029A])
        self.assertTrue(report["production"]["routed"])
        self.assertEqual(report["production"]["boundary_status"], "source_compiled")
        self.assertEqual(report["production"]["compiled_bytes"], 88)
        self.assertEqual(report["production"]["source_owned_bytes"] +
                         report["production"]["retained_official_bytes"], 146994)
        self.assertEqual(report["production"]["next_frontier"],
                         0x00424AB2)
        self.assertEqual(report["next_code_frontier"], {
            "start": 0x00424AF0, "end": 0x00424BD4,
            "identity": "am_hal_mspi_configure", "bytes": 228,
            "source_compiled_bytes": 152,
            "retained_literal_bytes": 76,
            "status": "source-compiled-with-retained-literals",
        })
        self.assertEqual(report["hardware_validation"],
                         "blocked by unavailable physical evidence")
        self.assertEqual(report["hardware_operations"], [])

    def test_production_source_uses_structured_c_not_raw_encoding(self) -> None:
        text = SOURCE.read_text(encoding="utf-8")
        self.assertNotIn(".byte", text)
        self.assertNotIn("__asm__", text)

    def test_success_initializes_exact_state_fields(self) -> None:
        self.loaded.open_cfw_test_mspi_initialize_reset(0xA5, 2, 0xA4001234)
        self.assertEqual(self.loaded.open_cfw_test_mspi_initialize_run(2, 1), 0)
        self.assertEqual(self.read(2, 0), 0xA5BEBEBE)
        self.assertEqual(self.read(2, 4), 2)
        self.assertEqual(self.read(2, 0x0C, 1), 0)
        self.assertEqual(self.read(2, 0x18), 0)
        self.assertEqual(self.read(2, 0x8C9, 1), 7)
        self.assertEqual(self.read(2, 0x8CC), 8)
        self.assertEqual(self.loaded.open_cfw_test_mspi_initialize_handle_module(), 2)
        self.assertEqual(self.read(2, 0x10), 0xA5A5A5A5)

    def test_out_of_range_is_non_mutating(self) -> None:
        self.loaded.open_cfw_test_mspi_initialize_reset(0x3C, 0, 0x00000000)
        self.assertEqual(self.loaded.open_cfw_test_mspi_initialize_run(4, 1), 5)
        self.assertEqual(self.read(0, 0), 0)
        self.assertEqual(self.read(0, 4), 0x3C3C3C3C)
        self.assertEqual(self.loaded.open_cfw_test_mspi_initialize_handle_module(),
                         0xFFFFFFFF)

    def test_null_output_is_rejected_before_state_access(self) -> None:
        self.loaded.open_cfw_test_mspi_initialize_reset(0x5A, 1, 0x00000000)
        self.assertEqual(self.loaded.open_cfw_test_mspi_initialize_run(1, 0), 6)
        self.assertEqual(self.read(1, 0), 0)
        self.assertEqual(self.read(1, 4), 0x5A5A5A5A)

    def test_allocated_state_is_rejected_without_mutation(self) -> None:
        self.loaded.open_cfw_test_mspi_initialize_reset(0x6B, 3, 0x01020304)
        self.assertEqual(self.loaded.open_cfw_test_mspi_initialize_run(3, 1), 7)
        self.assertEqual(self.read(3, 0), 0x01020304)
        self.assertEqual(self.read(3, 4), 0x6B6B6B6B)
        self.assertEqual(self.loaded.open_cfw_test_mspi_initialize_handle_module(),
                         0xFFFFFFFF)


if __name__ == "__main__":
    unittest.main()
