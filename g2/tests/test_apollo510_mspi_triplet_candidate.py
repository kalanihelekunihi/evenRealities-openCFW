#!/usr/bin/env python3

from __future__ import annotations

import ctypes
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_apollo510_mspi_triplet_candidate.py"
CANDIDATE = (
    ROOT
    / "components/shared/ambiqsuite/runtime_apollo510_mspi_stock_abi_candidate.c"
)
INCLUDE = CANDIDATE.parent
AMBIQ_ROOT = ROOT / "third_party/ambiqsuite-apollo510"
AMBIQ_SOURCE = AMBIQ_ROOT / "mcu/apollo510/hal/mcu/am_hal_mspi.c"
CMSIS_CORE = ROOT / "third_party/cmsis-core/CMSIS/Core/Include"


def load_analyzer():
    spec = importlib.util.spec_from_file_location(
        "analyze_g2_apollo510_mspi_triplet_candidate",
        ANALYZER,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load Apollo510 MSPI triplet analyzer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


HOST_FIXTURE = r"""
#include <stdint.h>
#include "runtime_apollo510_mspi_stock_abi_candidate.h"

static uint32_t calls;
static uint32_t last_request;
static void *last_handle;
static void *last_configuration;

uint32_t am_hal_mspi_control(
    void *handle,
    uint32_t request,
    void *configuration
)
{
    calls += 1u;
    last_request = request;
    last_handle = handle;
    last_configuration = configuration;
    return 0xa5000000u | request;
}

void fixture_reset(void)
{
    calls = 0u;
    last_request = 0xffffffffu;
    last_handle = 0;
    last_configuration = 0;
}

uint32_t fixture_calls(void) { return calls; }
uint32_t fixture_request(void) { return last_request; }
uintptr_t fixture_handle(void) { return (uintptr_t)last_handle; }
uintptr_t fixture_configuration(void) { return (uintptr_t)last_configuration; }
"""


class Apollo510MspiTripletCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("no host C compiler")
        cls.temporary = tempfile.TemporaryDirectory(prefix="opencfw-mspi-triplet-")
        temporary = Path(cls.temporary.name)
        fixture = temporary / "fixture.c"
        fixture.write_text(HOST_FIXTURE)
        library = temporary / "libmspi_triplet.so"
        subprocess.run(
            [
                compiler,
                "-std=c11",
                "-Wall",
                "-Wextra",
                "-Werror",
                "-fPIC",
                "-shared",
                "-I",
                str(INCLUDE),
                str(CANDIDATE),
                str(fixture),
                "-o",
                str(library),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        cls.library = ctypes.CDLL(str(library))
        cls.library.open_cfw_g2_mspi_request_translate.argtypes = [
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        cls.library.open_cfw_g2_mspi_request_translate.restype = ctypes.c_uint32
        cls.library.open_cfw_g2_mspi_control_stock_abi_candidate.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_void_p,
        ]
        cls.library.open_cfw_g2_mspi_control_stock_abi_candidate.restype = ctypes.c_uint32
        cls.library.fixture_calls.restype = ctypes.c_uint32
        cls.library.fixture_request.restype = ctypes.c_uint32
        cls.library.fixture_handle.restype = ctypes.c_size_t
        cls.library.fixture_configuration.restype = ctypes.c_size_t

    @classmethod
    def tearDownClass(cls) -> None:
        if hasattr(cls, "temporary"):
            cls.temporary.cleanup()

    def test_read_only_audit_binds_triplet_and_license(self) -> None:
        result = self.analyzer.run_audit()
        self.assertEqual(result["status"], "candidate-qualified")
        self.assertTrue(result["read_only"])
        self.assertFalse(result["hardware_operations"])
        self.assertEqual(result["upstream"]["license"], "BSD-3-Clause")
        self.assertEqual(
            [item["upstream_function"] for item in result["triplet"].values()],
            [
                "am_hal_mspi_device_configure",
                "am_hal_mspi_control",
                "am_hal_mspi_interrupt_service",
            ],
        )
        self.assertEqual(
            sum(len(item["direct_call_sites"]) for item in result["triplet"].values()),
            17,
        )
        self.assertFalse(result["admission"]["production_routed"])

    def test_complete_translation_matrix_executes(self) -> None:
        expected = self.analyzer.EXPECTED_TRANSLATION
        for stock in range(256):
            translated = ctypes.c_uint32(0xDEADBEEF)
            supported = self.library.open_cfw_g2_mspi_request_translate(
                stock,
                ctypes.byref(translated),
            )
            if stock in expected:
                self.assertEqual(supported, 1, stock)
                self.assertEqual(translated.value, expected[stock], stock)
            else:
                self.assertEqual(supported, 0, stock)
                self.assertEqual(translated.value, 0xFFFFFFFF, stock)

    def test_stock_low_byte_truncation_is_preserved(self) -> None:
        for high in (0x100, 0xAB00, 0xFFFF0000):
            translated = ctypes.c_uint32()
            self.assertEqual(
                self.library.open_cfw_g2_mspi_request_translate(
                    high | 18,
                    ctypes.byref(translated),
                ),
                1,
            )
            self.assertEqual(translated.value, 16)

    def test_observed_requests_dispatch_to_public_ordinals(self) -> None:
        for stock, upstream in ((16, 14), (18, 16), (21, 19), (24, 22)):
            self.library.fixture_reset()
            status = self.library.open_cfw_g2_mspi_control_stock_abi_candidate(
                ctypes.c_void_p(0x1234),
                stock,
                ctypes.c_void_p(0x5678),
            )
            self.assertEqual(status, 0xA5000000 | upstream)
            self.assertEqual(self.library.fixture_calls(), 1)
            self.assertEqual(self.library.fixture_request(), upstream)
            self.assertEqual(self.library.fixture_handle(), 0x1234)
            self.assertEqual(self.library.fixture_configuration(), 0x5678)

    def test_unsupported_requests_fail_closed_without_calling_provider(self) -> None:
        for stock in (10, 11, 40, 41, 255):
            self.library.fixture_reset()
            self.assertEqual(
                self.library.open_cfw_g2_mspi_control_stock_abi_candidate(
                    None,
                    stock,
                    None,
                ),
                6,
            )
            self.assertEqual(self.library.fixture_calls(), 0)

    def test_null_output_and_null_provider_fail_closed(self) -> None:
        self.assertEqual(
            self.library.open_cfw_g2_mspi_request_translate(18, None),
            0,
        )
        dispatch = self.library.open_cfw_g2_mspi_control_dispatch
        dispatch.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.c_void_p,
        ]
        dispatch.restype = ctypes.c_uint32
        self.assertEqual(dispatch(None, 18, None, None), 6)

    def test_translation_parser_rejects_duplicates(self) -> None:
        source = CANDIDATE.read_text().replace(
            "{  1u,  1u }",
            "{  0u,  1u }",
        )
        with self.assertRaises(self.analyzer.AuditError):
            self.analyzer.adapter_translation(source)

    def test_adapter_compiles_for_cortex_m55(self) -> None:
        compiler = shutil.which("clang")
        if compiler is None:
            self.skipTest("clang is unavailable")
        with tempfile.TemporaryDirectory(prefix="opencfw-mspi-arm-") as directory:
            output = Path(directory) / "adapter.o"
            subprocess.run(
                [
                    compiler,
                    "--target=arm-none-eabi",
                    "-mcpu=cortex-m55",
                    "-mthumb",
                    "-std=c11",
                    "-Oz",
                    "-ffreestanding",
                    "-fno-builtin",
                    "-ffunction-sections",
                    "-fdata-sections",
                    "-Wall",
                    "-Wextra",
                    "-Werror",
                    "-I",
                    str(INCLUDE),
                    "-c",
                    str(CANDIDATE),
                    "-o",
                    str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            data = output.read_bytes()
            self.assertEqual(data[:4], b"\x7fELF")
            self.assertEqual(data[18:20], b"(\x00")  # EM_ARM == 40

    def test_complete_upstream_translation_unit_exposes_triplet_sections(self) -> None:
        compiler = shutil.which("clang")
        if compiler is None:
            self.skipTest("clang is unavailable")
        with tempfile.TemporaryDirectory(prefix="opencfw-mspi-upstream-") as directory:
            output = Path(directory) / "am_hal_mspi.o"
            subprocess.run(
                [
                    compiler,
                    "--target=arm-none-eabi",
                    "-mcpu=cortex-m55",
                    "-mthumb",
                    "-Oz",
                    "-ffreestanding",
                    "-fno-builtin",
                    "-ffunction-sections",
                    "-fdata-sections",
                    "-Wno-unused-function",
                    "-I",
                    str(AMBIQ_ROOT / "mcu/apollo510"),
                    "-I",
                    str(AMBIQ_ROOT / "mcu/apollo510/hal"),
                    "-I",
                    str(AMBIQ_ROOT / "CMSIS/AmbiqMicro/Include"),
                    "-I",
                    str(CMSIS_CORE),
                    "-c",
                    str(AMBIQ_SOURCE),
                    "-o",
                    str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            data = output.read_bytes()
            for name in (
                b".text.am_hal_mspi_device_configure",
                b".text.am_hal_mspi_control",
                b".text.am_hal_mspi_interrupt_service",
            ):
                self.assertIn(name, data)

    def test_json_cli_is_machine_readable_and_software_only(self) -> None:
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            [sys.executable, str(ANALYZER), "--json"],
            cwd=ROOT,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)
        self.assertTrue(result["request_abi"]["all_observed_requests_supported"])
        self.assertEqual(result["request_abi"]["stock_only_unsupported"], [10, 11])
        self.assertFalse(result["admission"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
