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
SOURCE = COMPONENT_ROOT / "pwrctrl_syspll_enable.c"
FIXTURE = (
    OPENCFW_ROOT / "tests" / "fixtures" / "pwrctrl_syspll_enable_host.c"
)

CHIPREV = 0x4002000C
D2ASPARE = 0x400201B0
PLLCTL0 = 0x400204D8
ISOLATION = 0x00200000
VDDF_POWER_DOWN = 0x80000000
VDDH_POWER_DOWN = 0x40000000
UINT_MASK = 0xFFFFFFFF


class PwrctrlSyspllEnableTests(unittest.TestCase):
    IRQ_DISABLE = 1
    READ = 2
    WRITE = 3
    DELAY = 4
    IRQ_RESTORE = 5

    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "pwrctrl_syspll_enable.dylib"
            if sys.platform == "darwin"
            else "pwrctrl_syspll_enable.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_syspll_reset
        cls.reset_fixture.argtypes = [ctypes.c_uint] * 5
        cls.reset_fixture.restype = None
        cls.enable = cls.loaded.open_cfw_pwrctrl_syspll_enable
        cls.enable.argtypes = []
        cls.enable.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_syspll_{name}",
        )

    @classmethod
    def word_array(cls, name: str) -> ctypes.Array:
        return (ctypes.c_uint * 32).in_dll(
            cls.loaded,
            f"open_cfw_test_syspll_trace_{name}",
        )

    def reset(
        self,
        revision: int,
        d2aspare: int,
        pllctl0: int,
        primask: int = 0,
        injected_pll_bits: int = 0,
    ) -> None:
        self.reset_fixture(
            revision,
            d2aspare,
            pllctl0,
            primask,
            injected_pll_bits,
        )

    def trace(self) -> list[tuple[int, int, int]]:
        count = min(self.word("trace_count").value, 32)
        events = self.word_array("event")
        addresses = self.word_array("address")
        values = self.word_array("value")
        return [
            (events[index], addresses[index], values[index])
            for index in range(count)
        ]

    def test_pre_b1_skips_isolation_and_one_microsecond_delay(self) -> None:
        self.reset(
            revision=0xABCD0021,
            d2aspare=0xA5A5A5A5,
            pllctl0=0xFFFFFFFF,
            primask=1,
        )

        self.assertEqual(self.enable(), 0)
        self.assertEqual(self.word("d2aspare").value, 0xA5A5A5A5)
        self.assertEqual(self.word("pllctl0").value, 0x3FFFFFFF)
        self.assertEqual(self.word("restored_primask").value, 1)
        self.assertEqual(
            self.trace(),
            [
                (self.IRQ_DISABLE, 0, 1),
                (self.READ, CHIPREV, 0xABCD0021),
                (self.READ, PLLCTL0, 0xFFFFFFFF),
                (self.WRITE, PLLCTL0, 0x7FFFFFFF),
                (self.READ, PLLCTL0, 0x7FFFFFFF),
                (self.WRITE, PLLCTL0, 0x3FFFFFFF),
                (self.IRQ_RESTORE, 0, 1),
                (self.DELAY, 0, 5),
            ],
        )

    def test_b1_threshold_uses_only_low_revision_byte(self) -> None:
        for revision, expected_isolation in (
            (0x00000022, True),
            (0xFFFFFF22, True),
            (0x00000121, False),
        ):
            with self.subTest(revision=revision):
                self.reset(
                    revision=revision,
                    d2aspare=UINT_MASK,
                    pllctl0=0,
                )
                self.assertEqual(self.enable(), 0)
                self.assertEqual(
                    (self.word("d2aspare").value & ISOLATION) == 0,
                    expected_isolation,
                )
                delays = [
                    value
                    for event, _, value in self.trace()
                    if event == self.DELAY
                ]
                self.assertEqual(
                    delays,
                    [1, 5] if expected_isolation else [5],
                )

    def test_b1_path_has_exact_register_and_critical_section_order(self) -> None:
        self.reset(
            revision=0x22,
            d2aspare=0xFFFFFFFF,
            pllctl0=0xC1234567,
            primask=0xA5A5A5A5,
        )

        self.assertEqual(self.enable(), 0)
        self.assertEqual(
            self.trace(),
            [
                (self.IRQ_DISABLE, 0, 0xA5A5A5A5),
                (self.READ, CHIPREV, 0x22),
                (self.READ, D2ASPARE, 0xFFFFFFFF),
                (self.WRITE, D2ASPARE, 0xFFDFFFFF),
                (self.DELAY, 0, 1),
                (self.READ, PLLCTL0, 0xC1234567),
                (self.WRITE, PLLCTL0, 0x41234567),
                (self.READ, PLLCTL0, 0x41234567),
                (self.WRITE, PLLCTL0, 0x01234567),
                (self.IRQ_RESTORE, 0, 0xA5A5A5A5),
                (self.DELAY, 0, 5),
            ],
        )

    def test_unrelated_register_bits_are_preserved(self) -> None:
        self.reset(
            revision=0xFF,
            d2aspare=0xA5A5A5A5,
            pllctl0=0xDEADBEEF,
        )

        self.assertEqual(self.enable(), 0)
        self.assertEqual(
            self.word("d2aspare").value,
            0xA5A5A5A5 & ~ISOLATION,
        )
        self.assertEqual(
            self.word("pllctl0").value,
            0xDEADBEEF & ~VDDF_POWER_DOWN & ~VDDH_POWER_DOWN,
        )
        self.assertEqual(self.word("pll_write_count").value, 2)

    def test_second_pll_update_uses_a_fresh_volatile_read(self) -> None:
        injected = 0x00800000
        self.reset(
            revision=0,
            d2aspare=0,
            pllctl0=0xC0000001,
            injected_pll_bits=injected,
        )

        self.assertEqual(self.enable(), 0)
        self.assertEqual(self.word("pllctl0").value, 0x00800001)
        pll_reads = [
            value
            for event, address, value in self.trace()
            if event == self.READ and address == PLLCTL0
        ]
        self.assertEqual(pll_reads, [0xC0000001, 0x40800001])

    def test_randomized_stock_model(self) -> None:
        generator = random.Random(0x00480058)

        for _ in range(1000):
            revision = generator.getrandbits(32)
            d2aspare = generator.getrandbits(32)
            pllctl0 = generator.getrandbits(32)
            primask = generator.getrandbits(32)
            self.reset(revision, d2aspare, pllctl0, primask)

            self.assertEqual(self.enable(), 0)
            self.assertEqual(
                self.word("d2aspare").value,
                (
                    d2aspare & ~ISOLATION
                    if (revision & 0xFF) >= 0x22
                    else d2aspare
                ) & UINT_MASK,
            )
            self.assertEqual(
                self.word("pllctl0").value,
                pllctl0 & ~VDDF_POWER_DOWN & ~VDDH_POWER_DOWN,
            )
            self.assertEqual(self.word("restored_primask").value, primask)
            self.assertEqual(self.word("pll_write_count").value, 2)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "ef097e1eecb809d70f6493e7b9132a1b511224422f058a2b757669663a36581f",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "e04a7bf65941a8eb7cb40dc4686146b640407b951d2180c93e60333cd40e63ed",
        )


if __name__ == "__main__":
    unittest.main()
