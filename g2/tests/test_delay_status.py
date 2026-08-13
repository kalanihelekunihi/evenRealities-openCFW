from __future__ import annotations

import os

import ctypes
import hashlib
import random
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT_ROOT / "delay_status.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "delay_status_host.c"
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
STATUS_CHANGE_START = 0x004807FC
STATUS_CHANGE_END = 0x00480826
STATUS_CHECK_START = 0x00480826
STATUS_CHECK_END = 0x0048086A
REGISTER_ADDRESS = 0x40021008


class DelayStatusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "delay_status.dylib"
            if sys.platform == "darwin"
            else "delay_status.so"
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
        cls.reset = cls.loaded.open_cfw_test_delay_status_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.status_change = cls.loaded.open_cfw_delay_us_status_change
        cls.status_change.argtypes = [
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_uint,
        ]
        cls.status_change.restype = ctypes.c_uint
        cls.status_check = cls.loaded.open_cfw_delay_us_status_check
        cls.status_check.argtypes = [
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_ubyte,
        ]
        cls.status_check.restype = ctypes.c_uint
        cls.status_check_raw = (
            cls.loaded.open_cfw_test_delay_status_check_raw
        )
        cls.status_check_raw.argtypes = [
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_uint,
        ]
        cls.status_check_raw.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_delay_status_{name}",
        )

    @classmethod
    def array(cls, name: str, size: int) -> ctypes.Array:
        return (ctypes.c_uint * size).in_dll(
            cls.loaded,
            f"open_cfw_test_delay_status_{name}",
        )

    def configure(self, values: list[int]) -> None:
        self.reset()
        sequence = self.array("sequence", 256)
        for index, value in enumerate(values):
            sequence[index] = value
        self.word("sequence_count").value = len(values)

    def events(self) -> list[tuple[int, int, int]]:
        count = self.word("event_count").value
        return list(
            zip(
                self.array("event_kind", 512)[:count],
                self.array("event_address", 512)[:count],
                self.array("event_value", 512)[:count],
            )
        )

    def test_status_change_initial_match_returns_without_delay(self) -> None:
        self.configure([0xA5A50030])
        self.assertEqual(
            self.status_change(
                100,
                REGISTER_ADDRESS,
                0xF0,
                0x30,
            ),
            0,
        )
        self.assertEqual(self.word("read_count").value, 1)
        self.assertEqual(self.word("delay_count").value, 0)
        self.assertEqual(
            self.events(),
            [(1, REGISTER_ADDRESS, 0xA5A50030)],
        )

    def test_zero_timeout_still_reads_once(self) -> None:
        self.configure([0])
        self.assertEqual(
            self.status_change(0, REGISTER_ADDRESS, 1, 1),
            4,
        )
        self.assertEqual(self.word("read_count").value, 1)
        self.assertEqual(self.word("delay_count").value, 0)

        self.configure([1])
        self.assertEqual(
            self.status_check(0, REGISTER_ADDRESS, 1, 1, 0),
            4,
        )
        self.assertEqual(self.word("read_count").value, 1)
        self.assertEqual(self.word("delay_count").value, 0)

    def test_timeout_budget_is_exact_reads_plus_one(self) -> None:
        for maximum in (1, 2, 7, 31):
            with self.subTest(maximum=maximum):
                self.configure([0])
                self.assertEqual(
                    self.status_change(
                        maximum,
                        REGISTER_ADDRESS,
                        1,
                        1,
                    ),
                    4,
                )
                self.assertEqual(
                    self.word("read_count").value,
                    maximum + 1,
                )
                self.assertEqual(
                    self.word("delay_count").value,
                    maximum,
                )

    def test_success_after_each_possible_delay_preserves_event_order(
        self,
    ) -> None:
        for delay_count in range(1, 9):
            with self.subTest(delay_count=delay_count):
                self.configure([0] * delay_count + [0x80000004])
                self.assertEqual(
                    self.status_change(
                        delay_count,
                        REGISTER_ADDRESS,
                        4,
                        4,
                    ),
                    0,
                )
                self.assertEqual(
                    self.word("read_count").value,
                    delay_count + 1,
                )
                self.assertEqual(
                    self.word("delay_count").value,
                    delay_count,
                )
                self.assertEqual(
                    [kind for kind, _, _ in self.events()],
                    [1, 2] * delay_count + [1],
                )
                self.assertTrue(
                    all(
                        value == 1
                        for kind, _, value in self.events()
                        if kind == 2
                    )
                )

    def test_status_check_supports_equal_and_not_equal_modes(self) -> None:
        self.configure([0xA0, 0xB0])
        self.assertEqual(
            self.status_check(
                1,
                REGISTER_ADDRESS,
                0xF0,
                0xB0,
                1,
            ),
            0,
        )
        self.assertEqual(self.word("delay_count").value, 1)

        self.configure([0xB7, 0xA7])
        self.assertEqual(
            self.status_check(
                1,
                REGISTER_ADDRESS,
                0xF0,
                0xB0,
                0,
            ),
            0,
        )
        self.assertEqual(self.word("delay_count").value, 1)

    def test_status_check_truncates_mode_to_one_byte(self) -> None:
        self.configure([1])
        self.assertEqual(
            self.status_check_raw(0, REGISTER_ADDRESS, 1, 1, 0x100),
            4,
        )
        self.configure([1])
        self.assertEqual(
            self.status_check_raw(0, REGISTER_ADDRESS, 1, 1, 0x101),
            0,
        )

    def test_randomized_model_matches_both_helpers(self) -> None:
        rng = random.Random(0x4807FC)
        for _ in range(400):
            maximum = rng.randrange(0, 20)
            mask = rng.getrandbits(32)
            target = rng.getrandbits(32)
            values = [rng.getrandbits(32) for _ in range(maximum + 1)]
            if rng.randrange(2):
                target = values[rng.randrange(len(values))] & mask

            self.configure(values)
            matching = next(
                (
                    index
                    for index, value in enumerate(values)
                    if value & mask == target
                ),
                None,
            )
            expected = 0 if matching is not None else 4
            reads = matching + 1 if matching is not None else maximum + 1
            self.assertEqual(
                self.status_change(
                    maximum,
                    REGISTER_ADDRESS,
                    mask,
                    target,
                ),
                expected,
            )
            self.assertEqual(self.word("read_count").value, reads)
            self.assertEqual(
                self.word("delay_count").value,
                reads - 1,
            )

            is_equal = rng.getrandbits(8)
            self.configure(values)
            matching = next(
                (
                    index
                    for index, value in enumerate(values)
                    if (
                        (value & mask == target)
                        if is_equal
                        else (value & mask != target)
                    )
                ),
                None,
            )
            expected = 0 if matching is not None else 4
            reads = matching + 1 if matching is not None else maximum + 1
            self.assertEqual(
                self.status_check(
                    maximum,
                    REGISTER_ADDRESS,
                    mask,
                    target,
                    is_equal,
                ),
                expected,
            )
            self.assertEqual(self.word("read_count").value, reads)
            self.assertEqual(
                self.word("delay_count").value,
                reads - 1,
            )

    def test_stock_spans_and_next_boundary_are_review_pinned(self) -> None:
        application = OFFICIAL.read_bytes()[32:]
        expectations = (
            (
                STATUS_CHANGE_START,
                STATUS_CHANGE_END,
                "6420c4ecc4fd66dab58e4de017013ce9"
                "82e42299b5e4557d15a59007ea2a0ad2",
            ),
            (
                STATUS_CHECK_START,
                STATUS_CHECK_END,
                "c6bf044dbb8f4a358cc93e10eff0b2ec"
                "7065b47f8ff08cde9f912d749fd42ef9",
            ),
        )
        for start, end, digest in expectations:
            span = application[
                start - APPLICATION_BASE:end - APPLICATION_BASE
            ]
            self.assertEqual(len(span), end - start)
            self.assertEqual(hashlib.sha256(span).hexdigest(), digest)

        next_function = application[
            0x0048086A - APPLICATION_BASE:
            0x00480872 - APPLICATION_BASE
        ]
        self.assertEqual(len(next_function), 8)
        self.assertEqual(
            hashlib.sha256(next_function).hexdigest(),
            "28fbddc5962a26c875030d4bb760e1ab"
            "3a1c002294b2e957a125e35ecff3d1bd",
        )

    def test_raw_branch_topology_and_dependencies_are_pinned(self) -> None:
        application = OFFICIAL.read_bytes()[32:]
        sys.path.insert(0, str(OPENCFW_ROOT / "tools")); sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        import apollo_overlay

        expectations = (
            (
                STATUS_CHANGE_START,
                STATUS_CHANGE_END,
                (
                    0x0047EFC6, 0x0047F580, 0x0047F592,
                    0x0047F5B2, 0x0047F6C2, 0x004D4074,
                    0x00539278, 0x005392BC, 0x005392E6,
                    0x005A1DDC, 0x005A283C, 0x005A2BDA,
                    0x005A3046, 0x005A3480, 0x005A4E44,
                ),
                ((0x00480812, 0x004807A0),),
            ),
            (
                STATUS_CHECK_START,
                STATUS_CHECK_END,
                (
                    0x0044B238, 0x0047F2C2, 0x0047F2E4,
                    0x0047F4BE, 0x0047F6A8, 0x0047F80C,
                    0x0047F876, 0x0047FF70, 0x0047FF94,
                    0x004BFBAC, 0x004BFC0A, 0x004BFC2E,
                    0x004BFDEA, 0x004C21EC, 0x004D397E,
                    0x00539BB6, 0x0055C3F4, 0x0055C928,
                    0x0055CCB6, 0x0055CCD8, 0x0055CDEC,
                    0x0055CFE4, 0x0055D008, 0x0055D176,
                ),
                ((0x00480840, 0x004807A0),),
            ),
        )

        for start, end, expected_calls, expected_dependencies in expectations:
            calls = []
            jumps = []
            external_interior = []
            dependencies = []
            for offset in range(0, len(application) - 3, 2):
                address = APPLICATION_BASE + offset
                encoded = application[offset:offset + 4]
                for link, observed in ((True, calls), (False, jumps)):
                    try:
                        target = apollo_overlay.decode_thumb_branch(
                            address,
                            encoded,
                            link=link,
                        )
                    except apollo_overlay.BuildError:
                        continue
                    if target == start:
                        observed.append(address)
                    if (
                        start < target < end
                        and not start <= address < end
                    ):
                        external_interior.append((address, target, link))
                    if link and start <= address < end:
                        dependencies.append((address, target))
            self.assertEqual(tuple(calls), expected_calls)
            self.assertEqual(jumps, [])
            self.assertEqual(external_interior, [])
            self.assertEqual(tuple(dependencies), expected_dependencies)

            stored = []
            for offset in range(0, len(application) - 3, 4):
                value = struct.unpack_from("<I", application, offset)[0]
                target = value & ~1
                if value & 1 and start <= target < end:
                    stored.append((APPLICATION_BASE + offset, target))
            self.assertEqual(stored, [])

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "9fc43c102bb134523abe6d759db8d5da"
            "234dd70a8ee0b47e913aee6c5f6e1c74",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "c508af7e88237d2395bb3b069b02f0d2"
            "7d563f3f5d2ac688bd4b43383f7b6887",
        )


if __name__ == "__main__":
    unittest.main()
