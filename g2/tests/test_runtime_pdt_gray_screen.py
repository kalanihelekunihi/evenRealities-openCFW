#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RuntimePdtGrayScreenTests(unittest.TestCase):
    def test_registered_abi_and_symmetric_gray_bands(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / "pdt-gray-screen-host"
            subprocess.run([
                "clang", "-std=c11", "-Wall", "-Wextra", "-Werror",
                str(ROOT / "tests/fixtures/pdt_gray_screen_host.c"),
                "-o", str(binary),
            ], check=True)
            subprocess.run([str(binary)], check=True)


if __name__ == "__main__":
    unittest.main()
