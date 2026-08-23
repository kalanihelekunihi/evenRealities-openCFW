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


ROOT = Path(__file__).resolve().parent.parent
SOURCE = (
    ROOT
    / "components/shared/nanopb/runtime_nanopb_close_string_substream.c"
)
HEADER = SOURCE.with_suffix(".h")
SNAPSHOT = ROOT / "third_party/nanopb"
UPSTREAM = SNAPSHOT / "pb_decode.c"
CONFIG_HEADER = SNAPSHOT / "g2-config/pb_g2_options.h"
OFFICIAL = (
    ROOT
    / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
)
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"

FUNCTION = "open_cfw_nanopb_close_string_substream"
SECTION = ".text." + FUNCTION
APPLICATION_BASE = 0x0043_8000
PREAMBLE = 32
START = 0x0048_F7CA
END = 0x0048_F7F4
READ_ENTRY = 0x0048_F3BE
OVERLAY_RUNTIME_BASE = 0x0079_4324

SOURCE_SIZE = 2_061
SOURCE_SHA256 = (
    "736e7ec228f9282ba5b093fd482441e6"
    "e2017fff860d989dc3aadb2bdeff0fcb"
)
HEADER_SIZE = 2_537
HEADER_SHA256 = (
    "851af370162d79f4bd0be8b8bb9a573"
    "1d47cf02527078b9e278019340f2d65d4"
)
UPSTREAM_DEFINITION = (11_223, 11_568)
UPSTREAM_DEFINITION_SHA256 = (
    "527e5ca208a04366c0911baf793af7dc"
    "7045fd73014eefc6e31ce3a8b6dc332f"
)
ORACLE_CLOSURE = {
    SNAPSHOT / "pb.h": (
        44_072,
        "8cceb4abf46bc1df7f2e7ccb9ab87f84"
        "e509f9bfa5733f5ce1f70e7dbc82d18f",
    ),
    SNAPSHOT / "pb_common.h": (
        1_677,
        "6495a691aca68d6973f2274b5dd54b74"
        "fbb57f6b019c45fff255a857fe1abcfd",
    ),
    SNAPSHOT / "pb_common.c": (
        12_141,
        "8d2ec28baaaf2b7a5e90e4cb2fa9700"
        "d21cef7f826f051a637c30b7a1e6a0516",
    ),
    SNAPSHOT / "pb_decode.h": (
        7_870,
        "1747746e5961de5789bcf0795588da079"
        "0cd18b2e4e706ad9c7099a0fa1cc83f",
    ),
    UPSTREAM: (
        53_845,
        "e980f2a41d9abe37b7e6fb4c9ba1ebf"
        "d68507a6fd2653f8d755e1947a9c84b1a",
    ),
    CONFIG_HEADER: (
        1_551,
        "ae758999d239e49e2d5c5bf6de3f4ae"
        "f3aab5cd3c29d8de65c4db301c62899db",
    ),
}
STOCK_BYTES = bytes.fromhex(
    "38b504000d00a868002808d0aa6800212800fff7effd002801d1002004e0"
    "68686060e868e060012032bd"
)
STOCK_SHA256 = (
    "439bbeecb6a0b8266dc3dcd913e98793"
    "352b6b346a7a58cdd44322c734621818"
)
READ_BYTES = bytes.fromhex("fff7effd")
CALLERS = {
    0x0048_FA30: bytes.fromhex("fff7cbfe"),
    0x0048_FBA2: bytes.fromhex("fff712fe"),
    0x0049_0524: bytes.fromhex("fff751f9"),
}
CALLER_BODIES = {
    (0x0048_F968, 0x0048_FB1C): (
        "58eeda598e1b8e418e41323c1749fa1c"
        "d7270a38afb93f0e092bec2a8cfa19f1"
    ),
    (0x0048_FB30, 0x0048_FBE4): (
        "8e278f306b51ccd2cabc176f7674d176"
        "65ca0647facb310c2fe99cfd00a62379"
    ),
    (0x0049_048C, 0x0049_0538): (
        "3e28ac2fb953613cff7b8a7c30cfdc91"
        "aa6c585ea44769e7f64603be853f6f91"
    ),
}
NEIGHBORS = {
    (0x0048_F77E, START): (
        "db925e0c532bac2f2e38f398c7b7d996"
        "69afe4d41e6690b08116e9f06ec7d88d"
    ),
    (END, 0x0048_F968): (
        "2b1bf389327c0f6ccde636bbb51e36cd"
        "0bab3eccc811db9aa0efd3dbfef9e445"
    ),
    (READ_ENTRY, 0x0048_F454): (
        "69aecb900c749fd98bd2d05e2229e9a3"
        "d6829bd36f3e393f624e3579a9b4af7f"
    ),
}

