from __future__ import annotations

import os

import ctypes
import hashlib
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT_ROOT / "pwrctrl_periph_disable_mask_check.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "pwrctrl_periph_disable_mask_check_host.c"
)


class PwrctrlPeriphDisableMaskCheckTests(unittest.TestCase):
    GROUPS = (0x30000001, 0x1E, 0x1E0, 0xC0, 0x1E00)

    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "pwrctrl_periph_disable_mask_check.dylib"
            if sys.platform == "darwin"
            else "pwrctrl_periph_disable_mask_check.so"
        )
        command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(FIXTURE),
        ]
        if sys.platform == "darwin":
            command.extend(["-dynamiclib", "-o", str(library)])
        else:
            command.extend(["-shared", "-fPIC", "-o", str(library)])
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.reset_fixture = cls.loaded.open_cfw_test_disable_mask_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.check = cls.loaded.open_cfw_pwrctrl_periph_disable_mask_check
        cls.check.argtypes = [ctypes.c_uint]
        cls.check.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_disable_mask_{name}",
        )

    def test_descriptor_error_returns_true_and_truncates_enum(self) -> None:
        self.word("descriptor_result").value = 6
        self.assertEqual(self.check(0x12345678), 1)
        self.assertEqual(self.word("descriptor_peripheral").value, 0x78)
        self.assertEqual(self.word("read_count").value, 0)

    def test_each_shared_domain_detects_another_enabled_member(self) -> None:
        for group in self.GROUPS:
            self.reset_fixture()
            own = group & -group
            other = group & ~own
            self.word("status_mask").value = group
            self.word("enable_mask").value = own
            self.word("enable_value").value = other
            self.assertEqual(self.check(3), 0)
            self.assertEqual(self.word("read_count").value, 2)

    def test_empty_domain_short_circuits_true_after_one_read(self) -> None:
        self.word("enable_value").value = 0
        self.assertEqual(self.check(0), 1)
        self.assertEqual(self.word("read_count").value, 1)

    def test_requested_member_enabled_returns_true(self) -> None:
        self.word("status_mask").value = 0x1E
        self.word("enable_mask").value = 0x2
        self.word("enable_value").value = 0x1E
        self.assertEqual(self.check(2), 1)
        self.assertEqual(self.word("read_count").value, 2)

    def test_unknown_status_domain_defaults_true_without_read(self) -> None:
        self.word("status_mask").value = 0xDEADBEEF
        self.word("enable_value").value = 0xFFFFFFFF
        self.assertEqual(self.check(2), 1)
        self.assertEqual(self.word("read_count").value, 0)

    def test_randomized_stock_model(self) -> None:
        generator = random.Random(0x47F6F2)
        for _ in range(1000):
            self.reset_fixture()
            status = generator.choice(self.GROUPS + (0x55AA55AA,))
            own = generator.getrandbits(32)
            enabled = generator.getrandbits(32)
            self.word("status_mask").value = status
            self.word("enable_mask").value = own
            self.word("enable_value").value = enabled

            result = self.check(generator.getrandbits(32))

            expected = 1
            if status in self.GROUPS:
                expected = int(
                    not ((enabled & status) != 0 and (enabled & own) == 0)
                )
            self.assertEqual(result, expected)

    def test_sources_are_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "d9624ec87cea75f3119bfc57bf1411918be848476828b28b6a30658d9adbe74e",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "62a3ddfff7010dd216f4e6d5e25d7c9166c2e2597cb9625efac8dd0deb6b7e25",
        )


if __name__ == "__main__":
    unittest.main()
