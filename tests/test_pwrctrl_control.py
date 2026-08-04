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
SOURCE = COMPONENT_ROOT / "pwrctrl_control.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "pwrctrl_control_host.c"

READ = 1
WRITE = 2
SPOT_BEFORE_OVERRIDE = 3
OVERRIDE_INIT = 4
SPOT_BEFORE_ENABLE = 5
SPOT_AFTER_ENABLE = 6
PERIPH_ENABLED = 7
CRYPTO_QUIESCE = 8
PERIPH_DISABLE = 9
STATUS_CHECK = 10
SPOT_UPDATE = 11

VRSTATUS = 0x40021108
SIMOBUCK15 = 0x40020378
SIMOBUCK0 = 0x4002033C
VRCTRL = 0x40021100
XTALGENCTRL = 0x40020124
XTALCTRL = 0x40020120
DEMCR = 0xE000EDFC
DBGCTRL = 0x40020250
DEVPWREN = 0x40021004
AUDSSPWREN = 0x4002100C
CRYPTO = 0x17
UINT_MASK = 0xFFFFFFFF


class PwrctrlControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "pwrctrl_control.dylib"
            if sys.platform == "darwin"
            else "pwrctrl_control.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_pwrctrl_control_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.control = cls.loaded.open_cfw_pwrctrl_control
        cls.control.argtypes = [ctypes.c_uint, ctypes.c_void_p]
        cls.control.restype = ctypes.c_uint
        cls.set_register = cls.loaded.open_cfw_test_pwrctrl_control_set
        cls.set_register.argtypes = [ctypes.c_uint, ctypes.c_uint]
        cls.set_register.restype = None
        cls.get_register = cls.loaded.open_cfw_test_pwrctrl_control_get
        cls.get_register.argtypes = [ctypes.c_uint]
        cls.get_register.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_pwrctrl_control_{name}",
        )

    @classmethod
    def words(cls, name: str, count: int) -> ctypes.Array:
        return (ctypes.c_uint * count).in_dll(
            cls.loaded,
            f"open_cfw_test_pwrctrl_control_{name}",
        )

    def set(self, address: int, value: int) -> None:
        self.set_register(address, value)

    def get(self, address: int) -> int:
        return self.get_register(address)

    def operations(self) -> list[tuple[int, int, int, int, int, int]]:
        count = self.word("operation_count").value
        arrays = [
            self.words("operations", 64),
            self.words("arg0", 64),
            self.words("arg1", 64),
            self.words("arg2", 64),
            self.words("arg3", 64),
            self.words("arg4", 64),
        ]
        return list(zip(*(array[:count] for array in arrays)))

    @staticmethod
    def op(
        operation: int,
        arg0: int = 0,
        arg1: int = 0,
        arg2: int = 0,
        arg3: int = 0,
        arg4: int = 0,
    ) -> tuple[int, int, int, int, int, int]:
        return operation, arg0, arg1, arg2, arg3, arg4

    def test_invalid_command_uses_low_byte_and_ignores_arguments(self) -> None:
        self.assertEqual(self.control(6, ctypes.c_void_p(0x12345678)), 6)
        self.assertEqual(self.operations(), [])

        self.assertEqual(self.control(0xFFFFFF06, None), 6)
        self.assertEqual(self.operations(), [])

        self.set(VRSTATUS, 0x30)
        self.assertEqual(self.control(0xA5A50000, None), 0)
        self.assertEqual(
            self.operations(),
            [self.op(READ, VRSTATUS, 0x30)],
        )

    def test_simobuck_active_returns_without_side_effects(self) -> None:
        self.set(VRSTATUS, 0xA5A5A5B5)

        self.assertEqual(self.control(0, None), 0)
        self.assertEqual(
            self.operations(),
            [self.op(READ, VRSTATUS, 0xA5A5A5B5)],
        )

    def test_simobuck_init_preserves_bits_and_uses_stock_order(self) -> None:
        self.set(VRSTATUS, 0x10)
        self.set(SIMOBUCK15, 0x01234567)
        self.set(SIMOBUCK0, 0x89ABCDE0)
        self.set(VRCTRL, 0x76543210)

        self.assertEqual(self.control(0, ctypes.c_void_p(0xDEADBEEF)), 0)
        self.assertEqual(self.get(SIMOBUCK15), 0x81234567)
        self.assertEqual(self.get(SIMOBUCK0), 0x89ABCDEF)
        self.assertEqual(self.get(VRCTRL), 0x76543211)
        self.assertEqual(
            self.operations(),
            [
                self.op(READ, VRSTATUS, 0x10),
                self.op(SPOT_BEFORE_OVERRIDE),
                self.op(OVERRIDE_INIT),
                self.op(READ, SIMOBUCK15, 0x01234567),
                self.op(WRITE, SIMOBUCK15, 0x81234567),
                self.op(READ, SIMOBUCK0, 0x89ABCDE0),
                self.op(WRITE, SIMOBUCK0, 0x89ABCDEF),
                self.op(SPOT_BEFORE_ENABLE),
                self.op(READ, VRCTRL, 0x76543210),
                self.op(WRITE, VRCTRL, 0x76543211),
                self.op(SPOT_AFTER_ENABLE),
            ],
        )

    def test_crypto_disabled_ignores_enabled_query_status(self) -> None:
        self.word("enabled").value = 0
        self.word("enabled_status").value = 0x81

        self.assertEqual(self.control(1, None), 0)
        self.assertEqual(
            self.operations(),
            [self.op(PERIPH_ENABLED, CRYPTO)],
        )

    def test_crypto_enabled_propagates_each_failure_boundary(self) -> None:
        self.word("enabled").value = 1
        self.word("enabled_status").value = 0x80
        self.word("quiesce_status").value = 0x82

        self.assertEqual(self.control(1, None), 0x82)
        self.assertEqual(
            self.operations(),
            [
                self.op(PERIPH_ENABLED, CRYPTO),
                self.op(CRYPTO_QUIESCE),
            ],
        )

        self.reset_fixture()
        self.word("enabled").value = 0x101
        self.word("disable_status").value = 0x83
        self.assertEqual(self.control(1, None), 0x83)
        self.assertEqual(
            self.operations(),
            [
                self.op(PERIPH_ENABLED, CRYPTO),
                self.op(CRYPTO_QUIESCE),
                self.op(PERIPH_DISABLE, CRYPTO),
            ],
        )

    def test_xtal_powerdown_updates_exact_field_and_control_word(self) -> None:
        initial = 0xA5A55AFF
        self.set(XTALGENCTRL, initial)
        self.set(XTALCTRL, UINT_MASK)

        self.assertEqual(self.control(2, None), 0)
        expected = (initial & ~0xFC) | 0x80
        self.assertEqual(self.get(XTALGENCTRL), expected)
        self.assertEqual(self.get(XTALCTRL), 1)
        self.assertEqual(
            self.operations(),
            [
                self.op(READ, XTALGENCTRL, initial),
                self.op(WRITE, XTALGENCTRL, expected),
                self.op(WRITE, XTALCTRL, 1),
            ],
        )

    def expected_disable_prefix(
        self,
        demcr: int,
        dbgctrl: int,
    ) -> list[tuple[int, int, int, int, int, int]]:
        dbg_after_trace = dbgctrl & ~1
        dbg_after_clock = dbg_after_trace & ~0xE
        return [
            self.op(READ, DEMCR, demcr),
            self.op(WRITE, DEMCR, demcr & ~0x01000000),
            self.op(READ, DBGCTRL, dbgctrl),
            self.op(WRITE, DBGCTRL, dbg_after_trace),
            self.op(READ, DBGCTRL, dbg_after_trace),
            self.op(WRITE, DBGCTRL, dbg_after_clock),
            self.op(WRITE, DEVPWREN, 0),
            self.op(WRITE, AUDSSPWREN, 0),
        ]

    def test_disable_all_success_has_exact_wait_and_spot_sequence(
        self,
    ) -> None:
        demcr = 0xA5A5A5A5
        dbgctrl = 0x5A5A5A5F
        self.set(DEMCR, demcr)
        self.set(DBGCTRL, dbgctrl)
        self.set(DEVPWREN, UINT_MASK)
        self.set(AUDSSPWREN, UINT_MASK)
        self.words("spot_outputs", 2)[:] = [0x91, 0x92]

        self.assertEqual(self.control(3, None), 0)
        self.assertEqual(self.get(DEMCR), demcr & ~0x01000000)
        self.assertEqual(self.get(DBGCTRL), dbgctrl & ~0xF)
        self.assertEqual(self.get(DEVPWREN), 0)
        self.assertEqual(self.get(AUDSSPWREN), 0)
        self.assertEqual(
            self.operations(),
            self.expected_disable_prefix(demcr, dbgctrl)
            + [
                self.op(STATUS_CHECK, 5, DEVPWREN, 0x3FFFFFFF, 0, 1),
                self.op(SPOT_UPDATE, 3, 0, 0),
                self.op(STATUS_CHECK, 5, AUDSSPWREN, 0x4C4, 0, 1),
                self.op(SPOT_UPDATE, 4, 0, 0),
            ],
        )

    def test_disable_all_propagates_all_four_failure_boundaries(
        self,
    ) -> None:
        cases = [
            ("status_check_results", 0, 0xA1, 9),
            ("spot_results", 0, 0xA2, 10),
            ("status_check_results", 1, 0xA3, 11),
            ("spot_results", 1, 0xA4, 12),
        ]
        for array_name, index, result, operation_count in cases:
            with self.subTest(result=result):
                self.reset_fixture()
                self.words(array_name, 2)[index] = result

                self.assertEqual(self.control(3, None), result)
                self.assertEqual(len(self.operations()), operation_count)

    def test_randomized_register_preservation_model(self) -> None:
        generator = random.Random(0x0047FEA0)

        for _ in range(250):
            self.reset_fixture()
            values = [generator.getrandbits(32) for _ in range(7)]
            self.set(VRSTATUS, values[0] & ~0x30)
            self.set(SIMOBUCK15, values[1])
            self.set(SIMOBUCK0, values[2])
            self.set(VRCTRL, values[3])
            self.assertEqual(self.control(0, None), 0)
            self.assertEqual(self.get(SIMOBUCK15), values[1] | 0x80000000)
            self.assertEqual(self.get(SIMOBUCK0), values[2] | 0xF)
            self.assertEqual(self.get(VRCTRL), values[3] | 1)

            self.reset_fixture()
            self.set(XTALGENCTRL, values[4])
            self.assertEqual(self.control(2, None), 0)
            self.assertEqual(
                self.get(XTALGENCTRL),
                (values[4] & ~0xFC) | 0x80,
            )

            self.reset_fixture()
            self.set(DEMCR, values[5])
            self.set(DBGCTRL, values[6])
            self.assertEqual(self.control(3, None), 0)
            self.assertEqual(self.get(DEMCR), values[5] & ~0x01000000)
            self.assertEqual(self.get(DBGCTRL), values[6] & ~0xF)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "e36a11fd7900c478541d096b3bfaf5ef64de7b0b684c6a446658715a61223457",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "9bcbe8e30a84286971f240f5895256b010d46bdbf0b4d2a250b3ac5a392b333e",
        )


if __name__ == "__main__":
    unittest.main()