TARGET_TEXT = bytes.fromhex(
    "70b58a680c4605462ab1204600210026fff7feff20b16068e16801266860"
    "e960304670bd"
)
TARGET_TEXT_SHA256 = (
    "5e6ee5f441e5ba91e0e0147b8453a31"
    "186f3ce4bd0efc114edda60f00093a51e"
)
TARGET_OBJECT_SIZE = 968
TARGET_OBJECT_SHA256 = (
    "864cf56e2148b53a0938de80a05e25a"
    "81951adbb8ca147a0ddf6297968c126fc"
)
TARGET_FLAGS = [
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
]

PROFILE_PINS = {
    "apple-clang": {
        "compiler": "/usr/bin/clang",
        "version": "Apple clang version 21.0.0 (clang-2100.3.30.1)",
        "offset": 124_444,
        "runtime": 0x007B_2940,
        "relocated": (
            "c838be0dfb478fe7fa03d9d71069a200"
            "a6477eb5783b631d7d977cd501475438"
        ),
        "overlay": (
            165_412,
            "91449e27a73806e1537548657bed4486d77b275e4ee8a58b2bb1ef527c252ada",
        ),
        "component": (
            3_688_808,
            "9b2424332183f3415b0e2a745e22c7f1b9b0721fcfeaed074272de67d760068c",
        ),
        "package": (
            4_467_302,
            "88e7242268d2a5472e4c96e740dff637214940b5aa88f043bac29500eeb63d3f",
        ),
        "patch": (
            "23f3b9b8" + "00bf" * 19,
            "1b395a30b511a1732cec3791c0c0e1306"
            "eac8b3a5c9fb2c1ce3f92e6eaca2255",
        ),
        "plan": (
            1_287_172,
            "4d99c79858788bd41db79d4846d68186f1d0dac386e0e2f45a27f4f4c8eff161",
            (1807, 2, 5),
        ),
    },
    "linux-clang": {
        "compiler": "/home/linuxbrew/.linuxbrew/bin/clang",
        "version": "Homebrew clang version 22.1.8",
        "offset": 126_264,
        "runtime": 0x007B_305C,
        "relocated": (
            "a90a09f0f98c5b4cf7d885af34c914a"
            "e5d492ac7352b5e359ba68ad482cb3044"
        ),
        "overlay": (
            145_180,
            "afbcb57a8414e65a18c6c95396a0f32fe454cb2087e6a03d51717196a4854b57",
        ),
        "component": (
            3_668_576,
            "292f55478951dc8d41a8bc5e4cc01f80ae88f9c44350d8fec89958c939a4fac5",
        ),
        "package": (
            4_447_070,
            "be5c62a97b9d31f4df257615c28ce81d79ab186feadb68262f96ac5bc35a1c25",
        ),
        "patch": (
            "23f347bc" + "00bf" * 19,
            "bcffd3e5e32492e5c32143eac31bec47"
            "f2fabb91c8411a274eebd29e99f203f3",
        ),
        "plan": (
            640_188,
            "4480ca9a4a4f237a477ccccdc9cb039f071fb2f6547298595e98a91098302a20",
            (896, 2, 5),
        ),
    },
}

MANIFEST_STATUS = {
    "container_only": (1, 32),
    "generated_alignment": (185, 372),
    "generated_source_entry_replacement": (845, 119_096),
    "generated_source_exact_load_image": (1, 6),
    "generated_source_exact_replacement": (7, 134),
    "official_blob": (265, 3_403_910),
    "source_compiled": (441, 165_258),
}

