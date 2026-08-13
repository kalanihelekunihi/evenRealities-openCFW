from __future__ import annotations

import copy
import ctypes
import hashlib
import importlib.util
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
    ROOT / "components/shared/nanopb/runtime_nanopb_decode_svarint.c"
)
HEADER = SOURCE.with_suffix(".h")
PRODUCTION_VARINT_SOURCE = (
    ROOT / "components/shared/nanopb/runtime_nanopb_decode_varint.c"
)
PRODUCTION_VARINT_HEADER = PRODUCTION_VARINT_SOURCE.with_suffix(".h")
SNAPSHOT = ROOT / "third_party/nanopb"
UPSTREAM = SNAPSHOT / "pb_decode.c"
UPSTREAM_COMMON = SNAPSHOT / "pb_common.c"
CONFIG = SNAPSHOT / "g2-config/pb_g2_options.h"
PROVENANCE = SNAPSHOT / "PROVENANCE.json"
VERIFIER = SNAPSHOT / "verify_snapshot.py"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BOOTLOADER = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
MAKEFILE = ROOT / "Makefile"
AUDIT = ROOT / "docs/research/nanopb-decode-svarint-source-audit.md"
OVERLAY_TOOL = ROOT / "tools/apollo_overlay.py"

FUNCTION = "open_cfw_nanopb_decode_svarint_candidate"
PRODUCTION_FUNCTION = "open_cfw_nanopb_decode_svarint"
CALLEE = "open_cfw_nanopb_decode_varint"
SECTION = ".text." + PRODUCTION_FUNCTION
SOURCE_PATH = SOURCE.relative_to(ROOT).as_posix()
HEADER_PATH = HEADER.relative_to(ROOT).as_posix()
PATCH_NAME = "replace_nanopb_decode_svarint"

PACKAGE_SIZE = 3_523_396
PACKAGE_SHA256 = (
    "36c5b0e499a68ac2493a497bdab9740f"
    "d3e7027730c26a9094eca47268a27863"
)
PACKAGE_PREAMBLE = 32
APPLICATION_BASE = 0x0043_8000
APPLICATION_SIZE = 3_523_364
APPLICATION_SHA256 = (
    "19044a72bdfeb04c6b1b104d87da7b98"
    "e13cc18928528d84d999b6bcc0ba9701"
)
BOOTLOADER_PIN = (
    148_599,
    "f89a4c4657537cec6bfc572bdb831886"
    "6309b90a5d180c4307680d39824167b5",
)
OVERLAY_RUNTIME_ADDRESS = 0x0079_4324

START = 0x0049_0150
END = 0x0049_0190
STOCK = bytes.fromhex(
    "1cb50c006946fff72ffa002801d1002015e0dde90001c00709d5dde900014908"
    "5fea3000c043c943c4e9000106e0dde9000149085fea3000c4e90001012016bd"
)
STOCK_SHA256 = (
    "80b24be422cf924f3ae1b79669312535d"
    "c0d5a56dd88be8a6b9e4ee5ff064048"
)
PREDECESSOR = (0x0049_012C, START)
PREDECESSOR_SHA256 = (
    "946ebcb7df90360a19f331bbe5c3962d"
    "eade8c0525ce4c3ef2d1698263e94b1e"
)
SUCCESSOR = (END, 0x0049_01AC)
SUCCESSOR_SHA256 = (
    "1ee27599a8ac5b8d2a0cbaac59986fb"
    "49be7b24c348a960a216b8cbbecce5bf3"
)
CALLER = 0x0049_0290
CALL_ENCODING = bytes.fromhex("fff75eff")
CALLER_BODY = (0x0049_01D6, 0x0049_0352)
CALLER_BODY_SHA256 = (
    "ccae20aa7dff8515a5a2b6ad4a05248"
    "a865dfaa8c912fd38c8c5f77c3a6a8e0a"
)
OUTGOING = 0x0049_0156
OUTGOING_ENCODING = bytes.fromhex("fff72ffa")
CALLEE_START = 0x0048_F5B8
CALLEE_END = 0x0048_F628
CALLEE_STOCK_SHA256 = (
    "f93d678981f92603982c9afc6c6f9976"
    "ca14d1a7a7e0bfc949d3ff73f2791ff2"
)

