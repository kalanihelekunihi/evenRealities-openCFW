#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RuntimeServiceTimeTests(unittest.TestCase):
    def test_calendar_timezone_rtc_peer_and_retry_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / "service-time-host"
            subprocess.run([
                "clang", "-std=c11", "-Wall", "-Wextra", "-Werror",
                str(ROOT / "tests/fixtures/service_time_host.c"),
                "-o", str(binary),
            ], check=True)
            subprocess.run([str(binary)], check=True)


if __name__ == "__main__":
    unittest.main()
