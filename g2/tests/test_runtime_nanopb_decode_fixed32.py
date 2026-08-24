from __future__ import annotations

import ctypes
import hashlib
import json
import os
import random
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/shared/nanopb/runtime_nanopb_decode_fixed32.c"
HEADER = SOURCE.with_suffix(".h")
SNAPSHOT = ROOT / "third_party/nanopb"
UPSTREAM = SNAPSHOT / "pb_decode.c"
CONFIG_HEADER = SNAPSHOT / "g2-config/pb_g2_options.h"
PROVENANCE = SNAPSHOT / "PROVENANCE.json"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
OVERLAY_RUNTIME_BASE = 0x0079_4324

FUNCTION = "open_cfw_nanopb_decode_fixed32"
SECTION = ".text." + FUNCTION
APPLICATION_BASE = 0x0043_8000
PREAMBLE = 32
START = 0x0049_0190
END = 0x0049_01AC
READ_ENTRY = 0x0048_F3BE
CALLER = 0x0048_F89C

SOURCE_PIN = (
    1_975,
    "fefd8a899174fb9332c366df691dc2c8"
    "ec6f4792f3fd464b65dbb573ace8ee19",
)
HEADER_PIN = (
    1_750,
    "738e4c7d4ea983b0ba967fa42cdcc61c"
    "b2e20837531bc6176b7f95a5fe8e2460",
)
UPSTREAM_PIN = (
    53_845,
    "e980f2a41d9abe37b7e6fb4c9ba1ebf"
    "d68507a6fd2653f8d755e1947a9c84b1a",
)
UPSTREAM_DEFINITION = (43_210, 43_828)
UPSTREAM_DEFINITION_PIN = (
    618,
    "1952ee1f743334c82f206c910392f63b"
    "2e7fdd702cbdd404dae04367aa8ae518",
)
CONFIG_PIN = (
    1_551,
    "ae758999d239e49e2d5c5bf6de3f4ae"
    "f3aab5cd3c29d8de65c4db301c62899db",
)
STOCK = bytes.fromhex(
    "1cb50c0004226946fff711f9002801d1002002e000982060012016bd"
)
STOCK_SHA256 = (
    "1ee27599a8ac5b8d2a0cbaac59986fb4"
    "9be7b24c348a960a216b8cbbecce5bf3"
)
CALLER_BODY = (0x0048_F7F4, 0x0048_F968)
CALLER_BODY_SHA256 = (
    "2b1bf389327c0f6ccde636bbb51e36cd"
    "0bab3eccc811db9aa0efd3dbfef9e445"
)
READ_BODY = (READ_ENTRY, 0x0048_F454)
READ_BODY_SHA256 = (
    "69aecb900c749fd98bd2d05e2229e9a3"
    "d6829bd36f3e393f624e3579a9b4af7f"
)
PREDECESSOR = (0x0049_0180, START)
PREDECESSOR_SHA256 = (
    "afa606ddde93a21b59394932fc95e7cb"
    "628978dc62bfa49c337b750c80cfa813"
)
SUCCESSOR = (END, 0x0049_01C4)
SUCCESSOR_SHA256 = (
    "8ec2f1b9165e3c501eb931ba6ee6180a"
    "6733ddf61760423a60fef54b260710f9"
)

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
TARGET_OBJECT_PIN = (
    960,
    "499f6ec335b62a6af9a4f2370aaa5ef"
    "831a5ec2b3e8da99bcb6f7b8a4e83fedd",
)
TARGET_TEXT = bytes.fromhex(
    "b0b582b00d4601a90422fff7feff70b19df804109df805209df806309df80740"
    "41ea022141ea034141ea0461296002b0b0bd"
)
TARGET_TEXT_SHA256 = (
    "798f8f7cbed57f6ba11dad46a6de9d25"
    "cb1f1710eb4fa904d79b6fe449952a04"
)

