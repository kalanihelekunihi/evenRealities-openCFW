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
SOURCE = COMPONENT_ROOT / "mcuctrl_control.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "mcuctrl_control_host.c"
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
STOCK_START = 0x004809C4
STOCK_END = 0x00480C56
REGISTER_ADDRESSES = (
    0x40020120,
    0x40020128,
    0x4002012C,
    0x200001E0,
    0x200001E4,
)


class McuctrlControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "mcuctrl_control.dylib"
            if sys.platform == "darwin"
            else "mcuctrl_control.so"
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
        cls.reset = cls.loaded.open_cfw_test_mcuctrl_control_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.control = cls.loaded.open_cfw_mcuctrl_control
        cls.control.argtypes = [ctypes.c_uint, ctypes.c_void_p]
        cls.control.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_mcuctrl_control_{name}",
        )

    @classmethod
    def words(cls, name: str, count: int) -> ctypes.Array:
        return (ctypes.c_uint * count).in_dll(
            cls.loaded,
            f"open_cfw_test_mcuctrl_control_{name}",
        )

    def events(self) -> list[tuple[int, int, int, int]]:
        count = self.word("event_count").value
        return list(
            zip(
                self.words("event_kind", 128)[:count],
                self.words("event_address", 128)[:count],
                self.words("event_value", 128)[:count],
                self.words("event_result", 128)[:count],
            )
        )

    def run_control(
        self,
        control: int,
        registers: list[int],
        argument: int | None,
        *,
        request_result: int = 0,
        release_result: int = 0,
        argument32_sequence: tuple[int, ...] = (),
    ) -> tuple[int, list[int], list[tuple[int, int, int, int]]]:
        target = self.words("registers", 5)
        target[:] = registers
        self.word("clock_request_result").value = request_result
        self.word("clock_release_result").value = release_result
        if argument32_sequence:
            sequence = self.words("argument32_sequence", 8)
            sequence[:len(argument32_sequence)] = argument32_sequence
            self.word("argument32_count").value = len(argument32_sequence)

        holder = ctypes.c_uint(argument or 0)
        pointer = None if argument is None else ctypes.byref(holder)
        result = self.control(control, pointer)
        return result, list(target), self.events()

    @staticmethod
    def model(
        control: int,
        registers: list[int],
        argument: int | None,
        *,
        request_result: int = 0,
        release_result: int = 0,
        argument32_sequence: tuple[int, ...] = (),
    ) -> tuple[int, list[int], list[tuple[int, int, int, int]]]:
        values = list(registers)
        events: list[tuple[int, int, int, int]] = []
        argument32_index = 0

        def read(index: int) -> int:
            value = values[index] & 0xFFFFFFFF
            events.append((1, REGISTER_ADDRESSES[index], value, 0))
            return value

        def write(index: int, value: int) -> None:
            value &= 0xFFFFFFFF
            values[index] = value
            events.append((2, REGISTER_ADDRESSES[index], value, 0))

        def argument8() -> int:
            assert argument is not None
            value = argument & 0xFF
            events.append((3, 0, value, 0))
            return value

        def argument32() -> int:
            nonlocal argument32_index
            assert argument is not None
            if argument32_index < len(argument32_sequence):
                value = argument32_sequence[argument32_index]
            else:
                value = argument
            argument32_index += 1
            value &= 0xFFFFFFFF
            events.append((4, 0, value, 0))
            return value

        def trim(constant: int) -> int:
            return (
                (read(1) & 0xC0007000)
                | (read(3) & 0x3F)
                | ((read(4) & 0x0F) << 6)
                | constant
            ) & 0xFFFFFFFF

        command = control & 0xFF
        if command == 0:
            value = read(0) & 0xFFFFFFE0
            value |= 5 if argument is not None and argument8() == 1 else 0x19
            write(0, value)
        elif command == 1:
            write(0, read(0) & 0xFFFFFFFC)
        elif command == 2:
            write(1, trim(0x0FFF8C00))
            write(2, (read(2) & 0xFFFFFFDD) | 2)
            write(2, read(2) | 1)
            write(2, read(2) | 0x10)
            write(2, read(2) | 8)
            events.append((5, 0, 5, 0))
            write(2, read(2) & 0xFFFFFFEF)
            if argument is not None and argument8() == 1:
                write(2, (read(2) & 0xFFFFFEF6) | 0x100)
        elif command == 3:
            write(1, trim(0x0FFF8C00))
            write(2, (read(2) & 0xFFFFFFDD) | 0x22)
            write(2, read(2) | 1)
            value = read(2)
            if argument is not None and argument8() == 1:
                value = (value & 0xFFFFFEFE) | 0x100
            else:
                value = (value & 0xFFFFFFD7) | 8
            write(2, value)
        elif command == 4:
            write(1, trim(0x03118000))
            write(2, (read(2) & 0xFFFFFED4) | 2)
        elif command == 5:
            events.append((6, 2, 0x34, request_result & 0xFFFFFFFF))
            if request_result:
                return request_result & 0xFFFFFFFF, values, events
            if argument is None:
                strength = 4
            else:
                strength = argument32()
                if strength != 0 and not 3 <= strength <= 7:
                    return 6, values, events
                strength = argument32()
            write(1, (read(1) & 0xFFFF8FFF) | ((strength & 7) << 12))
            write(2, read(2) | 0x80)
        elif command == 6:
            write(1, read(1) | 0x7000)
            write(2, read(2) & 0xFFFFFF7F)
            events.append((7, 2, 0x34, release_result & 0xFFFFFFFF))
            if release_result:
                return release_result & 0xFFFFFFFF, values, events
        else:
            return 6, values, events
        return 0, values, events

    def assert_model(
        self,
        control: int,
        registers: list[int],
        argument: int | None,
        **kwargs: object,
    ) -> None:
        observed = self.run_control(
            control,
            registers,
            argument,
            **kwargs,
        )
        expected = self.model(
            control,
            registers,
            argument,
            **kwargs,
        )
        self.assertEqual(observed, expected)

    def test_32k_enable_disable_and_low_byte_dispatch(self) -> None:
        for argument in (None, 0, 1, 2, 0x101):
            with self.subTest(argument=argument):
                self.reset()
                self.assert_model(0xA500, [0xFFFFFFFF] * 5, argument)
        self.reset()
        self.assert_model(0x101, [0x89ABCDEF] * 5, None)

    def test_kick_start_preserves_exact_transaction_order(self) -> None:
        for argument in (None, 0, 1, 2):
            with self.subTest(argument=argument):
                self.reset()
                self.assert_model(
                    2,
                    [
                        0x01234567,
                        0xD5A5B6C7,
                        0xA5A55A5A,
                        0xFFFFFF2C,
                        0x12345674,
                    ],
                    argument,
                )

    def test_normal_and_disable_modes_match_register_model(self) -> None:
        registers = [
            0x87654321,
            0xC0007123,
            0xFFFFFEFF,
            0x00000015,
            0x0000000A,
        ]
        for control in (3, 4):
            for argument in (None, 0, 1, 2):
                with self.subTest(control=control, argument=argument):
                    self.reset()
                    self.assert_model(control, registers, argument)

    def test_clkout_enable_request_validation_and_fresh_argument(self) -> None:
        registers = [0, 0xABCDEF01, 0x12345678, 0, 0]
        for argument in (None, 0, 3, 4, 5, 6, 7, 1, 2, 8, 0xFFFFFFFF):
            with self.subTest(argument=argument):
                self.reset()
                self.assert_model(5, registers, argument)
        self.reset()
        self.assert_model(5, registers, 4, request_result=0xA5)
        self.reset()
        self.assert_model(
            5,
            registers,
            3,
            argument32_sequence=(3, 7),
        )

    def test_clkout_disable_writes_before_release_result(self) -> None:
        for result in (0, 1, 6, 0xFFFFFFFF):
            with self.subTest(result=result):
                self.reset()
                self.assert_model(
                    6,
                    [0, 0x12340000, 0xFFFFFFFF, 0, 0],
                    None,
                    release_result=result,
                )

    def test_randomized_all_command_model(self) -> None:
        rng = random.Random(0x4809C4)
        for iteration in range(500):
            with self.subTest(iteration=iteration):
                self.reset()
                command = rng.randrange(12)
                control = command | (rng.getrandbits(24) << 8)
                registers = [rng.getrandbits(32) for _ in range(5)]
                argument = (
                    None
                    if rng.randrange(4) == 0
                    else rng.getrandbits(32)
                )
                request_result = (
                    rng.choice((0, 0, 0, 1, 6))
                    if command == 5
                    else 0
                )
                release_result = (
                    rng.choice((0, 0, 1, 6))
                    if command == 6
                    else 0
                )
                self.assert_model(
                    control,
                    registers,
                    argument,
                    request_result=request_result,
                    release_result=release_result,
                )

    def test_stock_spans_literal_pool_and_dependencies_are_pinned(self) -> None:
        application = OFFICIAL.read_bytes()[32:]
        stock = application[
            STOCK_START - APPLICATION_BASE:STOCK_END - APPLICATION_BASE
        ]
        self.assertEqual(len(stock), 658)
        self.assertEqual(
            hashlib.sha256(stock).hexdigest(),
            "eb3d3bb0a11febea901aa2630257bf91"
            "b9993e4b363b608e875ac34871df3624",
        )
        following = application[
            STOCK_END - APPLICATION_BASE:
            0x00480C7C - APPLICATION_BASE
        ]
        self.assertEqual(len(following), 38)
        self.assertEqual(
            hashlib.sha256(following).hexdigest(),
            "19e5abd53ba53fb1a0b3f74bc40bbf57"
            "75c13e7b17d015c1598706fa788424e7",
        )
        pool = application[
            0x00480EB0 - APPLICATION_BASE:
            0x00480ED8 - APPLICATION_BASE
        ]
        self.assertEqual(
            struct.unpack("<10I", pool),
            (
                0x40020120,
                0x40020128,
                0xC0007000,
                0x200001E0,
                0x200001E4,
                0x0FFF8C00,
                0x4002012C,
                0xFFFFFEF6,
                0xFFFFFEFE,
                0xFFFFFED4,
            ),
        )

        sys.path.insert(0, str(OPENCFW_ROOT / "tools")); sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        import apollo_overlay

        callers = []
        jumps = []
        interior = []
        dependencies = []
        for offset in range(0, len(application) - 3, 2):
            address = APPLICATION_BASE + offset
            encoded = application[offset:offset + 4]
            for link, observed in ((True, callers), (False, jumps)):
                try:
                    target = apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except apollo_overlay.BuildError:
                    continue
                if target == STOCK_START:
                    observed.append(address)
                if (
                    STOCK_START < target < STOCK_END
                    and not STOCK_START <= address < STOCK_END
                ):
                    interior.append((address, target, link))
                if link and STOCK_START <= address < STOCK_END:
                    dependencies.append((address, target))
        self.assertEqual(
            callers,
            [
                0x0044B27E,
                0x0044B4A0,
                0x004C3E30,
                0x004C3E3A,
                0x004C3ED6,
            ],
        )
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(
            dependencies,
            [
                (0x00480AA2, 0x004807A0),
                (0x00480BC6, 0x004C44BC),
                (0x00480C46, 0x004C4530),
            ],
        )

        stored = []
        for offset in range(0, len(application) - 3, 4):
            value = struct.unpack_from("<I", application, offset)[0]
            target = value & ~1
            if value & 1 and STOCK_START <= target < STOCK_END:
                stored.append((APPLICATION_BASE + offset, target))
        self.assertEqual(stored, [])

    def test_source_uses_reviewed_fixed_dependencies(self) -> None:
        source = SOURCE.read_text()
        for token in (
            "OPEN_CFW_MCUCTRL_CONTROL_DELAY_US_ENTRY 0x004807A1U",
            "OPEN_CFW_MCUCTRL_CONTROL_CLOCK_REQUEST_ENTRY 0x004C44BDU",
            "OPEN_CFW_MCUCTRL_CONTROL_CLOCK_RELEASE_ENTRY 0x004C4531U",
            "switch ((unsigned char)control)",
            "OPEN_CFW_MCUCTRL_CONTROL_ARGUMENT32(arguments)",
            "value != 0U && (value < 3U || value > 7U)",
        ):
            self.assertIn(token, source)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "e4af74a7b4848c5c78178c75f225ee05"
            "e35eef147bc6f01fcfe692cfc07bdccb",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "b4a8529e0a37891a6f647717e1086d00"
            "ed812c2528110a9de92b88b9eacd9683",
        )


if __name__ == "__main__":
    unittest.main()
