from __future__ import annotations

import ctypes
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research/admission/bootloader_mspi_program_dma_42403e/runtime_bootloader_mspi_program_dma_candidate.c"
FIXTURE = SOURCE.parent / "host_fixture.c"
sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_bootloader_mspi_program_dma_42403e as analyzer


class Entry(ctypes.Structure):
    _fields_ = [
        ("dma_target_address", ctypes.c_uint32),
        ("dma_device_address", ctypes.c_uint32),
        ("dma_total_count", ctypes.c_uint32),
        ("dma_config", ctypes.c_uint32),
        ("callback", ctypes.c_void_p),
        ("callback_context", ctypes.c_void_p),
    ]


class BootloaderMspiProgramDmaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory(prefix="open-cfw-program-dma-host-")
        output = Path(cls.tmp.name) / (
            "program_dma.dylib" if sys.platform == "darwin" else "program_dma.so")
        command = ["/usr/bin/clang", "-std=c11", "-O2", "-Wall", "-Wextra",
                   "-Werror", str(SOURCE), str(FIXTURE)]
        command += ["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]
        subprocess.run([*command, "-o", str(output)], check=True,
                       capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(output))
        cls.loaded.open_cfw_test_mspi_program_dma_reset.argtypes = [ctypes.c_uint32]
        cls.loaded.open_cfw_test_mspi_program_dma_run.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
            ctypes.POINTER(Entry)]
        cls.loaded.open_cfw_test_mspi_program_dma_run.restype = ctypes.c_uint32
        cls.loaded.open_cfw_test_mspi_program_dma_value.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32]
        cls.loaded.open_cfw_test_mspi_program_dma_value.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    @classmethod
    def values(cls, selector: int, count: int = 1) -> list[int]:
        return [cls.loaded.open_cfw_test_mspi_program_dma_value(selector, index)
                for index in range(count)]

    @staticmethod
    def entries() -> ctypes.Array[Entry]:
        return (Entry * 3)(
            Entry(0x11110000, 0x22220000, 0x33330000, 0x44440000, None, None),
            Entry(0x11110001, 0x22220001, 0x33330001, 0x44440001, None, None),
            Entry(0x11110002, 0x22220002, 0x33330002, 0x44440002, None, None),
        )

    def test_analyzer_closes_exact_source_and_hardware_block(self) -> None:
        report = analyzer.audit()
        self.assertEqual(
            report["status"],
            "production-routed-exact-dual-profile-source / hardware-validation-blocked-by-unavailable-physical-evidence")
        self.assertEqual((report["stock"]["start"], report["stock"]["end"],
                          report["stock"]["bytes"]),
                         (0x0042403E, 0x004240AA, 108))
        self.assertEqual(report["callers"], [0x0042410E, 0x00426620])
        self.assertEqual(set(report["profiles"]), {"apple-clang", "linux-clang"})
        self.assertTrue(report["production"]["routed"])
        self.assertEqual(
            report["production"]["source_owned_bytes"]
            + report["production"]["retained_official_bytes"],
            146994,
        )
        self.assertEqual(report["production"]["next_frontier"], 0x004240AA)
        self.assertEqual(report["next_frontier"], {
            "start": 0x004240AA, "end": 0x00424120,
            "identity": "sched_hiprio", "bytes": 118,
        })
        self.assertEqual(report["hardware_validation"],
                         "blocked by unavailable physical evidence")
        self.assertEqual(report["hardware_operations"], [])

    def test_next_high_priority_entry_programs_exact_register_order(self) -> None:
        entries = self.entries()
        self.loaded.open_cfw_test_mspi_program_dma_reset(0)
        self.assertEqual(
            self.loaded.open_cfw_test_mspi_program_dma_run(2, 1, 3, entries), 0)
        self.assertEqual(self.values(0)[0], 1)
        self.assertEqual((self.values(1)[0], self.values(2)[0]), (4, 18))
        base = 0x40062000
        self.assertEqual(self.values(3)[0], 5)
        self.assertEqual(self.values(4, 5),
                         [base + 0x100, base + 0x108, base + 0x10C,
                          base + 0x110, base + 0x100])
        self.assertEqual(self.values(5, 5),
                         [0, 0x11110002, 0x22220002, 0x33330002, 0x44440002])

    def test_index_wrap_selects_entry_zero(self) -> None:
        entries = self.entries()
        self.loaded.open_cfw_test_mspi_program_dma_reset(0)
        self.assertEqual(
            self.loaded.open_cfw_test_mspi_program_dma_run(0, 2, 3, entries), 0)
        self.assertEqual(self.values(5, 5),
                         [0, 0x11110000, 0x22220000, 0x33330000, 0x44440000])

    def test_clock_failure_short_circuits_all_mmio(self) -> None:
        entries = self.entries()
        self.loaded.open_cfw_test_mspi_program_dma_reset(7)
        self.assertEqual(
            self.loaded.open_cfw_test_mspi_program_dma_run(1, 0, 3, entries), 7)
        self.assertEqual(self.values(0)[0], 1)
        self.assertEqual(self.values(3)[0], 0)

    def test_clock_user_preserves_uint8_conversion(self) -> None:
        entries = self.entries()
        self.loaded.open_cfw_test_mspi_program_dma_reset(9)
        self.assertEqual(
            self.loaded.open_cfw_test_mspi_program_dma_run(250, 0, 3, entries), 9)
        self.assertEqual(self.values(2)[0], 10)


if __name__ == "__main__":
    unittest.main()
