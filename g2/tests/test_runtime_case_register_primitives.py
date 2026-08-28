#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Behavior and Cortex-M0+ closure tests for case register primitives."""

from __future__ import annotations

import ctypes
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "components/shared/case"
SOURCE = CASE / "runtime_case_register_primitives.c"
FIXTURE = ROOT / "tests/fixtures/case_register_primitives_host.c"


class CaseRegisterPrimitiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("C compiler unavailable")
        cls.temp = tempfile.TemporaryDirectory(prefix="open-cfw-case-register-")
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        library = Path(cls.temp.name) / ("case_register" + suffix)
        command = [compiler, "-std=c11", "-Wall", "-Wextra", "-Werror"]
        command += ["-dynamiclib"] if platform.system() == "Darwin" else ["-shared", "-fPIC"]
        command += [str(FIXTURE), "-o", str(library)]
        subprocess.run(command, cwd=ROOT, check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_test_case_register_primitives.restype = ctypes.c_uint32
        cls.lib.open_cfw_test_case_register_null_guards.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_all_recovered_field_semantics(self) -> None:
        self.assertEqual(self.lib.open_cfw_test_case_register_primitives(), 0x3FF)

    def test_absent_state_fails_closed(self) -> None:
        self.assertEqual(self.lib.open_cfw_test_case_register_null_guards(), 0)

    def test_freestanding_cortex_m0plus_compile(self) -> None:
        clang = shutil.which("clang")
        if clang is None:
            self.skipTest("clang unavailable")
        output = Path(self.temp.name) / "case-register.o"
        subprocess.run([
            clang, "--target=thumbv6m-none-eabi", "-mthumb",
            "-mcpu=cortex-m0plus", "-O2", "-ffreestanding", "-fno-builtin",
            "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
            "-Werror", "-I" + str(CASE), "-c", str(SOURCE), "-o", str(output),
        ], cwd=ROOT, check=True, capture_output=True)
        self.assertGreater(output.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
