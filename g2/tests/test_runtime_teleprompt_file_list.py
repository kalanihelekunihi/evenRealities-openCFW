#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RuntimeTelepromptFileListTests(unittest.TestCase):
    def test_copy_get_reset_and_null_policy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / "teleprompt-file-list-host"
            subprocess.run([
                "clang", "-std=c11", "-Wall", "-Wextra", "-Werror",
                str(ROOT / "tests/fixtures/teleprompt_file_list_host.c"),
                "-o", str(binary),
            ], check=True)
            subprocess.run([str(binary)], check=True)


if __name__ == "__main__":
    unittest.main()