HOST_PROVIDER = r"""
#include <string.h>

#include "runtime_nanopb_close_string_substream.h"
#include "pb_decode.h"

static bool open_cfw_test_result;
static bool open_cfw_test_differential_mode;
static size_t open_cfw_test_calls;
static uint8_t *open_cfw_test_buffer;
static size_t open_cfw_test_count;
static void *open_cfw_test_state;
static const char *open_cfw_test_errmsg;
static size_t open_cfw_test_bytes_left;

void open_cfw_test_configure(
    bool result,
    void *state,
    const char *errmsg,
    size_t bytes_left
)
{
    open_cfw_test_result = result;
    open_cfw_test_differential_mode = false;
    open_cfw_test_calls = 0U;
    open_cfw_test_buffer = (uint8_t *)1;
    open_cfw_test_count = 0U;
    open_cfw_test_state = state;
    open_cfw_test_errmsg = errmsg;
    open_cfw_test_bytes_left = bytes_left;
}

bool open_cfw_nanopb_read(
    struct open_cfw_nanopb_istream *stream,
    uint8_t *buffer,
    size_t count
)
{
    if (open_cfw_test_differential_mode) {
        if (count == 0U) {
            return true;
        }
        if (buffer == NULL) {
            uint8_t temporary[16];
            while (count > sizeof(temporary)) {
                if (!open_cfw_nanopb_read(
                        stream, temporary, sizeof(temporary)
                    )) {
                    return false;
                }
                count -= sizeof(temporary);
            }
            return open_cfw_nanopb_read(stream, temporary, count);
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
        if (stream->bytes_left < count) {
            stream->bytes_left = 0U;
        } else {
            stream->bytes_left -= count;
        }
        return true;
    }

    open_cfw_test_calls++;
    open_cfw_test_buffer = buffer;
    open_cfw_test_count = count;
    stream->state = open_cfw_test_state;
    stream->errmsg = open_cfw_test_errmsg;
    stream->bytes_left = open_cfw_test_bytes_left;
    return open_cfw_test_result;
}

size_t open_cfw_test_calls_get(void) { return open_cfw_test_calls; }
uint8_t *open_cfw_test_buffer_get(void) { return open_cfw_test_buffer; }
size_t open_cfw_test_count_get(void) { return open_cfw_test_count; }

struct open_cfw_test_input {
    const uint8_t *bytes;
    size_t size;
    size_t offset;
    uint32_t calls;
    uint32_t fail_call;
};

struct open_cfw_test_differential_result {
    uint64_t parent_bytes_left;
    uint64_t child_bytes_left;
    uint64_t consumed;
    uint32_t status;
    uint32_t calls;
    uint32_t parent_state_synced;
    uint32_t parent_error;
    uint32_t child_error;
};

static const char open_cfw_test_parent_error[] = "parent-preexisting";
static const char open_cfw_test_child_error[] = "child-preexisting";

static bool open_cfw_test_input_read(
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
    return open_cfw_test_input_read(
        (struct open_cfw_test_input *)stream->state,
        buffer,
        count
    );
}

static bool open_cfw_test_upstream_callback(
    pb_istream_t *stream,
    pb_byte_t *buffer,
    size_t count
)
{
    return open_cfw_test_input_read(
        (struct open_cfw_test_input *)stream->state,
        buffer,
        count
    );
}

static uint32_t open_cfw_test_error_code(const char *error)
{
    if (error == NULL) {
        return 0U;
    }
    if (strcmp(error, "end-of-stream") == 0) {
        return 1U;
    }
    if (strcmp(error, "io error") == 0) {
        return 2U;
    }
    if (error == open_cfw_test_parent_error) {
        return 3U;
    }
    if (error == open_cfw_test_child_error) {
        return 4U;
    }
    return UINT32_MAX;
}

static void open_cfw_test_store_result(
    bool status,
    const void *parent_state,
    size_t parent_bytes_left,
    const char *parent_error,
    const void *child_state,
    size_t child_bytes_left,
    const char *child_error,
    const struct open_cfw_test_input *child_input,
    struct open_cfw_test_differential_result *result
)
{
    result->parent_bytes_left = parent_bytes_left;
    result->child_bytes_left = child_bytes_left;
    result->consumed = child_input->offset;
    result->status = status ? 1U : 0U;
    result->calls = child_input->calls;
    result->parent_state_synced = parent_state == child_state ? 1U : 0U;
    result->parent_error = open_cfw_test_error_code(parent_error);
    result->child_error = open_cfw_test_error_code(child_error);
}

void open_cfw_test_run_candidate(
    const uint8_t *bytes,
    size_t size,
    size_t parent_bytes_left,
    size_t child_bytes_left,
    uint32_t fail_call,
    uint32_t parent_has_error,
    uint32_t child_has_error,
    struct open_cfw_test_differential_result *result
)
{
    struct open_cfw_test_input parent_input = {
        bytes, size, 0U, 0U, 0U
    };
    struct open_cfw_test_input child_input = {
        bytes, size, 0U, 0U, fail_call
    };
    struct open_cfw_nanopb_istream parent = {
        open_cfw_test_candidate_callback,
        &parent_input,
        parent_bytes_left,
        parent_has_error ? open_cfw_test_parent_error : NULL
    };
    struct open_cfw_nanopb_istream child = {
        open_cfw_test_candidate_callback,
        &child_input,
        child_bytes_left,
        child_has_error ? open_cfw_test_child_error : NULL
    };
    bool status;

    open_cfw_test_differential_mode = true;
    status = open_cfw_nanopb_close_string_substream(&parent, &child);
    open_cfw_test_store_result(
        status,
        parent.state,
        parent.bytes_left,
        parent.errmsg,
        child.state,
        child.bytes_left,
        child.errmsg,
        &child_input,
        result
    );
}

void open_cfw_test_run_upstream(
    const uint8_t *bytes,
    size_t size,
    size_t parent_bytes_left,
    size_t child_bytes_left,
    uint32_t fail_call,
    uint32_t parent_has_error,
    uint32_t child_has_error,
    struct open_cfw_test_differential_result *result
)
{
    struct open_cfw_test_input parent_input = {
        bytes, size, 0U, 0U, 0U
    };
    struct open_cfw_test_input child_input = {
        bytes, size, 0U, 0U, fail_call
    };
    pb_istream_t parent = {
        open_cfw_test_upstream_callback,
        &parent_input,
        parent_bytes_left,
        parent_has_error ? open_cfw_test_parent_error : NULL
    };
    pb_istream_t child = {
        open_cfw_test_upstream_callback,
        &child_input,
        child_bytes_left,
        child_has_error ? open_cfw_test_child_error : NULL
    };
    bool status = pb_close_string_substream(&parent, &child);

    open_cfw_test_store_result(
        status,
        parent.state,
        parent.bytes_left,
        parent.errmsg,
        child.state,
        child.bytes_left,
        child.errmsg,
        &child_input,
        result
    );
}
"""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def wide_branch_target(
    address: int,
    first: int,
    second: int,
    *,
    link: bool,
) -> int | None:
    expected = 0xD000 if link else 0x9000
    if first & 0xF800 != 0xF000 or second & 0xD000 != expected:
        return None
    sign = (first >> 10) & 1
    imm10 = first & 0x03FF
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    i1 = 1 ^ (j1 ^ sign)
    i2 = 1 ^ (j2 ^ sign)
    immediate = (
        (sign << 24)
        | (i1 << 23)
        | (i2 << 22)
        | (imm10 << 12)
        | ((second & 0x07FF) << 1)
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


class Stream(ctypes.Structure):
    _fields_ = [
        ("callback", ctypes.c_void_p),
        ("state", ctypes.c_void_p),
        ("bytes_left", ctypes.c_size_t),
        ("errmsg", ctypes.c_void_p),
    ]


class DifferentialResult(ctypes.Structure):
    _fields_ = [
        ("parent_bytes_left", ctypes.c_uint64),
        ("child_bytes_left", ctypes.c_uint64),
        ("consumed", ctypes.c_uint64),
        ("status", ctypes.c_uint32),
        ("calls", ctypes.c_uint32),
        ("parent_state_synced", ctypes.c_uint32),
        ("parent_error", ctypes.c_uint32),
        ("child_error", ctypes.c_uint32),
    ]

    def values(self) -> tuple[int, ...]:
        return (
            self.status,
            self.parent_bytes_left,
            self.child_bytes_left,
            self.consumed,
            self.calls,
            self.parent_state_synced,
            self.parent_error,
            self.child_error,
        )


class NanopbCloseStringSubstreamProductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        for path, expected in ORACLE_CLOSURE.items():
            payload = path.read_bytes()
            actual = (len(payload), sha256(payload))
            if actual != expected:
                raise AssertionError(
                    f"unauthenticated differential oracle file: "
                    f"{path.relative_to(ROOT)} {actual!r}"
                )
        upstream = UPSTREAM.read_bytes()
        definition = upstream[slice(*UPSTREAM_DEFINITION)]
        if (len(definition), sha256(definition)) != (
            345,
            UPSTREAM_DEFINITION_SHA256,
        ):
            raise AssertionError("unauthenticated upstream function definition")

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
            name for name, pins in PROFILE_PINS.items()
            if (cls.clang, version) == (pins["compiler"], pins["version"])
        ]
        if len(profiles) != 1:
            raise AssertionError(f"unreviewed compiler: {(cls.clang, version)!r}")
        cls.profile = profiles[0]
        cls.pins = PROFILE_PINS[cls.profile]
        temporary_parent = ROOT / "build"
        temporary_parent.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="nanopb-close-string-substream-",
            dir=temporary_parent,
        )
        temporary = Path(cls.temporary.name)

        provider = temporary / "provider.c"
        provider.write_text(HOST_PROVIDER, encoding="utf-8")
        library = temporary / (
            "close.dylib" if sys.platform == "darwin" else "close.so"
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
        cls.close = cls.loaded.open_cfw_nanopb_close_string_substream
        cls.close.argtypes = [ctypes.POINTER(Stream), ctypes.POINTER(Stream)]
        cls.close.restype = ctypes.c_bool
        cls.configure = cls.loaded.open_cfw_test_configure
        cls.configure.argtypes = [
            ctypes.c_bool,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
        ]
        cls.calls = cls.loaded.open_cfw_test_calls_get
        cls.calls.restype = ctypes.c_size_t
        cls.buffer = cls.loaded.open_cfw_test_buffer_get
        cls.buffer.restype = ctypes.c_void_p
        cls.count = cls.loaded.open_cfw_test_count_get
        cls.count.restype = ctypes.c_size_t
        cls.differential_runners = (
            cls.loaded.open_cfw_test_run_candidate,
            cls.loaded.open_cfw_test_run_upstream,
        )
        for runner in cls.differential_runners:
            runner.argtypes = [
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.c_size_t,
                ctypes.c_size_t,
                ctypes.c_size_t,
                ctypes.c_uint32,
                ctypes.c_uint32,
                ctypes.c_uint32,
                ctypes.POINTER(DifferentialResult),
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

    def run_differential(
        self,
        runner: ctypes._CFuncPtr,
        data: bytes,
        parent_bytes_left: int,
        child_bytes_left: int,
        fail_call: int,
        parent_has_error: int,
        child_has_error: int,
    ) -> tuple[int, ...]:
        storage = (ctypes.c_uint8 * max(1, len(data)))()
        if data:
            ctypes.memmove(storage, data, len(data))
        result = DifferentialResult()
        runner(
            storage,
            len(data),
            parent_bytes_left,
            child_bytes_left,
            fail_call,
            parent_has_error,
            child_has_error,
            ctypes.byref(result),
        )
        return result.values()

    def test_source_upstream_and_stock_boundary_are_pinned(self) -> None:
        self.assertEqual((SOURCE.stat().st_size, sha256(SOURCE.read_bytes())),
                         (SOURCE_SIZE, SOURCE_SHA256))
        self.assertEqual((HEADER.stat().st_size, sha256(HEADER.read_bytes())),
                         (HEADER_SIZE, HEADER_SHA256))
        upstream = UPSTREAM.read_bytes()
        for path, expected in ORACLE_CLOSURE.items():
            payload = path.read_bytes()
            self.assertEqual((len(payload), sha256(payload)), expected)
        definition = upstream[slice(*UPSTREAM_DEFINITION)]
        self.assertEqual((len(definition), sha256(definition)),
                         (345, UPSTREAM_DEFINITION_SHA256))
        self.assertTrue(definition.startswith(
            b"bool checkreturn pb_close_string_substream("))
        self.assertEqual(self.span(START, END), STOCK_BYTES)
        self.assertEqual(sha256(STOCK_BYTES), STOCK_SHA256)
        for bounds, digest in NEIGHBORS.items():
            self.assertEqual(sha256(self.span(*bounds)), digest)
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn("substream->bytes_left", source)
        self.assertIn("stream->state = substream->state", source)
        self.assertIn("stream->errmsg = substream->errmsg", source)

    def test_host_semantics_match_zero_success_and_failure_contract(self) -> None:
        rng = random.Random(0x48F7CA)
        for index in range(96):
            remainder = 0 if index % 3 == 0 else rng.randrange(1, 1 << 18)
            succeeds = bool(index & 1)
            parent_callback = 0x10000 + index
            parent_state = 0x20000 + index
            parent_left = 0x30000 + index
            parent_error = 0x40000 + index
            sub_state = 0x50000 + index
            sub_error = 0x60000 + index
            mutated_state = 0x70000 + index
            mutated_error = 0x80000 + index
            mutated_left = rng.randrange(0, remainder + 1) if remainder else 0
            parent = Stream(
                parent_callback, parent_state, parent_left, parent_error
            )
            substream = Stream(
                0x90000 + index, sub_state, remainder, sub_error
            )
            self.configure(
                succeeds, mutated_state, mutated_error, mutated_left
            )
            result = bool(self.close(ctypes.byref(parent), ctypes.byref(substream)))
            if remainder == 0:
                self.assertTrue(result)
                self.assertEqual(self.calls(), 0)
                expected_state, expected_error = sub_state, sub_error
            else:
                self.assertEqual(self.calls(), 1)
                self.assertIsNone(self.buffer())
                self.assertEqual(self.count(), remainder)
                self.assertEqual(result, succeeds)
                if succeeds:
                    expected_state, expected_error = mutated_state, mutated_error
                else:
                    expected_state, expected_error = parent_state, parent_error
            self.assertEqual(parent.callback, parent_callback)
            self.assertEqual(parent.bytes_left, parent_left)
            self.assertEqual(parent.state, expected_state)
            self.assertEqual(parent.errmsg, expected_error)

    def test_authenticated_pristine_upstream_randomized_differential(
        self,
    ) -> None:
        edge_cases = (
            (b"", 9, 0, 0, 1, 0, (1, 9, 0, 0, 0, 1, 0, 0)),
            (
                bytes(range(33)),
                9,
                33,
                0,
                0,
                0,
                (1, 9, 0, 33, 3, 1, 0, 0),
            ),
            (
                bytes(range(33)),
                9,
                33,
                2,
                1,
                0,
                (0, 9, 17, 16, 2, 0, 3, 2),
            ),
            (
                bytes(range(20)),
                9,
                33,
                0,
                0,
                1,
                (0, 9, 17, 16, 2, 0, 0, 4),
            ),
        )
        for case in edge_cases:
            arguments, expected = case[:-1], case[-1]
            for runner in self.differential_runners:
                self.assertEqual(
                    self.run_differential(runner, *arguments),
                    expected,
                )

        rng = random.Random(0x48F7CA ^ 0x0409)
        for _ in range(1_000):
            data = rng.randbytes(rng.randrange(301))
            arguments = (
                data,
                rng.randrange(501),
                rng.randrange(341),
                rng.randrange(25),
                rng.randrange(2),
                rng.randrange(2),
            )
            production = self.run_differential(
                self.differential_runners[0], *arguments
            )
            pristine = self.run_differential(
                self.differential_runners[1], *arguments
            )
            self.assertEqual(production, pristine, arguments)

    def test_callers_callee_and_whole_image_ingress_are_exact(self) -> None:
        self.assertEqual(
            wide_conditional_target(0x1000, 0xF000, 0x8000),
            0x1004,
        )
        self.assertIsNone(wide_conditional_target(0x1000, 0xF380, 0x8000))
        self.assertIsNone(wide_conditional_target(0x1000, 0xF000, 0x9000))
        self.assertEqual(self.span(START + 0x12, START + 0x16), READ_BYTES)
        first, second = struct.unpack("<HH", READ_BYTES)
        self.assertEqual(
            wide_branch_target(START + 0x12, first, second, link=True),
            READ_ENTRY,
        )
        for address, encoding in CALLERS.items():
            self.assertEqual(self.span(address, address + 4), encoding)
        for bounds, digest in CALLER_BODIES.items():
            self.assertEqual(sha256(self.span(*bounds)), digest)

        incoming_bl = []
        incoming_bw = []
        wide_conditional_entry = []
        wide_conditional_interior = []
        narrow = []
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
            first, second = struct.unpack_from("<HH", self.application, offset)
            for link, owner in ((True, incoming_bl), (False, incoming_bw)):
                target = wide_branch_target(address, first, second, link=link)
                if target is not None and START <= target < END:
                    owner.append((address, target))
            conditional = wide_conditional_target(address, first, second)
            if (
                conditional is not None
                and START <= conditional < END
                and not (START <= address < END)
            ):
                owner = (
                    wide_conditional_entry
                    if conditional == START
                    else wide_conditional_interior
                )
                owner.append((address, conditional))

        for offset in range(0, len(self.application) - 1, 2):
            address = APPLICATION_BASE + offset
            halfword = struct.unpack_from("<H", self.application, offset)[0]
            for target in narrow_targets(address, halfword):
                if START <= target < END and not (START <= address < END):
                    narrow.append((address, target))
        self.assertEqual(incoming_bl, [(address, START) for address in CALLERS])
        self.assertEqual(incoming_bw, [])
        self.assertEqual(wide_conditional_entry, [])
        self.assertEqual(wide_conditional_interior, [])
        self.assertEqual(narrow, [])

        stored = []
        for offset in range(len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            canonical = value & ~1
            if START <= canonical < END:
                stored.append((APPLICATION_BASE + offset, value))
        self.assertEqual(stored, [])

    def test_target_object_text_and_relocation_closure_are_exact(self) -> None:
        self.assertEqual(
            self.pins["runtime"],
            OVERLAY_RUNTIME_BASE + self.pins["offset"],
        )
        first = self.objects[0].read_bytes()
        second = self.objects[1].read_bytes()
        self.assertEqual(first, second)
        self.assertEqual((len(first), sha256(first)),
                         (TARGET_OBJECT_SIZE, TARGET_OBJECT_SHA256))
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
            names.append(self.apollo_overlay.elf_string(
                strings, fields[0], "symbol"
            ))
        relocations = []
        for section in sections:
            if section["type"] != 9:
                continue
            target = sections[section["info"]]
            if target["name"] != SECTION:
                continue
            for index in range(section["size"] // 8):
                offset, information = struct.unpack_from(
                    "<II", data, section["offset"] + 8 * index
                )
                relocations.append(
                    (offset, information & 0xFF, names[information >> 8])
                )
        self.assertEqual(relocations, [(16, 10, "open_cfw_nanopb_read")])

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
        self.assertEqual(allocated, {
            SECTION: 36,
            ".ARM.exidx" + SECTION: 8,
        })

    def test_production_registration_patch_manifest_and_package_are_exact(
        self,
    ) -> None:
        config = json.loads(OVERLAY.read_text(encoding="utf-8"))
        self.assertEqual(
            (
                len(config["functions"]),
                len(config["patch_sites"]),
                len(config["relocated_leaves"]),
            ),
            (947, 886, 378),
        )
        self.assertEqual(config["functions"].count(FUNCTION), 1)
        leaves = [
            item for item in config["relocated_leaves"]
            if item["function"] == FUNCTION
        ]
        self.assertEqual(len(leaves), 1)
        leaf = leaves[0]
        self.assertTrue(leaf["strict_relocation_contract"])
        self.assertEqual(leaf["source"], {
            "path": SOURCE.relative_to(ROOT).as_posix(),
            "size": SOURCE_SIZE,
            "sha256": SOURCE_SHA256,
            "license": "Zlib",
            "origin": (
                "altered production adaptation of authenticated nanopb 0.4.9 "
                "pb_close_string_substream, selected as a compatibility "
                "baseline for the recovered G2 stream ABI"
            ),
            "upstream": (
                "https://github.com/nanopb/nanopb/blob/"
                "98bf4db69897b53434f3d0ba72e0a3ab1a902824/pb_decode.c"
            ),
            "upstream_commit": "98bf4db69897b53434f3d0ba72e0a3ab1a902824",
            "evidence": (
                "docs/research/"
                "nanopb-close-string-substream-source-audit.md"
            ),
        })
        self.assertEqual(
            (leaf["toolchain"]["target"], leaf["toolchain"]["flags"]),
            ("thumbv7em-none-eabi", TARGET_FLAGS[1:]),
        )
        relocation = [{
            "offset": 16,
            "type": "R_ARM_THM_CALL",
            "symbol": "open_cfw_nanopb_read",
            "symbol_type": "STT_NOTYPE",
            "target_address": READ_ENTRY,
        }]
        for profile, pins in PROFILE_PINS.items():
            expected = (
                leaf["expected"]
                if profile == "apple-clang"
                else leaf["toolchain_profiles"][profile]["expected"]
            )
            self.assertEqual(expected, {
                "size": 36,
                "sha256": pins["relocated"],
                "alignment": 4,
                "offset": pins["offset"],
                "unrelocated_sha256": TARGET_TEXT_SHA256,
            })
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
            item for item in config["patch_sites"]
            if item.get("target_function") == FUNCTION
        ]
        self.assertEqual(patch_config, [{
            "name": "replace_nanopb_close_string_substream",
            "runtime_address": START,
            "expected_size": END - START,
            "expected_sha256": STOCK_SHA256,
            "branch": "b_w",
            "target_function": FUNCTION,
        }])

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
            item for item in report["relocated_leaves"]
            if item["extraction"]["function"] == FUNCTION
        )
        self.assertEqual(extracted["placement"], {
            "offset": self.pins["offset"],
            "runtime_address": self.pins["runtime"],
            "runtime_address_hex": f"0x{self.pins['runtime']:08X}",
            "size": 36,
            "alignment": 4,
            "padding_before": 0,
        })
        self.assertEqual(
            extracted["extraction"]["sha256"],
            self.pins["relocated"],
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
            item for item in report["overlay"]["patched_sites"]
            if item["name"] == "replace_nanopb_close_string_substream"
        )
        replacement = bytes.fromhex(patch["replacement_hex"])
        self.assertEqual(
            (replacement.hex(), sha256(replacement)),
            self.pins["patch"],
        )
        self.assertEqual(patch["target_address"], self.pins["runtime"])
        component = (output / "ota_s200_firmware_ota.bin").read_bytes()
        patch_offset = PREAMBLE + START - APPLICATION_BASE
        self.assertEqual(
            component[patch_offset:patch_offset + END - START],
            replacement,
        )

        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        main = manifest["component_overrides"]["apollo_main"]
        regions = main["regions"]
        self.assertEqual(len(regions), 1745)
        self.assertEqual(main["source_appended_boundary"], len(self.package))
        for left, right in zip(regions, regions[1:]):
            self.assertEqual(
                left["file_offset"] + left["size"],
                right["file_offset"],
            )
        self.assertEqual(
            regions[-1]["file_offset"] + regions[-1]["size"],
            main["provider"]["size"],
        )
        status = {}
        for region in regions:
            count, size = status.get(region["address_status"], (0, 0))
            status[region["address_status"]] = (count + 1, size + region["size"])
        self.assertEqual(status, MANIFEST_STATUS)
        by_name = {region["name"]: region for region in regions}
        split = [
            (
                "nanopb_skip_string_source_replacement",
                0x0048_F64C,
                0x0048_F66C - 0x0048_F64C,
                "generated_source_entry_replacement",
            ),
            (
                "nanopb_close_string_substream_source_replacement",
                START,
                END - START,
                "generated_source_entry_replacement",
            ),
        ]
        for name, address, size, ownership in split:
            region = by_name[name]
            self.assertEqual(
                (region["target_address"], region["size"], region["address_status"]),
                (address, size, ownership),
            )
        self.assertEqual(by_name["apollo_nanopb_close_string_substream_source_leaf"], {
            "name": "apollo_nanopb_close_string_substream_source_leaf",
            "function": (
                "Zlib-licensed nanopb close-string-substream source "
                "compatibility leaf"
            ),
            "file_offset": 3_647_840,
            "size": 36,
            "target": "apollo510b_internal_mram",
            "target_address": PROFILE_PINS["apple-clang"]["runtime"],
            "address_status": "source_compiled",
            "output": (
                "apollo510b/main-source-nanopb-close-string-substream-"
                "0x007b2940.bin"
            ),
        })
        self.assertEqual(by_name["apollo_littlefs_file_rewind_private_source_leaf"], {
            "name": "apollo_littlefs_file_rewind_private_source_leaf",
            "function": (
                "BSD-3-Clause littlefs v2.10.1 private file-rewind "
                "source compatibility leaf"
            ),
            "file_offset": 3_647_876,
            "size": 16,
            "target": "apollo510b_internal_mram",
            "target_address": 0x007B_2964,
            "address_status": "source_compiled",
            "output": (
                "apollo510b/main-source-littlefs-file-rewind-private-"
                "0x007b2964.bin"
            ),
        })
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
            self.assertEqual((provider["size"], provider["sha256"]), pins["component"])
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
        plan_size, plan_hash, plan_counts = self.pins["plan"]
        self.assertEqual((len(plan), sha256(plan)), (plan_size, plan_hash))
        parsed_plan = json.loads(plan)
        counts = (
            len(parsed_plan["flash_regions"]),
            len(parsed_plan["unresolved_flash_regions"]),
            len(parsed_plan["container_only_regions"]),
        )
        self.assertEqual(counts, plan_counts)
        self.assertEqual(
            (
                package_report["placed_region_count"],
                package_report["unresolved_region_count"],
                len(parsed_plan["container_only_regions"]),
            ),
            plan_counts,
        )
        self.assertEqual(
            (package_report["package"]["size"], package_report["package"]["sha256"]),
            self.pins["package"],
        )


if __name__ == "__main__":
    unittest.main()
