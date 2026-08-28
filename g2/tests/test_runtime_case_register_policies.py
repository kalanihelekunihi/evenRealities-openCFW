# SPDX-License-Identifier: MIT
"""Host behavior and freestanding target tests for Case register policies."""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "components/shared/case"
SOURCE = CASE / "runtime_case_register_policies.c"
FIXTURE = ROOT / "tests/fixtures/runtime_case_register_policies_host.c"


class CaseRegisterPolicyTests(unittest.TestCase):
    def test_host_semantics_and_boundary_cases(self) -> None:
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            self.skipTest("C compiler unavailable")
        with tempfile.TemporaryDirectory(prefix="open-cfw-case-policy-host-") as raw:
            executable = Path(raw) / "case-register-policy"
            subprocess.run([
                compiler, "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                "-I", str(CASE), str(SOURCE), str(FIXTURE), "-o",
                str(executable),
            ], cwd=ROOT, check=True, capture_output=True)
            subprocess.run([str(executable)], check=True)

    def test_freestanding_cortex_m0plus_compile(self) -> None:
        clang = shutil.which("clang")
        if clang is None:
            self.skipTest("clang unavailable")
        with tempfile.TemporaryDirectory(prefix="open-cfw-case-policy-arm-") as raw:
            output = Path(raw) / "case-register-policy.o"
            subprocess.run([
                clang, "--target=thumbv6m-none-eabi", "-mthumb",
                "-mcpu=cortex-m0plus", "-std=c11", "-Oz", "-ffreestanding",
                "-fno-builtin", "-ffunction-sections", "-fdata-sections",
                "-Wall", "-Wextra", "-Werror", "-I", str(CASE), "-c",
                str(SOURCE), "-o", str(output),
            ], cwd=ROOT, check=True, capture_output=True)
            self.assertGreater(output.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
