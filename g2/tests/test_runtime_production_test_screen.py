#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RuntimeProductionTestScreenTests(unittest.TestCase):
    def test_registered_abi_and_three_by_three_grid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / "production-test-screen-host"
            subprocess.run([
                "clang", "-std=c11", "-Wall", "-Wextra", "-Werror",
                str(ROOT / "tests/fixtures/production_test_screen_host.c"),
                "-o", str(binary),
            ], check=True)
            subprocess.run([str(binary)], check=True)


if __name__ == "__main__":
    unittest.main()
