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
SOURCE = COMPONENT_ROOT / "pwrctrl_low_power_init.c"
FIXTURE = (
    OPENCFW_ROOT / "tests" / "fixtures" / "pwrctrl_low_power_init_host.c"
)

RSTGEN_STATUS = 0x4000885C
CHIP_REVISION = 0x4002000C
DEBUG_CONTROL = 0x40020250
SHADOW_VALID = 0x400201BC
WIC_CONTROL = 0x4002021C
CLOCK_MISC = 0x40004044
CLOCK_CONTROL = 0x40004120
AUDADC_DELAY = 0x40020448
VR_STATUS = 0x40021108
POWER_SWITCH_0 = 0x4002037C
POWER_SWITCH_1 = 0x40020380
MRAM_EXT_CONTROL = 0x400211C8
TRACE_COUNT = 0x20074F5E
ORIG_TRIMS_STORED = 0x20074F63
CURRENT_GPU_MODE = 0x20074F60
INFO1_CACHE = 0x20071948
TRIM_VERSION_CACHE = 0x200001E8
DEFAULT_MEMORY_CONFIG = 0x200001EC

BASELINE_OPERATIONS = [
    (3, 0x030303, 0),
    (6, 0, 0),
    (7, 0, 0),
    (9, 0, 0),
    (2, 0x17, 0),
    (2, 0x1D, 0),
    (10, 0x200001EC, 0),
    (11, 0x0078C984, 0),
    (12, 0, 0),
    (13, 0, 0),
    (14, 0, 2),
    (15, 1, 0),
    (16, 0, 0),
    (17, 0, 0),
]

TRIM_DESTINATIONS = {
    "tvrgc": 0x2007426C,
    "tvrgf": 0x20074270,
    "vddclkg": 0x20074274,
    "core_active": 0x2007427C,
    "act_vddf": 0x20074280,
    "mem_active": 0x20074284,
    "lp_vddf": 0x20074288,
    "mem_lp": 0x2007428C,
    "d2aspare": 0x20074290,
    "vddc_low": 0x20074294,
    "vddc_high": 0x20074298,
    "vddclv_low": 0x2007429C,
    "vddclv_high": 0x200742A0,
    "vddf_low": 0x200742A4,
    "vddf_high": 0x200742A8,
}

TRIM_SOURCES = {
    "act": 0x4002036C,
    "mem": 0x40020088,
    "tvrgc": 0x40020044,
    "tvrgf": 0x4002004C,
    "vddclkg": 0x40020374,
    "core": 0x40020080,
    "d2aspare": 0x400201B0,
    "vddc": 0x40020344,
    "vddclv": 0x4002034C,
    "vddf_low": 0x40020358,
    "vddf_high": 0x40020354,
}


class PwrctrlLowPowerInitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "pwrctrl_low_power_init.dylib"
            if sys.platform == "darwin"
            else "pwrctrl_low_power_init.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_low_power_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.initialize = cls.loaded.open_cfw_pwrctrl_low_power_init
        cls.initialize.argtypes = []
        cls.initialize.restype = ctypes.c_uint
        cls.set_register = cls.loaded.open_cfw_test_low_power_set
        cls.set_register.argtypes = [ctypes.c_uint, ctypes.c_uint]
        cls.set_register.restype = None
        cls.get_register = cls.loaded.open_cfw_test_low_power_get
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
            f"open_cfw_test_low_power_{name}",
        )

    @classmethod
    def words(cls, name: str, count: int) -> ctypes.Array:
        return (ctypes.c_uint * count).in_dll(
            cls.loaded,
            f"open_cfw_test_low_power_{name}",
        )

    def set(self, address: int, value: int) -> None:
        self.set_register(address, value)

    def get(self, address: int) -> int:
        return self.get_register(address)

    def operations(self) -> list[tuple[int, int, int]]:
        count = self.word("operation_count").value
        return list(
            zip(
                self.words("operations", 64)[:count],
                self.words("operation_arg0", 64)[:count],
                self.words("operation_arg1", 64)[:count],
            )
        )

    def test_baseline_sequence_and_register_policy(self) -> None:
        self.assertEqual(self.initialize(), 0)
        self.assertEqual(self.operations(), BASELINE_OPERATIONS)
        self.assertEqual(self.get(WIC_CONTROL), 0x11)
        self.assertEqual(
            self.get(CLOCK_MISC),
            (
                0x80004000
                | 0x000F80000
                | 0x0003BFC0
            ) & ~0x4000,
        )
        self.assertEqual(self.get(CLOCK_CONTROL), 0)
        self.assertEqual(self.get(AUDADC_DELAY), 0xA5A504A5)
        self.assertEqual(self.get(POWER_SWITCH_0), 0x40000100)
        self.assertEqual(self.get(POWER_SWITCH_1), 0x00011200)

    def test_reset_erratum_and_debug_shutdown(self) -> None:
        self.set(RSTGEN_STATUS, 0xFFFFFFFF)
        self.set(TRACE_COUNT, 0)
        self.set(DEBUG_CONTROL, 0xA5A5A5AF)

        self.assertEqual(self.initialize(), 0)
        self.assertEqual(self.get(RSTGEN_STATUS), 0xFFFFFFFB)
        self.assertEqual(self.get(DEBUG_CONTROL), 0xA5A5A5A0)
        self.assertEqual(
            self.operations()[:3],
            [(1, 0, 0), (2, 0x1C, 0), (3, 0x030303, 0)],
        )

    def test_otp_is_enabled_only_when_shadow_selects_it_and_it_is_off(
        self,
    ) -> None:
        self.set(SHADOW_VALID, 1 << 3)
        self.word("enabled_value").value = 0

        self.assertEqual(self.initialize(), 0)
        self.assertEqual(
            self.operations()[:3],
            [(3, 0x030303, 0), (4, 0x1D, 0), (5, 0x1D, 0)],
        )

        self.reset_fixture()
        self.set(SHADOW_VALID, 1 << 3)
        self.word("enabled_value").value = 1
        self.assertEqual(self.initialize(), 0)
        self.assertEqual(
            self.operations()[:2],
            [(3, 0x030303, 0), (4, 0x1D, 0)],
        )
        self.assertNotIn((5, 0x1D, 0), self.operations())

    def test_first_fallback_info1_failure_returns_immediately(self) -> None:
        self.set(INFO1_CACHE, 0)
        self.word("info1_fail_call").value = 0
        self.word("info1_fail_status").value = 0x81

        self.assertEqual(self.initialize(), 0x81)
        self.assertEqual(
            self.operations(),
            [
                (3, 0x030303, 0),
                (6, 0, 0),
                (7, 0, 0),
                (8, 0x210, INFO1_CACHE + 0x34),
            ],
        )

    def test_second_fallback_info1_failure_preserves_first_word(self) -> None:
        self.set(INFO1_CACHE, 0)
        self.word("info1_fail_call").value = 1
        self.word("info1_fail_status").value = 0x82

        self.assertEqual(self.initialize(), 0x82)
        self.assertEqual(self.get(INFO1_CACHE + 0x34), 0xA5000210)
        self.assertEqual(self.get(INFO1_CACHE + 0x44), 0)
        self.assertEqual(self.word("info1_call_count").value, 2)

    def test_successful_fallback_reads_exact_info1_words(self) -> None:
        self.set(INFO1_CACHE, 0)

        self.assertEqual(self.initialize(), 0)
        self.assertEqual(self.word("info1_call_count").value, 2)
        self.assertEqual(self.words("info1_space", 2)[:], [1, 1])
        self.assertEqual(
            self.words("info1_offset", 2)[:],
            [0x210, 0x245],
        )
        self.assertEqual(self.words("info1_count", 2)[:], [1, 1])
        self.assertEqual(
            self.words("info1_destination", 2)[:],
            [INFO1_CACHE + 0x34, INFO1_CACHE + 0x44],
        )
        self.assertEqual(self.get(INFO1_CACHE + 0x34), 0xA5000210)
        self.assertEqual(self.get(INFO1_CACHE + 0x44), 0xA5000245)

    def test_trim_snapshot_bitfields_match_stock(self) -> None:
        generator = random.Random(0x0047FAE8)
        for _ in range(200):
            self.reset_fixture()
            self.set(ORIG_TRIMS_STORED, 0)
            values = {
                name: generator.getrandbits(32)
                for name in TRIM_SOURCES
            }
            for name, address in TRIM_SOURCES.items():
                self.set(address, values[name])
            self.set(VR_STATUS, 0)

            self.assertEqual(self.initialize(), 0)
            expected = {
                "act_vddf": (values["act"] >> 20) & 0x3F,
                "lp_vddf": (values["act"] >> 26) & 0x3F,
                "mem_active": values["mem"] & 0x3F,
                "mem_lp": (values["mem"] >> 18) & 0x3F,
                "tvrgc": values["tvrgc"] & 0x7F,
                "tvrgf": values["tvrgf"] & 0x7F,
                "vddclkg": (values["vddclkg"] >> 29) & 0x3,
                "core_active": values["core"] & 0x3FF,
                "d2aspare": values["d2aspare"],
                "vddc_low": (values["vddc"] >> 25) & 0x1F,
                "vddc_high": (values["vddc"] >> 11) & 0x1F,
                "vddclv_low": (values["vddclv"] >> 25) & 0x1F,
                "vddclv_high": (values["vddclv"] >> 11) & 0x1F,
                "vddf_low": (values["vddf_low"] >> 8) & 0x1F,
                "vddf_high": (values["vddf_high"] >> 17) & 0x1F,
            }
            for name, expected_value in expected.items():
                self.assertEqual(
                    self.get(TRIM_DESTINATIONS[name]),
                    expected_value,
                    name,
                )
            self.assertEqual(self.get(ORIG_TRIMS_STORED) & 0xFF, 1)

    def test_core_ldo_revision_corrections_match_stock_matrix(self) -> None:
        cases = [
            (0x21, 0, 0),
            (0x21, 1, 6),
            (0x21, 2, 6),
            (0x21, 3, 7),
            (0x22, 0, 6),
            (0x22, 1, 7),
            (0x22, 2, 0),
            (0x23, 0, 7),
            (0x23, 1, 0),
        ]
        for revision, trim, adjustment in cases:
            with self.subTest(revision=revision, trim=trim):
                self.reset_fixture()
                self.set(ORIG_TRIMS_STORED, 0)
                self.set(CHIP_REVISION, revision)
                self.set(TRIM_VERSION_CACHE, trim)
                self.set(VR_STATUS, 3 << 4)
                self.set(TRIM_SOURCES["core"], 0x155)

                self.assertEqual(self.initialize(), 0)
                self.assertEqual(
                    self.get(TRIM_DESTINATIONS["core_active"]),
                    0x155 + adjustment,
                )

    def test_existing_trim_snapshot_is_not_overwritten(self) -> None:
        for address in TRIM_DESTINATIONS.values():
            self.set(address, 0xDEADBEEF)
        self.set(TRIM_SOURCES["core"], 0x123)

        self.assertEqual(self.initialize(), 0)
        for address in TRIM_DESTINATIONS.values():
            self.assertEqual(self.get(address), 0xDEADBEEF)

    def test_b1_policy_updates_default_rom_and_mram_control(self) -> None:
        self.set(CHIP_REVISION, 0x22)
        self.set(DEFAULT_MEMORY_CONFIG, 0xA5A5A500)
        self.set(MRAM_EXT_CONTROL, 0x100)

        self.assertEqual(self.initialize(), 0)
        self.assertEqual(self.get(DEFAULT_MEMORY_CONFIG), 0xA5A5A501)
        self.assertEqual(self.get(MRAM_EXT_CONTROL), 0x106)

        self.reset_fixture()
        self.set(CHIP_REVISION, 0x21)
        self.set(DEFAULT_MEMORY_CONFIG, 0xA5A5A500)
        self.set(MRAM_EXT_CONTROL, 0x100)
        self.assertEqual(self.initialize(), 0)
        self.assertEqual(self.get(DEFAULT_MEMORY_CONFIG), 0xA5A5A500)
        self.assertEqual(self.get(MRAM_EXT_CONTROL), 0x100)

    def test_subordinate_statuses_are_ignored_outside_info1_fallback(
        self,
    ) -> None:
        self.word("subordinate_status").value = 0xFFFFFFFF
        self.set(SHADOW_VALID, 1 << 3)

        self.assertEqual(self.initialize(), 0)
        self.assertEqual(self.operations()[-1], (17, 0, 0))

    def test_sources_are_pinned(self) -> None:
        expected = {
            SOURCE:
                "a6146d56b4de865f2d935f1f14e31b9d"
                "40cc07e7d4fa87c526d6e447fcde316b",
            FIXTURE:
                "61d14b19e29728b6f055e3223956e1abe"
                "1fc0a7517bded77bc190f0934fdfdbc",
        }
        for path, digest in expected.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                digest,
            )


if __name__ == "__main__":
    unittest.main()
