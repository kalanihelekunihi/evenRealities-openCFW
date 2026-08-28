#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Host behavior and Cortex-M0+ build tests for touch policy helpers."""

from __future__ import annotations

import ctypes
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/shared/touch/runtime_touch_policy_helpers.c"
FIXTURE = ROOT / "tests/fixtures/touch_policy_helpers_host.c"


class TouchPolicyHelperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory(prefix="open-cfw-touch-policy-")
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        library = Path(cls.temp.name) / ("touch_policy" + suffix)
        command = ["clang", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror"]
        command += ["-dynamiclib"] if platform.system() == "Darwin" else ["-shared", "-fPIC"]
        command += [str(FIXTURE), "-o", str(library)]
        subprocess.run(command, cwd=ROOT, check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(library))
        for name in (
            "open_cfw_test_touch_policy_config",
            "open_cfw_test_touch_policy_provider_boundaries",
            "open_cfw_test_touch_policy_defaults",
        ):
            getattr(cls.lib, name).restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_config_read_load_and_baseline(self) -> None:
        self.assertEqual(self.lib.open_cfw_test_touch_policy_config(), 0x1F)

    def test_provider_boundaries_fail_closed(self) -> None:
        self.assertEqual(
            self.lib.open_cfw_test_touch_policy_provider_boundaries(), 0x1F
        )

    def test_defaults_and_not_ready_behavior(self) -> None:
        self.assertEqual(self.lib.open_cfw_test_touch_policy_defaults(), 0x0F)

    def test_freestanding_cortex_m0plus_compile(self) -> None:
        clang = shutil.which("clang")
        self.assertIsNotNone(clang)
        with tempfile.TemporaryDirectory(prefix="open-cfw-touch-policy-target-") as raw:
            obj = Path(raw) / "touch_policy.o"
            subprocess.run([
                clang, "--target=thumbv6m-none-eabi", "-mthumb",
                "-mcpu=cortex-m0plus", "-std=c11", "-O2", "-ffreestanding",
                "-fno-builtin", "-ffunction-sections", "-fdata-sections",
                "-Wall", "-Wextra", "-Werror", "-I" + str(SOURCE.parent),
                "-c", str(SOURCE), "-o", str(obj),
            ], cwd=ROOT, check=True, capture_output=True)
            self.assertGreater(obj.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