SOURCE_PIN = (
    1_943,
    "f361cafc8813257e16fafb9ee986c88c"
    "632eb2c7edc604dcb02e27ec85a7df4d",
)
HEADER_PIN = (
    1_789,
    "d1ca3c0520784c4837c9570416934c78"
    "84eeeba2eba2a42091cd040d5222e72c",
)
PRODUCTION_VARINT_SOURCE_PIN = (
    2_224,
    "b1de68b98ee043bd07d1e10706166a13b"
    "13693534e382705bbad6866411fbe05",
)
PRODUCTION_VARINT_HEADER_PIN = (
    2_574,
    "73b98e49e6b97a84365b8eae582db2b0"
    "a65242808ce7de3bb22a0be44d6344ce",
)
UPSTREAM_PIN = (
    53_845,
    "e980f2a41d9abe37b7e6fb4c9ba1ebf"
    "d68507a6fd2653f8d755e1947a9c84b1a",
)
UPSTREAM_DEFINITION = (42_912, 43_210)
UPSTREAM_DEFINITION_PIN = (
    298,
    "df1caa71053163bdefaea7d6b19bdc72"
    "f10c63f09430003b88f10fb7dac3ff6e",
)
CONFIG_PIN = (
    1_551,
    "ae758999d239e49e2d5c5bf6de3f4ae"
    "f3aab5cd3c29d8de65c4db301c62899db",
)
PROVENANCE_PIN = (
    107_790,
    "4193c3987cdef108f320fd35c3b351d5"
    "ee56cba7d01b3940bcffb1e0ce7180f2",
)
VERIFIER_PIN = (
    209_808,
    "59bd1152353271dd19cf7ad3166c1bef"
    "239864457d45f93a41a6818dbf9d8e1e",
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
APPLE_CLANG = "/usr/bin/clang"
APPLE_CLANG_VERSION = "Apple clang version 21.0.0 (clang-2100.3.30.1)"
LINUX_CLANG = "/home/linuxbrew/.linuxbrew/bin/clang"
LINUX_CLANG_VERSION = "Homebrew clang version 22.1.8"
LINUX_SOURCE_ROOT = Path("/Users/kalani/Repo/SybilSightABCD/openCFW")
TARGET_OBJECT_PIN = (
    972,
    "ac61ef30926a714ee4338414dcdc0de3"
    "04d50b866f69a3f7c625b12c5d5a8435",
)
TARGET_TEXT = bytes.fromhex(
    "10b582b00c466946fff7feff88b1dde900215fea510c4fea320302f001025242"
    "4ff0000161f1000181ea0c015a402260616002b010bd"
)
TARGET_TEXT_SHA256 = (
    "19e103f83ab8879d36eb1b0513bf5416"
    "01e40bc82e69e0dc252308c0646d1286"
)
TARGET_EXIDX_SHA256 = (
    "01acecb507abfe1a354aa8064f4af5d3"
    "f1acd019e37db3c11c97523b71c76e9d"
)
LINUX_TARGET_OBJECT_PIN = (
    968,
    "866820ef347453a3cbf2feed221eeab0"
    "b571a9b79b6988cc17d2861b1aeaced5",
)
LINUX_TARGET_TEXT = bytes.fromhex(
    "b0b582b00d466946fff7feff78b1dde9002100245fea51014fea320302f00102"
    "524264f1000461405a40c5e9002102b0b0bd"
)
LINUX_TARGET_TEXT_SHA256 = (
    "3617ea95d4a2cbabf3a1abb375e572323"
    "fffcebfa68cb4e19874cb4a831d9662"
)
LINUX_RELOCATED_SHA256 = (
    "63e4707f5fd537094855d38f6b4df857"
    "8b77644c131e180db2e682d32fbc1fab"
)
LINUX_TARGET_ALIGNMENT = 4
LINUX_RUNTIME = 0x007B_323C
LINUX_PLACEMENT = LINUX_RUNTIME - OVERLAY_RUNTIME_ADDRESS
APPLE_PLACEMENT = 124_916
APPLE_RUNTIME = 0x007B_2B18
APPLE_RELOCATED_SHA256 = (
    "1b181a82adbbb72dc6fc09b1b70dd48f"
    "4c0eefdf25a8c4e71701710cb12dae3f"
)
PATCH_SHA256 = (
    "e8c5601b86e9a38362fb292b0a8ba702"
    "50d2ccc3094d0c8c117b1c33f5bf11cc"
)
LINUX_LEAF = {
    "size": len(LINUX_TARGET_TEXT),
    "sha256": LINUX_RELOCATED_SHA256,
    "alignment": LINUX_TARGET_ALIGNMENT,
    "offset": LINUX_PLACEMENT,
    "unrelocated_sha256": LINUX_TARGET_TEXT_SHA256,
}
LINUX_PATCH_PREFIX = "23f374b8"
LINUX_PATCH_SHA256 = (
    "e6bb4ee4baec73757a5f465cf99a32e7"
    "87fb25bd651b2b16e2e76fda4c6d18fd"
)
LINUX_AGGREGATE = {
    "overlay": (
        132_888,
        "7036c0e07a36376e5d98700c922ffeec"
        "7a6826388b75060a2b98b4228a411c61",
    ),
    "component": (
        3_656_284,
        "d5daf89121f44a61b303fa953da78550"
        "edd31e9159cf9b0b397aeb1b5cfef54d",
    ),
    "package": (
        4_434_778,
        "63d5cd1d1cbab2c3ece4a48f96b58a0"
        "cb14a7487917831f4c6d370b40ed41d90",
    ),
}

STAGED_CONSUMER_PINS = {
    MANIFEST: "1e8fd0b48bab1540e541bc8c87f72c2fbf9f8a31a4f55f2b2de1ce3bebd0d0fd",
    PROVENANCE: "4193c3987cdef108f320fd35c3b351d5ee56cba7d01b3940bcffb1e0ce7180f2",
    AUDIT: "b483e5b1915f54e99e8aefd047ece54153aadc6df4af51cdc4ef1cf81cc983d0",
    ROOT / "README.md": "a64e0af804fd79fe4f63d1146134dd97d9876d3d070d8b7d389649c59a466752",
    ROOT / "components/README.md": "377dab7fc580499112bceba87f9602c57550c8f438af1b5c4d1324e5003e2989",
    ROOT / "components/apollo_main/core_overlay/NOTICE.md": "8291aeb9e1a95b4b3b75fced4bfd1fde84fe4a45b1761b306aed21e7337f2b85",
    ROOT / "components/apollo_main/core_overlay/EVIDENCE.md": "c4a70bb1b3a7c513256e52736cca8fef7c34b3881b9aa51c66f7810695a33a4f",
    ROOT / "third_party/nanopb/README.openCFW.md": "f5ec1ac4423566060a685b0ccf4eb923119f927c4013894a94f972cb74f4df3a",
    ROOT / "docs/memory-map.md": "94a51987d887ac944b3ba83b738fc99100f7fc5c0d1a7f7a6c59f67468832552",
    ROOT / "docs/source-coverage.md": "7e13a46a687a97c9d15cd002342c8ca5a65338d90036e4dabf559084ea81c7e6",
    ROOT / "docs/upstream-inventory.md": "ffe9bd2c431db89bcf87421f26f3f054209fb0d67cfbaccfd0f1b2d2224cfeaa",
    ROOT / "docs/linux-reproducible-build.md": "5a349c013c753cf1864dd188b3b38c4c0d5bc02481e98a705c75dab5af9f89b8",
}


HOST_HARNESS = r"""
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "components/shared/nanopb/runtime_nanopb_decode_svarint.h"
#include "pb_decode.h"

struct open_cfw_test_input {
    const uint8_t *bytes;
    size_t size;
    size_t offset;
    uint32_t calls;
    uint32_t fail_call;
};

struct open_cfw_test_result {
    uint64_t value_bits;
    uint64_t bytes_left;
    uint64_t consumed;
    uint32_t status;
    uint32_t calls;
    uint32_t error;
};

static const char open_cfw_test_preexisting[] = "preexisting";

static bool open_cfw_test_read(
    struct open_cfw_test_input *input,
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

bool open_cfw_nanopb_readbyte(
    struct open_cfw_nanopb_istream *stream,
    uint8_t *byte
)
{
    if (stream->bytes_left == 0U) {
        if (stream->errmsg == (const char *)0) {
            stream->errmsg = "end-of-stream";
        }
        return false;
    }
    if (!stream->callback(stream, byte, 1U)) {
        if (stream->errmsg == (const char *)0) {
            stream->errmsg = "io error";
        }
        return false;
    }
    stream->bytes_left--;
    return true;
}

static uint32_t open_cfw_test_error(const char *error)
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
    if (strcmp(error, "varint overflow") == 0) {
        return 3U;
    }
    if (strcmp(error, open_cfw_test_preexisting) == 0) {
        return 4U;
    }
    return 0xFFFFU;
}

static void open_cfw_test_store(
    bool status,
    int64_t value,
    size_t bytes_left,
    const char *error,
    const struct open_cfw_test_input *input,
    struct open_cfw_test_result *output
)
{
    output->value_bits = (uint64_t)value;
    output->bytes_left = bytes_left;
    output->consumed = input->offset;
    output->status = status ? 1U : 0U;
    output->calls = input->calls;
    output->error = open_cfw_test_error(error);
}

void open_cfw_test_run_candidate(
    const uint8_t *bytes,
    size_t size,
    size_t bytes_left,
    uint32_t fail_call,
    uint32_t preexisting_error,
    uint64_t initial_bits,
    struct open_cfw_test_result *output
)
{
    struct open_cfw_test_input input = {
        bytes, size, 0U, 0U, fail_call
    };
    struct open_cfw_nanopb_istream stream = {
        open_cfw_test_candidate_callback,
        &input,
        bytes_left,
        preexisting_error ? open_cfw_test_preexisting : (const char *)0
    };
    int64_t value = (int64_t)initial_bits;
    bool status = open_cfw_nanopb_decode_svarint(&stream, &value);
    open_cfw_test_store(
        status, value, stream.bytes_left, stream.errmsg, &input, output
    );
}

void open_cfw_test_run_upstream(
    const uint8_t *bytes,
    size_t size,
    size_t bytes_left,
    uint32_t fail_call,
    uint32_t preexisting_error,
    uint64_t initial_bits,
    struct open_cfw_test_result *output
)
{
    struct open_cfw_test_input input = {
        bytes, size, 0U, 0U, fail_call
    };
    pb_istream_t stream = {
        open_cfw_test_upstream_callback,
        &input,
        bytes_left,
        preexisting_error ? open_cfw_test_preexisting : (const char *)0
    };
    int64_t value = (int64_t)initial_bits;
    bool status = pb_decode_svarint(&stream, &value);
    open_cfw_test_store(
        status, (int64_t)value, stream.bytes_left, stream.errmsg, &input, output
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


def encode_varint(value: int) -> bytes:
    output = bytearray()
    while value > 0x7F:
        output.append((value & 0x7F) | 0x80)
        value >>= 7
    output.append(value)
    return bytes(output)


class Result(ctypes.Structure):
    _fields_ = [
        ("value_bits", ctypes.c_uint64),
        ("bytes_left", ctypes.c_uint64),
        ("consumed", ctypes.c_uint64),
        ("status", ctypes.c_uint32),
        ("calls", ctypes.c_uint32),
        ("error", ctypes.c_uint32),
    ]

    def values(self) -> tuple[int, ...]:
        return (
            self.status,
            self.value_bits,
            self.bytes_left,
            self.consumed,
            self.calls,
            self.error,
        )


class NanopbDecodeSvarintProductionTests(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.package = OFFICIAL.read_bytes()
        cls.application = cls.package[PACKAGE_PREAMBLE:]
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="openCFW-nanopb-svarint-candidate-"
        )
        cls.output = Path(cls.temporary.name)
        cls.host_compiler = os.environ.get("CC", "clang")
        harness = cls.output / "host.c"
        harness.write_text(HOST_HARNESS, encoding="ascii")
        library = cls.output / "libnanopb_svarint_candidate.dylib"
        result = subprocess.run(
            [
                cls.host_compiler,
                "-std=c11",
                "-O2",
                "-shared",
                "-fPIC",
                "-Wall",
                "-Wextra",
                "-Werror",
                f"-I{ROOT}",
                f"-I{SNAPSHOT}",
                "-include",
                str(CONFIG),
                str(SOURCE),
                str(PRODUCTION_VARINT_SOURCE),
                str(UPSTREAM),
                str(UPSTREAM_COMMON),
                str(harness),
                "-o",
                str(library),
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stdout)
        cls.library = ctypes.CDLL(str(library))
        arguments = [
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.c_size_t,
            ctypes.c_size_t,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint64,
            ctypes.POINTER(Result),
        ]
        for name in ("candidate", "upstream"):
            function = getattr(cls.library, f"open_cfw_test_run_{name}")
            function.argtypes = arguments
            function.restype = None

        specification = importlib.util.spec_from_file_location(
            "open_cfw_svarint_apollo_overlay", OVERLAY_TOOL
        )
        assert specification is not None and specification.loader is not None
        cls.apollo_overlay = importlib.util.module_from_spec(specification)
        sys.modules[specification.name] = cls.apollo_overlay
        specification.loader.exec_module(cls.apollo_overlay)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def span(self, start: int, end: int) -> bytes:
        return self.application[
            start - APPLICATION_BASE : end - APPLICATION_BASE
        ]

    def run_case(
        self,
        name: str,
        payload: bytes,
        *,
        bytes_left: int | None = None,
        fail_call: int = 0,
        preexisting_error: int = 0,
        initial_bits: int = 0xA55A_F00D_DEAD_BEEF,
    ) -> tuple[int, ...]:
        storage = (ctypes.c_uint8 * max(1, len(payload)))()
        if payload:
            storage[: len(payload)] = payload
        output = Result()
        getattr(self.library, f"open_cfw_test_run_{name}")(
            storage,
            len(payload),
            len(payload) if bytes_left is None else bytes_left,
            fail_call,
            preexisting_error,
            initial_bits,
            ctypes.byref(output),
        )
        return output.values()

    def compare_case(self, payload: bytes, **kwargs: int) -> tuple[int, ...]:
        candidate = self.run_case("candidate", payload, **kwargs)
        upstream = self.run_case("upstream", payload, **kwargs)
        self.assertEqual(candidate, upstream)
        return candidate

    def linux_leaf_static_contract(self) -> dict[str, int | str]:
        return {
            "size": len(LINUX_TARGET_TEXT),
            "sha256": LINUX_RELOCATED_SHA256,
            "alignment": LINUX_TARGET_ALIGNMENT,
            "offset": LINUX_RUNTIME - OVERLAY_RUNTIME_ADDRESS,
            "unrelocated_sha256": sha256(LINUX_TARGET_TEXT),
        }

    def assert_linux_leaf_static_record(
        self,
        expected: dict[str, object],
        static_contract: dict[str, int | str],
    ) -> None:
        self.assertEqual(set(expected), set(static_contract))
        self.assertEqual(expected["size"], static_contract["size"])
        self.assertEqual(expected["sha256"], static_contract["sha256"])
        self.assertEqual(
            expected["alignment"], static_contract["alignment"]
        )
        self.assertEqual(expected["offset"], static_contract["offset"])
        self.assertEqual(
            expected["unrelocated_sha256"],
            static_contract["unrelocated_sha256"],
        )

    def test_authenticated_source_baseline_and_candidate_pins(self) -> None:
        for path, pin in (
            (SOURCE, SOURCE_PIN),
            (HEADER, HEADER_PIN),
            (PRODUCTION_VARINT_SOURCE, PRODUCTION_VARINT_SOURCE_PIN),
            (PRODUCTION_VARINT_HEADER, PRODUCTION_VARINT_HEADER_PIN),
            (UPSTREAM, UPSTREAM_PIN),
            (CONFIG, CONFIG_PIN),
            (PROVENANCE, PROVENANCE_PIN),
            (VERIFIER, VERIFIER_PIN),
        ):
            payload = path.read_bytes()
            self.assertEqual((len(payload), sha256(payload)), pin)

        definition = UPSTREAM.read_bytes()[slice(*UPSTREAM_DEFINITION)]
        self.assertEqual(
            (len(definition), sha256(definition)), UPSTREAM_DEFINITION_PIN
        )
        self.assertTrue(
            definition.startswith(b"bool pb_decode_svarint(")
        )
        self.assertIn(b"if (!pb_decode_varint(stream, &value))", definition)
        self.assertIn(b"~(value >> 1)", definition)

        provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        upstream = provenance["upstream"]
        selection = provenance["selection"]
        self.assertEqual(
            upstream["selected_commit"],
            "98bf4db69897b53434f3d0ba72e0a3ab1a902824",
        )
        self.assertEqual(upstream["selected_tag"], "nanopb-0.4.9")
        self.assertFalse(selection["exact_g2_point_release_proven"])
        self.assertEqual(
            selection["g2_compatible_pristine_release_range"],
            ["0.4.7", "0.4.8", "0.4.9", "0.4.9.1"],
        )
        self.assertEqual(provenance["license"], "Zlib")

        source_text = SOURCE.read_text(encoding="utf-8")
        header_text = HEADER.read_text(encoding="utf-8")
        self.assertIn("Altered production source", source_text)
        self.assertIn("0.4.7, 0.4.8, and 0.4.9", source_text)
        self.assertIn("not proof of the vendor's historical", source_text)
        self.assertIn("runtime_nanopb_decode_varint.h", header_text)
        self.assertIn("sizeof(int64_t) == 8U", header_text)

        verifier = subprocess.run(
            [sys.executable, str(VERIFIER)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        self.assertEqual(verifier.returncode, 0, verifier.stdout)
        self.assertIn(
            "nanopb 0.4.9 compatibility snapshot verification passed",
            verifier.stdout,
        )

    def test_stock_boundary_caller_and_only_call_seam_are_exact(self) -> None:
        self.assertEqual(
            (len(self.package), sha256(self.package)),
            (PACKAGE_SIZE, PACKAGE_SHA256),
        )
        self.assertEqual(
            (len(self.application), sha256(self.application)),
            (APPLICATION_SIZE, APPLICATION_SHA256),
        )
        self.assertEqual(self.span(START, END), STOCK)
        self.assertEqual(sha256(STOCK), STOCK_SHA256)
        self.assertEqual(
            sha256(self.span(*PREDECESSOR)), PREDECESSOR_SHA256
        )
        self.assertEqual(sha256(self.span(*SUCCESSOR)), SUCCESSOR_SHA256)
        self.assertEqual(
            sha256(self.span(*CALLER_BODY)), CALLER_BODY_SHA256
        )
        self.assertEqual(
            sha256(self.span(CALLEE_START, CALLEE_END)), CALLEE_STOCK_SHA256
        )

        call = self.span(CALLER, CALLER + 4)
        self.assertEqual(call, CALL_ENCODING)
        first, second = struct.unpack("<HH", call)
        self.assertEqual(
            wide_branch_target(CALLER, first, second, link=True), START
        )
        outgoing = self.span(OUTGOING, OUTGOING + 4)
        self.assertEqual(outgoing, OUTGOING_ENCODING)
        first, second = struct.unpack("<HH", outgoing)
        self.assertEqual(
            wide_branch_target(OUTGOING, first, second, link=True),
            CALLEE_START,
        )

        outgoing_calls = []
        for address in range(START, END - 3, 2):
            first, second = struct.unpack("<HH", self.span(address, address + 4))
            target = wide_branch_target(address, first, second, link=True)
            if target is not None:
                outgoing_calls.append((address, target))
        self.assertEqual(outgoing_calls, [(OUTGOING, CALLEE_START)])

    def test_whole_image_ingress_interior_and_pointer_closure(self) -> None:
        incoming_bl = []
        incoming_bw = []
        incoming_conditional = []
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
            if START <= address < END:
                continue
            first, second = struct.unpack_from("<HH", self.application, offset)
            for link, owner in ((True, incoming_bl), (False, incoming_bw)):
                target = wide_branch_target(address, first, second, link=link)
                if target is not None and START <= target < END:
                    owner.append((address, target))
            target = wide_conditional_target(address, first, second)
            if target is not None and START <= target < END:
                incoming_conditional.append((address, target))

        incoming_narrow = []
        for offset in range(0, len(self.application) - 1, 2):
            address = APPLICATION_BASE + offset
            if START <= address < END:
                continue
            halfword = struct.unpack_from("<H", self.application, offset)[0]
            for target in narrow_targets(address, halfword):
                if START <= target < END:
                    incoming_narrow.append((address, target))

        self.assertEqual(incoming_bl, [(CALLER, START)])
        self.assertEqual(incoming_bw, [])
        self.assertEqual(incoming_conditional, [])
        self.assertEqual(incoming_narrow, [])

        stored = []
        for offset in range(len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            if START <= (value & ~1) < END:
                stored.append((APPLICATION_BASE + offset, value))
        self.assertEqual(stored, [])

        # The predecessor returns through POP {...,pc}; the successor starts
        # with its own PUSH. Neither neighbor falls through into this body.
        self.assertEqual(self.span(START - 2, START), bytes.fromhex("16bd"))
        self.assertEqual(self.span(END, END + 2), bytes.fromhex("1cb5"))

    def test_g2_abi_config_and_source_owned_callee_contract(self) -> None:
        config_text = CONFIG.read_text(encoding="utf-8")
        self.assertIn("requires 64-bit scalar support", config_text)
        self.assertIn("retains callback stream support", config_text)
        self.assertIn("retains runtime error strings", config_text)

        source_text = SOURCE.read_text(encoding="utf-8")
        self.assertNotIn("stream->", source_text)
        self.assertIn(
            "open_cfw_nanopb_decode_varint(stream, &value)", source_text
        )
        self.assertIn("(int64_t)(~(value >> 1U))", source_text)
        self.assertIn("(int64_t)(value >> 1U)", source_text)

        overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
        self.assertEqual(overlay["functions"].count(CALLEE), 1)
        self.assertEqual(overlay["functions"].count(FUNCTION), 0)
        callee_leaves = [
            leaf for leaf in overlay["relocated_leaves"]
            if leaf["function"] == CALLEE
        ]
        self.assertEqual(len(callee_leaves), 1)
        self.assertEqual(
            callee_leaves[0]["source"]["path"],
            PRODUCTION_VARINT_SOURCE.relative_to(ROOT).as_posix(),
        )
        callee_patches = [
            patch for patch in overlay["patch_sites"]
            if patch.get("target_function") == CALLEE
        ]
        self.assertEqual(len(callee_patches), 1)
        self.assertEqual(callee_patches[0]["runtime_address"], CALLEE_START)

    def test_production_runtime_and_overlay_contract_is_exact(self) -> None:
        overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))

        # This is deliberately the first production assertion. Before Task 3,
        # the candidate remains fully compilable and all seven qualification
        # tests run, while this test reports one attributable RED mismatch.
        self.assertEqual(
            (
                len(overlay["functions"]),
                len(overlay["patch_sites"]),
                len(overlay["relocated_leaves"]),
            ),
            (684, 632, 115),
        )

        self.assertEqual(overlay["functions"].count(PRODUCTION_FUNCTION), 1)
        self.assertEqual(overlay["functions"].count(FUNCTION), 0)

        leaves = [
            leaf for leaf in overlay["relocated_leaves"]
            if leaf["function"] == PRODUCTION_FUNCTION
        ]
        self.assertEqual(len(leaves), 1)
        leaf = leaves[0]
        self.assertIs(leaf["strict_relocation_contract"], True)
        self.assertEqual(leaf["source"]["path"], SOURCE_PATH)
        self.assertNotIn("closure", leaf)
        self.assertEqual(leaf["expected"], {
            "size": len(TARGET_TEXT),
            "sha256": APPLE_RELOCATED_SHA256,
            "alignment": 4,
            "offset": APPLE_PLACEMENT,
            "unrelocated_sha256": TARGET_TEXT_SHA256,
        })
        self.assertEqual(
            OVERLAY_RUNTIME_ADDRESS + leaf["expected"]["offset"],
            APPLE_RUNTIME,
        )
        self.assertEqual(leaf["relocations"], [{
            "offset": 8,
            "type": "R_ARM_THM_CALL",
            "symbol": CALLEE,
            "symbol_type": "STT_NOTYPE",
            "target_function": CALLEE,
        }])
        self.assertNotIn("target_address", leaf["relocations"][0])

        patches = [
            patch for patch in overlay["patch_sites"]
            if patch.get("target_function") == PRODUCTION_FUNCTION
            or patch.get("name") == PATCH_NAME
        ]
        self.assertEqual(patches, [{
            "name": PATCH_NAME,
            "runtime_address": START,
            "expected_size": END - START,
            "expected_sha256": STOCK_SHA256,
            "branch": "b_w",
            "target_function": PRODUCTION_FUNCTION,
        }])
        replacement = (
            self.apollo_overlay.encode_thumb_b_w(START, APPLE_RUNTIME)
            + b"\x00\xbf" * 30
        )
        self.assertEqual(len(replacement), END - START)
        self.assertEqual(sha256(replacement), PATCH_SHA256)
        first, second = struct.unpack("<HH", replacement[:4])
        self.assertEqual(
            wide_branch_target(START, first, second, link=False),
            APPLE_RUNTIME,
        )
        self.assertEqual(replacement[4:], b"\x00\xbf" * 30)

        production_text = SOURCE.read_text(encoding="utf-8")
        production_header = HEADER.read_text(encoding="utf-8")
        self.assertNotIn(FUNCTION, production_text + production_header)
        self.assertIn(PRODUCTION_FUNCTION + "(", production_text)
        self.assertIn(PRODUCTION_FUNCTION + "(", production_header)

        bootloader = BOOTLOADER.read_bytes()
        self.assertEqual(
            (len(bootloader), sha256(bootloader)), BOOTLOADER_PIN
        )
        self.assertNotIn(STOCK, bootloader)
        for probe in (STOCK[:8], STOCK[-8:], STOCK[:12], STOCK[-12:]):
            self.assertNotIn(probe, bootloader)

        for path, digest in STAGED_CONSUMER_PINS.items():
            self.assertEqual(sha256(path.read_bytes()), digest, str(path))

    def test_deterministic_apple_target_object_and_relocation_closure(self) -> None:
        if not Path(APPLE_CLANG).is_file():
            self.skipTest("Apple target compiler is unavailable")
        version = subprocess.run(
            [APPLE_CLANG, "--version"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=True,
        ).stdout.splitlines()[0]
        self.assertEqual(version, APPLE_CLANG_VERSION)

        objects = []
        for index in range(2):
            output = self.output / f"candidate-{index}.o"
            result = subprocess.run(
                [
                    APPLE_CLANG,
                    *TARGET_FLAGS,
                    f"-I{SOURCE.parent}",
                    "-c",
                    str(SOURCE),
                    "-o",
                    str(output),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout)
            objects.append(output.read_bytes())
        self.assertEqual(objects[0], objects[1])
        self.assertEqual(
            (len(objects[0]), sha256(objects[0])), TARGET_OBJECT_PIN
        )

        data, sections = self.apollo_overlay.parse_elf32(
            self.output / "candidate-0.o"
        )
        symbols = self.apollo_overlay.parse_elf32_symbols(data, sections)
        function = next(
            symbol for symbol in symbols
            if symbol["name"] == PRODUCTION_FUNCTION
        )
        section = sections[function["section_index"]]
        text = data[section["offset"] : section["offset"] + section["size"]]
        self.assertEqual(section["name"], SECTION)
        self.assertEqual(section["alignment"], 4)
        self.assertEqual(text, TARGET_TEXT)
        self.assertEqual(sha256(text), TARGET_TEXT_SHA256)

        relocation_section = next(
            item for item in sections if item["name"] == ".rel" + SECTION
        )
        relocations = []
        for offset in range(
            relocation_section["offset"],
            relocation_section["offset"] + relocation_section["size"],
            8,
        ):
            relocation_offset, information = struct.unpack_from("<II", data, offset)
            relocations.append(
                (
                    relocation_offset,
                    information & 0xFF,
                    symbols[information >> 8]["name"],
                )
            )
        self.assertEqual(relocations, [(8, 10, CALLEE)])
        undefined = sorted(
            symbol["name"] for symbol in symbols
            if symbol["name"] and symbol["section_index"] == 0
        )
        self.assertEqual(undefined, [CALLEE])
        allocated = {
            item["name"]: item["size"]
            for item in sections if item["size"] and item["flags"] & 2
        }
        self.assertEqual(
            allocated, {SECTION: 54, ".ARM.exidx" + SECTION: 8}
        )
        exidx = next(
            item for item in sections
            if item["name"] == ".ARM.exidx" + SECTION
        )
        exidx_payload = data[
            exidx["offset"] : exidx["offset"] + exidx["size"]
        ]
        self.assertEqual(sha256(exidx_payload), TARGET_EXIDX_SHA256)

    def test_linux_profile_is_recorded_from_the_reviewed_exact_root(self) -> None:
        overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        leaf = next(
            item for item in overlay["relocated_leaves"]
            if item["function"] == PRODUCTION_FUNCTION
        )

        # Task 5 RED: the Apple promotion deliberately left this profile
        # absent until it can be recorded with the reviewed Linux compiler at
        # the exact reviewed source root.  This assertion must fail before the
        # recorder runs rather than accepting inherited Apple leaf bytes.
        self.assertIn("linux-clang", leaf.get("toolchain_profiles", {}))
        linux = leaf["toolchain_profiles"]["linux-clang"]
        self.assertEqual(
            linux["reviewed_version_prefix"], LINUX_CLANG_VERSION
        )
        self.assertEqual(
            overlay["toolchain_profiles"]["linux-clang"][
                "reviewed_source_root"
            ],
            str(LINUX_SOURCE_ROOT),
        )
        self.assertEqual(linux["expected"], LINUX_LEAF)
        self.assertEqual(linux["relocations"], [{
            "offset": 8,
            "type": "R_ARM_THM_CALL",
            "symbol": CALLEE,
            "symbol_type": "STT_NOTYPE",
            "target_function": CALLEE,
        }])
        self.assertNotIn("target_address", linux["relocations"][0])

        aggregate = overlay["toolchain_profiles"]["linux-clang"]["expected"]
        self.assertEqual(
            (aggregate["overlay_size"], aggregate["overlay_sha256"]),
            LINUX_AGGREGATE["overlay"],
        )
        self.assertEqual(
            (aggregate["component_size"], aggregate["component_sha256"]),
            LINUX_AGGREGATE["component"],
        )
        provider = manifest["component_overrides"]["apollo_main"]["provider"]
        self.assertEqual(
            (
                provider["profiles"]["linux-clang"]["size"],
                provider["profiles"]["linux-clang"]["sha256"],
            ),
            LINUX_AGGREGATE["component"],
        )
        package = manifest["package"]["profiles"]["linux-clang"]
        self.assertEqual(
            (package["expected_size"], package["expected_sha256"]),
            LINUX_AGGREGATE["package"],
        )

        replacement = (
            self.apollo_overlay.encode_thumb_b_w(START, LINUX_RUNTIME)
            + b"\x00\xbf" * 30
        )
        self.assertEqual(replacement[:4].hex(), LINUX_PATCH_PREFIX)
        self.assertEqual(sha256(replacement), LINUX_PATCH_SHA256)

    def test_deterministic_linux_target_object_and_relocation_closure(self) -> None:
        if os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") != "linux-clang":
            self.skipTest("exact Linux target-object gate requires linux-clang")
        self.assertEqual(ROOT, LINUX_SOURCE_ROOT)
        clang = os.environ.get("OPENCFW_CLANG", LINUX_CLANG)
        self.assertEqual(clang, LINUX_CLANG)
        version = subprocess.run(
            [clang, "--version"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=True,
        ).stdout.splitlines()[0]
        self.assertEqual(version, LINUX_CLANG_VERSION)

        objects = []
        for index in range(2):
            output = self.output / f"linux-production-{index}.o"
            result = subprocess.run(
                [
                    clang,
                    *TARGET_FLAGS,
                    f"-I{SOURCE.parent}",
                    "-c",
                    str(SOURCE),
                    "-o",
                    str(output),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout)
            objects.append(output.read_bytes())
        self.assertEqual(objects[0], objects[1])
        self.assertEqual(
            (len(objects[0]), sha256(objects[0])), LINUX_TARGET_OBJECT_PIN
        )

        data, sections = self.apollo_overlay.parse_elf32(
            self.output / "linux-production-0.o"
        )
        symbols = self.apollo_overlay.parse_elf32_symbols(data, sections)
        function = next(
            symbol for symbol in symbols
            if symbol["name"] == PRODUCTION_FUNCTION
        )
        section = sections[function["section_index"]]
        text = data[section["offset"] : section["offset"] + section["size"]]
        self.assertEqual(section["name"], SECTION)
        self.assertEqual(section["alignment"], 4)
        self.assertEqual(text, LINUX_TARGET_TEXT)
        self.assertEqual(sha256(text), LINUX_TARGET_TEXT_SHA256)

        relocation_section = next(
            item for item in sections if item["name"] == ".rel" + SECTION
        )
        relocations = []
        for offset in range(
            relocation_section["offset"],
            relocation_section["offset"] + relocation_section["size"],
            8,
        ):
            relocation_offset, information = struct.unpack_from(
                "<II", data, offset
            )
            relocations.append(
                (
                    relocation_offset,
                    information & 0xFF,
                    symbols[information >> 8]["name"],
                )
            )
        self.assertEqual(relocations, [(8, 10, CALLEE)])
        self.assertEqual(
            sorted(
                symbol["name"] for symbol in symbols
                if symbol["name"] and symbol["section_index"] == 0
            ),
            [CALLEE],
        )
        allocated = {
            item["name"]: item["size"]
            for item in sections if item["size"] and item["flags"] & 2
        }
        self.assertEqual(
            allocated, {SECTION: 50, ".ARM.exidx" + SECTION: 8}
        )
        self.assertFalse(
            any(
                item["size"] and item["flags"] & 2 and item["flags"] & 1
                for item in sections
            )
        )
        exidx = next(
            item for item in sections
            if item["name"] == ".ARM.exidx" + SECTION
        )
        exidx_payload = data[
            exidx["offset"] : exidx["offset"] + exidx["size"]
        ]
        self.assertEqual(sha256(exidx_payload), TARGET_EXIDX_SHA256)

    def test_linux_profile_static_record_is_complete(self) -> None:
        overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
        leaf = next(
            item for item in overlay["relocated_leaves"]
            if item["function"] == PRODUCTION_FUNCTION
        )
        expected = self.apollo_overlay.resolve_leaf_profile(
            leaf, "linux-clang"
        )["expected"]
        self.assert_linux_leaf_static_record(
            expected,
            self.linux_leaf_static_contract(),
        )

    def test_broad_differential_against_authenticated_upstream(self) -> None:
        mask = (1 << 64) - 1
        initial = 0xA55A_F00D_DEAD_BEEF
        fixed = [
            0,
            1,
            2,
            3,
            0x7F,
            0x80,
            0x3FFF,
            0x4000,
            0xFFFF_FFFF,
            0x8000_0000_0000_0000,
            0xFFFF_FFFF_FFFF_FFFE,
            0xFFFF_FFFF_FFFF_FFFF,
        ]
        generator = random.Random(0x490150)
        values = fixed + [generator.getrandbits(64) for _ in range(21_000)]
        comparisons = 0
        for raw in values:
            payload = encode_varint(raw)
            result = self.compare_case(payload, initial_bits=initial)
            expected = (~(raw >> 1) & mask) if raw & 1 else raw >> 1
            self.assertEqual(result, (1, expected, 0, len(payload), len(payload), 0))
            comparisons += 1

        for raw in values[:2_048]:
            canonical = encode_varint(raw)
            if len(canonical) >= 10:
                continue
            payload = canonical[:-1] + bytes([canonical[-1] | 0x80, 0])
            result = self.compare_case(payload, initial_bits=initial)
            expected = (~(raw >> 1) & mask) if raw & 1 else raw >> 1
            self.assertEqual(result[0:2], (1, expected))
            comparisons += 1

        systematic = [
            encode_varint(value)
            for value in (0, 1, 127, 128, 16_384, (1 << 63), mask)
        ]
        for payload in systematic:
            for length in range(len(payload)):
                for preexisting in (0, 1):
                    result = self.compare_case(
                        payload[:length],
                        bytes_left=length,
                        preexisting_error=preexisting,
                        initial_bits=initial,
                    )
                    self.assertEqual(result[0], 0)
                    self.assertEqual(result[1], initial)
                    comparisons += 1
            for fail_call in range(1, len(payload) + 1):
                result = self.compare_case(
                    payload,
                    fail_call=fail_call,
                    initial_bits=initial,
                )
                self.assertEqual(result[0], 0)
                self.assertEqual(result[1], initial)
                comparisons += 1

        overflow_forms = (
            bytes([0xFF] * 9 + [0x02]),
            bytes([0x80] * 9 + [0x80]),
            bytes([0xFF] * 10),
        )
        for payload in overflow_forms:
            for preexisting in (0, 1):
                result = self.compare_case(
                    payload,
                    preexisting_error=preexisting,
                    initial_bits=initial,
                )
                self.assertEqual(result[0], 0)
                self.assertEqual(result[1], initial)
                self.assertEqual(result[5], 4 if preexisting else 3)
                comparisons += 1

        for _ in range(4_096):
            size = generator.randrange(0, 13)
            payload = bytes(generator.getrandbits(8) for _ in range(size))
            bytes_left = generator.randrange(0, 14)
            fail_call = generator.randrange(0, 14)
            preexisting = generator.randrange(0, 2)
            self.compare_case(
                payload,
                bytes_left=bytes_left,
                fail_call=fail_call,
                preexisting_error=preexisting,
                initial_bits=generator.getrandbits(64),
            )
            comparisons += 1

        self.assertGreaterEqual(comparisons, 26_000)

    def test_candidate_naming_is_absent_and_production_docs_are_registered(self) -> None:
        for path in (OVERLAY, MANIFEST, MAKEFILE, PROVENANCE):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn(FUNCTION, text)

        self.assertIn(SOURCE_PATH, PROVENANCE.read_text(encoding="utf-8"))
        self.assertIn(HEADER_PATH, PROVENANCE.read_text(encoding="utf-8"))
        self.assertIn(
            "nanopb_decode_svarint_source_replacement",
            MANIFEST.read_text(encoding="utf-8"),
        )
        self.assertNotIn(SOURCE_PATH, MAKEFILE.read_text(encoding="utf-8"))

        self.assertTrue(AUDIT.is_file())
        audit = AUDIT.read_text(encoding="utf-8")
        self.assertIn("production-source audit", audit)
        self.assertIn("951", audit)
        self.assertIn("0.4.7", audit)
        self.assertIn("0.4.9", audit)
        self.assertIn("No firmware was signed or flashed", audit)
        self.assertNotIn("candidate header", audit.lower())

        nanopb_readme = (
            ROOT / "third_party/nanopb/README.openCFW.md"
        ).read_text(encoding="utf-8")
        production_boundary = nanopb_readme.split(
            "## Production boundary", 1
        )[1].split("## License", 1)[0]
        self.assertIn("exactly thirty-three bounded altered", production_boundary)
        self.assertIn(SOURCE_PATH, production_boundary)
        self.assertIn("All thirty-three", production_boundary)
        self.assertIn("only those thirty-three", production_boundary)
        self.assertNotIn("nine bounded", production_boundary)
        self.assertNotIn(
            "The production allowlist now contains ten",
            nanopb_readme,
        )

        historical_headings = {
            ROOT / "README.md": "## Preceding nanopb stream-constructor milestone",
            ROOT / "components/README.md": (
                "## Preceding Apollo-main nanopb stream-constructor milestone"
            ),
            ROOT / "components/apollo_main/core_overlay/EVIDENCE.md": (
                "## Preceding nanopb stream-constructor production milestone"
            ),
            ROOT / "docs/source-coverage.md": (
                "## Preceding nanopb stream-constructor coverage milestone"
            ),
            ROOT / "docs/memory-map.md": (
                "## Preceding Apollo-main nanopb stream-constructor map"
            ),
            ROOT / "docs/upstream-inventory.md": (
                "## Preceding bounded nanopb stream-constructor reuse milestone"
            ),
        }
        for path, heading in historical_headings.items():
            with self.subTest(historical_doc=path.relative_to(ROOT)):
                self.assertIn(heading, path.read_text(encoding="utf-8"))

        stale_relative_current_phrases = {
            ROOT / "README.md": (
                "Current aggregate pins and censuses are recorded in the "
                "stream-constructor increment immediately below."
            ),
            ROOT / "components/README.md": (
                "Current aggregate pins and censuses are in the stream "
                "constructor section immediately below."
            ),
            ROOT / "docs/memory-map.md": (
                "The current constructor map immediately below supersedes "
                "these aggregate endpoints."
            ),
            ROOT / "docs/source-coverage.md": (
                "The current 733,107-byte flash plan hashes to"
            ),
            ROOT / "components/apollo_main/core_overlay/EVIDENCE.md": (
                "the current constructor tranche below supersedes that boundary."
            ),
        }
        for path, stale_phrase in stale_relative_current_phrases.items():
            normalized = " ".join(path.read_text(encoding="utf-8").split())
            with self.subTest(stale_relative_current=path.relative_to(ROOT)):
                self.assertNotIn(stale_phrase, normalized)
                self.assertIn("subsequent signed-varint", normalized)


class NanopbDecodeSvarintLinuxBuildMutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") != "linux-clang":
            raise unittest.SkipTest(
                "real signed-varint mutation builds require linux-clang"
            )
        if ROOT != LINUX_SOURCE_ROOT:
            raise AssertionError(
                f"Linux mutation build root {ROOT} differs from reviewed "
                f"exact root {LINUX_SOURCE_ROOT}"
            )
        cls.clang = os.environ.get("OPENCFW_CLANG", LINUX_CLANG)
        if cls.clang != LINUX_CLANG:
            raise AssertionError(
                f"Linux mutation compiler {cls.clang} differs from reviewed "
                f"compiler {LINUX_CLANG}"
            )
        version = subprocess.run(
            [cls.clang, "--version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()[0]
        if version != LINUX_CLANG_VERSION:
            raise AssertionError(
                f"Linux mutation compiler version {version!r} differs from "
                f"reviewed {LINUX_CLANG_VERSION!r}"
            )

        specification = importlib.util.spec_from_file_location(
            "open_cfw_svarint_linux_mutation_apollo_overlay",
            OVERLAY_TOOL,
        )
        assert specification is not None and specification.loader is not None
        cls.apollo_overlay = importlib.util.module_from_spec(specification)
        sys.modules[specification.name] = cls.apollo_overlay
        specification.loader.exec_module(cls.apollo_overlay)
        cls.config = json.loads(OVERLAY.read_text(encoding="utf-8"))
        build_root = ROOT / "build"
        build_root.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="svarint-linux-build-mutations-",
            dir=build_root,
        )
        cls.output = Path(cls.temporary.name)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def build_full_config(self, config: dict[str, object], label: str) -> dict:
        config_path = self.output / f"{label}.json"
        config_path.write_text(
            json.dumps(config, indent=2) + "\n",
            encoding="utf-8",
        )
        return self.apollo_overlay.build(
            root=ROOT,
            config_path=config_path,
            output_dir=self.output / label,
            clang=self.clang,
            toolchain_profile="linux-clang",
        )

    def test_baseline_real_overlay_build_succeeds(self) -> None:
        report = self.build_full_config(
            copy.deepcopy(self.config),
            "baseline",
        )
        self.assertEqual(
            (
                report["overlay"]["size"],
                report["overlay"]["sha256"],
            ),
            LINUX_AGGREGATE["overlay"],
        )
        self.assertEqual(
            (
                report["component"]["size"],
                report["component"]["sha256"],
            ),
            LINUX_AGGREGATE["component"],
        )

    def test_full_overlay_leaf_pin_mutations_fail_closed(self) -> None:
        leaf = next(
            item for item in self.config["relocated_leaves"]
            if item["function"] == PRODUCTION_FUNCTION
        )
        expected = leaf["toolchain_profiles"]["linux-clang"]["expected"]
        mutations = (
            ("size", expected["size"] + 2),
            ("sha256", "0" * 64),
            ("alignment", expected["alignment"] // 2),
            ("offset", expected["offset"] + 2),
            ("unrelocated_sha256", "0" * 64),
        )
        for field, mutation in mutations:
            config = copy.deepcopy(self.config)
            mutated_leaf = next(
                item for item in config["relocated_leaves"]
                if item["function"] == PRODUCTION_FUNCTION
            )
            mutated_expected = mutated_leaf["toolchain_profiles"][
                "linux-clang"
            ]["expected"]
            mutated_expected[field] = mutation
            with self.subTest(field=field), self.assertRaises(
                self.apollo_overlay.BuildError
            ) as rejection:
                self.build_full_config(config, f"mutation-{field}")
            self.assertIn(PRODUCTION_FUNCTION, str(rejection.exception))


if __name__ == "__main__":
    unittest.main()
