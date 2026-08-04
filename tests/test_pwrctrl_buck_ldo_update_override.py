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
SOURCE = COMPONENT_ROOT / "pwrctrl_buck_ldo_update_override.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "pwrctrl_buck_ldo_update_override_host.c"
)

VRCTRL = 0x40020060
MASKS = (0x00010000, 0x00000001, 0x00000020)
UINT_MASK = 0xFFFFFFFF


def model(initial: int, enable: int) -> list[int]:
    value = initial & UINT_MASK
    writes = []
    for mask in MASKS:
        value = (value & ~mask) | (mask if enable & 1 else 0)
        value &= UINT_MASK
        writes.append(value)
    return writes


class PwrctrlBuckLdoUpdateOverrideTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "pwrctrl_buck_ldo_update_override.dylib"
            if sys.platform == "darwin"
            else "pwrctrl_buck_ldo_update_override.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_buck_ldo_update_reset
        cls.reset_fixture.argtypes = [ctypes.c_uint]
        cls.reset_fixture.restype = None
        cls.update = (
            cls.loaded.open_cfw_pwrctrl_buck_ldo_update_override
        )
        cls.update.argtypes = [ctypes.c_uint]
        cls.update.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_buck_ldo_update_{name}",
        )

    @classmethod
    def words(cls, name: str) -> ctypes.Array:
        return (ctypes.c_uint * 3).in_dll(
            cls.loaded,
            f"open_cfw_test_buck_ldo_update_{name}",
        )

    def run_case(self, initial: int, enable: int) -> list[int]:
        self.reset_fixture(initial)
        self.update(enable)
        return list(self.words("write_values"))

    def test_enable_sets_each_override_in_stock_order(self) -> None:
        self.assertEqual(self.run_case(0, 1), model(0, 1))
        self.assertEqual(self.word("read_count").value, 3)
        self.assertEqual(self.word("write_count").value, 3)
        self.assertEqual(list(self.words("read_addresses")), [VRCTRL] * 3)
        self.assertEqual(list(self.words("write_addresses")), [VRCTRL] * 3)

    def test_disable_clears_only_the_three_override_bits(self) -> None:
        initial = UINT_MASK
        writes = self.run_case(initial, 0)

        self.assertEqual(writes, model(initial, 0))
        self.assertEqual(writes[-1], UINT_MASK & ~sum(MASKS))

    def test_only_the_input_low_bit_controls_the_update(self) -> None:
        initial = 0xA5A55A5A

        self.assertEqual(self.run_case(initial, 0x100), model(initial, 0))
        self.assertEqual(self.run_case(initial, 0x101), model(initial, 1))
        self.assertEqual(
            self.run_case(initial, UINT_MASK),
            model(initial, 1),
        )

    def test_randomized_register_model_and_order(self) -> None:
        generator = random.Random(0x0047FE6C)

        for _ in range(1000):
            initial = generator.getrandbits(32)
            enable = generator.getrandbits(32)
            self.assertEqual(
                self.run_case(initial, enable),
                model(initial, enable),
            )

    def test_repeated_update_is_idempotent_but_not_elided(self) -> None:
        expected = model(0x13579BDF, 1)
        self.run_case(0x13579BDF, 1)
        self.assertEqual(
            self.run_case(expected[-1], 1),
            [expected[-1]] * 3,
        )
        self.assertEqual(self.word("read_count").value, 3)
        self.assertEqual(self.word("write_count").value, 3)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "c7c5e9145973ab1beaabf8aa4c024ca7"
            "6bbbf6fc398cae193422915635063428",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "d81b9c74df4a327e4c009db95a377551"
            "ca98219e1b10d95b51c0446c1339b3b5",
        )


if __name__ == "__main__":
    unittest.main()
