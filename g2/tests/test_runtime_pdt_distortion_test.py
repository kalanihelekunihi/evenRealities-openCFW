#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RuntimePdtDistortionTestTests(unittest.TestCase):
    def test_registered_abi_and_nested_resource_layout(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / "pdt-distortion-test-host"
            subprocess.run([
                "clang", "-std=c11", "-Wall", "-Wextra", "-Werror",
                str(ROOT / "tests/fixtures/pdt_distortion_test_host.c"),
                "-o", str(binary),
            ], check=True)
            subprocess.run([str(binary)], check=True)


if __name__ == "__main__":
    unittest.main()
