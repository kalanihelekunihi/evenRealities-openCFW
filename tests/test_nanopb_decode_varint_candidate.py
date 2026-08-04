from __future__ import annotations

import ctypes
import hashlib
import json
import os
from pathlib import Path
import random
import struct
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT / "components/shared/nanopb"
    / "runtime_nanopb_decode_varint_candidate.c"
)
HEADER = SOURCE.with_suffix(".h")
HOST_FIXTURE = (
    ROOT / "tests/fixtures/runtime_nanopb_decode_varint_candidate_host.c"
)
AUDIT = (
    ROOT / "docs/research/nanopb-decode-varint-source-candidate-audit.md"
)
SNAPSHOT = ROOT / "third_party/nanopb"
UPSTREAM = SNAPSHOT / "pb_decode.c"
CONFIG = SNAPSHOT / "g2-config/pb_g2_options.h"
PROVENANCE = SNAPSHOT / "PROVENANCE.json"
VERIFIER = SNAPSHOT / "verify_snapshot.py"
OFFICIAL = (
    ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
)
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
MAKEFILE = ROOT / "Makefile"

FUNCTION = "open_cfw_nanopb_decode_varint_candidate"
SEAM = "open_cfw_nanopb_readbyte_candidate"
FUNCTION_SECTION = ".text." + FUNCTION
SOURCE_PATH = SOURCE.relative_to(ROOT).as_posix()

PACKAGE_SIZE = 3_523_396
PACKAGE_SHA256 = (
    "36c5b0e499a68ac2493a497bdab9740f"
    "d3e7027730c26a9094eca47268a27863"
)
PACKAGE_PREAMBLE = 32
APPLICATION_BASE = 0x0043_8000
APPLICATION_SHA256 = (
    "19044a72bdfeb04c6b1b104d87da7b98"
    "e13cc18928528d84d999b6bcc0ba9701"
)
START = 0x0048_F5B8
END = 0x0048_F628
STOCK_HEX = (
    "2de9fc4106000f005ff000080024002569463000fff742ff002818d0b8f13f0f0"
    "4d39df8000010f0fe0f12d19df8000010f07f00c117424649f0acfd04430d43"
    "18f107089df800000006e1d40be000200ce0f068002801d0f06801e0dff8fc0a"
    "f060002002e0c7e900450120bde8f681"
)
STOCK_SHA256 = (
    "f93d678981f92603982c9afc6c6f9976"
    "ca14d1a7a7e0bfc949d3ff73f2791ff2"
)
PRECEDING = (
    0x0048_F5AE,
    START,
    10,
    "48218a658cffd7aeddfb623c9d0e7bd038ceb2a6898e9f8d08b10d5779f4f79b",
)
FOLLOWING = (
    END,
    0x0048_F66C,
    68,
    "5e6ebac0dfbc3643144fae98faa36f618e0394b3a95f0bbba491d3d08b256fb8",
)
CALLERS = [
    (0x0049_0156, "fff72ffa"),
    (0x0049_01EC, "fff7e4f9"),
    (0x0049_02A0, "fff78af9"),
]
CALLER_ADDRESS_SHA256 = (
    "0e5dfe5425e46893f310d2ba87a0dd66"
    "693d64ef5872b5491bd08ac6aa1f4ba6"
)
CALLER_RECORD_SHA256 = (
    "75504b52a651ac12823cb66035f7c706"
    "3172354f3a33b692ace3275fe2094b4f"
)
CALLER_SPANS = [
    (
        0x0049_0150,
        0x0049_0190,
        64,
        "80b24be422cf924f3ae1b79669312535dc0d5a56dd88be8a6b9e4ee5ff064048",
    ),
    (
        0x0049_01D6,
        0x0049_0352,
        380,
        "ccae20aa7dff8515a5a2b6ad4a05248a865dfaa8c912fd38c8c5f77c3a6a8e0a",
    ),
]