PROFILE_PINS = {
    "apple-clang": {
        "compiler": "/usr/bin/clang",
        "version": "Apple clang version 21.0.0 (clang-2100.3.30.1)",
        "offset": 124_496,
        "runtime": 0x007B_2974,
        "relocated": (
            "c9fc88c025ec843fa3ad3f77b4e1bfb8"
            "4126fd397a81d96c271646eb70632539"
        ),
        "overlay": (
            167_426,
            "800245ad7f4ba1044f01888fc0141f9f3304bc531773847ba9c0c29e62245491",
        ),
        "component": (
            3_690_822,
            "9ed3e77e10dd911ae34e9ba17f691f6988c592723b52a9676b8d414554a21459",
        ),
        "package": (
            4_469_316,
            "d4c7f82a3e0cfbfc4476f8ca72c1bfd6a3aba5b13d32c6b924686cbc4d78c10d",
        ),
        "plan": (
            1_337_744,
            "642d39802f988c3da5e108c97fdcff82102cfcdfffd75710bd6e0a3017f7758e",
        ),
        "patch": (
            "22f3f0bb" + "00bf" * 12,
            "34c42ae60118f9f3546e0ef05a41f4ca"
            "68983fc81503e9915e7c4d9361f15616",
        ),
    },
    "linux-clang": {
        "compiler": "/home/linuxbrew/.linuxbrew/bin/clang",
        "version": "Homebrew clang version 22.1.8",
        "offset": 126_316,
        "runtime": 0x007B_3090,
        "relocated": (
            "53a1961d2df94674da6890611087ab865"
            "498084ced6a6f0c6850dcee23c7bf60"
        ),
        "overlay": (
            145_208,
            "fac5b48b6ae2eac985a0a65ddb8d1595dd10e2abcbdd0c6a3bb562f72e43a826",
        ),
        "component": (
            3_668_604,
            "378c868e151060a59ab91b0de1a722e8678b8e1da8eede248c5702ccf8902798",
        ),
        "package": (
            4_447_098,
            "deb4cdb9d869abcb3aee5e122661ee45b541680cf277df5d1a7c6eed67bb7b6e",
        ),
        "plan": (
            836_433,
            "a63772c778639dfcaf296985e64b3e643012f41c83a2900d9d06b68132b2e40f",
        ),
        "patch": (
            "22f37ebf" + "00bf" * 12,
            "d6c11f5f1a5b6f89f12e30c476f27daf"
            "0301a2d17d7ad9bafd5039d0aa970085",
        ),
    },
}

MANIFEST_STATUS = {
    "container_only": (1, 32),
    "generated_alignment": (190, 382),
    "generated_source_entry_replacement": (858, 119_962),
    "generated_source_exact_load_image": (1, 6),
    "generated_source_exact_replacement": (7, 134),
    "official_blob": (268, 3_403_044),
    "source_compiled": (455, 166_412),
}

