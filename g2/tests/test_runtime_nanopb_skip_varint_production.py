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
SOURCE = ROOT / "components/shared/nanopb/runtime_nanopb_skip_varint.c"
HEADER = SOURCE.with_suffix(".h")
SOURCE_PATH = SOURCE.relative_to(ROOT).as_posix()
HEADER_PATH = HEADER.relative_to(ROOT).as_posix()
SNAPSHOT = ROOT / "third_party/nanopb"
UPSTREAM = SNAPSHOT / "pb_decode.c"
CONFIG_HEADER = SNAPSHOT / "g2-config/pb_g2_options.h"
PROVENANCE = SNAPSHOT / "PROVENANCE.json"
VERIFIER = SNAPSHOT / "verify_snapshot.py"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"

FUNCTION = "open_cfw_nanopb_skip_varint"
# Stable ABI dependency name. The call remains bound to 0x0048F3BE, whose
# entry now redirects to the separately registered source-owned pb_read leaf.
SEAM = "open_cfw_nanopb_read"
SECTION = ".text." + FUNCTION
START = 0x0048_F628
END = 0x0048_F64C
PB_READ_START = 0x0048_F3BE
PB_READ_END = 0x0048_F454
APPLICATION_BASE = 0x0043_8000
PACKAGE_PREAMBLE = 32
OVERLAY_RUNTIME_ADDRESS = 0x0079_4324

PACKAGE_SIZE = 3_523_396
PACKAGE_SHA256 = (
    "36c5b0e499a68ac2493a497bdab9740f"
    "d3e7027730c26a9094eca47268a27863"
)
APPLICATION_SIZE = 3_523_364
APPLICATION_SHA256 = (
    "19044a72bdfeb04c6b1b104d87da7b98"
    "e13cc18928528d84d999b6bcc0ba9701"
)

STOCK = bytes.fromhex(
    "1cb50400012269462000fff7c4fe002804d09df800000006"
    "f4d401e0002000e0012016bd"
)
STOCK_SHA256 = (
    "fae83b1a62a07bb9c7a3d3f6c398bc1"
    "3433ebe1cd75d01945f83f30e6fcc9c5d"
)
PREDECESSOR = (
    0x0048_F5B8,
    START,
    112,
    "f93d678981f92603982c9afc6c6f9976ca14d1a7a7e0bfc949d3ff73f2791ff2",
)
SUCCESSOR = (
    END,
    0x0048_F66C,
    32,
    "03afe2d60436676fffba342c7b8c9504992fa903d7cba768396fd1de2c6c66cd",
)
PB_READ_SHA256 = (
    "69aecb900c749fd98bd2d05e2229e9a3"
    "d6829bd36f3e393f624e3579a9b4af7f"
)
CALLER = (0x0048_F6B6, "fff7b7ff")
CALLER_ADDRESS_SHA256 = (
    "50928d08fafc23b989efcfa9f52fda5e"
    "a709f3d3f25ade154a3f5a26db7026a1"
)
CALLER_ENCODING_SHA256 = (
    "7ed7519397d8ee8f4521fa23f04205e9"
    "dbd1acb64edfed6355be43407196c50d"
)
CALLER_RECORD_SHA256 = (
    "b2397ecfb2eb9a346838d99fb183dcc9"
    "ab0ec287da915fdbf0d5217bbac88e93"
)
CALLER_SPAN = (
    0x0048_F6A0,
    0x0048_F6EA,
    74,
    "36089daffbbc82abad65d97ae0fd64b58b8ad227ed585aa704611bc30369912d",
)
OUTGOING = (0x0048_F632, "fff7c4fe", PB_READ_START)

