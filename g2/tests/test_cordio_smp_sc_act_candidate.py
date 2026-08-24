#!/usr/bin/env python3
from __future__ import annotations

import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/cordio_smp_sc_act_host.c"


class CordioSmpScActCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        output = Path(cls.temp.name) / "libsmp_sc_act.so"
        subprocess.run(
            [
                "clang", "-std=c11", "-shared", "-fPIC", "-O2",
                "-Wall", "-Wextra", "-Werror", str(FIXTURE),
                "-o", str(output),
            ],
            check=True,
        )
        cls.lib = ctypes.CDLL(str(output))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def check(self, suffix: str) -> None:
        function = getattr(self.lib, "open_cfw_test_smp_sc_act_" + suffix)
        function.restype = ctypes.c_int
        self.assertEqual(function(), 0)

    def test_address_concatenation(self) -> None:
        self.check("address_contract")

    def test_g2_hybrid_pairing_rule(self) -> None:
        self.check("pairing_hybrid_contract")

    def test_pairing_fail_closed_paths(self) -> None:
        self.check("pairing_failure_contract")

    def test_authentication_and_public_key_selection(self) -> None:
        self.check("auth_and_selection_contract")

    def test_passkey_and_cleanup(self) -> None:
        self.check("passkey_cleanup_contract")

    def test_crypto_construction(self) -> None:
        self.check("crypto_contract")


if __name__ == "__main__":
    unittest.main()