READBYTE_START = 0x0048_F454
READBYTE_END = 0x0048_F49C
READBYTE_SHA256 = (
    "15c8303c5c1dbf1b3f143142c6169026"
    "cb8bc56b37a6291dd0457b3664b67ae5"
)
SHIFT_START = 0x004D_914C
SHIFT_END = 0x004D_916E
SHIFT_SHA256 = (
    "b0eaecb9c4970d61ba662726c82e216b"
    "28ce4023456f6eb14df651c1def4dbb5"
)
ERROR_SLOT = 0x0049_0114
ERROR_ADDRESS = 0x0078_7C80
ERROR_SLOT_SHA256 = (
    "932b450ffea27c45062b59f6e45c640d"
    "894e6eae043fd124b694358e87e00ab4"
)
ERROR_BYTES = b"varint overflow\0"
ERROR_SHA256 = (
    "e9b62825b028cfc32f718b48de14fcbc"
    "783a9009279d2c88cf4394d54767141d"
)

LOCAL_PINS = {
    SOURCE: (
        2_254,
        "497b0389f2642485c03df7ffec7c17aea9d4534b1042295cbb4cf32ae7f83079",
    ),
    HEADER: (
        2_844,
        "4753669797e8c7fb33835c00773d8c5faa23531291f4c4e76b876a1de54e4051",
    ),
    HOST_FIXTURE: (
        4_329,
        "08f503f9989b67889848c92c90b9bac12c806f9d1ebb7fb87ae4c5f0dafacb37",
    ),
    AUDIT: (
        11_072,
        "a3e28acc2144b75ef5d8dc257ec818b41de129f769c6dfa3ba374ea9c1821810",
    ),
    UPSTREAM: (
        53_845,
        "e980f2a41d9abe37b7e6fb4c9ba1ebfd68507a6fd2653f8d755e1947a9c84b1a",
    ),
    CONFIG: (
        1_551,
        "ae758999d239e49e2d5c5bf6de3f4aef3aab5cd3c29d8de65c4db301c62899db",
    ),
}

TARGET_FLAGS = (
    "--target=thumbv7em-none-eabi",
    "-mthumb",
    "-O2",
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
)

PROFILE_PINS = {
    "apple-clang": {
        "compiler": "/usr/bin/clang",
        "version": "Apple clang version 21.0.0 (clang-2100.3.27.1)",
        "object": (
            1_284,
            "c5c95e69e834ab88c21b060813181598e9ec3696e7f3c76b814357f70f772a97",
        ),
        "text_size": 128,
        "text_sha256": (
            "b3f040de87b4fd22ba1e66c81121194d"
            "daa03f56253b5d9e0a322a9671247e94"
        ),
        "text_hex": (
            "2de9f04381b08846044600260df103090027002520464946fff7feff60b3f0b2"
            "9df803103f2828bf02291dd201f07f02c0f1200622fa06f6b0f1200358bf02fa"
            "03f602fa00f249b258bf002235431743002900f10706ddd4c8f80070c8f80450"
            "012001b0bde8f083e06828b94ff6f470cff6f8707844e060002001b0bde8f083"
        ),
        "text_relocations": [
            (24, 10, SEAM),
            (108, 49, ".L.str"),
            (112, 50, ".L.str"),
        ],
    },
    "linux-clang": {
        "compiler": "/home/linuxbrew/.linuxbrew/bin/clang",
        "version": "Homebrew clang version 22.1.8",
        "object": (
            1_260,
            "cfb795065b13944582e127b4cd6154f632d9dada423854db2f19697de4c876b0",
        ),
        "text_size": 124,
        "text_sha256": (
            "e820aa1b54f20ec1454462d356562177"
            "f8d03d98f21dff4bba77fa39fe282fa5"
        ),
        "text_hex": (
            "2de9f04381b08846044600260df103090027002520464946fff7feff50b3f0b2"
            "9df803103f2828bf02291bd201f07f02c0f1200622fa06f6b0f1200358bf02fa"
            "03f602fa00f249b258bf002235431743002900f10706ddd4c8e90075012001b0"
            "bde8f083e06828b94ff6f470cff6f8707844e060002001b0bde8f083"
        ),
        "text_relocations": [
            (24, 10, SEAM),
            (104, 49, ".L.str"),
            (108, 50, ".L.str"),
        ],
    },
}


def sha256(value: bytes | Path) -> str:
    if isinstance(value, Path):
        value = value.read_bytes()
    return hashlib.sha256(value).hexdigest()


