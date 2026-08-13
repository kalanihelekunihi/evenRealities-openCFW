from __future__ import annotations

import hashlib
import struct
import sys
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
STOCK_START = 0x00481836
STOCK_END = 0x004824EE
LITERAL_END = 0x00482518


def _sign_extend(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return value - (1 << bits) if value & sign else value


class RuntimeFormatCoreBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]

    @classmethod
    def span(cls, start: int, end: int) -> bytes:
        return cls.application[
            start - APPLICATION_BASE:end - APPLICATION_BASE
        ]

    def test_first_opaque_byte_is_a_complete_function_entry(self) -> None:
        body = self.span(STOCK_START, STOCK_END)
        self.assertEqual(len(body), 3256)
        self.assertEqual(
            hashlib.sha256(body).hexdigest(),
            "0ace800002b34fa464fd3a816691e77df"
            "43a7919b2747ef608d0b89213786fb0",
        )
        self.assertEqual(
            body[:16].hex(),
            "2de9f14fb0b0924604910df142013a9a",
        )
        self.assertEqual(
            body[-16:].hex(),
            "2c46fff7bcba4ff0ff3031b0bde8f08f",
        )

    def test_following_alignment_literal_pool_and_next_entry_are_exact(
        self,
    ) -> None:
        literal_pool = self.span(STOCK_END, LITERAL_END)
        self.assertEqual(len(literal_pool), 42)
        self.assertEqual(
            literal_pool.hex(),
            "0000cbcccc0c686a6c747a4c00007072696e74665f733a20"
            "62616420257320617267756d656e74000000",
        )
        self.assertEqual(
            hashlib.sha256(literal_pool).hexdigest(),
            "adc812e90c0f52b8d206815c60e08db9"
            "eaeae99c4c0357c3e5a06078be03415d",
        )
        next_body = self.span(0x00482518, 0x0048262C)
        self.assertEqual(len(next_body), 276)
        self.assertEqual(
            hashlib.sha256(next_body).hexdigest(),
            "be063cc5e8c7478419a02b8f09e24e93"
            "209ee2ec042cdcf325729564f91d4897",
        )

    def test_callers_dependencies_and_wide_topology_are_exact(self) -> None:
        sys.path.insert(0, str(OPENCFW_ROOT / "tools")); sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        from apollo_overlay import BuildError, decode_thumb_branch

        callers = []
        jumps = []
        interior = []
        dependencies = []
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
            encoded = self.application[offset:offset + 4]
            for link, observed in ((True, callers), (False, jumps)):
                try:
                    target = decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except BuildError:
                    continue
                if target == STOCK_START:
                    observed.append((address, encoded.hex()))
                if (
                    STOCK_START < target < STOCK_END
                    and not STOCK_START <= address < STOCK_END
                ):
                    interior.append((address, target, link))
                if link and STOCK_START <= address < STOCK_END:
                    dependencies.append(
                        (address, target, encoded.hex())
                    )

        self.assertEqual(
            callers,
            [
                (0x0044B74E, "36f072f8"),
                (0x0044B78C, "36f053f8"),
                (0x004B4746, "cdf776f8"),
                (0x00595A4C, "ebf6f3fe"),
            ],
        )
        self.assertEqual(
            hashlib.sha256(
                b"".join(
                    struct.pack("<I", address)
                    for address, _encoded in callers
                )
            ).hexdigest(),
            "5c4d0623883e5b1aa07f186af492a362"
            "080dc229d0556e25b3bd1e70c982bf31",
        )
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(
            dependencies,
            [
                (0x0048197E, 0x00481818, "fff74bff"),
                (0x00481A4E, 0x004D40A0, "52f027fb"),
                (0x00481A64, 0x00482684, "00f00efe"),
                (0x00481AAE, 0x00482684, "00f0e9fd"),
                (0x00481AF8, 0x00482684, "00f0c4fd"),
                (0x00481B46, 0x00482684, "00f09dfd"),
                (0x00481B76, 0x00482684, "00f085fd"),
                (0x00481B9A, 0x0044A43C, "c8f74ffc"),
                (0x00481BA6, 0x004D40E0, "52f09bfa"),
                (0x00481DDC, 0x00439BE4, "b7f702ff"),
                (0x00481DEE, 0x004D4150, "52f0aff9"),
                (0x00481E64, 0x004D41C0, "52f0acf9"),
                (0x00481E88, 0x0043C0B0, "baf712f9"),
                (0x00481E90, 0x004D41F4, "52f0b0f9"),
                (0x00481E98, 0x004D42F8, "52f02efa"),
                (0x00481EA4, 0x004D4306, "52f02ffa"),
                (0x00481EB0, 0x004D4314, "52f030fa"),
                (0x00481F90, 0x0048262C, "00f04cfb"),
                (0x00481F9E, 0x0048262C, "00f045fb"),
                (0x00481FAA, 0x004D4326, "52f0bcf9"),
                (0x00481FDA, 0x004D4338, "52f0adf9"),
                (0x00482020, 0x004D4346, "52f091f9"),
                (0x0048202C, 0x004D4314, "52f072f9"),
                (0x00482036, 0x004D4354, "52f08df9"),
                (0x004820C0, 0x004D43A8, "52f072f9"),
                (0x0048216A, 0x00439BE4, "b7f73bfd"),
                (0x004821F4, 0x00439BE4, "b7f7f6fc"),
                (0x00482298, 0x00439BE4, "b7f7a4fc"),
                (0x004822D2, 0x00439BE4, "b7f787fc"),
                (0x00482308, 0x00439BE4, "b7f76cfc"),
                (0x00482478, 0x00482518, "00f04ef8"),
            ],
        )
        self.assertEqual(
            hashlib.sha256(
                b"".join(
                    struct.pack("<II", address, target)
                    for address, target, _encoded in dependencies
                )
            ).hexdigest(),
            "1db72aaf69d631cace1e56697dbf0876"
            "a912c59075095164d251a571d028f83e",
        )

    def test_direct_literal_references_are_exact(self) -> None:
        expected = {
            0x004824F0: "cbcccc0c",
            0x004824F4: "686a6c747a4c00",
            0x004824FC:
                "7072696e74665f733a2062616420257320617267756d656e7400",
            0x00482674: "a0860100",
            0x00482678: "0000f03f",
            0x0048267C: "84d79741",
            0x004826B4: "7072696e74665f733a20256e20646973616c6c6f77656400",
            0x004826CC: "7072696e74663a2062616420256e20617267756d656e7400",
            0x004826E4: "00",
            0x004826E8: "6e616e00",
            0x004826EC: "4e414e00",
            0x004826F0: "696e6600",
            0x004826F4: "494e4600",
            0x004826F8: "3000",
        }
        for address, expected_hex in expected.items():
            with self.subTest(address=hex(address)):
                self.assertEqual(
                    self.span(
                        address,
                        address + len(bytes.fromhex(expected_hex)),
                    ).hex(),
                    expected_hex,
                )

    def test_no_narrow_topology_and_stored_words_are_unaligned(self) -> None:
        narrow_entry = []
        narrow_interior = []
        for offset in range(0, len(self.application) - 1, 2):
            address = APPLICATION_BASE + offset
            halfword = struct.unpack_from(
                "<H",
                self.application,
                offset,
            )[0]
            candidates = []
            if halfword & 0xF800 == 0xE000:
                candidates.append(
                    address
                    + 4
                    + _sign_extend((halfword & 0x7FF) << 1, 12)
                )
            condition = (halfword >> 8) & 0xF
            if halfword & 0xF000 == 0xD000 and condition < 0xE:
                candidates.append(
                    address
                    + 4
                    + _sign_extend((halfword & 0xFF) << 1, 9)
                )
            if halfword & 0xF500 == 0xB100:
                immediate = (
                    ((halfword >> 9) & 1) << 6
                    | ((halfword >> 3) & 0x1F) << 1
                )
                candidates.append(address + 4 + immediate)
            if STOCK_START in candidates:
                narrow_entry.append((address, halfword))
            for target in candidates:
                if (
                    STOCK_START < target < STOCK_END
                    and not STOCK_START <= address < STOCK_END
                ):
                    narrow_interior.append(
                        (address, target, halfword)
                    )
        self.assertEqual(narrow_entry, [])
        self.assertEqual(narrow_interior, [])

        stored = []
        for target in range(STOCK_START, STOCK_END, 2):
            needle = struct.pack("<I", target | 1)
            position = self.application.find(needle)
            while position >= 0:
                stored.append((APPLICATION_BASE + position, target))
                position = self.application.find(needle, position + 1)
        self.assertEqual(len(stored), 39)
        self.assertTrue(
            all(storage_address & 3 for storage_address, _target in stored)
        )
        self.assertEqual(
            hashlib.sha256(
                b"".join(
                    struct.pack("<II", storage_address, target)
                    for storage_address, target in stored
                )
            ).hexdigest(),
            "ec943777cea15067fb4791e6b0f00d8d"
            "c18bff43a01d435b2be5e782a0b2caa1",
        )

    def test_semantic_feature_markers_remain_in_retained_blob(self) -> None:
        body_and_literals = self.span(STOCK_START, 0x004826FC)
        for marker in (
            b"hjltzL\x00",
            b"printf_s: bad %s argument\x00",
            b"printf_s: %n disallowed\x00",
            b"printf: bad %n argument\x00",
            b"nan\x00",
            b"NAN\x00",
            b"inf\x00",
            b"INF\x00",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, body_and_literals)


if __name__ == "__main__":
    unittest.main()
