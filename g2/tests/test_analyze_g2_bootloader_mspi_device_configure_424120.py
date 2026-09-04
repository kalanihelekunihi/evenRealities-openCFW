from __future__ import annotations

import ctypes
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_device_configure_424120.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mspi_device_configure_host.c"
sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_bootloader_mspi_device_configure_424120 as analyzer


MODES = (
    (1, 1, 0, 0x103, 0x80000013), (2, 1, 0, 0x103, 0x80000013),
    (5, 0, 0, 0x103, 0x80000013), (6, 0, 0, 0x103, 0x80000013),
    (9, 0, 0, 0x10F, 0x8000001F), (10, 0, 0, 0x10F, 0x8000001F),
    (13, 0, 0, 0x3FF, 0), (14, 0, 0, 0x3FF, 0),
    (13, 0, 0, 0x3FF, 0), (14, 0, 0, 0x3FF, 0),
    (17, 0, 0, 0x7FFFF, 0), (18, 0, 0, 0x7FFFF, 0),
    (1, 0, 1, 0x103, 0x80000013), (2, 0, 1, 0x103, 0x80000013),
    (1, 0, 3, 0x103, 0x80000013), (2, 0, 3, 0x103, 0x80000013),
    (1, 0, 5, 0x10F, 0x8000001F), (2, 0, 5, 0x10F, 0x8000001F),
    (1, 0, 7, 0x10F, 0x8000001F), (2, 0, 7, 0x10F, 0x8000001F),
    (1, 0, 0, 0x103, 0x80000013), (2, 0, 0, 0x103, 0x80000013),
    (1, 0, 9, 0x3FF, 0), (2, 0, 9, 0x3FF, 0),
    (1, 0, 11, 0x3FF, 0), (2, 0, 11, 0x3FF, 0),
)


class BootloaderMspiDeviceConfigureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory(prefix="open-cfw-device-config-host-")
        output = Path(cls.tmp.name) / (
            "device_config.dylib" if sys.platform == "darwin" else "device_config.so")
        command = ["/usr/bin/clang", "-std=c11", "-O2", "-Wall", "-Wextra",
                   "-Werror", str(FIXTURE)]
        command += ["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]
        subprocess.run([*command, "-o", str(output)], check=True,
                       capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(output))
        cls.loaded.open_cfw_test_mspi_device_reset.argtypes = [ctypes.c_uint32,
                                                               ctypes.c_uint32]
        cls.loaded.open_cfw_test_mspi_device_run.argtypes = [ctypes.c_uint32,
                                                             ctypes.c_uint32,
                                                             ctypes.c_uint32]
        cls.loaded.open_cfw_test_mspi_device_run.restype = ctypes.c_uint32
        cls.loaded.open_cfw_test_mspi_device_value.argtypes = [ctypes.c_uint32,
                                                               ctypes.c_uint32]
        cls.loaded.open_cfw_test_mspi_device_value.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def value(self, selector: int, index: int = 0) -> int:
        return self.loaded.open_cfw_test_mspi_device_value(selector, index)

    def test_analyzer_closes_complete_function_and_hardware_block(self) -> None:
        report = analyzer.audit()
        self.assertEqual(report["status"],
                         "structured-source-dual-profile / production-source-in-place / hardware-validation-blocked-by-unavailable-physical-evidence")
        self.assertEqual((report["stock"]["start"], report["stock"]["end"],
                          report["stock"]["bytes"]),
                         (0x00424120, 0x0042488E, 1902))
        self.assertEqual(report["callers"], [0x00425012, 0x004258E4])
        self.assertEqual(report["identity"]["supported_modes"], 26)
        self.assertTrue(report["production"]["routed"])
        self.assertEqual(report["production"]["boundary_status"], "source_compiled")
        self.assertEqual(report["production"]["compiled_bytes"], 284)
        self.assertEqual(report["production"]["compiled_sha256"],
                         analyzer.TARGET_SHA)
        self.assertEqual(report["production"]["source_owned_bytes"] +
                         report["production"]["retained_official_bytes"], 146994)
        self.assertEqual(report["production"]["next_frontier"],
                         0x0042488E)
        self.assertEqual(report["next_frontier"], {
            "start": 0x0042488E, "end": 0x00424976,
            "identity": "mspi_piomixed_configure", "bytes": 232,
            "source_compiled_bytes": 84,
            "retained_unreachable_tail_bytes": 148,
            "status": "source-compiled-with-retained-unreachable-tail",
        })
        self.assertEqual(report["hardware_validation"],
                         "blocked by unavailable physical evidence")
        self.assertEqual(report["hardware_operations"], [])

    def test_production_source_uses_structured_c_not_raw_encoding(self) -> None:
        text = SOURCE.read_text(encoding="utf-8")
        self.assertNotIn(".byte", text)
        self.assertNotIn("__asm__", text)

    def test_all_twenty_six_modes_preserve_exact_register_semantics(self) -> None:
        initial_devcfg = 0xA5A5A5A5
        initial_xip = 0x5A5A5A5A
        module = 3
        base = 0x40063000
        for index, (device, separate, mixed, pad, d4pad) in enumerate(MODES):
            for clock_on_d4 in (0, 1):
                with self.subTest(mode=index, clock_on_d4=clock_on_d4):
                    self.loaded.open_cfw_test_mspi_device_reset(initial_devcfg,
                                                               initial_xip)
                    self.assertEqual(self.loaded.open_cfw_test_mspi_device_run(
                        module, clock_on_d4, index), 0)
                    expected_devcfg = ((initial_devcfg & ~0x1F) | device)
                    expected_devcfg = ((expected_devcfg & ~(1 << 25)) |
                                       (separate << 25))
                    expected_xip = ((initial_xip & ~(0xF << 8)) | (mixed << 8))
                    expected_pad = d4pad if clock_on_d4 and d4pad else pad
                    self.assertEqual((self.value(0), self.value(1)), (2, 3))
                    self.assertEqual((self.value(2), self.value(3)),
                                     (expected_devcfg, expected_xip))
                    self.assertEqual([self.value(4, i) for i in range(3)],
                                     [base + 0x84, base + 0x90, base + 0x44])
                    self.assertEqual([self.value(5, i) for i in range(3)],
                                     [expected_devcfg, expected_xip, expected_pad])

    def test_unknown_mode_is_successful_no_op(self) -> None:
        self.loaded.open_cfw_test_mspi_device_reset(0x11223344, 0x55667788)
        self.assertEqual(self.loaded.open_cfw_test_mspi_device_run(1, 1, 26), 0)
        self.assertEqual((self.value(0), self.value(1), self.value(2),
                          self.value(3)), (0, 0, 0x11223344, 0x55667788))

    def test_uint8_conversion_preserves_default_case(self) -> None:
        self.loaded.open_cfw_test_mspi_device_reset(1, 2)
        self.assertEqual(self.loaded.open_cfw_test_mspi_device_run(0, 0, 0x11A), 0)
        self.assertEqual((self.value(0), self.value(1)), (0, 0))


if __name__ == "__main__":
    unittest.main()
