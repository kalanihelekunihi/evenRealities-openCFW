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
SOURCE = COMPONENT_ROOT / "pwrctrl_cpdlp_get.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "pwrctrl_cpdlp_get_host.c"

CPDLP_STATE = 0xE001E300
UINT_MASK = 0xFFFFFFFF


def model(state: int) -> tuple[int, int, int]:
    state &= UINT_MASK
    return (
        (state >> 8) & 0x3,
        (state >> 4) & 0x3,
        state & 0x3,
    )


class PwrctrlCpdlpGetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "pwrctrl_cpdlp_get.dylib"
            if sys.platform == "darwin"
            else "pwrctrl_cpdlp_get.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_cpdlp_get_reset
        cls.reset_fixture.argtypes = [ctypes.c_uint]
        cls.reset_fixture.restype = None
        cls.get = cls.loaded.open_cfw_pwrctrl_cpdlp_get
        cls.get.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]
        cls.get.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_cpdlp_get_{name}",
        )

    def run_case(self, state: int) -> ctypes.Array:
        output = (ctypes.c_ubyte * 5)(0xA5, 0xA5, 0xA5, 0xA5, 0xA5)
        self.reset_fixture(state)
        self.get(ctypes.cast(output, ctypes.POINTER(ctypes.c_ubyte)))
        return output

    def test_extracts_rlp_elp_and_clp_in_stock_byte_order(self) -> None:
        output = self.run_case(0x00000312)

        self.assertEqual(tuple(output[:3]), (3, 1, 2))

    def test_unrelated_state_bits_do_not_affect_outputs(self) -> None:
        base = 0x00000312

        self.assertEqual(
            tuple(self.run_case(base)[:3]),
            tuple(self.run_case(base | 0xFFFFFCCC)[:3]),
        )

    def test_writes_exactly_three_output_bytes(self) -> None:
        output = self.run_case(0xFFFFFFFF)

        self.assertEqual(tuple(output), (3, 3, 3, 0xA5, 0xA5))

    def test_state_register_is_read_exactly_once(self) -> None:
        self.run_case(0x12345678)

        self.assertEqual(self.word("read_count").value, 1)
        self.assertEqual(self.word("read_address").value, CPDLP_STATE)

    def test_randomized_extraction_model(self) -> None:
        generator = random.Random(0x00480008)

        for _ in range(1000):
            state = generator.getrandbits(32)
            output = self.run_case(state)
            self.assertEqual(tuple(output[:3]), model(state))
            self.assertEqual(tuple(output[3:]), (0xA5, 0xA5))
            self.assertEqual(self.word("read_count").value, 1)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "23524c09437c54bcf50929d0d422b4e4ab0dbccf25d7a62f2fe0cc67a9208432",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "543ee8470f04d79809d4afe8f7f160d584bc5a73c1e168acef0996c4c4536f2e",
        )


if __name__ == "__main__":
    unittest.main()
