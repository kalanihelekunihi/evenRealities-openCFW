from __future__ import annotations

import ctypes
import hashlib
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OFFICIAL = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_bootloader.bin"
)
IMAGE_BASE = 0x0041_0000
OFFICIAL_SIZE = 148_599
OFFICIAL_SHA256 = (
    "f89a4c4657537cec6bfc572bdb831886"
    "6309b90a5d180c4307680d39824167b5"
)

STOCK_FUNCTIONS = {
    "open_cfw_easylogger_strcpy": (
        0x0041_B158,
        0x0041_B1FA,
        "9708f61ea38bbac62f5542fdd2701a950"
        "ba1bde9fd480c5baf7cb0be6a8461b5",
    ),
    "open_cfw_easylogger_get_fmt_enabled": (
        0x0041_7AD4,
        0x0041_7B3E,
        "eb04732c56e958be0b715c98f23dafc9"
        "aa9c29a6321a1b58297529e39eb3eb5a",
    ),
    "open_cfw_easylogger_get_fmt_used_and_enabled_u32": (
        0x0041_7B48,
        0x0041_7B62,
        "95bba933ae9e65022ef0ff0daa763246"
        "78aa539c2ba79435b80181ce34a23db7",
    ),
    "open_cfw_easylogger_get_fmt_used_and_enabled_ptr": (
        0x0041_7B62,
        0x0041_7B7C,
        "3af2631ad7a44be557a9454da2df6886"
        "2b6458bf2359f58d41c3d6d2ff86c8a2",
    ),
}
STOCK_ORDER = (
    "open_cfw_easylogger_get_fmt_enabled",
    "open_cfw_easylogger_get_fmt_used_and_enabled_u32",
    "open_cfw_easylogger_get_fmt_used_and_enabled_ptr",
    "open_cfw_easylogger_strcpy",
)
STOCK_CLOSURE_SIZE = 320
STOCK_CLOSURE_SHA256 = (
    "472bbec3de86da7dc9b322d6c1a52a8d"
    "b714397786b24a556c0171d7a650c250"
)
STOCK_NEIGHBORS = {
    "open_cfw_easylogger_strcpy": ("70470000", "0000647374007372"),
    "open_cfw_easylogger_get_fmt_enabled": (
        "1b5b0000",
        "0000200000005b00",
    ),
    "open_cfw_easylogger_get_fmt_used_and_enabled_u32": (
        "5b000000",
        "80b5002a06d0c0b2",
    ),
    "open_cfw_easylogger_get_fmt_used_and_enabled_ptr": (
        "c0b202bd",
        "80b5134981f8f200",
    ),
}
STOCK_CALLERS = {
    0x0041_B158: [
        (0x0041_77BE, "03f0cbfc"),
        (0x0041_77D6, "03f0bffc"),
        (0x0041_7800, "03f0aafc"),
        (0x0041_7820, "03f09afc"),
        (0x0041_7846, "03f087fc"),
        (0x0041_7854, "03f080fc"),
        (0x0041_7874, "03f070fc"),
        (0x0041_7894, "03f060fc"),
        (0x0041_78B0, "03f052fc"),
        (0x0041_78D0, "03f042fc"),
        (0x0041_78EC, "03f034fc"),
        (0x0041_790C, "03f024fc"),
        (0x0041_791A, "03f01dfc"),
        (0x0041_7960, "03f0fafb"),
        (0x0041_797E, "03f0ebfb"),
        (0x0041_799C, "03f0dcfb"),
        (0x0041_79BC, "03f0ccfb"),
        (0x0041_79E6, "03f0b7fb"),
        (0x0041_7A04, "03f0a8fb"),
        (0x0041_7A22, "03f099fb"),
        (0x0041_7A30, "03f092fb"),
        (0x0041_7AA6, "03f057fb"),
        (0x0041_7AB4, "03f050fb"),
    ],
    0x0041_7AD4: [
        (0x0041_77E2, "00f077f9"),
        (0x0041_780C, "00f062f9"),
        (0x0041_7860, "00f038f9"),
        (0x0041_7880, "00f028f9"),
        (0x0041_78A0, "00f018f9"),
        (0x0041_78BC, "00f00af9"),
        (0x0041_78DC, "00f0faf8"),
        (0x0041_78F8, "00f0ecf8"),
        (0x0041_7B50, "fff7c0ff"),
        (0x0041_7B6A, "fff7b3ff"),
    ],
    0x0041_7B48: [
        (0x0041_794C, "00f0fcf8"),
        (0x0041_79AC, "00f0ccf8"),
        (0x0041_79CA, "00f0bdf8"),
    ],
    0x0041_7B62: [
        (0x0041_792C, "00f019f9"),
        (0x0041_793C, "00f011f9"),
        (0x0041_796E, "00f0f8f8"),
        (0x0041_798C, "00f0e9f8"),
        (0x0041_79F4, "00f0b5f8"),
        (0x0041_7A12, "00f0a6f8"),
    ],
}
STOCK_CALLER_DIGESTS = {
    0x0041_B158: (
        "35c930490c7eae4ba9b6aa797fdfd34c"
        "0594ecbc282ccdee4ebb5f7526ff4804"
    ),
    0x0041_7AD4: (
        "0ace983e92fb8734b4dc3ea0aaafde11"
        "87704f013b42c8234cb878332c8c1d66"
    ),
    0x0041_7B48: (
        "77a0d6e0c29d5b8f913ca98fbe13a674"
        "3e3d59d566fdf2f5e1341d2c32f38ca9"
    ),
    0x0041_7B62: (
        "fa60b266620a201d141332a4a84ff23d"
        "a9e1b54d38f3c60bc85ddca9d0fcc2b3"
    ),
}
STOCK_OUTGOING = [
    (0x0041_7B0A, "fff7e0fd", 0x0041_76CE),
    (0x0041_7B0E, "03f0bcf8", 0x0041_AC8A),
    (0x0041_7B50, "fff7c0ff", 0x0041_7AD4),
    (0x0041_7B6A, "fff7b3ff", 0x0041_7AD4),
    (0x0041_B18A, "fcf7a0fa", 0x0041_76CE),
    (0x0041_B18E, "fff77cfd", 0x0041_AC8A),
    (0x0041_B1C4, "fcf783fa", 0x0041_76CE),
    (0x0041_B1C8, "fff75ffd", 0x0041_AC8A),
]

