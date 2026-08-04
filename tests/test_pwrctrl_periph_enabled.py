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
SOURCE = COMPONENT_ROOT / "pwrctrl_periph_enabled.c"
FIXTURE = (
    OPENCFW_ROOT / "tests" / "fixtures" / "pwrctrl_periph_enabled_host.c"
)


class PwrctrlPeriphEnabledTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "pwrctrl_periph_enabled.dylib"
            if sys.platform == "darwin"
            else "pwrctrl_periph_enabled.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_enabled_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.query = cls.loaded.open_cfw_pwrctrl_periph_enabled
        cls.query.argtypes = [
            ctypes.c_uint,
            ctypes.POINTER(ctypes.c_ubyte),
        ]
        cls.query.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_enabled_{name}",
        )

    def test_null_output_is_rejected_without_descriptor_lookup(self) -> None:
        self.assertEqual(self.query(4, None), 6)
        self.assertEqual(self.word("descriptor_calls").value, 0)
        self.assertEqual(self.word("read_calls").value, 0)

    def test_descriptor_error_clears_output_and_is_propagated(self) -> None:
        output = ctypes.c_ubyte(0xA5)
        self.word("descriptor_result").value = 7

        self.assertEqual(self.query(2, ctypes.byref(output)), 7)
        self.assertEqual(output.value, 0)
        self.assertEqual(self.word("descriptor_calls").value, 1)
        self.assertEqual(self.word("read_calls").value, 0)

    def test_low_byte_abi_and_disabled_state(self) -> None:
        output = ctypes.c_ubyte(0xFF)

        self.assertEqual(
            self.query(0x12345678, ctypes.byref(output)),
            0,
        )
        self.assertEqual(self.word("last_peripheral").value, 0x78)
        self.assertEqual(output.value, 0)
        self.assertEqual(self.word("read_calls").value, 1)

    def test_any_selected_status_bit_reports_true(self) -> None:
        output = ctypes.c_ubyte(0)
        self.word("status_mask").value = 0x240
        self.word("status_register").value = 0xA5000200

        self.assertEqual(self.query(8, ctypes.byref(output)), 0)
        self.assertEqual(output.value, 1)

    def test_randomized_register_model(self) -> None:
        generator = random.Random(0x47F90C)

        for _ in range(1000):
            self.reset_fixture()
            peripheral = generator.getrandbits(32)
            mask = generator.getrandbits(32)
            register = generator.getrandbits(32)
            output = ctypes.c_ubyte(0xA5)
            self.word("status_mask").value = mask
            self.word("status_register").value = register

            self.assertEqual(
                self.query(peripheral, ctypes.byref(output)),
                0,
            )
            self.assertEqual(output.value, int(bool(register & mask)))
            self.assertEqual(
                self.word("last_peripheral").value,
                peripheral & 0xFF,
            )

    def test_sources_are_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "12689a577aff71fd5ea378399ae9139585c53f76f14e93a43184d4ec730f7b34",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "acbcd6831aaa87d3fc59e09b75bd90f75bb8c56cae4271066fd2096e1fb8f4ab",
        )


if __name__ == "__main__":
    unittest.main()