HOST_PROVIDER = r"""
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "runtime_nanopb_decode_fixed32.h"
#include "pb_decode.h"

struct open_cfw_test_input {
    const uint8_t *bytes;
    size_t size;
    size_t offset;
    uint32_t calls;
    uint32_t fail_call;
};

struct open_cfw_test_result {
    uint64_t bytes_left;
    uint64_t consumed;
    uint32_t status;
    uint32_t destination;
    uint32_t calls;
    uint32_t error;
};

static const char open_cfw_test_existing_error[] = "existing";

static bool open_cfw_test_read(
    struct open_cfw_test_input *input,
    uint8_t *buffer,
    size_t count
)
{
    input->calls++;
    if ((input->fail_call != 0U && input->calls == input->fail_call) ||
        count > input->size - input->offset) {
        return false;
    }
    memcpy(buffer, input->bytes + input->offset, count);
    input->offset += count;
    return true;
}

static bool open_cfw_test_candidate_callback(
    struct open_cfw_nanopb_istream *stream,
    uint8_t *buffer,
    size_t count
)
{
    return open_cfw_test_read(
        (struct open_cfw_test_input *)stream->state, buffer, count
    );
}

static bool open_cfw_test_upstream_callback(
    pb_istream_t *stream,
    pb_byte_t *buffer,
    size_t count
)
{
    return open_cfw_test_read(
        (struct open_cfw_test_input *)stream->state, buffer, count
    );
}

bool open_cfw_nanopb_read(
    struct open_cfw_nanopb_istream *stream,
    uint8_t *buffer,
    size_t count
)
{
    if (count == 0U) {
        return true;
    }
    if (stream->bytes_left < count) {
        if (stream->errmsg == NULL) {
            stream->errmsg = "end-of-stream";
        }
        return false;
    }
    if (!stream->callback(stream, buffer, count)) {
        if (stream->errmsg == NULL) {
            stream->errmsg = "io error";
        }
        return false;
    }
    stream->bytes_left -= count;
    return true;
}

static uint32_t open_cfw_test_error(const char *error)
{
    if (error == NULL) return 0U;
    if (strcmp(error, "end-of-stream") == 0) return 1U;
    if (strcmp(error, "io error") == 0) return 2U;
    if (error == open_cfw_test_existing_error) return 3U;
    return UINT32_MAX;
}

static void open_cfw_test_store(
    bool status,
    size_t bytes_left,
    uint32_t destination,
    const char *error,
    const struct open_cfw_test_input *input,
    struct open_cfw_test_result *result
)
{
    result->bytes_left = bytes_left;
    result->consumed = input->offset;
    result->status = status ? 1U : 0U;
    result->destination = destination;
    result->calls = input->calls;
    result->error = open_cfw_test_error(error);
}

void open_cfw_test_run_candidate(
    const uint8_t *bytes,
    size_t size,
    size_t bytes_left,
    uint32_t fail_call,
    uint32_t existing_error,
    uint32_t initial_destination,
    struct open_cfw_test_result *result
)
{
    struct open_cfw_test_input input = {
        bytes, size, 0U, 0U, fail_call
    };
    struct open_cfw_nanopb_istream stream = {
        open_cfw_test_candidate_callback,
        &input,
        bytes_left,
        existing_error ? open_cfw_test_existing_error : NULL
    };
    uint32_t destination = initial_destination;
    bool status = open_cfw_nanopb_decode_fixed32(&stream, &destination);
    open_cfw_test_store(
        status, stream.bytes_left, destination, stream.errmsg, &input, result
    );
}

void open_cfw_test_run_upstream(
    const uint8_t *bytes,
    size_t size,
    size_t bytes_left,
    uint32_t fail_call,
    uint32_t existing_error,
    uint32_t initial_destination,
    struct open_cfw_test_result *result
)
{
    struct open_cfw_test_input input = {
        bytes, size, 0U, 0U, fail_call
    };
    pb_istream_t stream = {
        open_cfw_test_upstream_callback,
        &input,
        bytes_left,
        existing_error ? open_cfw_test_existing_error : NULL
    };
    uint32_t destination = initial_destination;
    bool status = pb_decode_fixed32(&stream, &destination);
    open_cfw_test_store(
        status, stream.bytes_left, destination, stream.errmsg, &input, result
    );
}
"""


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def wide_branch_target(
    address: int, first: int, second: int, *, link: bool
) -> int | None:
    expected = 0xD000 if link else 0x9000
    if first & 0xF800 != 0xF000 or second & 0xD000 != expected:
        return None
    sign = (first >> 10) & 1
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    immediate = (
        (sign << 24)
        | ((1 ^ (j1 ^ sign)) << 23)
        | ((1 ^ (j2 ^ sign)) << 22)
        | ((first & 0x03FF) << 12)
        | ((second & 0x07FF) << 1)
    )
    if sign:
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFF_FFFF


def wide_conditional_target(address: int, first: int, second: int) -> int | None:
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0x8000:
        return None
    if (first >> 6) & 0x0F >= 0x0E:
        return None
    sign = (first >> 10) & 1
    immediate = (
        (sign << 20)
        | (((second >> 11) & 1) << 19)
        | (((second >> 13) & 1) << 18)
        | ((first & 0x003F) << 12)
        | ((second & 0x07FF) << 1)
    )
    if sign:
        immediate -= 1 << 21
    return (address + 4 + immediate) & 0xFFFF_FFFF


def narrow_targets(address: int, halfword: int) -> tuple[int, ...]:
    if halfword & 0xF800 == 0xE000:
        immediate = halfword & 0x07FF
        if immediate & 0x0400:
            immediate -= 0x0800
        return (address + 4 + 2 * immediate,)
    if halfword & 0xF000 == 0xD000 and (halfword >> 8) & 0xF < 0xE:
        immediate = halfword & 0xFF
        if immediate & 0x80:
            immediate -= 0x100
        return (address + 4 + 2 * immediate,)
    if halfword & 0xF500 == 0xB100:
        immediate = (((halfword >> 9) & 1) << 5) | ((halfword >> 3) & 0x1F)
        return (address + 4 + 2 * immediate,)
    return ()