def thumb_wide_branch_target(
    address: int,
    first: int,
    second: int,
    *,
    link: bool,
) -> int | None:
    expected_second = 0xD000 if link else 0x9000
    if first & 0xF800 != 0xF000 or second & 0xD000 != expected_second:
        return None
    sign = (first >> 10) & 1
    imm10 = first & 0x03FF
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    imm11 = second & 0x07FF
    i1 = 1 ^ (j1 ^ sign)
    i2 = 1 ^ (j2 ^ sign)
    immediate = (
        (sign << 24) | (i1 << 23) | (i2 << 22) |
        (imm10 << 12) | (imm11 << 1)
    )
    if sign:
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFF_FFFF


def wide_conditional_target(
    address: int,
    first: int,
    second: int,
) -> int | None:
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0x8000:
        return None
    if ((first >> 6) & 0x0F) >= 0x0E:
        return None
    sign = (first >> 10) & 1
    immediate = (
        sign << 20 |
        ((second >> 11) & 1) << 19 |
        ((second >> 13) & 1) << 18 |
        (first & 0x003F) << 12 |
        (second & 0x07FF) << 1
    )
    if sign:
        immediate -= 1 << 21
    return address + 4 + immediate


def narrow_targets(address: int, halfword: int) -> tuple[int, ...]:
    if halfword & 0xF800 == 0xE000:
        immediate = halfword & 0x07FF
        if immediate & 0x0400:
            immediate -= 0x0800
        return (address + 4 + immediate * 2,)
    if halfword & 0xF000 == 0xD000 and ((halfword >> 8) & 0x0F) < 0x0E:
        immediate = halfword & 0x00FF
        if immediate & 0x0080:
            immediate -= 0x0100
        return (address + 4 + immediate * 2,)
    if halfword & 0xF500 == 0xB100:
        immediate = (
            (((halfword >> 9) & 1) << 5) |
            ((halfword >> 3) & 0x1F)
        )
        return (address + 4 + immediate * 2,)
    return ()


class HostResult(ctypes.Structure):
    _fields_ = [
        ("value", ctypes.c_uint64),
        ("bytes_left", ctypes.c_uint64),
        ("consumed", ctypes.c_uint64),
        ("status", ctypes.c_uint32),
        ("calls", ctypes.c_uint32),
        ("error", ctypes.c_uint32),
    ]

    def tuple(self) -> tuple[int, ...]:
        return (
            self.status,
            self.value,
            self.bytes_left,
            self.consumed,
            self.calls,
            self.error,
        )


