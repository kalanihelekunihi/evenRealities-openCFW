#!/usr/bin/env python3
"""Behavior and Cortex-M0+ build tests for the charging-case protocol."""

from __future__ import annotations

import ctypes
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/shared/case/runtime_case_uart_update.c"
FIXTURE = ROOT / "tests/fixtures/case_uart_update_host.c"


class CaseUartUpdateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory(prefix="open-cfw-case-uart-")
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        library = Path(cls.temp.name) / ("case_uart_update" + suffix)
        command = ["clang", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror"]
        command += ["-dynamiclib"] if platform.system() == "Darwin" else ["-shared", "-fPIC"]
        command += [str(FIXTURE), "-o", str(library)]
        subprocess.run(command, cwd=ROOT, check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(library))
        for name in (
            "open_cfw_test_case_frame_scenario",
            "open_cfw_test_case_checksum_scenario",
            "open_cfw_test_case_offer_chunk_scenario",
            "open_cfw_test_case_retry_scenario",
            "open_cfw_test_case_ota_scenario",
        ):
            getattr(cls.lib, name).restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_frame_search_bounds_and_checksum(self) -> None:
        self.assertEqual(self.lib.open_cfw_test_case_frame_scenario(), 0x1F)

    def test_big_endian_word_sum(self) -> None:
        self.assertEqual(self.lib.open_cfw_test_case_checksum_scenario(), 0x03)

    def test_ota_offer_and_chunk_checks(self) -> None:
        self.assertEqual(self.lib.open_cfw_test_case_offer_chunk_scenario(), 0x1F)

    def test_symmetric_retry_bound_and_failure_fill(self) -> None:
        self.assertEqual(self.lib.open_cfw_test_case_retry_scenario(), 0x1F)

    def test_ota_sequence_preserves_serial_before_programming(self) -> None:
        self.assertEqual(self.lib.open_cfw_test_case_ota_scenario(), 0x1F)

    def test_freestanding_cortex_m0plus_compile(self) -> None:
        clang = shutil.which("clang")
        self.assertIsNotNone(clang)
        with tempfile.TemporaryDirectory(prefix="open-cfw-case-target-") as tmp:
            obj = Path(tmp) / "case.o"
            subprocess.run(
                [
                    clang, "--target=thumbv6m-none-eabi", "-mthumb",
                    "-mcpu=cortex-m0plus", "-O2", "-ffreestanding",
                    "-fno-builtin", "-ffunction-sections", "-fdata-sections",
                    "-Wall", "-Wextra", "-Werror", "-I" + str(SOURCE.parent),
                    "-c", str(SOURCE), "-o", str(obj),
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
            )
            self.assertGreater(obj.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
