#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RuntimeAtCoreTests(unittest.TestCase):
    def test_init_parse_dispatch_output_and_callback_policy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / "at-core-host"
            subprocess.run([
                "clang", "-std=c11", "-Wall", "-Wextra", "-Werror",
                str(ROOT / "tests/fixtures/at_core_host.c"),
                "-o", str(binary),
            ], check=True)
            subprocess.run([str(binary)], check=True)


if __name__ == "__main__":
    unittest.main()
