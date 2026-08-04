from __future__ import annotations

import ctypes
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT / "components/shared/cmbacktrace"
    / "runtime_cmbacktrace_get_cur_thread_name_candidate.c"
)
HEADER = SOURCE.with_suffix(".h")
HOST_FIXTURE = (
    ROOT / "tests/fixtures"
    / "runtime_cmbacktrace_get_cur_thread_name_candidate_host.c"
)
AUDIT = (
    ROOT / "docs/research"
    / "cmbacktrace-get-cur-thread-name-source-candidate-audit.md"
)
SNAPSHOT = ROOT / "third_party/cmbacktrace"
UPSTREAM = SNAPSHOT / "cm_backtrace/cm_backtrace.c"
PROVENANCE = SNAPSHOT / "PROVENANCE.json"
VERIFIER = SNAPSHOT / "verify_snapshot.py"
OFFICIAL = (
    ROOT / "blobs/official/g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
MAKEFILE = ROOT / "Makefile"

FUNCTION = "open_cfw_cmbacktrace_get_cur_thread_name_candidate"
SEAM = "open_cfw_cmbacktrace_pc_task_get_name_current_candidate"
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
START = 0x0059_3AF6
END = 0x0059_3AFE
STOCK_HEX = "80b5c2f699fa02bd"
STOCK_SHA256 = (
    "75f860b4a8f7d60464eeb5216946dbef"
    "e0875c65fb0c7a6641abdd9f9daa979b"
)
PRECEDING = (
    0x0059_3AEE,
    START,
    "e54578c8ef0d67d4eb13235c926437812c0fa1bdea88e04bdff8a9cfdc01739b",
)
FOLLOWING = (
    END,
    0x0059_3B06,
    "8dda716ee93857cdfdc9faf824123a7c6ccd461fb72c60bbc0bee4be38fd7161",
)
CALLERS = [
    (0x0059_457E, "fff7bafa"),
    (0x0059_4586, "fff7b6fa"),
    (0x0059_459E, "fff7aafa"),
    (0x0059_45A6, "fff7a6fa"),
]
CALLER_ADDRESS_SHA256 = (
    "082fc78b557ca674f0bf367869ea98c44"
    "f0b85aaff047caf1f0a3f4f62d5bfed"
)
CALLER_RECORD_SHA256 = (
    "7f677fa382b59698fb8a8728783ffcbe"
    "4626160d8f0c7bbc28c0c4bc9ba8d618"
)
CALLER_SPAN = (
    0x0059_455C,
    0x0059_45AC,
    "ec739a3bf1d609c09f128391dcbcb14b5772e3dec9462dc62a7c7c834e4b3d0b",
)

DEPENDENCY_START = 0x0045_602E
DEPENDENCY_END = 0x0045_6036
DEPENDENCY_HEX = "0b48006834307047"
DEPENDENCY_SHA256 = (
    "a4150246c7816b7ffab201b6ae3bc6d"
    "a8c6147e9a5541a921733369dd1e6c09b"
)
DEPENDENCY_LITERAL_SLOT = 0x0045_605C
PX_CURRENT_TCB = 0x2007_4A20
TASK_NAME_OFFSET = 0x34
DEPENDENCY_CALLERS = [(0x0059_3AF8, "c2f699fa")]

UPSTREAM_SIZE = 26_436
UPSTREAM_SHA256 = (
    "6e444224af3ef223067849b88f61281e"
    "c0661e3f38425e84758bf12be057e01c"
)
UPSTREAM_MARKER = b"static const char *get_cur_thread_name(void) {"
UPSTREAM_SLICE_OFFSET = 8_261
UPSTREAM_SLICE_SIZE = 974
UPSTREAM_SLICE_SHA256 = (
    "fc81b35576ed317335f04c411907037d"
    "faed7490dd0e90a2ca72b7deba8dceca"
)
SELECTED_COMMIT = "73714489f9d8af130aacb515586b397b604a5768"
SELECTED_TREE = "541c20dbeb1165f9b2862e2b84cdc63b3d7c718f"
COMPATIBLE_FLOOR = "4abadfa0c4f86f22352aa5ab9ebbb4f687125a1c"

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
    "-fno-ident",
)
PROFILE_PINS = {
    "apple-clang": {
        "compiler": "/usr/bin/clang",
        "version": "Apple clang version 21.0.0 (clang-2100.3.27.1)",
    },
    "linux-clang": {
        "compiler": "/home/linuxbrew/.linuxbrew/bin/clang",
        "version": "Homebrew clang version 22.1.8",
    },
}
OBJECT_SIZE = 1_004
OBJECT_SHA256 = (
    "29bcaab263166fec8765c937acb907158"
    "963e5e03ff3f7d8f18161a2faaf589a"
)
TEXT_HEX = "fff7febf"
TEXT_SHA256 = (
    "90a54a1f68a806a1795bd04485690823"
    "5426b3c0f67be605fb94d3d5344a747f"
)
EXIDX_HEX = "0000000001000000"
EXIDX_SHA256 = (
    "01acecb507abfe1a354aa8064f4af5d3"
    "f1acd019e37db3c11c97523b71c76e9d"
)
LOCAL_PINS = {
    SOURCE: (
        2_034,
        "3d0b2de640b3bdfbbc26b50d632b191edefa60405602b5108b86162668c6991b",
    ),
    HEADER: (
        777,
        "380b605a611c5b8b7136f940f8ef33a5b33259821ccf109ecc43e51c8a384ae0",
    ),
    HOST_FIXTURE: (
        1_418,
        "9ea49da2e20909c0779995ff75bf8b3c994e61bbc86e7bd02e242eb30126d3b6",
    ),
    AUDIT: (
        8_377,
        "254cd6ecda1c88776e3c9c4f1a6973bb58f4530ee70dc69f7f79309e1f122fcd",
    ),
}


