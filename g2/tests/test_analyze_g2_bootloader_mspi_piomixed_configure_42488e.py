from __future__ import annotations

import ctypes
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research/admission/bootloader_mspi_piomixed_configure_42488e/runtime_bootloader_mspi_piomixed_configure_candidate.c"
FIXTURE = SOURCE.parent / "host_fixture.c"
sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_bootloader_mspi_piomixed_configure_42488e as analyzer


class BootloaderMspiPioMixedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory(prefix="open-cfw-piomixed-host-")
        output = Path(cls.tmp.name) / ("piomixed.dylib" if sys.platform == "darwin" else "piomixed.so")
        command = ["/usr/bin/clang", "-std=c11", "-O2", "-Wall", "-Wextra",
                   "-Werror", str(SOURCE), str(FIXTURE)]
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
                         "piomixed-candidate-exact-retained-official / callbacks-production-source / hardware-validation-deferred-by-project-direction")
        self.assertFalse(report["production"]["routed"])
        self.assertEqual(report["production"]["boundary_status"], "official_blob")
        self.assertEqual(report["production"]["source_owned_bytes"] +
                         report["production"]["retained_official_bytes"], 147296)
        self.assertEqual(report["production"]["next_frontier"],
                         0x0042499C)
        self.assertEqual(report["next_frontier"], {
            "start": 0x0042499C, "end": 0x004249A0,
            "identity": "mspi0_base_literal", "bytes": 4,
        })
        self.assertEqual(report["hardware_validation"],
                         "deferred by project direction")

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
