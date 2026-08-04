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
SOURCE = COMPONENT_ROOT / "pwrctrl_buck_ldo_override_init.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "pwrctrl_buck_ldo_override_init_host.c"
)

VRCTRL = 0x40020060
STEPS = (
    (0x00020000, 0),
    (0x00040000, 0),
    (0x00080000, 0),
    (0x00010000, 0),
    (0, 0x00000010),
    (0x0000000E, 0),
    (0x00000001, 0),
    (0, 0x00000200),
    (0x000001C0, 0),
    (0x00000020, 0),
)
UINT_MASK = 0xFFFFFFFF


def model(initial: int) -> list[int]:
    value = initial & UINT_MASK
    writes = []
    for set_mask, clear_mask in STEPS:
        value = ((value | set_mask) & ~clear_mask) & UINT_MASK
        writes.append(value)
    return writes


class PwrctrlBuckLdoOverrideInitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "pwrctrl_buck_ldo_override_init.dylib"
            if sys.platform == "darwin"
            else "pwrctrl_buck_ldo_override_init.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_buck_ldo_reset
        cls.reset_fixture.argtypes = [ctypes.c_uint]
        cls.reset_fixture.restype = None
        cls.initialize = (
            cls.loaded.open_cfw_pwrctrl_buck_ldo_override_init
        )
        cls.initialize.argtypes = []
        cls.initialize.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_buck_ldo_{name}",
        )

    @classmethod
    def words(cls, name: str) -> ctypes.Array:
        return (ctypes.c_uint * 10).in_dll(
            cls.loaded,
            f"open_cfw_test_buck_ldo_{name}",
        )

    def run_case(self, initial: int) -> list[int]:
        self.reset_fixture(initial)
        self.initialize()
        return list(self.words("write_values"))

    def test_zero_register_preserves_exact_override_order(self) -> None:
        self.assertEqual(self.run_case(0), model(0))
        self.assertEqual(self.word("read_count").value, 10)
        self.assertEqual(self.word("write_count").value, 10)
        self.assertEqual(
            list(self.words("read_addresses")),
            [VRCTRL] * 10,
        )
        self.assertEqual(
            list(self.words("write_addresses")),
            [VRCTRL] * 10,
        )

    def test_all_bits_set_preserves_unrelated_bits(self) -> None:
        writes = self.run_case(UINT_MASK)

        self.assertEqual(writes, model(UINT_MASK))
        self.assertEqual(writes[-1], UINT_MASK & ~0x210)

    def test_randomized_register_model_and_order(self) -> None:
        generator = random.Random(0x0047FE12)

        for _ in range(1000):
            initial = generator.getrandbits(32)
            self.assertEqual(self.run_case(initial), model(initial))

    def test_second_initialization_is_idempotent_but_not_elided(self) -> None:
        expected = model(0xA5A55A5A)
        self.run_case(0xA5A55A5A)
        self.assertEqual(self.run_case(expected[-1]), [expected[-1]] * 10)
        self.assertEqual(self.word("read_count").value, 10)
        self.assertEqual(self.word("write_count").value, 10)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "511fba5ad895bfcbdfe0af165cbcdeacc"
            "1d66eafd8ecbe6ab1210d67def1c671",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "2e8c45299e89cec0d6ecd1aae62f2798"
            "edb9d0d919a9af092265092954c8253a",
        )


if __name__ == "__main__":
    unittest.main()