def sha256(value: bytes | Path) -> str:
    if isinstance(value, Path):
        value = value.read_bytes()
    return hashlib.sha256(value).hexdigest()


def extract_upstream_function(source: bytes) -> bytes:
    start = source.index(UPSTREAM_MARKER)
    brace = source.index(b"{", start)
    depth = 0
    for cursor in range(brace, len(source)):
        if source[cursor] == ord("{"):
            depth += 1
        elif source[cursor] == ord("}"):
            depth -= 1
            if depth == 0:
                end = cursor + 1
                if source[end:end + 2] == b"\r\n":
                    end += 2
                elif source[end:end + 1] == b"\n":
                    end += 1
                result = source[start:end]
                if start != UPSTREAM_SLICE_OFFSET:
                    raise AssertionError("upstream function moved")
                return result
    raise AssertionError("unterminated upstream function")


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
        (sign << 24) | (i1 << 23) | (i2 << 22)
        | (imm10 << 12) | (imm11 << 1)
    )
    if sign:
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFF_FFFF


def wide_conditional_target(address: int, first: int, second: int) -> int | None:
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0x8000:
        return None
    if ((first >> 6) & 0x0F) >= 0x0E:
        return None
    sign = (first >> 10) & 1
    immediate = (
        sign << 20
        | ((second >> 11) & 1) << 19
        | ((second >> 13) & 1) << 18
        | (first & 0x003F) << 12
        | (second & 0x07FF) << 1
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
        immediate = (((halfword >> 9) & 1) << 5) | ((halfword >> 3) & 0x1F)
        return (address + 4 + immediate * 2,)
    return ()


class CmBacktraceGetCurThreadNameCandidateTests(unittest.TestCase):
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
        if (cls.clang, version) != (
            PROFILE_PINS[cls.profile]["compiler"],
            PROFILE_PINS[cls.profile]["version"],
        ):
            raise AssertionError((cls.clang, version, PROFILE_PINS[cls.profile]))

        upstream = UPSTREAM.read_bytes()
        cls.upstream_slice = extract_upstream_function(upstream)
        if (
            len(upstream) != UPSTREAM_SIZE
            or sha256(upstream) != UPSTREAM_SHA256
            or len(cls.upstream_slice) != UPSTREAM_SLICE_SIZE
            or sha256(cls.upstream_slice) != UPSTREAM_SLICE_SHA256
        ):
            raise AssertionError("unauthenticated CmBacktrace source/configuration")
        verification = subprocess.run(
            [sys.executable, str(VERIFIER)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        if verification.stdout != (
            "CmBacktrace compatibility snapshot verification passed\n"
        ):
            raise AssertionError("CmBacktrace verifier did not authenticate snapshot")
        cls.provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        selection = cls.provenance["selection"]
        if not (
            cls.provenance["license"] == "MIT"
            and cls.provenance["upstream"]["selected_commit"] == SELECTED_COMMIT
            and cls.provenance["upstream"]["selected_tree"] == SELECTED_TREE
            and selection["exact_g2_checkout_proven"] is False
            and selection["compatible_floor_commit"] == COMPATIBLE_FLOOR
            and selection["compatible_ceiling_commit"] == SELECTED_COMMIT
            and cls.provenance["g2_boundary"]["proven_effective_configuration"]
            ["CMB_OS_PLATFORM_TYPE"] == "CMB_OS_PLATFORM_FREERTOS"
        ):
            raise AssertionError("unauthenticated CmBacktrace provenance/configuration")

        parent = ROOT / "build"
        parent.mkdir(exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="open-cfw-cmbacktrace-get-name-candidate-",
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

        oracle = temporary / "upstream-oracle.c"
        prefix = b"""\
#define CMB_OS_PLATFORM_RTT 1
#define CMB_OS_PLATFORM_UCOSII 2
#define CMB_OS_PLATFORM_UCOSIII 3
#define CMB_OS_PLATFORM_FREERTOS 4
#define CMB_OS_PLATFORM_RTX5 5
#define CMB_OS_PLATFORM_THREADX 6
#define CMB_OS_PLATFORM_TYPE CMB_OS_PLATFORM_FREERTOS
const char *vTaskName(void);
"""
        renamed = cls.upstream_slice.replace(
            UPSTREAM_MARKER,
            b"const char *open_cfw_cmbacktrace_get_cur_thread_name_upstream_oracle(void) {",
            1,
        )
        oracle.write_bytes(prefix + renamed)
        library = temporary / (
            "cmbacktrace-get-name-candidate.dylib"
            if sys.platform == "darwin"
            else "cmbacktrace-get-name-candidate.so"
        )
        command = [
            cls.clang,
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-I",
            str(ROOT),
            str(SOURCE),
            str(HOST_FIXTURE),
            str(oracle),
        ]
        if sys.platform == "darwin":
            command.extend(("-dynamiclib", "-o", str(library)))
        else:
            command.extend(("-shared", "-fPIC", "-o", str(library)))
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.library = ctypes.CDLL(str(library))
        cls.reset = cls.library.open_cfw_test_cmbacktrace_get_cur_thread_name_reset
        cls.reset.argtypes = [ctypes.c_void_p]
        cls.reset.restype = None
        cls.candidate = (
            cls.library.open_cfw_test_cmbacktrace_get_cur_thread_name_candidate
        )
        cls.upstream_oracle = (
            cls.library.open_cfw_test_cmbacktrace_get_cur_thread_name_upstream
        )
        for function in (cls.candidate, cls.upstream_oracle):
            function.argtypes = []
            function.restype = ctypes.c_void_p
        cls.candidate_calls = (
            cls.library.open_cfw_test_cmbacktrace_candidate_seam_calls
        )
        cls.upstream_calls = (
            cls.library.open_cfw_test_cmbacktrace_upstream_seam_calls
        )
        for function in (cls.candidate_calls, cls.upstream_calls):
            function.argtypes = []
            function.restype = ctypes.c_uint32

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

    def test_authenticated_snapshot_and_candidate_provenance_are_pinned(self) -> None:
        for path, (size, digest) in LOCAL_PINS.items():
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertEqual(path.stat().st_size, size)
                self.assertEqual(sha256(path), digest)

        provenance = self.provenance
        self.assertEqual(provenance["license"], "MIT")
        self.assertEqual(provenance["upstream"]["selected_commit"], SELECTED_COMMIT)
        self.assertEqual(provenance["upstream"]["selected_tree"], SELECTED_TREE)
        selection = provenance["selection"]
        self.assertFalse(selection["exact_g2_checkout_proven"])
        self.assertEqual(selection["compatible_floor_commit"], COMPATIBLE_FLOOR)
        self.assertEqual(selection["compatible_ceiling_commit"], SELECTED_COMMIT)
        self.assertEqual(
            provenance["g2_boundary"]["proven_effective_configuration"]
            ["CMB_OS_PLATFORM_TYPE"],
            "CMB_OS_PLATFORM_FREERTOS",
        )
        self.assertEqual(len(self.upstream_slice), UPSTREAM_SLICE_SIZE)
        self.assertEqual(sha256(self.upstream_slice), UPSTREAM_SLICE_SHA256)
        self.assertIn(b"return vTaskName();", self.upstream_slice)

        source = SOURCE.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        for token in (
            "Copyright (c) 2016-2019, Armink",
            "SPDX-License-Identifier: MIT",
            SELECTED_COMMIT,
            "not a claim that Even used that exact",
            "[0x00593AF6,0x00593AFE)",
        ):
            self.assertIn(token, source)
        self.assertIn("pcTaskGetName(NULL)", header)
        audit = AUDIT.read_text(encoding="utf-8")
        for token in (
            "Complete ingress proof",
            "R_ARM_THM_JUMP24",
            "Production promotion result",
            "Hardware use remains disabled",
        ):
            self.assertIn(token, audit)

    def test_candidate_is_absent_from_production_registrations(self) -> None:
        for path in (OVERLAY, MANIFEST, MAKEFILE):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn(SOURCE_PATH, text, path)
            self.assertNotIn(FUNCTION, text, path)
        self.assertTrue(SOURCE.name.endswith("_candidate.c"))

    def test_stock_boundary_and_dependency_adapter_are_exact(self) -> None:
        self.assertEqual(len(self.package), PACKAGE_SIZE)
        self.assertEqual(sha256(self.package), PACKAGE_SHA256)
        self.assertEqual(sha256(self.application), APPLICATION_SHA256)
        stock = self.span(START, END)
        self.assertEqual(stock.hex(), STOCK_HEX)
        self.assertEqual(sha256(stock), STOCK_SHA256)
        for start, end, digest in (PRECEDING, FOLLOWING):
            self.assertEqual(sha256(self.span(start, end)), digest)

        dependency = self.span(DEPENDENCY_START, DEPENDENCY_END)
        self.assertEqual(dependency.hex(), DEPENDENCY_HEX)
        self.assertEqual(sha256(dependency), DEPENDENCY_SHA256)
        literal_instruction = struct.unpack_from("<H", dependency)[0]
        literal_address = (
            ((DEPENDENCY_START + 4) & ~3)
            + ((literal_instruction & 0x00FF) << 2)
        )
        self.assertEqual(literal_address, DEPENDENCY_LITERAL_SLOT)
        self.assertEqual(
            struct.unpack("<I", self.span(literal_address, literal_address + 4))[0],
            PX_CURRENT_TCB,
        )
        self.assertEqual(struct.unpack_from("<H", dependency, 4)[0], 0x3034)
        self.assertEqual(TASK_NAME_OFFSET, 0x34)
        outgoing = []
        for offset in range(0, len(stock) - 3, 2):
            target = thumb_wide_branch_target(
                START + offset,
                *struct.unpack_from("<HH", stock, offset),
                link=True,
            )
            if target is not None:
                outgoing.append((START + offset, target, stock[offset:offset + 4].hex()))
        self.assertEqual(outgoing, [(0x0059_3AF8, DEPENDENCY_START, "c2f699fa")])

    def test_whole_image_four_caller_and_all_ingress_closure_is_exact(self) -> None:
        # Keep every ingress decoder independently live even when the official
        # image has no ingress of that class to this particular boundary.
        first, second = struct.unpack(
            "<HH", self.apollo_overlay.encode_thumb_b_w(0x1000, 0x1010)
        )
        self.assertEqual(
            thumb_wide_branch_target(0x1000, first, second, link=False),
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
        interior = []
        conditional_or_narrow = []
        dependency_callers = []
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
            first, second = struct.unpack_from("<HH", self.application, offset)
            encoding = self.application[offset:offset + 4]
            for link in (True, False):
                target = thumb_wide_branch_target(
                    address, first, second, link=link
                )
                if target == DEPENDENCY_START and link:
                    dependency_callers.append((address, encoding.hex()))
                if target is None or not START <= target < END:
                    continue
                if target == START:
                    (direct_bl if link else direct_bw).append(
                        (address, encoding.hex())
                    )
                elif not START <= address < END:
                    interior.append((address, target, link, encoding.hex()))
            conditional = wide_conditional_target(address, first, second)
            targets = (
                *((conditional,) if conditional is not None else ()),
                *narrow_targets(address, first),
            )
            for target in targets:
                if START <= target < END and not START <= address < END:
                    conditional_or_narrow.append(
                        (address, target, encoding.hex())
                    )

        self.assertEqual(direct_bl, CALLERS)
        self.assertEqual(direct_bw, [])
        self.assertEqual(interior, [])
        self.assertEqual(conditional_or_narrow, [])
        self.assertEqual(dependency_callers, DEPENDENCY_CALLERS)
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
        self.assertEqual(sha256(self.span(*CALLER_SPAN[:2])), CALLER_SPAN[2])

        stored = []
        for canonical in range(START, END):
            for value in {canonical, canonical | 1}:
                needle = struct.pack("<I", value)
                position = self.application.find(needle)
                while position >= 0:
                    stored.append((APPLICATION_BASE + position, value))
                    position = self.application.find(needle, position + 1)
        self.assertEqual(stored, [])

    def test_host_candidate_matches_authenticated_upstream_source_slice(self) -> None:
        buffers = [
            ctypes.create_string_buffer(b""),
            ctypes.create_string_buffer(b"main"),
            ctypes.create_string_buffer(b"x" * 40),
        ]
        for storage in buffers:
            address = ctypes.addressof(storage)
            with self.subTest(value=bytes(storage)):
                self.reset(address)
                self.assertEqual(self.candidate(), address)
                self.assertEqual((self.candidate_calls(), self.upstream_calls()), (1, 0))
                self.reset(address)
                self.assertEqual(self.upstream_oracle(), address)
                self.assertEqual((self.candidate_calls(), self.upstream_calls()), (0, 1))
        self.reset(None)
        self.assertIsNone(self.candidate())
        self.assertEqual((self.candidate_calls(), self.upstream_calls()), (1, 0))
        self.reset(None)
        self.assertIsNone(self.upstream_oracle())
        self.assertEqual((self.candidate_calls(), self.upstream_calls()), (0, 1))

    def test_apple_and_linux_target_object_contract_is_exact(self) -> None:
        self.assertEqual(self.objects[0].read_bytes(), self.objects[1].read_bytes())
        for path in self.objects:
            with self.subTest(object=path.name):
                self.assertEqual(path.stat().st_size, OBJECT_SIZE)
                self.assertEqual(sha256(path), OBJECT_SHA256)
                data, sections = self.apollo_overlay.parse_elf32(path)
                function = self.apollo_overlay.section_named(sections, FUNCTION_SECTION)
                text = data[
                    int(function["offset"]):
                    int(function["offset"]) + int(function["size"])
                ]
                self.assertEqual(int(function["alignment"]), 4)
                self.assertEqual(text.hex(), TEXT_HEX)
                self.assertEqual(sha256(text), TEXT_SHA256)
                executable = [
                    section["name"] for section in sections
                    if int(section["size"]) > 0 and int(section["flags"]) & 0x4
                ]
                self.assertEqual(executable, [FUNCTION_SECTION])

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
                    symbols.append((
                        self.apollo_overlay.elf_string(strings, fields[0], "symbol"),
                        fields,
                    ))
                by_name = {name: fields for name, fields in symbols if name}
                self.assertEqual(by_name[FUNCTION][2], 4)
                self.assertEqual(
                    [name for name, fields in symbols if name and fields[5] == 0],
                    [SEAM],
                )

                text_relocations = []
                exidx_relocations = []
                for section in sections:
                    if int(section["type"]) != 9:
                        continue
                    target = sections[int(section["info"])]
                    for index in range(int(section["size"]) // 8):
                        offset, information = struct.unpack_from(
                            "<II", data, int(section["offset"]) + index * 8
                        )
                        record = (
                            offset,
                            information & 0xFF,
                            symbols[information >> 8][0],
                        )
                        if target["name"] == FUNCTION_SECTION:
                            text_relocations.append(record)
                        elif target["name"] == ".ARM.exidx" + FUNCTION_SECTION:
                            exidx_relocations.append(record)
                self.assertEqual(text_relocations, [(0, 30, SEAM)])
                self.assertEqual(exidx_relocations, [(0, 42, "")])
                exidx = self.apollo_overlay.section_named(
                    sections, ".ARM.exidx" + FUNCTION_SECTION
                )
                exidx_bytes = data[
                    int(exidx["offset"]):int(exidx["offset"]) + int(exidx["size"])
                ]
                self.assertEqual(exidx_bytes.hex(), EXIDX_HEX)
                self.assertEqual(sha256(exidx_bytes), EXIDX_SHA256)


if __name__ == "__main__":
    unittest.main()
