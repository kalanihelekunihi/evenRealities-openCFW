#!/usr/bin/env python3
"""Exercise the production Cordio SMP Secure Connections main adapter."""

from __future__ import annotations

import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/cordio_smp_sc_main_host.c"


class CordioSmpScMainCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        cls.library = Path(cls.temp.name) / "cordio_smp_sc_main.so"
        subprocess.run(
            [
                "clang", "-std=c11", "-Wall", "-Wextra", "-Werror",
                "-fPIC", "-shared", str(FIXTURE), "-o", str(cls.library),
            ],
            check=True,
        )
        cls.loaded = ctypes.CDLL(str(cls.library))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def check_contract(self, name: str) -> None:
        function = getattr(self.loaded, name)
        function.restype = ctypes.c_int
        self.assertEqual(function(), 0)

    def test_init_and_scratch_lifecycle(self) -> None:
        self.check_contract("open_cfw_test_smp_sc_init_and_scratch")

    def test_allocation_and_cmac_failures_cancel_pairing(self) -> None:
        self.check_contract("open_cfw_test_smp_sc_failure_paths")

    def test_f4_input_concatenation(self) -> None:
        self.check_contract("open_cfw_test_smp_sc_f4")

    def test_secure_connections_pdus(self) -> None:
        self.check_contract("open_cfw_test_smp_sc_packets")

    def test_passkey_and_repeated_attempts(self) -> None:
        self.check_contract("open_cfw_test_smp_sc_passkey_and_attempts")

    def test_event_state_and_byte_diagnostics(self) -> None:
        self.check_contract("open_cfw_test_smp_sc_diagnostics")


if __name__ == "__main__":
    unittest.main()
