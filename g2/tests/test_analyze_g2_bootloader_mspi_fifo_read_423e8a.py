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
ANALYZER = ROOT / "tools/analyze_g2_bootloader_mspi_fifo_read_423e8a.py"
BOUNDARY_DIR = ROOT / "research/admission/bootloader_mspi_fifo_read_423e8a"
BOUNDARY = BOUNDARY_DIR / "runtime_bootloader_mspi_fifo_read_boundary.c"
HEADER = BOUNDARY.with_suffix(".h")

READ = ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.c_void_p, ctypes.c_uint32)
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
        ("rxfifo_offset", ctypes.c_uint32),
        ("rxentries_offset", ctypes.c_uint32),
        ("rxentries_mask", ctypes.c_uint32),
        ("module_count", ctypes.c_uint32),
        ("upstream_function", ctypes.c_char_p),
        ("upstream_provider", ctypes.c_char_p),
        ("upstream_commit", ctypes.c_char_p),
        ("source_license", ctypes.c_char_p),
        ("blocker", ctypes.c_char_p),
        ("status", ctypes.c_int),
    )


class Ports(ctypes.Structure):
    _fields_ = (("context", ctypes.c_void_p), ("read_word", READ), ("status_check", STATUS))


class BootloaderMspiFifoReadBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("CC") or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("clang is required")
        cls.temporary = tempfile.TemporaryDirectory(prefix="open-cfw-mspi-read-")
        cls.output = Path(cls.temporary.name)
        library = cls.output / (
            "mspi-read.dylib" if sys.platform == "darwin" else "mspi-read.so"
        )
        command = [
            cls.clang, "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
            str(BOUNDARY),
        ]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        command += ["-o", str(library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.loaded.open_cfw_bootloader_mspi_fifo_read_boundary.restype = ctypes.POINTER(Descriptor)
        cls.loaded.open_cfw_bootloader_mspi_fifo_read_admission_status.restype = ctypes.c_int
        cls.loaded.open_cfw_bootloader_mspi_fifo_read_model.argtypes = [
            ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32,
            ctypes.c_uint32, ctypes.POINTER(Ports),
        ]
        cls.loaded.open_cfw_bootloader_mspi_fifo_read_model.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_analyzer_closes_identity_and_records_both_toolchain_mismatches(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ANALYZER), "--json"], cwd=ROOT,
            check=True, capture_output=True, text=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "implemented-in-source / hardware-validation-blocked-by-unavailable-physical-evidence")
        self.assertEqual(report["identity"]["function"], "mspi_fifo_read")
        self.assertEqual(report["identity"]["provider"], "am_hal_delay_us_status_check")
        self.assertEqual(report["identity"]["license"], "BSD-3-Clause")
        self.assertEqual(report["stock"]["bytes"], 158)
        self.assertEqual(report["stock"]["sole_caller"], 0x004263F6)
        self.assertEqual(report["toolchain"]["apple_clang_bytes"], 156)
        self.assertEqual(report["toolchain"]["homebrew_clang_bytes"], 148)
        self.assertEqual(report["toolchain"]["stock_bytes"], 158)
        self.assertFalse(report["toolchain"]["exact_match"])
        self.assertTrue(report["production"]["routed"])
        self.assertEqual(report["production"]["next_frontier"], 0x00423F28)
        self.assertEqual(report["production"]["local_successor"], {
            "start": 0x00423F28,
            "end": 0x00423F54,
            "address_status": "source_compiled",
        })
        self.assertEqual(
            report["production"]["source_owned_bytes"]
            + report["production"]["retained_official_bytes"],
            146994,
        )
        self.assertEqual(report["hardware_validation"], "blocked by unavailable physical evidence")
        self.assertEqual(report["hardware_operations"], [])

    def test_descriptor_pins_offsets_provider_chain_and_fail_closed_status(self) -> None:
        descriptor = self.loaded.open_cfw_bootloader_mspi_fifo_read_boundary().contents
        self.assertEqual(
            (descriptor.stock_start, descriptor.stock_end), (0x00423E8A, 0x00423F28)
        )
        self.assertEqual(
            (descriptor.status_check_start, descriptor.delay_start,
             descriptor.bootrom_delay_start),
            (0x0041D246, 0x0041D1C0, 0x40),
        )
        self.assertEqual(
            (descriptor.mspi_base, descriptor.mspi_stride,
             descriptor.rxfifo_offset, descriptor.rxentries_offset,
             descriptor.rxentries_mask, descriptor.module_count),
            (0x40060000, 0x1000, 0x14, 0x1C, 0x3F, 4),
        )
        self.assertEqual(descriptor.source_license, b"BSD-3-Clause")
        self.assertIn(b"mspi_fifo_read", descriptor.upstream_function)
        self.assertIn(b"IAR compiler", descriptor.blocker)
        self.assertEqual(descriptor.status, 1)
        self.assertEqual(self.loaded.open_cfw_bootloader_mspi_fifo_read_admission_status(), 1)

    def make_ports(
        self, words: list[int], statuses: list[int]
    ) -> tuple[Ports, list[int], list[tuple[int, ...]]]:
        reads: list[int] = []
        checks: list[tuple[int, ...]] = []
        pending_words = list(words)
        pending_statuses = list(statuses)

        @READ
        def read(_context, address):
            reads.append(address)
            return pending_words.pop(0)

        @STATUS
        def check(_context, timeout, address, mask, value, is_equal):
            checks.append((timeout, address, mask, value, is_equal))
            return pending_statuses.pop(0)

        self.callbacks = (read, check)
        return Ports(None, read, check), reads, checks

    def test_full_words_and_leftovers_are_copied_little_endian(self) -> None:
        ports, reads, checks = self.make_ports(
            [0x44332211, 0x88776655], [0, 0]
        )
        output = (ctypes.c_uint8 * 8)(*([0xAA] * 8))
        self.assertEqual(
            self.loaded.open_cfw_bootloader_mspi_fifo_read_model(
                3, output, 6, 55, ctypes.byref(ports)
            ),
            0,
        )
        self.assertEqual(list(output), [0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0xAA, 0xAA])
        self.assertEqual(reads, [0x40063014, 0x40063014])
        self.assertEqual(
            checks,
            [(55, 0x4006301C, 0x3F, 0, 0), (55, 0x4006301C, 0x3F, 0, 0)],
        )

    def test_timeout_short_circuits_before_fifo_read(self) -> None:
        ports, reads, checks = self.make_ports([0x12345678], [4])
        output = (ctypes.c_uint8 * 4)(*([0xAA] * 4))
        self.assertEqual(
            self.loaded.open_cfw_bootloader_mspi_fifo_read_model(
                1, output, 4, 9, ctypes.byref(ports)
            ),
            4,
        )
        self.assertEqual(list(output), [0xAA] * 4)
        self.assertEqual(reads, [])
        self.assertEqual(checks, [(9, 0x4006101C, 0x3F, 0, 0)])

    def test_leftover_timeout_preserves_bytes_after_completed_words(self) -> None:
        ports, reads, _checks = self.make_ports([0x04030201], [0, 7])
        output = (ctypes.c_uint8 * 6)(*([0xAA] * 6))
        self.assertEqual(
            self.loaded.open_cfw_bootloader_mspi_fifo_read_model(
                0, output, 6, 3, ctypes.byref(ports)
            ),
            7,
        )
        self.assertEqual(list(output), [1, 2, 3, 4, 0xAA, 0xAA])
        self.assertEqual(reads, [0x40060014])

    def test_invalid_module_and_zero_length_have_no_provider_side_effects(self) -> None:
        ports, reads, checks = self.make_ports([], [])
        output = (ctypes.c_uint8 * 1)(0xAA)
        self.assertEqual(
            self.loaded.open_cfw_bootloader_mspi_fifo_read_model(
                4, output, 1, 1, ctypes.byref(ports)
            ),
            5,
        )
        self.assertEqual(
            self.loaded.open_cfw_bootloader_mspi_fifo_read_model(
                0, output, 0, 1, ctypes.byref(ports)
            ),
            0,
        )
        self.assertEqual(reads, [])
        self.assertEqual(checks, [])

    def test_boundary_cross_compiles_without_runtime_or_mmio_dependencies(self) -> None:
        for compiler in (Path("/usr/bin/clang"), Path("/opt/homebrew/opt/llvm@22/bin/clang")):
            if not compiler.is_file():
                continue
            output = self.output / (compiler.parent.name + "-read-boundary.o")
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


if __name__ == "__main__":
    unittest.main()