class NanopbDecodeVarintCandidateTests(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        version = subprocess.run(
            [cls.clang, "--version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()[0]
        if version.startswith("Apple clang version 21.0.0"):
            cls.profile = "apple-clang"
        elif version.startswith("Homebrew clang version 22.1.8"):
            cls.profile = "linux-clang"
        else:
            raise AssertionError(f"unreviewed compiler: {version!r}")
        cls.pins = PROFILE_PINS[cls.profile]
        if cls.clang != cls.pins["compiler"] or version != cls.pins["version"]:
            raise AssertionError((cls.clang, version, cls.pins))

        parent = ROOT / "build"
        parent.mkdir(exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="open-cfw-nanopb-varint-candidate-",
            dir=parent,
        )
        temporary = Path(cls.temporary.name)
        cls.objects = [temporary / "candidate-a.o", temporary / "candidate-b.o"]
        for output in cls.objects:
            subprocess.run(
                [
                    cls.clang,
                    *TARGET_FLAGS,
                    "-c",
                    SOURCE_PATH,
                    "-o",
                    str(output),
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

        library = temporary / (
            "nanopb-varint-candidate.dylib"
            if sys.platform == "darwin"
            else "nanopb-varint-candidate.so"
        )
        command = [
            cls.clang,
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-I",
            str(ROOT),
            "-I",
            str(SNAPSHOT),
            "-include",
            str(CONFIG),
            str(SOURCE),
            str(HOST_FIXTURE),
            str(UPSTREAM),
            str(SNAPSHOT / "pb_common.c"),
        ]
        if sys.platform == "darwin":
            command.extend(("-dynamiclib", "-o", str(library)))
        else:
            command.extend(("-shared", "-fPIC", "-o", str(library)))
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.library = ctypes.CDLL(str(library))
        cls.candidate = cls.library.open_cfw_test_nanopb_run_candidate
        cls.upstream = cls.library.open_cfw_test_nanopb_run_upstream
        for function in (cls.candidate, cls.upstream):
            function.argtypes = [
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.c_size_t,
                ctypes.c_size_t,
                ctypes.c_uint32,
                ctypes.c_uint32,
                ctypes.c_uint64,
                ctypes.POINTER(HostResult),
            ]
            function.restype = None

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.apollo_overlay = apollo_overlay
        cls.package = OFFICIAL.read_bytes()
        cls.application = cls.package[PACKAGE_PREAMBLE:]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def span(cls, start: int, end: int) -> bytes:
        return cls.application[
            start - APPLICATION_BASE:end - APPLICATION_BASE
        ]

    def run_host(
        self,
        function: ctypes._CFuncPtr,
        data: bytes,
        bytes_left: int,
        fail_call: int,
        preexisting_error: int,
        initial_value: int,
    ) -> tuple[int, ...]:
        storage = (ctypes.c_uint8 * max(1, len(data)))()
        if data:
            ctypes.memmove(storage, data, len(data))
        result = HostResult()
        function(
            storage,
            len(data),
            bytes_left,
            fail_call,
            preexisting_error,
            initial_value,
            ctypes.byref(result),
        )
        return result.tuple()

    def test_authenticated_baseline_and_local_candidate_are_pinned(self) -> None:
        for path, (size, digest) in LOCAL_PINS.items():
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertEqual(path.stat().st_size, size)
                self.assertEqual(sha256(path), digest)

        verification = subprocess.run(
            [sys.executable, str(VERIFIER)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            verification.stdout,
            "nanopb 0.4.9 compatibility snapshot verification passed\n",
        )
        provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        selection = provenance["selection"]
        self.assertEqual(selection["compatibility_choice"], "nanopb-0.4.9")
        self.assertFalse(selection["exact_g2_point_release_proven"])
        self.assertEqual(
            selection["g2_compatible_pristine_release_range"],
            ["0.4.7", "0.4.8", "0.4.9"],
        )

        source = SOURCE.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        audit = AUDIT.read_text(encoding="utf-8")
        for token in (
            "Altered, production-excluded source candidate",
            "98bf4db69897b53434f3d0ba72e0a3ab1a902824",
            "not proof of the vendor's historical point release",
            "[0x0048F5B8, 0x0048F628)",
            "bit_position >= 63U && (byte & 0xFEU) != 0U",
            'stream->errmsg = "varint overflow";',
        ):
            self.assertIn(token, source)
        for token in (
            "callback) == 0U",
            "state) == 4U",
            "bytes_left) == 8U",
            "errmsg) == 12U",
            "pb_istream_t size",
        ):
            self.assertIn(token, header)
        for token in (
            "compatibility choice",
            "does **not** prove the vendor's",
            "no alternate-entry ABI",
            "R_ARM_THM_CALL",
            "Production promotion",
            "offline snapshot verifier",
        ):
            self.assertIn(token, audit)

    def test_candidate_is_absent_from_every_production_registration(self) -> None:
        for path in (OVERLAY, MANIFEST, MAKEFILE):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn(SOURCE_PATH, text, path)
            self.assertNotIn(FUNCTION, text, path)
        self.assertTrue(SOURCE.name.endswith("_candidate.c"))
        self.assertNotIn("runtime_nanopb_decode_varint_candidate", UPSTREAM.read_text())

    def test_stock_boundary_body_and_adjacent_entries_are_exact(self) -> None:
        self.assertEqual(len(self.package), PACKAGE_SIZE)
        self.assertEqual(sha256(self.package), PACKAGE_SHA256)
        self.assertEqual(sha256(self.application), APPLICATION_SHA256)
        stock = self.span(START, END)
        self.assertEqual(len(stock), 112)
        self.assertEqual(stock.hex(), STOCK_HEX)
        self.assertEqual(sha256(stock), STOCK_SHA256)
        for start, end, size, digest in (PRECEDING, FOLLOWING):
            body = self.span(start, end)
            self.assertEqual(len(body), size)
            self.assertEqual(sha256(body), digest)

    def test_whole_image_caller_and_ingress_closure_is_exact(self) -> None:
        # Keep each independent instruction decoder live even when the stock
        # image contains no external ingress of that particular form.
        first, second = struct.unpack(
            "<HH",
            self.apollo_overlay.encode_thumb_b_w(0x1000, 0x1010),
        )
        self.assertEqual(
            thumb_wide_branch_target(
                0x1000, first, second, link=False
            ),
            0x1010,
        )
        self.assertEqual(
            wide_conditional_target(0x1000, 0xF000, 0x8000),
            0x1004,
        )
        self.assertEqual(narrow_targets(0x1000, 0xE000), (0x1004,))
        self.assertEqual(narrow_targets(0x1000, 0xD000), (0x1004,))
        self.assertEqual(narrow_targets(0x1000, 0xB100), (0x1004,))

        direct_bl = []
        direct_bw = []
        external_interior = []
        external_conditional_or_narrow = []
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
            first, second = struct.unpack_from("<HH", self.application, offset)
            encoding = self.application[offset:offset + 4]
            for link in (True, False):
                target = thumb_wide_branch_target(
                    address, first, second, link=link
                )
                if target is None or not START <= target < END:
                    continue
                if target == START:
                    (direct_bl if link else direct_bw).append(
                        (address, encoding.hex())
                    )
                elif not START <= address < END:
                    external_interior.append(
                        (address, target, link, encoding.hex())
                    )

            conditional = wide_conditional_target(address, first, second)
            targets = (
                *((conditional,) if conditional is not None else ()),
                *narrow_targets(address, first),
            )
            for target in targets:
                if (
                    START <= target < END and
                    not START <= address < END
                ):
                    external_conditional_or_narrow.append(
                        (address, target, encoding.hex())
                    )

        self.assertEqual(direct_bl, CALLERS)
        self.assertEqual(direct_bw, [])
        self.assertEqual(external_interior, [])
        self.assertEqual(external_conditional_or_narrow, [])
        self.assertEqual(
            sha256(b"".join(struct.pack("<I", address) for address, _ in CALLERS)),
            CALLER_ADDRESS_SHA256,
        )
        self.assertEqual(
            sha256(b"".join(
                struct.pack("<I", address) + bytes.fromhex(encoding)
                for address, encoding in CALLERS
            )),
            CALLER_RECORD_SHA256,
        )
        for start, end, size, digest in CALLER_SPANS:
            body = self.span(start, end)
            self.assertEqual(len(body), size)
            self.assertEqual(sha256(body), digest)

        stored = []
        for canonical in range(START, END):
            for value in {canonical, canonical | 1}:
                needle = struct.pack("<I", value)
                position = 0
                while True:
                    position = self.application.find(needle, position)
                    if position < 0:
                        break
                    stored.append(
                        (
                            APPLICATION_BASE + position,
                            value,
                            canonical,
                            position % 4,
                        )
                    )
                    position += 1
        self.assertEqual(stored, [])

    def test_stock_abi_configuration_and_outgoing_closure_are_exact(self) -> None:
        stock = self.span(START, END)
        outgoing = []
        for offset in range(0, len(stock) - 3, 2):
            target = thumb_wide_branch_target(
                START + offset,
                *struct.unpack_from("<HH", stock, offset),
                link=True,
            )
            if target is not None:
                outgoing.append((START + offset, target))
        self.assertEqual(
            outgoing,
            [(0x0048_F5CC, READBYTE_START), (0x0048_F5F0, SHIFT_START)],
        )
        self.assertEqual(
            sha256(self.span(READBYTE_START, READBYTE_END)),
            READBYTE_SHA256,
        )
        self.assertEqual(
            sha256(self.span(SHIFT_START, SHIFT_END)),
            SHIFT_SHA256,
        )

        literal_instruction = 0x0048_F614
        first, second = struct.unpack(
            "<HH", self.span(literal_instruction, literal_instruction + 4)
        )
        self.assertEqual((first, second & 0xF000), (0xF8DF, 0x0000))
        literal_address = (
            ((literal_instruction + 4) & ~3) + (second & 0x0FFF)
        )
        self.assertEqual(literal_address, ERROR_SLOT)
        slot = self.span(ERROR_SLOT, ERROR_SLOT + 4)
        self.assertEqual(sha256(slot), ERROR_SLOT_SHA256)
        self.assertEqual(struct.unpack("<I", slot)[0], ERROR_ADDRESS)
        error = self.span(ERROR_ADDRESS, ERROR_ADDRESS + len(ERROR_BYTES))
        self.assertEqual(error, ERROR_BYTES)
        self.assertEqual(sha256(error), ERROR_SHA256)

        # Stream+8 is bytes_left and stream+12 is first-error storage.
        self.assertIn(bytes.fromhex("a068"), self.span(READBYTE_START, READBYTE_END))
        self.assertIn(bytes.fromhex("e060"), self.span(READBYTE_START, READBYTE_END))
        self.assertEqual(stock[82:88].hex(), "f068002801d0")
        self.assertEqual(stock[-10:-4].hex(), "c7e900450120")

        options = CONFIG.read_text(encoding="utf-8")
        for token in (
            "PB_ENABLE_MALLOC",
            "PB_FIELD_32BIT",
            "PB_WITHOUT_64BIT",
            "PB_VALIDATE_UTF8",
            "PB_NO_ERRMSG",
            "PB_BUFFER_ONLY",
            "PB_MAX_REQUIRED_FIELDS != 64",
            "#define PB_MAX_REQUIRED_FIELDS 64",
        ):
            self.assertIn(token, options)

    def test_host_candidate_matches_authenticated_upstream_exhaustively(self) -> None:
        initial = 0xA55A_F00D_C33C_9696
        cases = []

        def encode(value: int) -> bytes:
            output = bytearray()
            while value >= 0x80:
                output.append((value & 0x7F) | 0x80)
                value >>= 7
            output.append(value)
            return bytes(output)

        for value in (
            0,
            1,
            0x7F,
            0x80,
            0x12C,
            0xFFFF_FFFF,
            1 << 63,
            0xFFFF_FFFF_FFFF_FFFF,
        ):
            encoded = encode(value)
            cases.append((encoded, len(encoded), 0, 0, initial))
        cases.extend(
            (
                (b"\x80\x00", 2, 0, 0, initial),
                (b"\x81\x00", 2, 0, 0, initial),
                (b"", 0, 0, 0, initial),
                (b"\x80", 1, 0, 0, initial),
                (b"\x80\x00", 1, 0, 0, initial),
                (b"\x80\x00", 2, 1, 0, initial),
                (b"\x80\x00", 2, 2, 0, initial),
                (b"\xff" * 10, 10, 0, 0, initial),
                (b"\xff" * 9 + b"\x02", 10, 0, 0, initial),
                (b"\xff" * 9 + b"\x01", 10, 0, 0, initial),
                (b"\xff" * 10, 10, 0, 1, initial),
                (b"", 0, 0, 1, initial),
                (b"\x80", 1, 1, 1, initial),
            )
        )

        generator = random.Random(0x48F5B8)
        for _ in range(1_000):
            size = generator.randrange(0, 14)
            data = bytes(generator.randrange(0, 256) for _ in range(size))
            cases.append(
                (
                    data,
                    generator.randrange(0, 15),
                    generator.randrange(0, 15),
                    generator.randrange(0, 2),
                    generator.randrange(0, 1 << 64),
                )
            )

        for data, bytes_left, fail_call, preexisting, initial_value in cases:
            candidate = self.run_host(
                self.candidate,
                data,
                bytes_left,
                fail_call,
                preexisting,
                initial_value,
            )
            upstream = self.run_host(
                self.upstream,
                data,
                bytes_left,
                fail_call,
                preexisting,
                initial_value,
            )
            self.assertEqual(
                candidate,
                upstream,
                (data.hex(), bytes_left, fail_call, preexisting, initial_value),
            )

        self.assertEqual(
            self.run_host(self.candidate, b"", 0, 0, 0, initial),
            (0, initial, 0, 0, 0, 1),
        )
        self.assertEqual(
            self.run_host(self.candidate, b"\x80", 1, 1, 0, initial),
            (0, initial, 1, 0, 1, 2),
        )
        self.assertEqual(
            self.run_host(self.candidate, b"\xff" * 10, 10, 0, 0, initial),
            (0, initial, 0, 10, 10, 3),
        )
        self.assertEqual(
            self.run_host(self.candidate, b"\xff" * 9 + b"\x01", 10, 0, 0, initial),
            (1, 0xFFFF_FFFF_FFFF_FFFF, 0, 10, 10, 0),
        )
        self.assertEqual(
            self.run_host(self.candidate, b"\xff" * 10, 10, 0, 1, initial),
            (0, initial, 0, 10, 10, 4),
        )

    def test_both_compiler_objects_and_relocation_closure_are_pinned(self) -> None:
        for profile, pins in PROFILE_PINS.items():
            recorded = bytes.fromhex(pins["text_hex"])
            with self.subTest(recorded_profile=profile):
                self.assertEqual(len(recorded), pins["text_size"])
                self.assertEqual(sha256(recorded), pins["text_sha256"])

        parsed = [self.apollo_overlay.parse_elf32(path) for path in self.objects]
        self.assertEqual(self.objects[0].read_bytes(), self.objects[1].read_bytes())
        for path, (data, sections) in zip(self.objects, parsed):
            with self.subTest(object=path.name):
                self.assertEqual(path.stat().st_size, self.pins["object"][0])
                self.assertEqual(sha256(path), self.pins["object"][1])
                function = next(
                    section for section in sections
                    if section["name"] == FUNCTION_SECTION
                )
                text = data[
                    int(function["offset"]):
                    int(function["offset"]) + int(function["size"])
                ]
                self.assertEqual(int(function["alignment"]), 4)
                self.assertEqual(text.hex(), self.pins["text_hex"])
                self.assertEqual(sha256(text), self.pins["text_sha256"])

                rodata = next(
                    section for section in sections
                    if section["name"] == ".rodata.str1.1"
                )
                string = data[
                    int(rodata["offset"]):
                    int(rodata["offset"]) + int(rodata["size"])
                ]
                self.assertEqual(string, ERROR_BYTES)
                self.assertEqual(sha256(string), ERROR_SHA256)
                executable = [
                    section["name"] for section in sections
                    if int(section["size"]) > 0 and int(section["flags"]) & 0x4
                ]
                self.assertEqual(executable, [FUNCTION_SECTION])
                writable = [
                    section["name"] for section in sections
                    if int(section["size"]) > 0
                    and int(section["flags"]) & 0x3 == 0x3
                ]
                self.assertEqual(writable, [])

        data, sections = parsed[0]
        symbol_table = self.apollo_overlay.section_named(sections, ".symtab")
        string_table = sections[int(symbol_table["link"])]
        strings = data[
            int(string_table["offset"]):
            int(string_table["offset"]) + int(string_table["size"])
        ]
        symbols = []
        for index in range(int(symbol_table["size"]) // 16):
            fields = struct.unpack_from(
                "<IIIBBH",
                data,
                int(symbol_table["offset"]) + index * 16,
            )
            symbols.append(
                (
                    self.apollo_overlay.elf_string(strings, fields[0], "symbol"),
                    fields,
                )
            )
        by_name = {name: fields for name, fields in symbols if name}
        self.assertEqual(by_name[FUNCTION][2], self.pins["text_size"])
        self.assertEqual(
            [name for name, fields in symbols if name and fields[5] == 0],
            [SEAM],
        )

        relocations = []
        exidx = []
        for section in sections:
            if int(section["type"]) != 9:
                continue
            target = sections[int(section["info"])]
            for index in range(int(section["size"]) // 8):
                offset, information = struct.unpack_from(
                    "<II",
                    data,
                    int(section["offset"]) + index * 8,
                )
                record = (
                    offset,
                    information & 0xFF,
                    symbols[information >> 8][0],
                )
                if target["name"] == FUNCTION_SECTION:
                    relocations.append(record)
                else:
                    exidx.append((target["name"], *record))
        self.assertEqual(relocations, self.pins["text_relocations"])
        self.assertEqual(
            exidx,
            [(".ARM.exidx" + FUNCTION_SECTION, 0, 42, "")],
        )


if __name__ == "__main__":
    unittest.main()
