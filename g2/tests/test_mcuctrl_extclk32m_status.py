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
SOURCE = COMPONENT_ROOT / "mcuctrl_extclk32m_status.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "mcuctrl_extclk32m_status_host.c"
)
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
STOCK_START = 0x00480C56
STOCK_END = 0x00480C7C
REGISTER_ADDRESS = 0x4002012C


class McuctrlExtclk32mStatusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "mcuctrl_extclk32m_status.dylib"
            if sys.platform == "darwin"
            else "mcuctrl_extclk32m_status.so"
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
        cls.reset = (
            cls.loaded.open_cfw_test_mcuctrl_extclk32m_status_reset
        )
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.status_get = (
            cls.loaded.open_cfw_mcuctrl_extclk32m_status_get
        )
        cls.status_get.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]
        cls.status_get.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_mcuctrl_extclk32m_status_{name}",
        )

    @classmethod
    def words(cls, name: str) -> ctypes.Array:
        return (ctypes.c_uint * 4).in_dll(
            cls.loaded,
            f"open_cfw_test_mcuctrl_extclk32m_status_{name}",
        )

    def run_status(self, reads: tuple[int, ...]) -> tuple[int, int, list[int]]:
        self.reset()
        source = self.words("reads")
        source[:len(reads)] = reads
        status = ctypes.c_ubyte(0xA5)
        result = self.status_get(ctypes.byref(status))
        count = self.word("read_count").value
        addresses = list(self.words("addresses")[:count])
        return result, status.value, addresses

    def test_external_clock_has_precedence_and_one_read(self) -> None:
        for value in (0x100, 0x101, 0xFFFFFFFF):
            with self.subTest(value=value):
                self.assertEqual(
                    self.run_status((value, 0)),
                    (0, 2, [REGISTER_ADDRESS]),
                )

    def test_powered_crystal_uses_fresh_second_read(self) -> None:
        self.assertEqual(
            self.run_status((0, 1)),
            (0, 1, [REGISTER_ADDRESS, REGISTER_ADDRESS]),
        )
        self.assertEqual(
            self.run_status((1, 0)),
            (0, 0, [REGISTER_ADDRESS, REGISTER_ADDRESS]),
        )

    def test_off_state_reads_register_twice(self) -> None:
        self.assertEqual(
            self.run_status((0, 0)),
            (0, 0, [REGISTER_ADDRESS, REGISTER_ADDRESS]),
        )

    def test_randomized_two_read_model(self) -> None:
        rng = random.Random(STOCK_START)
        for iteration in range(500):
            with self.subTest(iteration=iteration):
                first = rng.getrandbits(32)
                second = rng.getrandbits(32)
                if first & 0x100:
                    expected = (0, 2, [REGISTER_ADDRESS])
                elif second & 1:
                    expected = (
                        0,
                        1,
                        [REGISTER_ADDRESS, REGISTER_ADDRESS],
                    )
                else:
                    expected = (
                        0,
                        0,
                        [REGISTER_ADDRESS, REGISTER_ADDRESS],
                    )
                self.assertEqual(self.run_status((first, second)), expected)

    def test_stock_span_caller_and_literal_are_pinned(self) -> None:
        application = OFFICIAL.read_bytes()[32:]
        stock = application[
            STOCK_START - APPLICATION_BASE:STOCK_END - APPLICATION_BASE
        ]
        self.assertEqual(len(stock), 38)
        self.assertEqual(
            hashlib.sha256(stock).hexdigest(),
            "19e5abd53ba53fb1a0b3f74bc40bbf57"
            "75c13e7b17d015c1598706fa788424e7",
        )
        following = application[
            STOCK_END - APPLICATION_BASE:
            0x00480D72 - APPLICATION_BASE
        ]
        self.assertEqual(len(following), 246)
        self.assertEqual(
            hashlib.sha256(following).hexdigest(),
            "4e7c5d4c775be7a1a4cc04083e48387"
            "e4afbee82847afee4566ed22133804179",
        )
        self.assertEqual(
            struct.unpack_from(
                "<I",
                application,
                0x00480EC8 - APPLICATION_BASE,
            )[0],
            REGISTER_ADDRESS,
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
        self.assertEqual(callers, [0x004C3DFE])
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(dependencies, [])

        stored = []
        for offset in range(0, len(application) - 3, 4):
            value = struct.unpack_from("<I", application, offset)[0]
            target = value & ~1
            if value & 1 and STOCK_START <= target < STOCK_END:
                stored.append((APPLICATION_BASE + offset, target))
        self.assertEqual(stored, [])

    def test_source_preserves_short_enum_and_fresh_read(self) -> None:
        source = SOURCE.read_text()
        self.assertIn(
            "OPEN_CFW_MCUCTRL_XTALHSCTRL_ADDRESS 0x4002012CU",
            source,
        )
        self.assertEqual(
            source.count("OPEN_CFW_MCUCTRL_EXTCLK32M_STATUS_READ32("),
            3,
        )
        self.assertIn("unsigned char *status", source)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "986c0e4341672855f16ed7cd4cdab437"
            "2549bcfae58436ba8526fa26ad1224c7",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "6872f5d86bafce6884b7d0fe612e4abc"
            "eab0c9e780f85d0f2959c7256866a91c",
        )


if __name__ == "__main__":
    unittest.main()
