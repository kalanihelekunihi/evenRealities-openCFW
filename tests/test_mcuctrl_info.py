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
SOURCE = COMPONENT_ROOT / "mcuctrl_info.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "mcuctrl_info_host.c"
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
STOCK_START = 0x00480D72
STOCK_END = 0x00480E6C
SKU_ADDRESS = 0x40020014


class McuctrlInfoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "mcuctrl_info.dylib"
            if sys.platform == "darwin"
            else "mcuctrl_info.so"
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
        cls.reset = cls.loaded.open_cfw_test_mcuctrl_info_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.get_info = cls.loaded.open_cfw_mcuctrl_info_get
        cls.get_info.argtypes = [ctypes.c_uint, ctypes.c_void_p]
        cls.get_info.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_mcuctrl_info_{name}",
        )

    @classmethod
    def words(cls, name: str) -> ctypes.Array:
        return (ctypes.c_uint * 12).in_dll(
            cls.loaded,
            f"open_cfw_test_mcuctrl_info_{name}",
        )

    def buffer(self) -> ctypes.Array:
        result = (ctypes.c_ubyte * 64)(*([0xCC] * 64))
        expected_pointer = ctypes.c_void_p.in_dll(
            self.loaded,
            "open_cfw_test_mcuctrl_info_expected_pointer",
        )
        expected_pointer.value = ctypes.addressof(result)
        return result

    def set_sku_reads(self, values: tuple[int, ...]) -> None:
        self.words("sku_values")[:len(values)] = values

    def test_null_and_invalid_arguments_have_no_side_effects(self) -> None:
        for selector in (0, 1, 2, 0xFFFFFFFF):
            with self.subTest(selector=selector):
                self.reset()
                self.assertEqual(self.get_info(selector, None), 6)
                self.assertEqual(self.word("sku_reads").value, 0)
                self.assertEqual(self.word("trim_calls").value, 0)
                self.assertEqual(self.word("device_calls").value, 0)

        for selector in (2, 0x102, 0xFF):
            with self.subTest(selector=selector):
                self.reset()
                output = self.buffer()
                before = bytes(output)
                self.assertEqual(self.get_info(selector, output), 6)
                self.assertEqual(bytes(output), before)
                self.assertEqual(self.word("sku_reads").value, 0)
                self.assertEqual(self.word("trim_calls").value, 0)
                self.assertEqual(self.word("device_calls").value, 0)

    def test_all_sram_feature_mappings(self) -> None:
        expected = (
            (0, 0, 0),
            (0, 0, 1),
            (1, 1, 1),
            (1, 1, 2),
        )
        for sku_size, fields in enumerate(expected):
            with self.subTest(sku_size=sku_size):
                self.reset()
                output = self.buffer()
                self.set_sku_reads((sku_size,) * 9)

                self.assertEqual(self.get_info(0, output), 0)

                self.assertEqual(tuple(output[:3]), fields)
                self.assertEqual(self.word("sku_reads").value, 9)
                self.assertEqual(
                    list(self.words("sku_addresses")[:9]),
                    [SKU_ADDRESS] * 9,
                )
                self.assertEqual(self.word("trim_calls").value, 1)
                self.assertEqual(self.word("device_calls").value, 0)

    def test_each_feature_uses_a_fresh_sku_read(self) -> None:
        values = (
            3,
            2 << 2,
            1 << 6,
            1 << 7,
            1 << 8,
            1 << 9,
            1 << 10,
            1 << 19,
            2 << 20,
        )
        output = self.buffer()
        self.set_sku_reads(values)
        self.word("trim_status").value = 0xFFFFFFFF

        self.assertEqual(self.get_info(0, output), 0)

        self.assertEqual(
            tuple(output[:11]),
            (1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 2),
        )
        self.assertEqual(output[11], 0xCC)
        self.assertEqual(
            struct.unpack_from("<I", bytes(output), 12)[0],
            0xA5A55A5A,
        )
        self.assertEqual(self.word("trim_calls").value, 1)
        self.assertEqual(self.word("trim_pointer_matches").value, 1)
        self.assertEqual(self.word("device_calls").value, 0)

    def test_low_byte_selector_and_device_dispatch(self) -> None:
        output = self.buffer()
        self.assertEqual(self.get_info(0x101, output), 0)
        self.assertEqual(
            struct.unpack_from("<I", bytes(output), 0)[0],
            0xD3D1C3D1,
        )
        self.assertEqual(self.word("device_calls").value, 1)
        self.assertEqual(self.word("device_pointer_matches").value, 1)
        self.assertEqual(self.word("trim_calls").value, 0)
        self.assertEqual(self.word("sku_reads").value, 0)

        self.reset()
        output = self.buffer()
        self.set_sku_reads((0,) * 9)
        self.assertEqual(self.get_info(0x100, output), 0)
        self.assertEqual(self.word("trim_calls").value, 1)
        self.assertEqual(self.word("device_calls").value, 0)

    def test_randomized_feature_model(self) -> None:
        rng = random.Random(STOCK_START)
        mappings = (
            (0, 0, 0),
            (0, 0, 1),
            (1, 1, 1),
            (1, 1, 2),
        )
        for iteration in range(500):
            with self.subTest(iteration=iteration):
                self.reset()
                values = tuple(rng.getrandbits(32) for _ in range(9))
                output = self.buffer()
                self.set_sku_reads(values)
                self.word("trim_status").value = rng.getrandbits(32)

                self.assertEqual(self.get_info(0, output), 0)

                expected = mappings[values[0] & 3] + (
                    (values[1] >> 2) & 3,
                    (values[2] >> 6) & 1,
                    (values[3] >> 7) & 1,
                    (values[4] >> 8) & 1,
                    (values[5] >> 9) & 1,
                    (values[6] >> 10) & 1,
                    (values[7] >> 19) & 1,
                    (values[8] >> 20) & 3,
                )
                self.assertEqual(tuple(output[:11]), expected)
                self.assertEqual(output[11], 0xCC)
                self.assertEqual(self.word("sku_reads").value, 9)
                self.assertEqual(self.word("trim_calls").value, 1)
                self.assertEqual(self.word("device_calls").value, 0)

    def test_stock_span_topology_dependencies_and_literal_are_pinned(
        self,
    ) -> None:
        application = OFFICIAL.read_bytes()[32:]
        stock = application[
            STOCK_START - APPLICATION_BASE:STOCK_END - APPLICATION_BASE
        ]
        self.assertEqual(len(stock), 250)
        self.assertEqual(
            hashlib.sha256(stock).hexdigest(),
            "0c18f10e46821f635613de6df1d3a364"
            "319902ac828dd3f87f1146975b2b9199",
        )
        following = application[
            STOCK_END - APPLICATION_BASE:
            0x00480ED8 - APPLICATION_BASE
        ]
        self.assertEqual(len(following), 108)
        self.assertEqual(
            hashlib.sha256(following).hexdigest(),
            "4664f5a57e3b6a2fb5f9ce35b8570c1"
            "206f968cfad80379ef25a54da04695483",
        )
        self.assertEqual(
            struct.unpack_from(
                "<I",
                application,
                0x00480E84 - APPLICATION_BASE,
            )[0],
            SKU_ADDRESS,
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
        # A whole-image byte scan also finds two branch-shaped encodings in
        # non-code ranges. Ghidra has no containing function for either site,
        # so pin them separately instead of treating them as executable
        # callers or silently discarding the raw evidence.
        self.assertEqual(
            callers,
            [
                0x004B4980,
                0x00512C98,
                0x005A4F0E,
                0x005D9F56,
            ],
        )
        self.assertEqual(
            application[
                0x005A4F0E - APPLICATION_BASE:
                0x005A4F12 - APPLICATION_BASE
            ],
            bytes.fromhex("dbf630ff"),
        )
        self.assertEqual(
            application[
                0x005D9F56 - APPLICATION_BASE:
                0x005D9F5A - APPLICATION_BASE
            ],
            bytes.fromhex("a6f60cff"),
        )
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(
            dependencies,
            [
                (0x00480E58, 0x00480C7C),
                (0x00480E62, 0x00480874),
            ],
        )

        stored = []
        for offset in range(0, len(application) - 3, 4):
            value = struct.unpack_from("<I", application, offset)[0]
            target = value & ~1
            if value & 1 and STOCK_START <= target < STOCK_END:
                stored.append((APPLICATION_BASE + offset, target))
        self.assertEqual(stored, [])

    def test_source_preserves_short_enum_layout_and_source_calls(
        self,
    ) -> None:
        source = SOURCE.read_text()
        for token in (
            "switch ((unsigned char)info_get)",
            "OPEN_CFW_MCUCTRL_INFO_SKU_ADDRESS 0x40020014U",
            "feature[10]",
            "OPEN_CFW_MCUCTRL_INFO_TRIM_VERSION_GET(information)",
            "OPEN_CFW_MCUCTRL_INFO_DEVICE_INFO_GET(information)",
        ):
            self.assertIn(token, source)
        self.assertEqual(
            source.count("OPEN_CFW_MCUCTRL_INFO_READ32("),
            10,
        )

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "46d0b960cca257c251805a71d76eeb7d"
            "b6b7cba16e1eb1bbaf5564c3951698b0",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "5f0ecb79904fc5b2c521565fb598a2de"
            "206a4b9d5c1340767a194474c649286d",
        )


if __name__ == "__main__":
    unittest.main()