LOGGER_ADDRESS = 0x2002_6700
ASSERT_HOOK_ADDRESS = 0x2002_70E4
ASSERT_OUTPUT_ADDRESS = 0x0041_76CE
ASSERT_WAIT_ADDRESS = 0x0041_AC8A
LEVEL_COUNT = 6
LINE_BUFFER_SIZE = 1024
SOURCE = (
    ROOT
    / "components"
    / "shared"
    / "easylogger"
    / "runtime_easylogger_helpers.c"
)
HEADER = SOURCE.with_suffix(".h")
SOURCE_SIZE = 4_975
SOURCE_SHA256 = (
    "8f2850f789fba3b08bdc3e1fa8f3a464"
    "6aaef7e4b16862f3be53478071aa22b5"
)
HEADER_SIZE = 6_505
HEADER_SHA256 = (
    "f3a7e9bce0f136a2ff4a76929c317aef"
    "7bbc7c29dfc60d58311d94e58f6e2393"
)
TARGET_FLAGS = [
    "--target=arm-none-eabi",
    "-mcpu=cortex-m55",
    "-mthumb",
    "-Oz",
    "-ffreestanding",
    "-fno-jump-tables",
    "-fomit-frame-pointer",
    "-fno-builtin",
    "-mno-unaligned-access",
    "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables",
    "-fropi",
    "-ffunction-sections",
    "-fdata-sections",
    "-Wall",
    "-Wextra",
    "-Werror",
]
TARGET_PROFILE_DEFINE = (
    "OPEN_CFW_EASYLOGGER_HELPERS_PROFILE="
    "OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_BOOTLOADER"
)
TARGET_LEAVES = {
    "open_cfw_easylogger_get_fmt_enabled": {
        "define": "OPEN_CFW_EASYLOGGER_HELPERS_LEAF_GET_FMT_ENABLED",
        "size": 38,
        "sha256": (
            "563bc931557c5aae324ecfb98dbc4aa23"
            "42c43c90163d462bea5e215c0de6390"
        ),
        "hex": (
            "b0b506280c46054624bf40f2e720fff7fefffff7feff"
            "00eb8500d0f8d80020425fea0f90b0bd"
        ),
        "relocations": [
            (14, 10, "open_cfw_easylogger_helpers_assert_failed"),
            (18, 10, "open_cfw_easylogger_helpers_get_logger"),
        ],
        "undefined": {
            "open_cfw_easylogger_helpers_assert_failed",
            "open_cfw_easylogger_helpers_get_logger",
        },
    },
    "open_cfw_easylogger_get_fmt_used_and_enabled_u32": {
        "define": (
            "OPEN_CFW_EASYLOGGER_HELPERS_"
            "LEAF_GET_FMT_USED_AND_ENABLED_U32"
        ),
        "size": 20,
        "sha256": (
            "3e6f46ecf152d9192ec638cd0eafa92f"
            "9c8adcfe7b36e8581add1a865234629a"
        ),
        "hex": "32b180b5fff7feff00285fea0f9080bd00207047",
        "relocations": [
            (4, 10, "open_cfw_easylogger_get_fmt_enabled"),
        ],
        "undefined": {"open_cfw_easylogger_get_fmt_enabled"},
    },
    "open_cfw_easylogger_get_fmt_used_and_enabled_ptr": {
        "define": (
            "OPEN_CFW_EASYLOGGER_HELPERS_"
            "LEAF_GET_FMT_USED_AND_ENABLED_PTR"
        ),
        "size": 20,
        "sha256": (
            "3e6f46ecf152d9192ec638cd0eafa92f"
            "9c8adcfe7b36e8581add1a865234629a"
        ),
        "hex": "32b180b5fff7feff00285fea0f9080bd00207047",
        "relocations": [
            (4, 10, "open_cfw_easylogger_get_fmt_enabled"),
        ],
        "undefined": {"open_cfw_easylogger_get_fmt_enabled"},
    },
    "open_cfw_easylogger_strcpy": {
        "define": "OPEN_CFW_EASYLOGGER_HELPERS_LEAF_STRCPY",
        "size": 52,
        "sha256": (
            "1fac8de3a83876460e17014da0f84538"
            "4b253a88d5b79e25f6e5e838e6f46013"
        ),
        "hex": (
            "70b514460d46064611b92c20fff7feff14b92d20fff7feff"
            "00210020227842b13318b1eb932f04d105f8012b01300134f4e770bd"
        ),
        "relocations": [
            (12, 10, "open_cfw_easylogger_helpers_assert_failed"),
            (20, 10, "open_cfw_easylogger_helpers_assert_failed"),
        ],
        "undefined": {"open_cfw_easylogger_helpers_assert_failed"},
    },
}
TARGET_ORDER = (
    "open_cfw_easylogger_get_fmt_enabled",
    "open_cfw_easylogger_get_fmt_used_and_enabled_u32",
    "open_cfw_easylogger_get_fmt_used_and_enabled_ptr",
    "open_cfw_easylogger_strcpy",
)
TARGET_CLOSURE_SIZE = 130
TARGET_CLOSURE_SHA256 = (
    "a806e83b595bfa8d37cf27c095b94d6d"
    "dfcf359c2c53dad9ab29f3dd2e7c083b"
)