UPSTREAM_COMMIT = "98bf4db69897b53434f3d0ba72e0a3ab1a902824"
UPSTREAM_TREE = "2c4c260bcff3f9f7081238d377274dd385d76582"
UPSTREAM_SIZE = 53_845
UPSTREAM_SHA256 = (
    "e980f2a41d9abe37b7e6fb4c9ba1ebf"
    "d68507a6fd2653f8d755e1947a9c84b1a"
)
UPSTREAM_FUNCTION_SIZE = 200
UPSTREAM_FUNCTION_SHA256 = (
    "4c9c2629d6c8bf7e8e986a8cb54413d3"
    "9a804ddb0e848c64aae009d3b10aac62"
)
CONFIG_SIZE = 1_551
CONFIG_SHA256 = (
    "ae758999d239e49e2d5c5bf6de3f4ae"
    "f3aab5cd3c29d8de65c4db301c62899db"
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
EXIDX = bytes.fromhex("0000000001000000")
EXIDX_SHA256 = (
    "01acecb507abfe1a354aa8064f4af5d3"
    "f1acd019e37db3c11c97523b71c76e9d"
)

# Production pins recorded only after independent deterministic Apple/Linux
# source, object, overlay, component, and package builds completed.
LOCAL_PINS: dict[Path, tuple[int, str] | None] = {
    SOURCE: (
        1_925,
        "89e53ebc01a2d28c4a94ac4a38313b8213788a23ed55bf767a9e8a5c6d961225",
    ),
    HEADER: (
        2_401,
        "30a8aea087894af29396746a31bbebfc9195e12ee4d66e79b4b637828eeab103",
    ),
}
PROFILE_PINS: dict[str, dict[str, object]] = {
    "apple-clang": {
        "compiler": "/usr/bin/clang",
        "version": "Apple clang version 21.0.0 (clang-2100.3.30.1)",
        "object": (
            932,
            "651b45c3291a106f6e930129db85af7bbcba416f9ccc260f87b4d5a417eb53d4",
        ),
        "text": (
            36,
            "b0b582b004460df1070500bf204629460122fff7feff18b19df907100029f5d402b0b0bd",
            "7e2f6a8b3dca56e4c2d0499a6d4f12ad97dc4bc7f127ff6f4c31b8d379f0ba3b",
        ),
        "relocation_offset": 18,
        "placement": 124_300,
        "relocated_sha256": "d3a60ee83a801c7f7ae58b45d0a1e7b6d85fd920484f738ea5698b1196897df7",
        "patch": (
            "23f342b900bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf",
            "ec17aa0a8e01050d8b30f737e7ca83d4b8842da1d7d33f6b3b74fa199a4f4519",
        ),
        "overlay": (
            164_536,
            "a437e33ec76c3531ecb2b66d7239229b3a1d905bdc76b00cb564bd05b7ac2546",
        ),
        "component": (
            3_687_932,
            "4fdb5af59a3ae68ce25c2d3255fcc4f4ea0c9a77f2ac89a1d16532496c082c07",
        ),
        "package": (
            4_466_426,
            "cc1642fdf85d2af71ba4c3c40335fe4e8b431eb5f578d501b1b260f43fcdd3f4",
        ),
    },
    "linux-clang": {
        "compiler": "/home/linuxbrew/.linuxbrew/bin/clang",
        "version": "Homebrew clang version 22.1.8",
        "object": (
            932,
            "651b45c3291a106f6e930129db85af7bbcba416f9ccc260f87b4d5a417eb53d4",
        ),
        "text": (
            36,
            "b0b582b004460df1070500bf204629460122fff7feff18b19df907100029f5d402b0b0bd",
            "7e2f6a8b3dca56e4c2d0499a6d4f12ad97dc4bc7f127ff6f4c31b8d379f0ba3b",
        ),
        "relocation_offset": 18,
        "placement": 126_120,
        "relocated_sha256": "09b1b218b4b222b284b44d433b5ae257e70c13b9cab13e7d53ca9168e7bcf27c",
        "patch": (
            "23f3d0bc00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf",
            "f54c433a31f74f74b34709901da696d850b4dd2d0fb743b8166d49256c287303",
        ),
        "overlay": (
            144_266,
            "4c95f20608c70a065b05837415d2d4471fc7eeeb61fa30ce1c1c9f07f717ddb9",
        ),
        "component": (
            3_667_662,
            "686ea217db2837bffd8a190485f0a6f719242e927fba17281c6f54aa066767f6",
        ),
        "package": (
            4_446_156,
            "2cca0fbac8da01ede95a3cecd55dd0706f6dad3a8437605f8a68949cee3c6bc3",
        ),
    },
}

# (region_count, {address_status: (count, total_size)}).
MANIFEST_PIN: tuple[int, dict[str, tuple[int, int]]] | None = (
    1730,
    {
        "container_only": (1, 32),
        "generated_alignment": (181, 364),
        "generated_source_entry_replacement": (841, 118_572),
        "generated_source_exact_load_image": (1, 6),
        "generated_source_exact_replacement": (7, 134),
        "official_blob": (264, 3_404_434),
        "source_compiled": (435, 164_390),
    },
)


def sha256(value: bytes | Path) -> str:
    if isinstance(value, Path):
        value = value.read_bytes()
    return hashlib.sha256(value).hexdigest()


def required_pin(value: object, label: str) -> object:
    if value is None:
        raise AssertionError(
            f"unrecorded production pin {label}; record it only after the "
            "planned integration has an isolated deterministic build"
        )
    return value


def extract_c_function(source: bytes, marker: bytes) -> bytes:
    start = source.index(marker)
    opening = source.index(b"{", start)
    depth = 0
    for index in range(opening, len(source)):
        if source[index:index + 1] == b"{":
            depth += 1
        elif source[index:index + 1] == b"}":
            depth -= 1
            if depth == 0:
                return source[start:index + 1]
    raise AssertionError(f"unterminated function at {marker!r}")


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
        (sign << 24)
        | (i1 << 23)
        | (i2 << 22)
        | (imm10 << 12)
        | (imm11 << 1)
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
        (sign << 20)
        | (((second >> 11) & 1) << 19)
        | (((second >> 13) & 1) << 18)
        | ((first & 0x003F) << 12)
        | ((second & 0x07FF) << 1)
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


def host_source() -> str:
    return r'''
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "components/shared/nanopb/runtime_nanopb_skip_varint.h"
#include "third_party/nanopb/pb_decode.c"

struct open_cfw_test_skip_input {
    const uint8_t *bytes;
    size_t size;
    size_t offset;
    uint32_t calls;
    uint32_t fail_call;
};

struct open_cfw_test_skip_result {
    uint64_t bytes_left;
    uint64_t consumed;
    uint32_t status;
    uint32_t calls;
    uint32_t error;
};

static const char open_cfw_test_skip_preexisting[] = "preexisting";

static bool open_cfw_test_skip_read(
    struct open_cfw_test_skip_input *input,
    uint8_t *buffer,
    size_t count
)
{
    input->calls++;
    if (
        input->calls == input->fail_call ||
        count > input->size - input->offset
    ) {
        return false;
    }
    memcpy(buffer, input->bytes + input->offset, count);
    input->offset += count;
    return true;
}

static bool open_cfw_test_skip_candidate_callback(
    struct open_cfw_nanopb_istream *stream,
    uint8_t *buffer,
    size_t count
)
{
    return open_cfw_test_skip_read(
        (struct open_cfw_test_skip_input *)stream->state,
        buffer,
        count
    );
}

static bool open_cfw_test_skip_upstream_callback(
    pb_istream_t *stream,
    pb_byte_t *buffer,
    size_t count
)
{
    return open_cfw_test_skip_read(
        (struct open_cfw_test_skip_input *)stream->state,
        buffer,
        count
    );
}

static void open_cfw_test_skip_set_error(
    struct open_cfw_nanopb_istream *stream,
    const char *error
)
{
    if (stream->errmsg == (const char *)0) {
        stream->errmsg = error;
    }
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
        open_cfw_test_skip_set_error(stream, "end-of-stream");
        return false;
    }
    if (!stream->callback(stream, buffer, count)) {
        open_cfw_test_skip_set_error(stream, "io error");
        return false;
    }
    if (stream->bytes_left < count) {
        stream->bytes_left = 0U;
    } else {
        stream->bytes_left -= count;
    }
    return true;
}

static uint32_t open_cfw_test_skip_error(const char *error)
{
    if (error == (const char *)0) {
        return 0U;
    }
    if (strcmp(error, "end-of-stream") == 0) {
        return 1U;
    }
    if (strcmp(error, "io error") == 0) {
        return 2U;
    }
    if (strcmp(error, open_cfw_test_skip_preexisting) == 0) {
        return 3U;
    }
    return 0xFFFFU;
}

void open_cfw_test_skip_run_candidate(
    const uint8_t *bytes,
    size_t size,
    size_t bytes_left,
    uint32_t fail_call,
    uint32_t preexisting_error,
    struct open_cfw_test_skip_result *output
)
{
    struct open_cfw_test_skip_input input = {
        bytes, size, 0U, 0U, fail_call
    };
    struct open_cfw_nanopb_istream stream = {
        open_cfw_test_skip_candidate_callback,
        &input,
        bytes_left,
        preexisting_error ? open_cfw_test_skip_preexisting : (const char *)0
    };
    bool status = open_cfw_nanopb_skip_varint(&stream);

    output->bytes_left = stream.bytes_left;
    output->consumed = input.offset;
    output->status = status ? 1U : 0U;
    output->calls = input.calls;
    output->error = open_cfw_test_skip_error(stream.errmsg);
}

void open_cfw_test_skip_run_upstream(
    const uint8_t *bytes,
    size_t size,
    size_t bytes_left,
    uint32_t fail_call,
    uint32_t preexisting_error,
    struct open_cfw_test_skip_result *output
)
{
    struct open_cfw_test_skip_input input = {
        bytes, size, 0U, 0U, fail_call
    };
    pb_istream_t stream = {
        open_cfw_test_skip_upstream_callback,
        &input,
        bytes_left,
        preexisting_error ? open_cfw_test_skip_preexisting : (const char *)0
    };
    bool status = pb_skip_varint(&stream);

    output->bytes_left = stream.bytes_left;
    output->consumed = input.offset;
    output->status = status ? 1U : 0U;
    output->calls = input.calls;
    output->error = open_cfw_test_skip_error(stream.errmsg);
}

size_t open_cfw_test_skip_stream_size(void)
{
    return sizeof(struct open_cfw_nanopb_istream);
}

size_t open_cfw_test_skip_state_offset(void)
{
    return offsetof(struct open_cfw_nanopb_istream, state);
}

size_t open_cfw_test_skip_bytes_left_offset(void)
{
    return offsetof(struct open_cfw_nanopb_istream, bytes_left);
}

size_t open_cfw_test_skip_errmsg_offset(void)
{
    return offsetof(struct open_cfw_nanopb_istream, errmsg);
}
'''


class Stream32(ctypes.Structure):
    _fields_ = [
        ("callback", ctypes.c_uint32),
        ("state", ctypes.c_uint32),
        ("bytes_left", ctypes.c_uint32),
        ("errmsg", ctypes.c_uint32),
    ]


class StreamNative(ctypes.Structure):
    _fields_ = [
        ("callback", ctypes.c_void_p),
        ("state", ctypes.c_void_p),
        ("bytes_left", ctypes.c_size_t),
        ("errmsg", ctypes.c_void_p),
    ]


class HostResult(ctypes.Structure):
    _fields_ = [
        ("bytes_left", ctypes.c_uint64),
        ("consumed", ctypes.c_uint64),
        ("status", ctypes.c_uint32),
        ("calls", ctypes.c_uint32),
        ("error", ctypes.c_uint32),
    ]

    def tuple(self) -> tuple[int, ...]:
        return (
            self.status,
            self.bytes_left,
            self.consumed,
            self.calls,
            self.error,
        )


class NanopbSkipVarintProductionTests(unittest.TestCase):
    maxDiff = None
    temporary: tempfile.TemporaryDirectory[str] | None = None
    products_ready = False

    @classmethod
    def setUpClass(cls) -> None:
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.apollo_overlay = apollo_overlay
        cls.package = OFFICIAL.read_bytes()
        cls.application = cls.package[PACKAGE_PREAMBLE:]

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.temporary is not None:
            cls.temporary.cleanup()

    def require_planned_source(self) -> None:
        missing = [path for path in (SOURCE, HEADER) if not path.is_file()]
        if missing:
            self.skipTest(
                "planned pb_skip_varint source integration has not landed: "
                + ", ".join(path.relative_to(ROOT).as_posix() for path in missing)
            )

    @classmethod
    def prepare_products(cls) -> None:
        if cls.products_ready:
            return

        cls.clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        version = subprocess.run(
            [cls.clang, "--version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()[0]
        matches = [
            name for name, pins in PROFILE_PINS.items()
            if (cls.clang, version) == (pins["compiler"], pins["version"])
        ]
        if len(matches) != 1:
            raise AssertionError(f"unreviewed compiler: {(cls.clang, version)!r}")
        cls.profile = matches[0]
        cls.pins = PROFILE_PINS[cls.profile]

        temporary_parent = ROOT / "build"
        temporary_parent.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="open-cfw-nanopb-skip-varint-production-",
            dir=temporary_parent,
        )
        temporary = Path(cls.temporary.name)
        cls.objects = [temporary / "skip-a.o", temporary / "skip-b.o"]
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

        host = temporary / "skip-varint-host.c"
        host.write_text(host_source(), encoding="utf-8")
        library = temporary / (
            "skip-varint-host.dylib"
            if sys.platform == "darwin"
            else "skip-varint-host.so"
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
            str(CONFIG_HEADER),
            str(SOURCE),
            str(host),
            str(SNAPSHOT / "pb_common.c"),
        ]
        if sys.platform == "darwin":
            command.extend(("-dynamiclib", "-o", str(library)))
        else:
            command.extend(("-shared", "-fPIC", "-o", str(library)))
        subprocess.run(
            command,
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.library = ctypes.CDLL(str(library))
        cls.runners = [
            cls.library.open_cfw_test_skip_run_candidate,
            cls.library.open_cfw_test_skip_run_upstream,
        ]
        for function in cls.runners:
            function.argtypes = [
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.c_size_t,
                ctypes.c_size_t,
                ctypes.c_uint32,
                ctypes.c_uint32,
                ctypes.POINTER(HostResult),
            ]
            function.restype = None
        cls.host_stream_size = cls.library.open_cfw_test_skip_stream_size
        cls.host_stream_size.argtypes = []
        cls.host_stream_size.restype = ctypes.c_size_t
        cls.host_state_offset = cls.library.open_cfw_test_skip_state_offset
        cls.host_state_offset.argtypes = []
        cls.host_state_offset.restype = ctypes.c_size_t
        cls.host_bytes_left_offset = (
            cls.library.open_cfw_test_skip_bytes_left_offset
        )
        cls.host_bytes_left_offset.argtypes = []
        cls.host_bytes_left_offset.restype = ctypes.c_size_t
        cls.host_errmsg_offset = cls.library.open_cfw_test_skip_errmsg_offset
        cls.host_errmsg_offset.argtypes = []
        cls.host_errmsg_offset.restype = ctypes.c_size_t
        cls.products_ready = True

    def span(self, start: int, end: int) -> bytes:
        return self.application[
            start - APPLICATION_BASE:end - APPLICATION_BASE
        ]

    def run_host(
        self,
        function: ctypes._CFuncPtr,
        data: bytes,
        bytes_left: int,
        fail_call: int,
        preexisting_error: int,
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
            ctypes.byref(result),
        )
        return result.tuple()

    def parse_relocations(
        self,
        data: bytes,
        sections: list[dict[str, object]],
    ) -> dict[str, list[tuple[int, int, str]]]:
        parsed: dict[str, list[tuple[int, int, str]]] = {}
        for relocation_section in sections:
            if int(relocation_section["type"]) != 9:
                continue
            target = sections[int(relocation_section["info"])]
            symbol_table = sections[int(relocation_section["link"])]
            string_table = sections[int(symbol_table["link"])]
            strings = data[
                int(string_table["offset"]):
                int(string_table["offset"]) + int(string_table["size"])
            ]
            symbols = []
            for index in range(int(symbol_table["size"]) // 16):
                name_offset = struct.unpack_from(
                    "<I",
                    data,
                    int(symbol_table["offset"]) + index * 16,
                )[0]
                symbols.append(
                    self.apollo_overlay.elf_string(
                        strings,
                        name_offset,
                        "symbol",
                    )
                )
            records = []
            for index in range(int(relocation_section["size"]) // 8):
                offset, information = struct.unpack_from(
                    "<II",
                    data,
                    int(relocation_section["offset"]) + index * 8,
                )
                records.append((
                    offset,
                    information & 0xFF,
                    symbols[information >> 8],
                ))
            parsed[str(target["name"])] = records
        return parsed

    def test_authenticated_upstream_skip_semantics_are_exact(self) -> None:
        upstream = UPSTREAM.read_bytes()
        self.assertEqual(len(upstream), UPSTREAM_SIZE)
        self.assertEqual(sha256(upstream), UPSTREAM_SHA256)
        body = extract_c_function(
            upstream,
            b"bool checkreturn pb_skip_varint(pb_istream_t *stream)\n{",
        )
        self.assertEqual(len(body), UPSTREAM_FUNCTION_SIZE)
        self.assertEqual(sha256(body), UPSTREAM_FUNCTION_SHA256)
        for token in (
            b"pb_byte_t byte;",
            b"if (!pb_read(stream, &byte, 1))",
            b"} while (byte & 0x80);",
            b"return true;",
        ):
            self.assertIn(token, body)
        self.assertNotIn(b"overflow", body)
        self.assertNotIn(b"bitpos", body)

        self.assertEqual(CONFIG_HEADER.stat().st_size, CONFIG_SIZE)
        self.assertEqual(sha256(CONFIG_HEADER), CONFIG_SHA256)
        configuration = CONFIG_HEADER.read_text(encoding="utf-8")
        for token in (
            "callback stream support",
            "runtime error strings",
            "default 16-bit pb_size_t ABI",
            "PB_MAX_REQUIRED_FIELDS 64",
        ):
            self.assertIn(token, configuration)

        provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        self.assertEqual(provenance["license"], "Zlib")
        self.assertEqual(
            provenance["upstream"]["selected_commit"],
            UPSTREAM_COMMIT,
        )
        self.assertEqual(provenance["upstream"]["selected_tree"], UPSTREAM_TREE)
        selection = provenance["selection"]
        self.assertEqual(selection["compatibility_choice"], "nanopb-0.4.9")
        self.assertFalse(selection["exact_g2_point_release_proven"])
        self.assertEqual(
            selection["g2_compatible_pristine_release_range"],
            ["0.4.7", "0.4.8", "0.4.9", "0.4.9.1"],
        )
        verification = subprocess.run(
            [sys.executable, str(VERIFIER)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            verification.returncode,
            0,
            "authenticated nanopb snapshot verifier rejected the current "
            f"integration: {verification.stderr.strip()}",
        )
        self.assertEqual(
            verification.stdout,
            "nanopb 0.4.9 compatibility snapshot verification passed\n",
        )

    def test_stock_body_neighbors_and_pb_read_dependency_are_exact(self) -> None:
        self.assertEqual(len(self.package), PACKAGE_SIZE)
        self.assertEqual(sha256(self.package), PACKAGE_SHA256)
        self.assertEqual(len(self.application), APPLICATION_SIZE)
        self.assertEqual(sha256(self.application), APPLICATION_SHA256)
        stock = self.span(START, END)
        self.assertEqual(len(stock), 36)
        self.assertEqual(stock, STOCK)
        self.assertEqual(sha256(stock), STOCK_SHA256)
        for start, end, size, digest in (PREDECESSOR, SUCCESSOR):
            body = self.span(start, end)
            self.assertEqual(len(body), size)
            self.assertEqual(sha256(body), digest)
        pb_read = self.span(PB_READ_START, PB_READ_END)
        self.assertEqual(len(pb_read), 150)
        self.assertEqual(sha256(pb_read), PB_READ_SHA256)

        outgoing = []
        for address in range(START, END - 3, 2):
            encoded = self.span(address, address + 4)
            first, second = struct.unpack("<HH", encoded)
            for link in (True, False):
                target = thumb_wide_branch_target(
                    address,
                    first,
                    second,
                    link=link,
                )
                if target is not None and not START <= target < END:
                    outgoing.append((address, encoded.hex(), target, link))
        self.assertEqual(outgoing, [(*OUTGOING, True)])

    def test_sole_caller_and_whole_image_ingress_topology_are_exact(self) -> None:
        caller_start, caller_end, caller_size, caller_hash = CALLER_SPAN
        caller = self.span(caller_start, caller_end)
        self.assertEqual(len(caller), caller_size)
        self.assertEqual(sha256(caller), caller_hash)

        first, second = struct.unpack(
            "<HH",
            self.apollo_overlay.encode_thumb_b_w(0x1000, 0x1010),
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
        for relative in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + relative
            first, second = struct.unpack_from("<HH", self.application, relative)
            encoded = self.application[relative:relative + 4]
            for link in (True, False):
                target = thumb_wide_branch_target(
                    address,
                    first,
                    second,
                    link=link,
                )
                if target is None or not START <= target < END:
                    continue
                if target == START:
                    (direct_bl if link else direct_bw).append(
                        (address, encoded.hex())
                    )
                elif not START <= address < END:
                    interior.append((address, target, link, encoded.hex()))
            conditional = wide_conditional_target(address, first, second)
            targets = (
                *((conditional,) if conditional is not None else ()),
                *narrow_targets(address, first),
            )
            for target in targets:
                if START <= target < END and not START <= address < END:
                    conditional_or_narrow.append((address, target, encoded.hex()))

        self.assertEqual(direct_bl, [CALLER])
        self.assertEqual(direct_bw, [])
        self.assertEqual(interior, [])
        self.assertEqual(conditional_or_narrow, [])
        self.assertEqual(
            sha256(b"".join(struct.pack("<I", address) for address, _ in direct_bl)),
            CALLER_ADDRESS_SHA256,
        )
        self.assertEqual(
            sha256(b"".join(bytes.fromhex(encoded) for _, encoded in direct_bl)),
            CALLER_ENCODING_SHA256,
        )
        self.assertEqual(
            sha256(b"".join(
                struct.pack("<I", address) + bytes.fromhex(encoded)
                for address, encoded in direct_bl
            )),
            CALLER_RECORD_SHA256,
        )

        stored = []
        for canonical in range(START, END):
            for value in {canonical, canonical | 1}:
                needle = struct.pack("<I", value)
                position = self.application.find(needle)
                while position >= 0:
                    stored.append((
                        APPLICATION_BASE + position,
                        value,
                        canonical,
                        position % 4,
                    ))
                    position = self.application.find(needle, position + 1)
        self.assertEqual(stored, [])

    def test_planned_source_license_abi_and_semantics_are_pinned(self) -> None:
        self.require_planned_source()
        for path, pin in LOCAL_PINS.items():
            with self.subTest(path=path.relative_to(ROOT)):
                size, digest = required_pin(
                    pin,
                    f"LOCAL_PINS[{path.relative_to(ROOT)}]",
                )
                self.assertEqual(path.stat().st_size, size)
                self.assertEqual(sha256(path), digest)

        source = SOURCE.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        combined = source + header
        for token in (
            "Copyright (c) 2011 Petteri Aimonen",
            "This notice may not be removed or altered",
            "Altered production source",
            UPSTREAM_COMMIT,
            "not proof of the vendor's historical point release",
            "[0x0048F628, 0x0048F64C)",
            FUNCTION,
            SEAM,
            "bytes_left",
            "errmsg",
        ):
            self.assertIn(token, combined)
        for token in (
            "if (!open_cfw_nanopb_read(stream, &byte, 1U))",
            "while ((byte & 0x80U) != 0U)",
            "return false;",
            "return true;",
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
        self.assertNotIn("_candidate", combined)
        self.assertNotIn("varint overflow", source)
        self.assertNotIn("bit_position", source)

        self.assertEqual(ctypes.sizeof(Stream32), 16)
        self.assertEqual(Stream32.callback.offset, 0)
        self.assertEqual(Stream32.state.offset, 4)
        self.assertEqual(Stream32.bytes_left.offset, 8)
        self.assertEqual(Stream32.errmsg.offset, 12)

    def test_randomized_host_equivalence_and_unbounded_continuations(self) -> None:
        self.require_planned_source()
        self.prepare_products()

        self.assertEqual(self.host_stream_size(), ctypes.sizeof(StreamNative))
        self.assertEqual(self.host_state_offset(), StreamNative.state.offset)
        self.assertEqual(
            self.host_bytes_left_offset(),
            StreamNative.bytes_left.offset,
        )
        self.assertEqual(self.host_errmsg_offset(), StreamNative.errmsg.offset)

        cases = [
            (b"", 0, 0, 0),
            (b"\x00", 1, 0, 0),
            (b"\x7f", 1, 0, 0),
            (b"\x80", 1, 0, 0),
            (b"\x80\x00", 2, 0, 0),
            (b"\x80\x80\x00", 3, 2, 0),
            (b"\x80\x80\x00", 3, 3, 0),
            (b"\x80\x80\x00", 3, 4, 0),
            (b"\x80\x80", 8, 0, 0),
            (b"\x80\x80", 2, 0, 1),
        ]
        generator = random.Random(0x48F628)
        for _ in range(1_000):
            size = generator.randrange(0, 513)
            data = bytes(generator.randrange(0, 256) for _ in range(size))
            bytes_left = generator.randrange(0, size + 6)
            fail_call = generator.randrange(0, size + 6)
            preexisting = generator.randrange(0, 2)
            cases.append((data, bytes_left, fail_call, preexisting))

        for case in cases:
            with self.subTest(
                size=len(case[0]),
                bytes_left=case[1],
                fail_call=case[2],
                preexisting=case[3],
            ):
                observed = [self.run_host(function, *case) for function in self.runners]
                self.assertEqual(observed[0], observed[1])

        for length in (1, 2, 7, 10, 127, 1_024, 4_096, 65_536):
            data = b"\x80" * length
            expected = (0, 0, length, length, 1)
            for function in self.runners:
                with self.subTest(long_continuation=length, function=function):
                    self.assertEqual(
                        self.run_host(function, data, length, 0, 0),
                        expected,
                    )

        failure = (b"\x80\x80\x00", 3, 2, 0)
        expected_failure = (0, 2, 1, 2, 2)
        for function in self.runners:
            self.assertEqual(self.run_host(function, *failure), expected_failure)

    def test_strict_objects_have_only_the_intended_dependency(self) -> None:
        self.require_planned_source()
        self.prepare_products()
        object_size, object_hash = required_pin(
            self.pins["object"],
            f"PROFILE_PINS[{self.profile}].object",
        )
        text_size, text_hex, text_hash = required_pin(
            self.pins["text"],
            f"PROFILE_PINS[{self.profile}].text",
        )
        relocation_offset = required_pin(
            self.pins["relocation_offset"],
            f"PROFILE_PINS[{self.profile}].relocation_offset",
        )

        parsed = [
            (*self.apollo_overlay.parse_elf32(path), path)
            for path in self.objects
        ]
        self.assertEqual(self.objects[0].read_bytes(), self.objects[1].read_bytes())
        for data, sections, path in parsed:
            self.assertEqual((path.stat().st_size, sha256(path)), (
                object_size,
                object_hash,
            ))
            sections_by_name = {
                str(section["name"]): section for section in sections
            }
            text = sections_by_name[SECTION]
            body = data[
                int(text["offset"]):int(text["offset"]) + int(text["size"])
            ]
            self.assertEqual((len(body), body.hex(), sha256(body)), (
                text_size,
                text_hex,
                text_hash,
            ))
            self.assertEqual(int(text["alignment"]), 4)
            self.assertEqual(int(text["flags"]) & 7, 6)

            symbols = self.apollo_overlay.parse_elf32_symbols(data, sections)
            symbols_by_name = {
                str(symbol["name"]): symbol
                for symbol in symbols
                if symbol["name"]
            }
            undefined = sorted(
                str(symbol["name"])
                for symbol in symbols
                if symbol["name"] and int(symbol["section_index"]) == 0
            )
            self.assertEqual(undefined, [SEAM])
            symbol = symbols_by_name[FUNCTION]
            self.assertEqual(int(symbol["binding"]), 1)
            self.assertEqual(int(symbol["type"]), 2)
            self.assertEqual(int(symbol["size"]), len(body))
            self.assertEqual(int(symbol["value"]) & ~1, 0)
            self.assertEqual(int(symbol["value"]) & 1, 1)

            relocations = self.parse_relocations(data, sections)
            self.assertEqual(
                relocations.get(SECTION),
                [(relocation_offset, 10, SEAM)],
            )
            self.assertEqual(
                relocations.get(".ARM.exidx" + SECTION),
                [(0, 42, "")],
            )
            self.assertEqual(
                set(relocations),
                {SECTION, ".ARM.exidx" + SECTION},
            )
            exidx = sections_by_name[".ARM.exidx" + SECTION]
            exidx_bytes = data[
                int(exidx["offset"]):
                int(exidx["offset"]) + int(exidx["size"])
            ]
            self.assertEqual(exidx_bytes, EXIDX)
            self.assertEqual(sha256(exidx_bytes), EXIDX_SHA256)

            allocated = {
                str(section["name"]): int(section["size"])
                for section in sections
                if int(section["size"]) and int(section["flags"]) & 2
            }
            self.assertEqual(allocated, {
                SECTION: text_size,
                ".ARM.exidx" + SECTION: len(EXIDX),
            })

    def test_future_overlay_registration_patch_and_artifacts_are_exact(self) -> None:
        config = json.loads(OVERLAY.read_text(encoding="utf-8"))
        leaves = [
            item for item in config["relocated_leaves"]
            if item["function"] == FUNCTION
        ]
        if not leaves:
            self.skipTest(
                "planned pb_skip_varint relocated-leaf registration has not landed"
            )
        self.require_planned_source()
        self.assertEqual(len(leaves), 1)
        self.assertEqual(config["functions"].count(FUNCTION), 1)
        leaf = leaves[0]
        self.assertTrue(leaf["strict_relocation_contract"])
        self.assertEqual(leaf["source"]["path"], SOURCE_PATH)
        source_size, source_hash = required_pin(
            LOCAL_PINS[SOURCE],
            "LOCAL_PINS[SOURCE]",
        )
        self.assertEqual(
            (leaf["source"]["size"], leaf["source"]["sha256"]),
            (source_size, source_hash),
        )
        self.assertEqual(leaf["source"]["license"], "Zlib")
        self.assertEqual(leaf["source"]["upstream_commit"], UPSTREAM_COMMIT)
        self.assertEqual(leaf["toolchain"]["target"], "thumbv7em-none-eabi")
        self.assertEqual(tuple(leaf["toolchain"]["flags"]), TARGET_FLAGS[1:])
        self.assertNotIn("closure", leaf)

        for profile, pins in PROFILE_PINS.items():
            expected = (
                leaf["expected"]
                if profile == "apple-clang"
                else leaf["toolchain_profiles"][profile]["expected"]
            )
            text_size, _text_hex, text_hash = required_pin(
                pins["text"],
                f"PROFILE_PINS[{profile}].text",
            )
            relocation_offset = required_pin(
                pins["relocation_offset"],
                f"PROFILE_PINS[{profile}].relocation_offset",
            )
            placement = required_pin(
                pins["placement"],
                f"PROFILE_PINS[{profile}].placement",
            )
            relocated_hash = required_pin(
                pins["relocated_sha256"],
                f"PROFILE_PINS[{profile}].relocated_sha256",
            )
            relocations = (
                leaf["relocations"]
                if profile == "apple-clang"
                else leaf["toolchain_profiles"][profile]["relocations"]
            )
            self.assertEqual(relocations, [{
                "offset": relocation_offset,
                "type": "R_ARM_THM_CALL",
                "symbol": SEAM,
                "symbol_type": "STT_NOTYPE",
                "target_address": PB_READ_START,
            }])
            self.assertEqual(expected["size"], text_size)
            self.assertEqual(expected["unrelocated_sha256"], text_hash)
            self.assertEqual(expected["sha256"], relocated_hash)
            self.assertEqual(expected["offset"], placement)
            aggregate = (
                config["expected"]
                if profile == "apple-clang"
                else config["toolchain_profiles"][profile]["expected"]
            )
            self.assertEqual(
                (aggregate["overlay_size"], aggregate["overlay_sha256"]),
                required_pin(
                    pins["overlay"],
                    f"PROFILE_PINS[{profile}].overlay",
                ),
            )
            self.assertEqual(
                (aggregate["component_size"], aggregate["component_sha256"]),
                required_pin(
                    pins["component"],
                    f"PROFILE_PINS[{profile}].component",
                ),
            )

        patches = [
            item for item in config["patch_sites"]
            if item.get("target_function") == FUNCTION
        ]
        self.assertEqual(patches, [{
            "name": "replace_nanopb_skip_varint",
            "runtime_address": START,
            "expected_size": END - START,
            "expected_sha256": STOCK_SHA256,
            "branch": "b_w",
            "target_function": FUNCTION,
        }])
        registration_text = OVERLAY.read_text(encoding="utf-8") + MANIFEST.read_text(
            encoding="utf-8"
        )
        self.assertNotIn("runtime_nanopb_skip_varint_candidate", registration_text)
        self.assertNotIn("open_cfw_nanopb_skip_varint_candidate", registration_text)

        self.prepare_products()
        output = Path(self.temporary.name) / "registered-overlay"
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
            item for item in report["relocated_leaves"]
            if item["extraction"]["function"] == FUNCTION
        )
        placement = required_pin(
            self.pins["placement"],
            f"PROFILE_PINS[{self.profile}].placement",
        )
        runtime = OVERLAY_RUNTIME_ADDRESS + placement
        self.assertEqual(extracted["placement"]["offset"], placement)
        self.assertEqual(extracted["placement"]["runtime_address"], runtime)
        self.assertEqual(extracted["extraction"]["relocation_count"], 1)
        self.assertEqual(
            extracted["extraction"]["relocations"][0]["target_address"],
            PB_READ_START,
        )
        self.assertNotIn("rodata", extracted["extraction"])

        patch = next(
            item for item in report["overlay"]["patched_sites"]
            if item["name"] == "replace_nanopb_skip_varint"
        )
        replacement = bytes.fromhex(patch["replacement_hex"])
        patch_hex, patch_hash = required_pin(
            self.pins["patch"],
            f"PROFILE_PINS[{self.profile}].patch",
        )
        self.assertEqual((replacement.hex(), sha256(replacement)), (
            patch_hex,
            patch_hash,
        ))
        self.assertEqual(len(replacement), END - START)
        first, second = struct.unpack("<HH", replacement[:4])
        self.assertEqual(
            thumb_wide_branch_target(START, first, second, link=False),
            runtime,
        )
        self.assertEqual(replacement[4:], b"\x00\xbf" * 16)

        component = (output / "ota_s200_firmware_ota.bin").read_bytes()
        patch_offset = PACKAGE_PREAMBLE + START - APPLICATION_BASE
        self.assertEqual(
            component[patch_offset:patch_offset + len(replacement)],
            replacement,
        )
        successor_patch = next(
            item for item in report["overlay"]["patched_sites"]
            if item["name"] == "replace_nanopb_skip_string"
        )
        successor_replacement = bytes.fromhex(
            successor_patch["replacement_hex"]
        )
        self.assertEqual(successor_patch["runtime_address"], END)
        self.assertEqual(
            component[
                patch_offset + len(replacement):
                patch_offset + len(replacement) + len(successor_replacement)
            ],
            successor_replacement,
        )
        successor_end = (
            patch_offset + len(replacement) + len(successor_replacement)
        )
        decode_tag_patch = next(
            item for item in report["overlay"]["patched_sites"]
            if item["name"] == "replace_nanopb_decode_tag"
        )
        decode_tag_replacement = bytes.fromhex(
            decode_tag_patch["replacement_hex"]
        )
        self.assertEqual(decode_tag_patch["runtime_address"], 0x0048_F66C)
        self.assertEqual(
            component[
                successor_end:successor_end + len(decode_tag_replacement)
            ],
            decode_tag_replacement,
        )

        application = component[PACKAGE_PREAMBLE:]
        direct_bl = []
        direct_bw = []
        interior = []
        conditional_or_narrow = []
        for relative in range(0, len(application) - 3, 2):
            address = APPLICATION_BASE + relative
            first, second = struct.unpack_from("<HH", application, relative)
            for link in (True, False):
                target = thumb_wide_branch_target(
                    address,
                    first,
                    second,
                    link=link,
                )
                if target is None or not START <= target < END:
                    continue
                if target == START:
                    (direct_bl if link else direct_bw).append(address)
                elif not START <= address < END:
                    interior.append((address, target, link))
            conditional = wide_conditional_target(address, first, second)
            targets = (
                *((conditional,) if conditional is not None else ()),
                *narrow_targets(address, first),
            )
            for target in targets:
                if START <= target < END and not START <= address < END:
                    conditional_or_narrow.append((address, target))
        self.assertEqual(direct_bl, [])
        self.assertEqual(direct_bw, [])
        self.assertEqual(interior, [])
        self.assertEqual(conditional_or_narrow, [])

    def test_future_manifest_tiling_ownership_and_artifact_pins_are_exact(
        self,
    ) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        main = manifest["component_overrides"]["apollo_main"]
        regions = main["regions"]
        replacements = [
            item for item in regions
            if item["address_status"] == "generated_source_entry_replacement"
            and item.get("target_address") == START
            and item["size"] == END - START
        ]
        if not replacements:
            self.skipTest(
                "planned pb_skip_varint manifest replacement has not landed"
            )
        self.assertEqual(len(replacements), 1)
        self.assertIn("nanopb_skip_varint", replacements[0]["name"])

        region_count, accounting_pin = required_pin(MANIFEST_PIN, "MANIFEST_PIN")
        self.assertEqual(len(regions), region_count)
        self.assertEqual(regions[0]["file_offset"], 0)
        for left, right in zip(regions, regions[1:]):
            self.assertEqual(
                left["file_offset"] + left["size"],
                right["file_offset"],
            )
        provider = main["provider"]
        self.assertEqual(
            regions[-1]["file_offset"] + regions[-1]["size"],
            provider["size"],
        )
        accounting: dict[str, tuple[int, int]] = {}
        for status in {item["address_status"] for item in regions}:
            selected = [
                item for item in regions if item["address_status"] == status
            ]
            accounting[status] = (
                len(selected),
                sum(item["size"] for item in selected),
            )
        self.assertEqual(accounting, accounting_pin)

        package = manifest["package"]
        for profile, pins in PROFILE_PINS.items():
            selected_provider = (
                provider
                if profile == "apple-clang"
                else provider["profiles"][profile]
            )
            selected_package = (
                package
                if profile == "apple-clang"
                else package["profiles"][profile]
            )
            self.assertEqual(
                (selected_provider["size"], selected_provider["sha256"]),
                required_pin(
                    pins["component"],
                    f"PROFILE_PINS[{profile}].component",
                ),
            )
            self.assertEqual(
                (
                    selected_package["expected_size"],
                    selected_package["expected_sha256"],
                ),
                required_pin(
                    pins["package"],
                    f"PROFILE_PINS[{profile}].package",
                ),
            )

        for region in regions:
            if region["address_status"] != "official_blob":
                continue
            region_start = region.get("target_address")
            if not isinstance(region_start, int):
                continue
            region_end = region_start + region["size"]
            self.assertFalse(
                region_start < END and START < region_end,
                region,
            )

        apple_pins = PROFILE_PINS["apple-clang"]
        placement = required_pin(
            apple_pins["placement"],
            "PROFILE_PINS[apple-clang].placement",
        )
        text_size, _text_hex, _text_hash = required_pin(
            apple_pins["text"],
            "PROFILE_PINS[apple-clang].text",
        )
        runtime = OVERLAY_RUNTIME_ADDRESS + placement
        source_regions = [
            item for item in regions
            if item["address_status"] == "source_compiled"
            and item.get("target_address") == runtime
            and item["size"] == text_size
        ]
        self.assertEqual(len(source_regions), 1)
        self.assertIn("nanopb_skip_varint", source_regions[0]["name"])


if __name__ == "__main__":
    unittest.main()
