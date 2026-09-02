from __future__ import annotations

import ctypes
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_piomixed_configure_42488e.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mspi_piomixed_configure_host.c"
sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_bootloader_mspi_piomixed_configure_42488e as analyzer


class BootloaderMspiPioMixedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory(prefix="open-cfw-piomixed-host-")
        output = Path(cls.tmp.name) / ("piomixed.dylib" if sys.platform == "darwin" else "piomixed.so")
        command = ["/usr/bin/clang", "-std=c11", "-O2", "-Wall", "-Wextra",
                   "-Werror", str(FIXTURE)]
        command += ["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]
        subprocess.run([*command, "-o", str(output)], check=True,
                       capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(output))
        cls.loaded.open_cfw_test_mspi_piomixed_reset.argtypes = [ctypes.c_uint32]
        cls.loaded.open_cfw_test_mspi_piomixed_run.argtypes = [ctypes.c_uint32,
                                                               ctypes.c_uint32]
        cls.loaded.open_cfw_test_mspi_piomixed_run.restype = ctypes.c_uint32
        cls.loaded.open_cfw_test_mspi_piomixed_value.argtypes = [ctypes.c_uint32]
        cls.loaded.open_cfw_test_mspi_piomixed_value.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_analyzer_closes_both_functions_and_hardware_block(self) -> None:
        report = analyzer.audit()
        self.assertEqual(report["status"],
                         "piomixed-structured-source-dual-profile / callbacks-production-source / hardware-validation-blocked-by-unavailable-physical-evidence")
        self.assertTrue(report["production"]["routed"])
        self.assertEqual(report["production"]["boundary_status"], "source_compiled")
        self.assertEqual(report["production"]["compiled_bytes"], 84)
        self.assertEqual(report["production"]["source_owned_bytes"] +
                         report["production"]["retained_official_bytes"], 146994)
        self.assertEqual(report["production"]["next_frontier"],
                         0x0042499C)
        self.assertEqual(report["next_frontier"], {
            "start": 0x0042499C, "end": 0x004249A0,
            "identity": "mspi0_base_literal", "bytes": 4,
        })
        self.assertEqual(report["hardware_validation"],
                         "blocked by unavailable physical evidence")

    def test_production_source_uses_structured_c_not_raw_encoding(self) -> None:
        text = SOURCE.read_text(encoding="utf-8")
        self.assertNotIn(".byte", text)
        self.assertNotIn("__asm__", text)

    def test_all_modes_map_to_exact_pio_mixed_values(self) -> None:
        expected = [0] * 12 + [1, 1, 3, 3, 5, 5, 7, 7, 0, 0, 9, 9, 11, 11]
        for mode, mixed in enumerate(expected):
            with self.subTest(mode=mode):
                self.loaded.open_cfw_test_mspi_piomixed_reset(0xA5A5A5A5)
                self.assertEqual(self.loaded.open_cfw_test_mspi_piomixed_run(2, mode), 0)
                values = [self.loaded.open_cfw_test_mspi_piomixed_value(i)
                          for i in range(4)]
                self.assertEqual(values, [1, 1, 0x40062004,
                                          (0xA5A5A5A5 & ~0xF) | mixed])

    def test_unknown_uint8_mode_is_successful_no_op(self) -> None:
        self.loaded.open_cfw_test_mspi_piomixed_reset(0x12345678)
        self.assertEqual(self.loaded.open_cfw_test_mspi_piomixed_run(1, 0x11A), 0)
        self.assertEqual([self.loaded.open_cfw_test_mspi_piomixed_value(i)
                          for i in range(2)], [0, 0])


if __name__ == "__main__":
    unittest.main()
