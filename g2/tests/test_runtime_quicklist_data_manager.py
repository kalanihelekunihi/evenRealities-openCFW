#!/usr/bin/env python3
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RuntimeQuicklistDataManagerTests(unittest.TestCase):
    def test_record_and_packet_state_machine(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / "quicklist-host"
            subprocess.run([
                "clang", "-std=c11", "-Wall", "-Wextra", "-Werror",
                str(ROOT / "tests/fixtures/quicklist_data_manager_host.c"),
                "-o", str(binary),
            ], check=True)
            subprocess.run([str(binary)], check=True)


if __name__ == "__main__":
    unittest.main()
