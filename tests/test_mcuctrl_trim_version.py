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
SOURCE = COMPONENT_ROOT / "mcuctrl_trim_version.c"
FIXTURE = (
    OPENCFW_ROOT / "tests" / "fixtures" / "mcuctrl_trim_version_host.c"
)
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
STOCK_START = 0x00480C7C
STOCK_END = 0x00480D72
CHIPREV_ADDRESS = 0x4002000C
INFO1_READ_ENTRY = 0x004D3F3C


class McuctrlTrimVersionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "mcuctrl_trim_version.dylib"
            if sys.platform == "darwin"
            else "mcuctrl_trim_version.so"
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
        cls.reset = cls.loaded.open_cfw_test_mcuctrl_trim_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.get_trim = cls.loaded.open_cfw_mcuctrl_trim_version_get
        cls.get_trim.argtypes = [ctypes.POINTER(ctypes.c_uint)]
        cls.get_trim.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_mcuctrl_trim_{name}",
        )

    @classmethod
    def words(cls, name: str) -> ctypes.Array:
        return (ctypes.c_uint * 4).in_dll(
            cls.loaded,
            f"open_cfw_test_mcuctrl_trim_{name}",
        )

    def run_trim(
        self,
        trim_version: int,
        read_status: int,
        chiprevs: tuple[int, ...],
    ) -> tuple[int, tuple[int, ...], list[int]]:
        self.word("read_value").value = trim_version
        self.word("read_status").value = read_status
        values = self.words("chiprev_values")
        values[:len(chiprevs)] = chiprevs
        feature = (ctypes.c_uint * 4)(
            0x11111111,
            0x22222222,
            0x33333333,
            0x44444444,
        )

        status = self.get_trim(feature)

        reads = self.word("chiprev_reads").value
        addresses = list(self.words("chiprev_addresses")[:reads])
        return status, tuple(feature), addresses

    def assert_info1_abi(self) -> None:
        self.assertEqual(self.word("read_calls").value, 1)
        self.assertEqual(self.word("info_space").value, 1)
        self.assertEqual(self.word("word_offset").value, 0x244)
        self.assertEqual(self.word("word_count").value, 1)
        self.assertEqual(self.word("destination_nonnull").value, 1)

    def test_non_pcm_success_packs_minor_and_valid_flag(self) -> None:
        self.assertEqual(
            self.run_trim(0x123456AB, 0, (0x10,)),
            (
                0,
                (0x11111111, 0x22222222, 0x33333333, 0x000100AB),
                [CHIPREV_ADDRESS],
            ),
        )
        self.assert_info1_abi()

    def test_pcm_b1_is_one_based_and_b2_is_zero_based(self) -> None:
        self.assertEqual(
            self.run_trim(7, 0, (0x20, 0x22, 0x22)),
            (
                0,
                (0x11111111, 0x22222222, 0x33333333, 0x00030206),
                [CHIPREV_ADDRESS] * 3,
            ),
        )
        self.reset()
        self.assertEqual(
            self.run_trim(7, 0, (0x20, 0x23, 0x23)),
            (
                0,
                (0x11111111, 0x22222222, 0x33333333, 0x00030207),
                [CHIPREV_ADDRESS] * 3,
            ),
        )

    def test_pcm_qualification_short_circuits_register_reads(self) -> None:
        cases = (
            ((0x10,), 254, 0x000100FE, 1),
            ((0x20, 0x21), 254, 0x000100FE, 2),
            ((0x20, 0x22), 255, 0x000100FF, 2),
            ((0x20, 0x22, 0x24), 254, 0x000302FD, 3),
        )
        for chiprevs, trim_version, packed, reads in cases:
            with self.subTest(
                chiprevs=chiprevs,
                trim_version=trim_version,
            ):
                self.reset()
                status, feature, addresses = self.run_trim(
                    trim_version,
                    0,
                    chiprevs,
                )
                self.assertEqual(status, 0)
                self.assertEqual(feature[3], packed)
                self.assertEqual(addresses, [CHIPREV_ADDRESS] * reads)

    def test_reader_failure_keeps_minor_but_clears_flags(self) -> None:
        for status in (1, 6, 0xFFFFFFFF):
            with self.subTest(status=status):
                self.reset()
                observed = self.run_trim(
                    0x123456AB,
                    status,
                    (0x23,),
                )
                self.assertEqual(
                    observed,
                    (
                        status,
                        (
                            0x11111111,
                            0x22222222,
                            0x33333333,
                            0x000000AB,
                        ),
                        [],
                    ),
                )
                self.assert_info1_abi()

    def test_randomized_stock_model(self) -> None:
        rng = random.Random(STOCK_START)
        for iteration in range(1000):
            with self.subTest(iteration=iteration):
                self.reset()
                trim_version = rng.getrandbits(32)
                status = rng.getrandbits(32)
                chiprevs = tuple(rng.getrandbits(32) for _ in range(3))
                observed_status, feature, addresses = self.run_trim(
                    trim_version,
                    status,
                    chiprevs,
                )

                expected_reads = 0
                packed = trim_version & 0xFF
                if status == 0:
                    packed |= 0x10000
                    expected_reads = 1
                    if ((chiprevs[0] >> 4) & 0xF) == 2:
                        expected_reads = 2
                        if (
                            (chiprevs[1] & 0xF) >= 2
                            and trim_version < 0xFF
                        ):
                            expected_reads = 3
                            minor = trim_version
                            if (chiprevs[2] & 0xF) != 3:
                                minor -= 1
                            packed = 0x30200 | (minor & 0xFF)

                self.assertEqual(observed_status, status)
                self.assertEqual(
                    feature,
                    (
                        0x11111111,
                        0x22222222,
                        0x33333333,
                        packed,
                    ),
                )
                self.assertEqual(
                    addresses,
                    [CHIPREV_ADDRESS] * expected_reads,
                )
                self.assert_info1_abi()

    def test_stock_span_topology_dependency_and_literal_are_pinned(
        self,
    ) -> None:
        application = OFFICIAL.read_bytes()[32:]
        stock = application[
            STOCK_START - APPLICATION_BASE:STOCK_END - APPLICATION_BASE
        ]
        self.assertEqual(len(stock), 246)
        self.assertEqual(
            hashlib.sha256(stock).hexdigest(),
            "4e7c5d4c775be7a1a4cc04083e48387"
            "e4afbee82847afee4566ed22133804179",
        )
        following = application[
            STOCK_END - APPLICATION_BASE:
            0x00480E6C - APPLICATION_BASE
        ]
        self.assertEqual(len(following), 250)
        self.assertEqual(
            hashlib.sha256(following).hexdigest(),
            "0c18f10e46821f635613de6df1d3a364"
            "319902ac828dd3f87f1146975b2b9199",
        )
        self.assertEqual(
            struct.unpack_from(
                "<I",
                application,
                0x00480E7C - APPLICATION_BASE,
            )[0],
            CHIPREV_ADDRESS,
        )

        sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
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
        self.assertEqual(callers, [0x00480E58])
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(dependencies, [(0x00480C8A, INFO1_READ_ENTRY)])

        stored = []
        for offset in range(0, len(application) - 3, 4):
            value = struct.unpack_from("<I", application, offset)[0]
            target = value & ~1
            if value & 1 and STOCK_START <= target < STOCK_END:
                stored.append((APPLICATION_BASE + offset, target))
        self.assertEqual(stored, [])

    def test_source_preserves_info1_abi_and_packed_field(self) -> None:
        source = SOURCE.read_text()
        self.assertIn(
            "OPEN_CFW_MCUCTRL_TRIM_REVISION_WORD_OFFSET 0x244U",
            source,
        )
        self.assertIn(
            "OPEN_CFW_MCUCTRL_CHIPREV_ADDRESS 0x4002000CU",
            source,
        )
        self.assertIn("feature_words[3] = packed_trim", source)
        self.assertEqual(
            source.count("OPEN_CFW_MCUCTRL_TRIM_READ32("),
            4,
        )

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "83c6cb5803000cd94ff0cf626b9aebddd"
            "49200f36947b4c766a86a5e23ba17f5",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "df87dbe0d1b586d6c2eb1f9026363a35"
            "e8bafe3bf909abeb1a17630b278b19e2",
        )


if __name__ == "__main__":
    unittest.main()
