from __future__ import annotations

import ctypes
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_bootloader_mspi_fifo_write_423e40.py"
BOUNDARY_DIR = ROOT / "research/admission/bootloader_mspi_fifo_write_423e40"
BOUNDARY = BOUNDARY_DIR / "runtime_bootloader_mspi_fifo_write_boundary.c"
HEADER = BOUNDARY.with_suffix(".h")
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_fifo_write_423e40.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mspi_fifo_write_host.c"

WRITE = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32)
STATUS = ctypes.CFUNCTYPE(
    ctypes.c_uint32, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32,
    ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint8,
)


class Descriptor(ctypes.Structure):
    _fields_ = (
        ("stock_start", ctypes.c_uint32),
        ("stock_end", ctypes.c_uint32),
        ("status_check_start", ctypes.c_uint32),
        ("delay_start", ctypes.c_uint32),
        ("bootrom_delay_start", ctypes.c_uint32),
        ("mspi_base", ctypes.c_uint32),
        ("mspi_stride", ctypes.c_uint32),
        ("txfifo_offset", ctypes.c_uint32),
        ("txentries_offset", ctypes.c_uint32),
        ("txentries_mask", ctypes.c_uint32),
        ("txentries_full", ctypes.c_uint32),
        ("module_count", ctypes.c_uint32),
        ("upstream_function", ctypes.c_char_p),
        ("upstream_provider", ctypes.c_char_p),
        ("upstream_commit", ctypes.c_char_p),
        ("source_license", ctypes.c_char_p),
        ("blocker", ctypes.c_char_p),
        ("status", ctypes.c_int),
    )


class Ports(ctypes.Structure):
    _fields_ = (("context", ctypes.c_void_p), ("write_word", WRITE), ("status_check", STATUS))


class BootloaderMspiFifoWriteBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("CC") or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("clang is required")
        cls.temporary = tempfile.TemporaryDirectory(prefix="open-cfw-mspi-fifo-")
        cls.output = Path(cls.temporary.name)
        library = cls.output / (
            "mspi-fifo.dylib" if sys.platform == "darwin" else "mspi-fifo.so"
        )
        command = [
            cls.clang, "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
            str(BOUNDARY),
        ]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        command += ["-o", str(library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.loaded.open_cfw_bootloader_mspi_fifo_write_boundary.restype = ctypes.POINTER(Descriptor)
        cls.loaded.open_cfw_bootloader_mspi_fifo_write_admission_status.restype = ctypes.c_int
        cls.loaded.open_cfw_bootloader_mspi_fifo_write_model.argtypes = [
            ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32,
            ctypes.c_uint32, ctypes.POINTER(Ports),
        ]
        cls.loaded.open_cfw_bootloader_mspi_fifo_write_model.restype = ctypes.c_uint32
        production_library = cls.output / (
            "mspi-fifo-production.dylib" if sys.platform == "darwin"
            else "mspi-fifo-production.so"
        )
        production_command = [
            cls.clang, "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
            str(FIXTURE),
        ]
        production_command += (
            ["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]
        )
        production_command += ["-o", str(production_library)]
        subprocess.run(production_command, check=True, capture_output=True, text=True)
        cls.production = ctypes.CDLL(str(production_library))
        cls.production.open_cfw_bootloader_mspi_fifo_write_423e40.argtypes = [
            ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32,
            ctypes.c_uint32, ctypes.POINTER(Ports),
        ]
        cls.production.open_cfw_bootloader_mspi_fifo_write_423e40.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_analyzer_closes_exact_production_source_and_hardware_block(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ANALYZER), "--json"], cwd=ROOT,
            check=True, capture_output=True, text=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(
            report["status"],
            "implemented-in-source / hardware-validation-blocked-by-unavailable-physical-evidence",
        )
        self.assertEqual(report["identity"]["function"], "mspi_fifo_write")
        self.assertEqual(report["identity"]["provider"], "am_hal_delay_us_status_check")
        self.assertEqual(report["identity"]["license"], "BSD-3-Clause")
        self.assertEqual(report["stock"]["bytes"], 74)
        self.assertEqual(report["stock"]["sole_caller"], 0x0042640C)
        self.assertEqual(report["toolchain"]["upstream_semantic_clang_bytes"], 80)
        self.assertEqual(report["toolchain"]["production_bytes"], 74)
        self.assertTrue(report["toolchain"]["exact_match"])
        self.assertTrue(report["production"]["routed"])
        self.assertEqual(
            report["production"]["source_owned_bytes"]
            + report["production"]["retained_official_bytes"],
            147350,
        )
        self.assertEqual(report["production"]["next_frontier"], 0x00423F28)
        self.assertEqual(report["production"]["local_successor"], {
            "start": 0x00423E8A,
            "end": 0x00423F28,
            "address_status": "source_compiled",
        })
        self.assertEqual(report["hardware_validation"], "blocked by unavailable physical evidence")
        self.assertIn("authorized G2 qualification", report["hardware_gate"]["required_future_evidence"])
        self.assertEqual(report["hardware_operations"], [])

    def test_descriptor_preserves_upstream_provider_license_and_rom_boundary(self) -> None:
        descriptor = self.loaded.open_cfw_bootloader_mspi_fifo_write_boundary().contents
        self.assertEqual(
            (descriptor.stock_start, descriptor.stock_end), (0x00423E40, 0x00423E8A)
        )
        self.assertEqual(
            (descriptor.status_check_start, descriptor.delay_start,
             descriptor.bootrom_delay_start),
            (0x0041D246, 0x0041D1C0, 0x40),
        )
        self.assertEqual(
            (descriptor.mspi_base, descriptor.mspi_stride,
             descriptor.txfifo_offset, descriptor.txentries_offset,
             descriptor.txentries_mask, descriptor.txentries_full,
             descriptor.module_count),
            (0x40060000, 0x1000, 0x10, 0x18, 0x3F, 0x10, 4),
        )
        self.assertEqual(descriptor.source_license, b"BSD-3-Clause")
        self.assertIn(b"mspi_fifo_write", descriptor.upstream_function)
        self.assertIn(b"IAR compiler", descriptor.blocker)
        self.assertEqual(descriptor.status, 1)
        self.assertEqual(
            self.loaded.open_cfw_bootloader_mspi_fifo_write_admission_status(), 1
        )

    def test_model_rejects_out_of_range_module_without_side_effects(self) -> None:
        writes: list[tuple[int, int]] = []
        checks: list[tuple[int, ...]] = []

        @WRITE
        def write(_context, address, value):
            writes.append((address, value))

        @STATUS
        def check(_context, timeout, address, mask, value, is_equal):
            checks.append((timeout, address, mask, value, is_equal))
            return 0

        ports = Ports(None, write, check)
        data = (ctypes.c_uint32 * 1)(0xA5)
        self.assertEqual(
            self.production.open_cfw_bootloader_mspi_fifo_write_423e40(
                4, data, 4, 99, ctypes.byref(ports)
            ),
            5,
        )
        self.assertEqual(writes, [])
        self.assertEqual(checks, [])

    def test_model_rounds_partial_byte_count_to_words_and_returns_last_status(self) -> None:
        writes: list[tuple[int, int]] = []
        checks: list[tuple[int, ...]] = []
        results = [4, 0]

        @WRITE
        def write(_context, address, value):
            writes.append((address, value))

        @STATUS
        def check(_context, timeout, address, mask, value, is_equal):
            checks.append((timeout, address, mask, value, is_equal))
            return results.pop(0)

        ports = Ports(None, write, check)
        data = (ctypes.c_uint32 * 2)(0x11223344, 0x55667788)
        self.assertEqual(
            self.production.open_cfw_bootloader_mspi_fifo_write_423e40(
                2, data, 5, 77, ctypes.byref(ports)
            ),
            0,
        )
        self.assertEqual(
            writes,
            [(0x40062010, 0x11223344), (0x40062010, 0x55667788)],
        )
        self.assertEqual(
            checks,
            [(77, 0x40062018, 0x3F, 0x10, 0),
             (77, 0x40062018, 0x3F, 0x10, 0)],
        )

    def test_zero_length_returns_success_without_touching_mmio_model(self) -> None:
        calls = 0

        @WRITE
        def write(_context, _address, _value):
            nonlocal calls
            calls += 1

        @STATUS
        def check(_context, _timeout, _address, _mask, _value, _equal):
            nonlocal calls
            calls += 1
            return 9

        ports = Ports(None, write, check)
        data = (ctypes.c_uint32 * 1)(0)
        self.assertEqual(
            self.production.open_cfw_bootloader_mspi_fifo_write_423e40(
                0, data, 0, 1, ctypes.byref(ports)
            ),
            0,
        )
        self.assertEqual(calls, 0)

    def test_boundary_cross_compiles_without_hardware_or_runtime_dependencies(self) -> None:
        for compiler in (Path("/usr/bin/clang"), Path("/opt/homebrew/opt/llvm@22/bin/clang")):
            if not compiler.is_file():
                continue
            output = self.output / (compiler.parent.name + "-boundary.o")
            subprocess.run(
                [str(compiler), "--target=arm-none-eabi", "-mcpu=cortex-m55",
                 "-mthumb", "-std=c11", "-Oz", "-ffreestanding", "-fno-builtin",
                 "-Wall", "-Wextra", "-Werror", "-c", str(BOUNDARY), "-o", str(output)],
                check=True, capture_output=True, text=True,
            )
            self.assertGreater(output.stat().st_size, 0)
        text = BOUNDARY.read_text(encoding="utf-8") + HEADER.read_text(encoding="utf-8")
        self.assertIn("SPDX-License-Identifier: MIT", text)
        self.assertIn("EXACT_TOOLCHAIN_UNRESOLVED", text)
        production = SOURCE.read_text(encoding="utf-8")
        self.assertIn("open_cfw_bootloader_mspi_fifo_write_423e40", production)
        self.assertIn("open_cfw_bootloader_retained_status_check_41d246", production)


if __name__ == "__main__":
    unittest.main()