sys.path.insert(0, str(ROOT / "tools"))
import apollo_overlay  # noqa: E402


class EasyLoggerTagLevel32(ctypes.Structure):
    _fields_ = [
        ("level", ctypes.c_uint8),
        ("tag", ctypes.c_char * 31),
        ("tag_use_flag", ctypes.c_uint8),
    ]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def narrow_branch_targets(address: int, halfword: int) -> tuple[int, ...]:
    if halfword & 0xF800 == 0xE000:
        immediate = halfword & 0x07FF
        if immediate & 0x0400:
            immediate -= 0x0800
        return (address + 4 + immediate * 2,)
    if (
        halfword & 0xF000 == 0xD000
        and ((halfword >> 8) & 0x0F) < 0x0E
    ):
        immediate = halfword & 0x00FF
        if immediate & 0x0080:
            immediate -= 0x0100
        return (address + 4 + immediate * 2,)
    if halfword & 0xF500 == 0xB100:
        immediate = (
            (((halfword >> 9) & 1) << 5)
            | ((halfword >> 3) & 0x1F)
        )
        return (address + 4 + immediate * 2,)
    return ()


class RuntimeEasyLoggerHelpersBootTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.image = OFFICIAL.read_bytes()
        cls.clang = shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("clang is unavailable")
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="test-runtime-easylogger-helpers-boot-",
        )
        temporary = Path(cls.temporary.name)
        cls.target_reports = {}
        for symbol, expected in TARGET_LEAVES.items():
            target_object = temporary / f"{symbol}.o"
            compile_result = subprocess.run(
                [
                    cls.clang,
                    *TARGET_FLAGS,
                    f"-D{TARGET_PROFILE_DEFINE}",
                    "-DOPEN_CFW_EASYLOGGER_HELPERS_BUILD_LEAF",
                    f"-D{expected['define']}",
                    "-c",
                    str(SOURCE),
                    "-o",
                    str(target_object),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            cls.target_reports[symbol] = cls.parse_target_object(
                target_object,
                symbol,
                compile_result,
            )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def span(cls, start: int, end: int) -> bytes:
        return cls.image[start - IMAGE_BASE:end - IMAGE_BASE]

    @staticmethod
    def parse_target_object(
        target_object: Path,
        symbol: str,
        compile_result: subprocess.CompletedProcess[str],
    ) -> dict:
        data, sections = apollo_overlay.parse_elf32(target_object)
        text = apollo_overlay.section_named(sections, f".text.{symbol}")
        body = data[
            int(text["offset"]):
            int(text["offset"]) + int(text["size"])
        ]

        symbol_table = apollo_overlay.section_named(sections, ".symtab")
        string_table = sections[int(symbol_table["link"])]
        strings = data[
            int(string_table["offset"]):
            int(string_table["offset"]) + int(string_table["size"])
        ]
        parsed_symbols = []
        for index in range(int(symbol_table["size"]) // 16):
            fields = struct.unpack_from(
                "<IIIBBH",
                data,
                int(symbol_table["offset"]) + index * 16,
            )
            name = apollo_overlay.elf_string(
                strings,
                fields[0],
                "symbol",
            )
            parsed_symbols.append((name, fields))
        symbols = {
            name: fields
            for name, fields in parsed_symbols
            if name
        }

        relocations = []
        for section in sections:
            if (
                int(section["type"]) == 9
                and int(section["info"]) == int(text["index"])
            ):
                for index in range(int(section["size"]) // 8):
                    offset, information = struct.unpack_from(
                        "<II",
                        data,
                        int(section["offset"]) + index * 8,
                    )
                    relocations.append(
                        (
                            offset,
                            information & 0xFF,
                            parsed_symbols[information >> 8][0],
                        )
                    )

        writable_allocated = [
            (
                str(section["name"]),
                int(section["size"]),
                int(section["flags"]),
            )
            for section in sections
            if (
                int(section["size"]) > 0
                and int(section["flags"]) & 0x2
                and int(section["flags"]) & 0x1
            )
        ]
        return {
            "body": body,
            "text": text,
            "symbols": symbols,
            "parsed_symbols": parsed_symbols,
            "relocations": relocations,
            "writable_allocated": writable_allocated,
            "compile": compile_result,
        }

    def test_official_image_and_stock_body_pins_are_exact(self) -> None:
        self.assertEqual(len(self.image), OFFICIAL_SIZE)
        self.assertEqual(sha256(self.image), OFFICIAL_SHA256)

        closure = bytearray()
        for name in STOCK_ORDER:
            start, end, expected_hash = STOCK_FUNCTIONS[name]
            with self.subTest(function=name):
                body = self.span(start, end)
                self.assertEqual(len(body), end - start)
                self.assertEqual(sha256(body), expected_hash)
                closure.extend(body)

                before, after = STOCK_NEIGHBORS[name]
                self.assertEqual(self.span(start - 4, start).hex(), before)
                self.assertEqual(self.span(end, end + 8).hex(), after)

        self.assertEqual(len(closure), STOCK_CLOSURE_SIZE)
        self.assertEqual(sha256(bytes(closure)), STOCK_CLOSURE_SHA256)

    def test_all_wide_callers_and_packed_digests_are_exact(self) -> None:
        observed = {entry: [] for entry in STOCK_CALLERS}
        jumps = []
        for offset in range(0, len(self.image) - 3, 2):
            address = IMAGE_BASE + offset
            encoded = self.image[offset:offset + 4]
            for link in (True, False):
                try:
                    target = apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except apollo_overlay.BuildError:
                    continue
                if target not in observed:
                    continue
                if link:
                    observed[target].append((address, encoded.hex()))
                else:
                    jumps.append((address, target, encoded.hex()))

        self.assertEqual(observed, STOCK_CALLERS)
        self.assertEqual(jumps, [])
        self.assertEqual(
            {entry: len(callers) for entry, callers in observed.items()},
            {
                0x0041_B158: 23,
                0x0041_7AD4: 10,
                0x0041_7B48: 3,
                0x0041_7B62: 6,
            },
        )
        for entry, callers in observed.items():
            with self.subTest(entry=f"0x{entry:08X}"):
                packed = b"".join(
                    struct.pack("<I", address)
                    for address, _encoded in callers
                )
                self.assertEqual(
                    sha256(packed),
                    STOCK_CALLER_DIGESTS[entry],
                )

    def test_outgoing_calls_and_source_predicate_closure_are_exact(
        self,
    ) -> None:
        outgoing = []
        for name in STOCK_ORDER:
            start, end, _expected_hash = STOCK_FUNCTIONS[name]
            for address in range(start, end - 3, 2):
                encoded = self.span(address, address + 4)
                try:
                    target = apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=True,
                    )
                except apollo_overlay.BuildError:
                    continue
                if target != address:
                    outgoing.append((address, encoded.hex(), target))

        self.assertEqual(outgoing, STOCK_OUTGOING)
        self.assertIn(
            (0x0041_7B50, "fff7c0ff", 0x0041_7AD4),
            outgoing,
        )
        self.assertIn(
            (0x0041_7B6A, "fff7b3ff", 0x0041_7AD4),
            outgoing,
        )
        self.assertEqual(
            {
                target
                for address, _encoded, target in outgoing
                if address not in (0x0041_7B50, 0x0041_7B6A)
            },
            {ASSERT_OUTPUT_ADDRESS, ASSERT_WAIT_ADDRESS},
        )

    def test_no_external_interior_narrow_or_stored_reference_exists(
        self,
    ) -> None:
        spans = [
            (start, end)
            for start, end, _expected_hash in STOCK_FUNCTIONS.values()
        ]
        wide_interior = []
        narrow = []

        for offset in range(0, len(self.image) - 3, 2):
            address = IMAGE_BASE + offset
            encoded = self.image[offset:offset + 4]
            for link in (True, False):
                try:
                    target = apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except apollo_overlay.BuildError:
                    continue
                for start, end in spans:
                    if (
                        start < target < end
                        and not start <= address < end
                    ):
                        wide_interior.append(
                            (address, target, link, encoded.hex())
                        )

        for offset in range(0, len(self.image) - 1, 2):
            address = IMAGE_BASE + offset
            halfword = struct.unpack_from("<H", self.image, offset)[0]
            for target in narrow_branch_targets(address, halfword):
                for start, end in spans:
                    if (
                        start <= target < end
                        and not start <= address < end
                    ):
                        narrow.append((address, target, halfword))

        stored = []
        for offset in range(0, len(self.image) - 3):
            value = struct.unpack_from("<I", self.image, offset)[0]
            target = value & ~1
            if any(start <= target < end for start, end in spans):
                stored.append((IMAGE_BASE + offset, value))

        self.assertEqual(wide_interior, [])
        self.assertEqual(narrow, [])
        self.assertEqual(stored, [])

    def test_recovered_boot_profile_and_tag_level_layout_are_exact(
        self,
    ) -> None:
        self.assertEqual(ctypes.sizeof(ctypes.c_uint32), 4)
        self.assertEqual(LEVEL_COUNT, 6)
        self.assertEqual(LINE_BUFFER_SIZE, 1024)
        self.assertEqual(ctypes.sizeof(EasyLoggerTagLevel32), 0x21)
        self.assertEqual(EasyLoggerTagLevel32.level.offset, 0x00)
        self.assertEqual(EasyLoggerTagLevel32.tag.offset, 0x01)
        self.assertEqual(EasyLoggerTagLevel32.tag_use_flag.offset, 0x20)

        packed_logger = struct.pack("<I", LOGGER_ADDRESS)
        packed_hook = struct.pack("<I", ASSERT_HOOK_ADDRESS)
        self.assertEqual(
            [
                IMAGE_BASE + offset
                for offset in range(len(self.image) - 3)
                if self.image[offset:offset + 4] == packed_logger
            ],
            [0x0041_7BCC],
        )
        self.assertEqual(
            [
                IMAGE_BASE + offset
                for offset in range(len(self.image) - 3)
                if self.image[offset:offset + 4] == packed_hook
            ],
            [0x0041_7BE8, 0x0041_B204],
        )

    def test_boot_target_leaf_bytes_symbols_and_relocations_are_exact(
        self,
    ) -> None:
        closure = bytearray()
        for symbol in TARGET_ORDER:
            expected = TARGET_LEAVES[symbol]
            report = self.target_reports[symbol]
            with self.subTest(symbol=symbol):
                self.assertEqual(report["compile"].stdout, "")
                self.assertEqual(report["compile"].stderr, "")
                self.assertEqual(len(report["body"]), expected["size"])
                self.assertEqual(
                    sha256(report["body"]),
                    expected["sha256"],
                )
                self.assertEqual(report["body"].hex(), expected["hex"])
                self.assertEqual(int(report["text"]["alignment"]), 2)
                self.assertEqual(int(report["text"]["flags"]) & 7, 6)
                self.assertEqual(
                    report["relocations"],
                    expected["relocations"],
                )

                fields = report["symbols"][symbol]
                self.assertEqual(fields[1] & ~1, 0)
                self.assertEqual(fields[1] & 1, 1)
                self.assertEqual(fields[2], expected["size"])
                self.assertEqual(fields[3] >> 4, 1)
                self.assertEqual(fields[3] & 0x0F, 2)
                self.assertEqual(fields[5], int(report["text"]["index"]))

                undefined = {
                    name
                    for name, undefined_fields in report[
                        "parsed_symbols"
                    ]
                    if name and undefined_fields[5] == 0
                }
                self.assertEqual(undefined, expected["undefined"])
                self.assertEqual(report["writable_allocated"], [])
                closure.extend(report["body"])

        self.assertEqual(len(closure), TARGET_CLOSURE_SIZE)
        self.assertEqual(sha256(bytes(closure)), TARGET_CLOSURE_SHA256)

    def test_boot_target_profile_and_assertion_metadata_are_explicit(
        self,
    ) -> None:
        header_bytes = HEADER.read_bytes()
        source_bytes = SOURCE.read_bytes()
        self.assertEqual(len(source_bytes), SOURCE_SIZE)
        self.assertEqual(sha256(source_bytes), SOURCE_SHA256)
        self.assertEqual(len(header_bytes), HEADER_SIZE)
        self.assertEqual(sha256(header_bytes), HEADER_SHA256)
        header = header_bytes.decode("utf-8")
        source = source_bytes.decode("utf-8")
        for literal in (
            "#define OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_BOOTLOADER 2",
            "#define OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_STATE_ADDRESS "
            "0x20026700U",
            "#define OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_ASSERT_HOOK_ADDRESS "
            "0x200270E4U",
            "#define OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_OUTPUT_ADDRESS "
            "0x004176CEU",
            "#define OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_ASSERT_WAIT_ADDRESS "
            "0x0041AC8AU",
            "OPEN_CFW_EASYLOGGER_HELPERS_LEVEL_COUNT = 6",
            "OPEN_CFW_EASYLOGGER_HELPERS_LINE_BUFFER_SIZE = 1024",
            "OPEN_CFW_EASYLOGGER_HELPERS_ASSERT_STRCPY_DST_LINE = 44",
            "OPEN_CFW_EASYLOGGER_HELPERS_ASSERT_STRCPY_SRC_LINE = 45",
            "OPEN_CFW_EASYLOGGER_HELPERS_ASSERT_GET_FMT_LINE = 743",
        ):
            self.assertIn(literal, header)
        for literal in (
            "open_cfw_easylogger_helpers_get_logger",
            "open_cfw_easylogger_helpers_assert_failed",
            "open_cfw_easylogger_get_fmt_enabled(level, format_set)",
        ):
            self.assertIn(literal, source + header)


if __name__ == "__main__":
    unittest.main()