class Result(ctypes.Structure):
    _fields_ = [
        ("bytes_left", ctypes.c_uint64),
        ("consumed", ctypes.c_uint64),
        ("status", ctypes.c_uint32),
        ("destination", ctypes.c_uint32),
        ("calls", ctypes.c_uint32),
        ("error", ctypes.c_uint32),
    ]

    def values(self) -> tuple[int, ...]:
        return (
            self.status,
            self.destination,
            self.bytes_left,
            self.consumed,
            self.calls,
            self.error,
        )


class NanopbDecodeFixed32ProductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.package = OFFICIAL.read_bytes()
        cls.application = cls.package[PREAMBLE:]
        cls.clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        version = subprocess.run(
            [cls.clang, "--version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()[0]
        profiles = [
            name
            for name, pins in PROFILE_PINS.items()
            if (cls.clang, version) == (pins["compiler"], pins["version"])
        ]
        if len(profiles) != 1:
            raise AssertionError(f"unreviewed compiler: {(cls.clang, version)!r}")
        cls.profile = profiles[0]
        cls.pins = PROFILE_PINS[cls.profile]

        temporary_parent = ROOT / "build"
        temporary_parent.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="nanopb-fixed32-production-", dir=temporary_parent
        )
        temporary = Path(cls.temporary.name)
        provider = temporary / "provider.c"
        provider.write_text(HOST_PROVIDER, encoding="utf-8")
        library = temporary / (
            "fixed32.dylib" if sys.platform == "darwin" else "fixed32.so"
        )
        command = [
            cls.clang,
            "-O2",
            "-fPIC",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-I",
            str(SOURCE.parent),
            "-I",
            str(SNAPSHOT),
            "-include",
            str(CONFIG_HEADER),
            str(SOURCE),
            str(provider),
            str(UPSTREAM),
            str(SNAPSHOT / "pb_common.c"),
        ]
        command.extend(
            ["-dynamiclib", "-o", str(library)]
            if sys.platform == "darwin"
            else ["-shared", "-o", str(library)]
        )
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.runners = (
            cls.loaded.open_cfw_test_run_candidate,
            cls.loaded.open_cfw_test_run_upstream,
        )
        for runner in cls.runners:
            runner.argtypes = [
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.c_size_t,
                ctypes.c_size_t,
                ctypes.c_uint32,
                ctypes.c_uint32,
                ctypes.c_uint32,
                ctypes.POINTER(Result),
            ]
            runner.restype = None

        cls.objects = []
        for index in range(2):
            target = temporary / f"target-{index}.o"
            subprocess.run(
                [cls.clang, *TARGET_FLAGS, "-c", str(SOURCE), "-o", str(target)],
                check=True,
                capture_output=True,
                text=True,
            )
            cls.objects.append(target)

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay
        import open_cfw

        cls.apollo_overlay = apollo_overlay
        cls.open_cfw = open_cfw

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def span(cls, start: int, end: int) -> bytes:
        return cls.application[start - APPLICATION_BASE:end - APPLICATION_BASE]

    @staticmethod
    def run_case(
        runner: ctypes._CFuncPtr,
        data: bytes,
        bytes_left: int,
        fail_call: int,
        existing_error: int,
        initial_destination: int,
    ) -> tuple[int, ...]:
        storage = (ctypes.c_uint8 * max(1, len(data)))()
        if data:
            ctypes.memmove(storage, data, len(data))
        result = Result()
        runner(
            storage,
            len(data),
            bytes_left,
            fail_call,
            existing_error,
            initial_destination,
            ctypes.byref(result),
        )
        return result.values()

    def test_source_upstream_and_stock_inputs_are_exact(self) -> None:
        self.assertEqual((SOURCE.stat().st_size, sha256(SOURCE.read_bytes())), SOURCE_PIN)
        self.assertEqual((HEADER.stat().st_size, sha256(HEADER.read_bytes())), HEADER_PIN)
        self.assertEqual((UPSTREAM.stat().st_size, sha256(UPSTREAM.read_bytes())), UPSTREAM_PIN)
        self.assertEqual(
            (CONFIG_HEADER.stat().st_size, sha256(CONFIG_HEADER.read_bytes())),
            CONFIG_PIN,
        )
        definition = UPSTREAM.read_bytes()[slice(*UPSTREAM_DEFINITION)]
        self.assertEqual((len(definition), sha256(definition)), UPSTREAM_DEFINITION_PIN)
        self.assertTrue(definition.startswith(b"bool pb_decode_fixed32("))

        provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        self.assertEqual(
            provenance["upstream"]["selected_commit"],
            "98bf4db69897b53434f3d0ba72e0a3ab1a902824",
        )
        self.assertEqual(
            provenance["selection"]["g2_compatible_pristine_release_range"],
            ["0.4.7", "0.4.8", "0.4.9", "0.4.9.1"],
        )
        self.assertFalse(provenance["selection"]["exact_g2_point_release_proven"])
        self.assertEqual(
            provenance["selection"]["production_decode_fixed32_leaf"],
            {
                "upstream_function": "pb_decode_fixed32",
                "upstream_source": "pb_decode.c",
                "upstream_commit": provenance["upstream"]["selected_commit"],
                "upstream_definition_span": "pb_decode.c bytes [43210,43828)",
                "upstream_definition_size": 618,
                "upstream_definition_sha256": UPSTREAM_DEFINITION_PIN[1],
                "local_source": SOURCE.relative_to(ROOT).as_posix(),
                "local_source_size": SOURCE_PIN[0],
                "local_source_sha256": SOURCE_PIN[1],
                "local_header": HEADER.relative_to(ROOT).as_posix(),
                "local_header_size": HEADER_PIN[0],
                "local_header_sha256": HEADER_PIN[1],
                "stock_span": "[0x00490190,0x004901AC)",
                "stock_size": END - START,
                "stock_sha256": STOCK_SHA256,
                "stock_read_seam": "0x0048F3BE",
                "configuration": "g2-config/pb_g2_options.h",
                "qualification": (
                    "Altered local source selected against authenticated "
                    "nanopb 0.4.9 as a compatibility baseline within the "
                    "authenticated 0.4.7-0.4.9 range; not proof of the vendor "
                    "nanopb revision or checkout. The broader pristine "
                    "pb_common, pb_decode, and pb_encode translation units "
                    "remain unregistered."
                ),
            },
        )

        self.assertEqual(self.span(START, END), STOCK)
        self.assertEqual(sha256(STOCK), STOCK_SHA256)
        self.assertEqual(sha256(self.span(*CALLER_BODY)), CALLER_BODY_SHA256)
        self.assertEqual(sha256(self.span(*READ_BODY)), READ_BODY_SHA256)
        self.assertEqual(sha256(self.span(*PREDECESSOR)), PREDECESSOR_SHA256)
        self.assertEqual(sha256(self.span(*SUCCESSOR)), SUCCESSOR_SHA256)


    def test_authenticated_pristine_upstream_randomized_differential(self) -> None:
        cases = [
            (b"\x01\x02\x03\x04", 4, 0, 0, 0xA5A5A5A5),
            (b"\x01\x02\x03\x04", 3, 0, 0, 0xA5A5A5A5),
            (b"\x01\x02\x03", 4, 0, 0, 0xA5A5A5A5),
            (b"\x01\x02\x03\x04", 4, 1, 1, 0xA5A5A5A5),
        ]
        rng = random.Random(0x490190 ^ 0x0409)
        for _ in range(1_000):
            cases.append((
                rng.randbytes(rng.randrange(9)),
                rng.randrange(9),
                rng.randrange(2),
                rng.randrange(2),
                rng.getrandbits(32),
            ))
        for arguments in cases:
            candidate = self.run_case(self.runners[0], *arguments)
            pristine = self.run_case(self.runners[1], *arguments)
            self.assertEqual(candidate, pristine, arguments)
            if not candidate[0]:
                self.assertEqual(candidate[1], arguments[-1], arguments)

    def test_target_object_text_and_single_call_relocation_are_exact(self) -> None:
        self.assertEqual(
            self.pins["runtime"],
            OVERLAY_RUNTIME_BASE + self.pins["offset"],
        )
        first = self.objects[0].read_bytes()
        second = self.objects[1].read_bytes()
        self.assertEqual(first, second)
        self.assertEqual((len(first), sha256(first)), TARGET_OBJECT_PIN)
        data, sections = self.apollo_overlay.parse_elf32(self.objects[0])
        text = self.apollo_overlay.section_named(sections, SECTION)
        payload = data[text["offset"]:text["offset"] + text["size"]]
        self.assertEqual(payload, TARGET_TEXT)
        self.assertEqual(sha256(payload), TARGET_TEXT_SHA256)
        self.assertEqual(text["alignment"], 4)

        symtab = self.apollo_overlay.section_named(sections, ".symtab")
        strtab = sections[symtab["link"]]
        strings = data[strtab["offset"]:strtab["offset"] + strtab["size"]]
        names = []
        for index in range(symtab["size"] // 16):
            fields = struct.unpack_from(
                "<IIIBBH", data, symtab["offset"] + 16 * index
            )
            names.append(self.apollo_overlay.elf_string(strings, fields[0], "symbol"))
        relocations = []
        for section in sections:
            if section["type"] != 9 or sections[section["info"]]["name"] != SECTION:
                continue
            for index in range(section["size"] // 8):
                offset, information = struct.unpack_from(
                    "<II", data, section["offset"] + 8 * index
                )
                relocations.append(
                    (offset, information & 0xFF, names[information >> 8])
                )
        self.assertEqual(relocations, [(10, 10, "open_cfw_nanopb_read")])

        symbols = self.apollo_overlay.parse_elf32_symbols(data, sections)
        undefined = sorted(
            symbol["name"] for symbol in symbols
            if symbol["name"] and symbol["section_index"] == 0
        )
        self.assertEqual(undefined, ["open_cfw_nanopb_read"])
        allocated = {
            section["name"]: section["size"]
            for section in sections
            if section["size"] and section["flags"] & 2
        }
        self.assertEqual(allocated, {SECTION: 50, ".ARM.exidx" + SECTION: 8})

    def test_call_graph_and_whole_image_ingress_are_closed(self) -> None:
        call = self.span(CALLER, CALLER + 4)
        self.assertEqual(call, bytes.fromhex("00f078fc"))
        first, second = struct.unpack("<HH", call)
        self.assertEqual(
            wide_branch_target(CALLER, first, second, link=True), START
        )
        outgoing = self.span(START + 8, START + 12)
        first, second = struct.unpack("<HH", outgoing)
        self.assertEqual(
            wide_branch_target(START + 8, first, second, link=True), READ_ENTRY
        )

        incoming_bl = []
        incoming_bw = []
        conditional = []
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
            first, second = struct.unpack_from("<HH", self.application, offset)
            if not (START <= address < END):
                for link, owner in ((True, incoming_bl), (False, incoming_bw)):
                    target = wide_branch_target(address, first, second, link=link)
                    if target is not None and START <= target < END:
                        owner.append((address, target))
                target = wide_conditional_target(address, first, second)
                if target is not None and START <= target < END:
                    conditional.append((address, target))

        narrow = []
        for offset in range(0, len(self.application) - 1, 2):
            address = APPLICATION_BASE + offset
            if START <= address < END:
                continue
            halfword = struct.unpack_from("<H", self.application, offset)[0]
            for target in narrow_targets(address, halfword):
                if START <= target < END:
                    narrow.append((address, target))
        self.assertEqual(incoming_bl, [(CALLER, START)])
        self.assertEqual(incoming_bw, [])
        self.assertEqual(conditional, [])
        self.assertEqual(narrow, [])

        stored = []
        for offset in range(len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            if START <= (value & ~1) < END:
                stored.append((APPLICATION_BASE + offset, value))
        self.assertEqual(stored, [])

    def test_production_overlay_patch_manifest_package_and_plan_are_exact(
        self,
    ) -> None:
        config = json.loads(OVERLAY.read_text(encoding="utf-8"))
        self.assertEqual(
            (
                len(config["functions"]),
                len(config["patch_sites"]),
                len(config["relocated_leaves"]),
            ),
            (975, 914, 406),
        )
        self.assertEqual(config["functions"].count(FUNCTION), 1)
        leaves = [
            item
            for item in config["relocated_leaves"]
            if item["function"] == FUNCTION
        ]
        self.assertEqual(len(leaves), 1)
        leaf = leaves[0]
        self.assertTrue(leaf["strict_relocation_contract"])
        self.assertEqual(
            leaf["source"],
            {
                "path": SOURCE.relative_to(ROOT).as_posix(),
                "size": SOURCE_PIN[0],
                "sha256": SOURCE_PIN[1],
                "license": "Zlib",
                "origin": (
                    "altered production adaptation of authenticated nanopb "
                    "0.4.9 pb_decode_fixed32, selected as a compatibility "
                    "baseline for the recovered G2 stream ABI"
                ),
                "upstream": (
                    "https://github.com/nanopb/nanopb/blob/"
                    "98bf4db69897b53434f3d0ba72e0a3ab1a902824/pb_decode.c"
                ),
                "upstream_commit": (
                    "98bf4db69897b53434f3d0ba72e0a3ab1a902824"
                ),
                "evidence": (
                    "docs/research/nanopb-decode-fixed32-source-audit.md"
                ),
            },
        )
        self.assertEqual(
            (leaf["toolchain"]["target"], leaf["toolchain"]["flags"]),
            ("thumbv7em-none-eabi", list(TARGET_FLAGS[1:])),
        )
        relocation = [
            {
                "offset": 10,
                "type": "R_ARM_THM_CALL",
                "symbol": "open_cfw_nanopb_read",
                "symbol_type": "STT_NOTYPE",
                "target_address": READ_ENTRY,
            }
        ]
        for profile, pins in PROFILE_PINS.items():
            expected = (
                leaf["expected"]
                if profile == "apple-clang"
                else leaf["toolchain_profiles"][profile]["expected"]
            )
            self.assertEqual(
                expected,
                {
                    "size": 50,
                    "sha256": pins["relocated"],
                    "alignment": 4,
                    "offset": pins["offset"],
                    "unrelocated_sha256": TARGET_TEXT_SHA256,
                },
            )
            selected_relocations = (
                leaf["relocations"]
                if profile == "apple-clang"
                else leaf["toolchain_profiles"][profile]["relocations"]
            )
            self.assertEqual(selected_relocations, relocation)
            aggregate = (
                config["expected"]
                if profile == "apple-clang"
                else config["toolchain_profiles"][profile]["expected"]
            )
            self.assertEqual(
                (aggregate["overlay_size"], aggregate["overlay_sha256"]),
                pins["overlay"],
            )
            self.assertEqual(
                (aggregate["component_size"], aggregate["component_sha256"]),
                pins["component"],
            )

        patch_config = [
            item
            for item in config["patch_sites"]
            if item.get("target_function") == FUNCTION
        ]
        self.assertEqual(
            patch_config,
            [
                {
                    "name": "replace_nanopb_decode_fixed32",
                    "runtime_address": START,
                    "expected_size": END - START,
                    "expected_sha256": STOCK_SHA256,
                    "branch": "b_w",
                    "target_function": FUNCTION,
                }
            ],
        )

        output = Path(self.temporary.name) / "production-overlay"
        report = self.apollo_overlay.build(
            root=ROOT,
            config_path=OVERLAY,
            output_dir=output,
            clang=self.clang,
            toolchain_profile=self.profile,
        )
        self.assertEqual(
            (report["overlay"]["size"], report["overlay"]["sha256"]),
            self.pins["overlay"],
        )
        self.assertEqual(
            (report["component"]["size"], report["component"]["sha256"]),
            self.pins["component"],
        )
        extracted = next(
            item
            for item in report["relocated_leaves"]
            if item["extraction"]["function"] == FUNCTION
        )
        self.assertEqual(
            extracted["placement"],
            {
                "offset": self.pins["offset"],
                "runtime_address": self.pins["runtime"],
                "runtime_address_hex": f"0x{self.pins['runtime']:08X}",
                "size": 50,
                "alignment": 4,
                "padding_before": 0,
            },
        )
        self.assertEqual(
            extracted["extraction"]["sha256"], self.pins["relocated"]
        )
        self.assertEqual(
            extracted["extraction"]["unrelocated_sha256"],
            TARGET_TEXT_SHA256,
        )
        self.assertEqual(extracted["extraction"]["relocation_count"], 1)
        self.assertEqual(
            extracted["extraction"]["relocations"][0]["target_address"],
            READ_ENTRY,
        )
        patch = next(
            item
            for item in report["overlay"]["patched_sites"]
            if item["name"] == "replace_nanopb_decode_fixed32"
        )
        replacement = bytes.fromhex(patch["replacement_hex"])
        self.assertEqual(len(replacement), END - START)
        first, second = struct.unpack("<HH", replacement[:4])
        self.assertEqual(
            wide_branch_target(START, first, second, link=False),
            self.pins["runtime"],
        )
        self.assertEqual(replacement[4:], bytes.fromhex("00bf") * 12)
        self.assertEqual(
            (replacement.hex(), sha256(replacement)),
            self.pins["patch"],
        )
        component = (output / "ota_s200_firmware_ota.bin").read_bytes()
        patch_offset = PREAMBLE + START - APPLICATION_BASE
        self.assertEqual(
            component[patch_offset:patch_offset + END - START], replacement
        )

        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        main = manifest["component_overrides"]["apollo_main"]
        regions = main["regions"]
        self.assertEqual(len(regions), 1818)
        self.assertEqual(main["source_appended_boundary"], len(self.package))
        for left, right in zip(regions, regions[1:]):
            self.assertEqual(
                left["file_offset"] + left["size"], right["file_offset"]
            )
        self.assertEqual(
            regions[-1]["file_offset"] + regions[-1]["size"],
            main["provider"]["size"],
        )
        status = {}
        for region in regions:
            count, size = status.get(region["address_status"], (0, 0))
            status[region["address_status"]] = (
                count + 1,
                size + region["size"],
            )
        self.assertEqual(status, MANIFEST_STATUS)
        by_name = {region["name"]: region for region in regions}
        split = [
            (
                "nanopb_decode_svarint_source_replacement",
                0x0049_0150,
                START - 0x0049_0150,
                "generated_source_entry_replacement",
            ),
            (
                "nanopb_decode_fixed32_source_replacement",
                START,
                END - START,
                "generated_source_entry_replacement",
            ),
            (
                "nanopb_decode_fixed64_source_replacement",
                END,
                0x0049_01CC - END,
                "generated_source_entry_replacement",
            ),
        ]
        for name, address, size, ownership in split:
            region = by_name[name]
            self.assertEqual(
                (
                    region["target_address"],
                    region["size"],
                    region["address_status"],
                ),
                (address, size, ownership),
            )
        self.assertEqual(
            by_name["apollo_nanopb_decode_fixed32_source_leaf"],
            {
                "name": "apollo_nanopb_decode_fixed32_source_leaf",
                "function": (
                    "Zlib-licensed nanopb fixed32 decode source "
                    "compatibility leaf"
                ),
                "file_offset": 3_647_892,
                "size": 50,
                "target": "apollo510b_internal_mram",
                "target_address": PROFILE_PINS["apple-clang"]["runtime"],
                "address_status": "source_compiled",
                "output": (
                    "apollo510b/main-source-nanopb-decode-fixed32-"
                    "0x007b2974.bin"
                ),
            },
        )
        for profile, pins in PROFILE_PINS.items():
            provider = (
                main["provider"]
                if profile == "apple-clang"
                else main["provider"]["profiles"][profile]
            )
            package = (
                manifest["package"]
                if profile == "apple-clang"
                else manifest["package"]["profiles"][profile]
            )
            self.assertEqual(
                (provider["size"], provider["sha256"]), pins["component"]
            )
            self.assertEqual(
                (package["expected_size"], package["expected_sha256"]),
                pins["package"],
            )

        package_output = Path(self.temporary.name) / "production-package"
        package_report = self.open_cfw.build(
            MANIFEST,
            package_output,
            toolchain_profile=self.profile,
        )
        plan = (package_output / "flash-plan.json").read_bytes()
        self.assertEqual(
            (len(plan), sha256(plan)), self.pins["plan"]
        )
        self.assertEqual(
            (
                package_report["package"]["size"],
                package_report["package"]["sha256"],
            ),
            self.pins["package"],
        )


if __name__ == "__main__":
    unittest.main()
