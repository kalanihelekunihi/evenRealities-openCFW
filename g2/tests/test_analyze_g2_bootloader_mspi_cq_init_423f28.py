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
ANALYZER = ROOT / "tools/analyze_g2_bootloader_mspi_cq_init_423f28.py"
BOUNDARY_DIR = ROOT / "research/admission/bootloader_mspi_cq_init_423f28"
BOUNDARY = BOUNDARY_DIR / "runtime_bootloader_mspi_cq_init_boundary.c"
HEADER = BOUNDARY.with_suffix(".h")
PROVIDER_FRAGMENT = BOUNDARY_DIR / "upstream_am_hal_cmdq_init_fragment.c"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_cq_init_423f28.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mspi_cq_init_host.c"


class Config(ctypes.Structure):
    _fields_ = (
        ("cmdq_size", ctypes.c_uint32),
        ("cmdq_buffer", ctypes.POINTER(ctypes.c_uint32)),
        ("priority", ctypes.c_uint8),
    )


CMDQ_INIT = ctypes.CFUNCTYPE(
    ctypes.c_uint32, ctypes.c_void_p, ctypes.c_uint8,
    ctypes.POINTER(Config), ctypes.c_uint32,
)


class Ports(ctypes.Structure):
    _fields_ = (("context", ctypes.c_void_p), ("cmdq_init", CMDQ_INIT))


class Descriptor(ctypes.Structure):
    _fields_ = (
        ("stock_start", ctypes.c_uint32), ("stock_end", ctypes.c_uint32),
        ("cmdq_init_start", ctypes.c_uint32), ("cmdq_init_end", ctypes.c_uint32),
        ("mspi_state_base", ctypes.c_uint32), ("mspi_state_stride", ctypes.c_uint32),
        ("cmdq_handle_offset", ctypes.c_uint32), ("cmdq_interface_base", ctypes.c_uint32),
        ("cmdq_interface_count", ctypes.c_uint32), ("cmdq_state_base", ctypes.c_uint32),
        ("cmdq_register_table", ctypes.c_uint32),
        ("upstream_function", ctypes.c_char_p), ("upstream_provider", ctypes.c_char_p),
        ("upstream_commit", ctypes.c_char_p), ("source_license", ctypes.c_char_p),
        ("blocker", ctypes.c_char_p), ("status", ctypes.c_int),
    )


class BootloaderMspiCqInitBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("CC") or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("clang is required")
        cls.temporary = tempfile.TemporaryDirectory(prefix="open-cfw-mspi-cq-init-")
        cls.output = Path(cls.temporary.name)
        library = cls.output / ("cq-init.dylib" if sys.platform == "darwin" else "cq-init.so")
        command = [cls.clang, "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                   str(BOUNDARY)]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        command += ["-o", str(library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.loaded.open_cfw_bootloader_mspi_cq_init_boundary.restype = ctypes.POINTER(Descriptor)
        cls.loaded.open_cfw_bootloader_mspi_cq_init_admission_status.restype = ctypes.c_int
        cls.loaded.open_cfw_bootloader_mspi_cq_init_model.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(Ports),
        ]
        cls.loaded.open_cfw_bootloader_mspi_cq_init_model.restype = ctypes.c_uint32
        production_library = cls.output / (
            "cq-init-production.dylib" if sys.platform == "darwin"
            else "cq-init-production.so"
        )
        production_command = [cls.clang, "-std=c11", "-O2", "-Wall", "-Wextra",
                              "-Werror", str(FIXTURE)]
        production_command += (
            ["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]
        )
        production_command += ["-o", str(production_library)]
        subprocess.run(production_command, check=True, capture_output=True, text=True)
        cls.production = ctypes.CDLL(str(production_library))
        cls.production.open_cfw_bootloader_mspi_cq_init_423f28.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(Ports),
        ]
        cls.production.open_cfw_bootloader_mspi_cq_init_423f28.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_analyzer_closes_source_provider_and_short_enum_mismatch(self) -> None:
        completed = subprocess.run([sys.executable, str(ANALYZER), "--json"], cwd=ROOT,
                                   check=True, capture_output=True, text=True)
        report = json.loads(completed.stdout)
        self.assertEqual(
            report["status"],
            "implemented-in-source / hardware-validation-blocked-by-unavailable-physical-evidence",
        )
        self.assertEqual(report["identity"]["function"], "mspi_cq_init")
        self.assertEqual(report["identity"]["provider"], "am_hal_cmdq_init")
        self.assertEqual(report["identity"]["license"], "BSD-3-Clause")
        self.assertEqual(report["stock"]["bytes"], 44)
        self.assertEqual(report["stock"]["sole_caller"], 0x0042509C)
        self.assertEqual(report["toolchain"]["upstream_default_enum_bytes"], 40)
        self.assertEqual(report["toolchain"]["upstream_short_enum_bytes"], 44)
        self.assertTrue(report["toolchain"]["exact_match"])
        self.assertTrue(report["production"]["routed"])
        self.assertEqual(
            report["production"]["source_owned_bytes"]
            + report["production"]["retained_official_bytes"],
            146994,
        )
        self.assertEqual(report["production"]["next_frontier"], 0x00423F54)
        self.assertEqual(report["production"]["local_successor"], {
            "start": 0x00423F54,
            "end": 0x00423F8E,
            "address_status": "source_compiled",
        })
        self.assertTrue(report["production"]["next_identity"])
        self.assertEqual(
            report["hardware_validation"],
            "blocked by unavailable physical evidence",
        )
        self.assertIn("authorized G2 qualification", report["hardware_gate"]["required_future_evidence"])
        self.assertEqual(report["hardware_operations"], [])

    def test_descriptor_pins_complete_bounded_provider_graph(self) -> None:
        descriptor = self.loaded.open_cfw_bootloader_mspi_cq_init_boundary().contents
        self.assertEqual((descriptor.stock_start, descriptor.stock_end),
                         (0x00423F28, 0x00423F54))
        self.assertEqual((descriptor.cmdq_init_start, descriptor.cmdq_init_end),
                         (0x00427794, 0x00427878))
        self.assertEqual((descriptor.mspi_state_base, descriptor.mspi_state_stride,
                          descriptor.cmdq_handle_offset), (0x2001CAA0, 0x8D0, 0x828))
        self.assertEqual((descriptor.cmdq_interface_base, descriptor.cmdq_interface_count),
                         (8, 12))
        self.assertEqual((descriptor.cmdq_state_base, descriptor.cmdq_register_table),
                         (0x200262F0, 0x00430880))
        self.assertEqual(descriptor.source_license, b"BSD-3-Clause")
        self.assertIn(b"short-enum ABI", descriptor.blocker)
        self.assertEqual(descriptor.status, 1)
        self.assertEqual(self.loaded.open_cfw_bootloader_mspi_cq_init_admission_status(), 1)

    def test_model_builds_exact_config_and_handle_slot(self) -> None:
        calls: list[tuple[int, int, int, int, int]] = []
        buffer = (ctypes.c_uint32 * 8)(*range(8))

        @CMDQ_INIT
        def provider(_context, interface, config, slot):
            calls.append((interface, config.contents.cmdq_size,
                          config.contents.priority,
                          ctypes.addressof(config.contents.cmdq_buffer.contents), slot))
            return 9

        self.callbacks = (provider,)
        ports = Ports(None, provider)
        result = self.production.open_cfw_bootloader_mspi_cq_init_423f28(
            2, 7, buffer, ctypes.byref(ports))
        self.assertEqual(result, 9)
        self.assertEqual(calls, [(10, 3, 1, ctypes.addressof(buffer),
                                  0x2001CAA0 + 2 * 0x8D0 + 0x828)])

    def test_model_preserves_wrapper_lack_of_prevalidation(self) -> None:
        calls: list[tuple[int, int]] = []

        @CMDQ_INIT
        def provider(_context, interface, _config, slot):
            calls.append((interface, slot))
            return 5

        self.callbacks = (provider,)
        ports = Ports(None, provider)
        self.assertEqual(self.production.open_cfw_bootloader_mspi_cq_init_423f28(
            4, 4, None, ctypes.byref(ports)), 5)
        self.assertEqual(calls, [(12, 0x2001CAA0 + 4 * 0x8D0 + 0x828)])

    def test_model_preserves_uint8_enum_conversion_and_u32_address_wrap(self) -> None:
        calls: list[tuple[int, int]] = []

        @CMDQ_INIT
        def provider(_context, interface, _config, slot):
            calls.append((interface, slot))
            return 0

        self.callbacks = (provider,)
        ports = Ports(None, provider)
        module = 0xFFFFFFFA
        self.assertEqual(self.production.open_cfw_bootloader_mspi_cq_init_423f28(
            module, 0, None, ctypes.byref(ports)), 0)
        expected_slot = (0x2001CAA0 + module * 0x8D0 + 0x828) & 0xFFFFFFFF
        self.assertEqual(calls, [(2, expected_slot)])

    def test_missing_provider_is_fail_closed_and_has_no_side_effect(self) -> None:
        self.assertEqual(self.production.open_cfw_bootloader_mspi_cq_init_423f28(
            0, 4, None, None), 0xFFFFFFFF)

    def test_boundary_cross_compiles_and_provider_fragment_keeps_bsd_terms(self) -> None:
        for compiler in (Path("/usr/bin/clang"), Path("/opt/homebrew/opt/llvm@22/bin/clang")):
            if not compiler.is_file():
                continue
            output = self.output / ("apple-boundary.o" if compiler == Path("/usr/bin/clang")
                                    else "homebrew-boundary.o")
            subprocess.run([str(compiler), "--target=arm-none-eabi", "-mcpu=cortex-m55",
                            "-mthumb", "-std=c11", "-Oz", "-ffreestanding", "-fno-builtin",
                            "-Wall", "-Wextra", "-Werror", "-c", str(BOUNDARY), "-o", str(output)],
                           check=True, capture_output=True, text=True)
            self.assertGreater(output.stat().st_size, 0)
        project = BOUNDARY.read_text(encoding="utf-8") + HEADER.read_text(encoding="utf-8")
        upstream = PROVIDER_FRAGMENT.read_text(encoding="utf-8")
        self.assertIn("SPDX-License-Identifier: MIT", project)
        self.assertIn("SPDX-License-Identifier: BSD-3-Clause", upstream)
        self.assertIn("Copyright (c) 2025, Ambiq Micro, Inc.", upstream)
        self.assertIn("This fragment is not compiled", upstream)
        self.assertIn("open_cfw_bootloader_mspi_cq_init_423f28",
                      SOURCE.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
