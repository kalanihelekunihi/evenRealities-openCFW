from __future__ import annotations

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
SOURCE = ROOT / "components/shared/nanopb/runtime_nanopb_decode_fixed64.c"
HEADER = SOURCE.with_suffix(".h")
SNAPSHOT = ROOT / "third_party/nanopb"
UPSTREAM = SNAPSHOT / "pb_decode.c"
UPSTREAM_COMMON = SNAPSHOT / "pb_common.c"
CONFIG = SNAPSHOT / "g2-config/pb_g2_options.h"
PROVENANCE = SNAPSHOT / "PROVENANCE.json"
VERIFIER = SNAPSHOT / "verify_snapshot.py"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OVERLAY_TOOL = ROOT / "tools/apollo_overlay.py"
POINT_RELEASE_TOOL = ROOT / "tools/analyze_g2_nanopb_point_release.py"
AUDIT = ROOT / "docs/research/nanopb-decode-fixed64-candidate-audit.md"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
BOOT_OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"

FUNCTION = "open_cfw_nanopb_decode_fixed64"
READ_SYMBOL = "open_cfw_nanopb_read"
SECTION = ".text." + FUNCTION
SOURCE_PATH = SOURCE.relative_to(ROOT).as_posix()
HEADER_PATH = HEADER.relative_to(ROOT).as_posix()

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

START = 0x0049_01AC
END = 0x0049_01CC
STOCK = bytes.fromhex(
    "1cb50c0008226946fff703f9002801d1002004e0dde90001c4e90001012016bd"
)
STOCK_SHA256 = (
    "96228dfbdfe30665d79281ba0fd5ba3b"
    "3af38701396671cd20b77623ffd82d54"
)
PREDECESSOR = (0x0049_0190, START)
PREDECESSOR_SHA256 = (
    "1ee27599a8ac5b8d2a0cbaac59986fb4"
    "9be7b24c348a960a216b8cbbecce5bf3"
)
SUCCESSOR = (END, 0x0049_01E4)
SUCCESSOR_SHA256 = (
    "f86ba3605d946c51e45452a18f09d848"
    "c26c0373dd08fb9e68206dedc1f68a36"
)
CALLER = 0x0048_F8C6
CALL_ENCODING = bytes.fromhex("00f071fc")
CALLER_BODY = (0x0048_F7F4, 0x0048_F968)
CALLER_BODY_SHA256 = (
    "2b1bf389327c0f6ccde636bbb51e36cd"
    "0bab3eccc811db9aa0efd3dbfef9e445"
)
OUTGOING = 0x0049_01B4
OUTGOING_ENCODING = bytes.fromhex("fff703f9")
READ_ENTRY = 0x0048_F3BE
READ_BODY = (READ_ENTRY, 0x0048_F454)
READ_BODY_SHA256 = (
    "69aecb900c749fd98bd2d05e2229e9a3"
    "d6829bd36f3e393f624e3579a9b4af7f"
)

SOURCE_PIN = (
    2_119,
    "a8b7fe49a1107080776bc0b753a77d55"
    "a861180c4090db270f4f9d04ef67cb63",
)
HEADER_PIN = (
    1_726,
    "6394df89057700817341e0550ae21033"
    "629d3a1ea458d5a68a6edc2b233cc6bd",
)
UPSTREAM_PIN = (
    53_845,
    "e980f2a41d9abe37b7e6fb4c9ba1ebf"
    "d68507a6fd2653f8d755e1947a9c84b1a",
)
UPSTREAM_DEFINITION = (43_854, 44_688)
UPSTREAM_DEFINITION_PIN = (
    834,
    "7f9da692a631280aa5b91a5d08440ac6"
    "8f5060a64814997dde8dcbdb2f0b4974",
)
RELEASE_DEFINITION_RECORDS = {
    "0.4.7": {
        "commit": "b97aa657a706d3ba4a9a6ccca7043c9d6fe41cba",
        "source": (
            "9ed9e255e433324fc28557adb03bf494a"
            "3711c2a0480c97b3690a6871ce29c66"
        ),
        "span": (43_768, 44_602),
    },
    "0.4.8": {
        "commit": "6cfe48d6f1593f8fa5c0f90437f5e6522587745e",
        "source": (
            "9ed9e255e433324fc28557adb03bf494a"
            "3711c2a0480c97b3690a6871ce29c66"
        ),
        "span": (43_768, 44_602),
    },
    "0.4.9": {
        "commit": "98bf4db69897b53434f3d0ba72e0a3ab1a902824",
        "source": UPSTREAM_PIN[1],
        "span": UPSTREAM_DEFINITION,
    },
}
CONFIG_PIN = (
    1_551,
    "ae758999d239e49e2d5c5bf6de3f4ae"
    "f3aab5cd3c29d8de65c4db301c62899db",
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
OVERLAY_RUNTIME_BASE = 0x0079_4324
PROFILE_PINS = {
    "apple-clang": {
        "compiler": "/usr/bin/clang",
        "version": "Apple clang version 21.0.0 (clang-2100.3.33.1)",
        "object": (
            936,
            "fc8f839b98f4a6da48fa022a5c35c22"
            "e19f38bee8045bb731b1230395b485d2e",
        ),
        "text": bytes.fromhex(
            "10b582b00c4669460822fff7feff18b1d"
            "de900216160226002b010bd"
        ),
        "unrelocated": (
            "c4cfb6fece88a057c874d8f2ffcce961"
            "df9ef15fb16c78421f48396f0cceff2c"
        ),
        "offset": 124_612,
        "runtime": 0x007B_29E8,
        "relocated_text": bytes.fromhex(
            "10b582b00c4669460822dcf4e4fc18b1d"
            "de900216160226002b010bd"
        ),
        "relocated": (
            "6e970db6346919f9937f459489b5699b"
            "1b5bf5e0d2b4f19a327cbbe6d2b4adb0"
        ),
        "patch": (
            "22f31cbc" + "00bf" * 14,
            "8d2dc699f879d4fb1a33813da444d5af"
            "1565cd9e17a93dac0922c9b66f6f3382",
        ),
    },
    "linux-clang": {
        "compiler": "/home/linuxbrew/.linuxbrew/bin/clang",
        "version": "Homebrew clang version 22.1.8",
        "object": (
            940,
            "f447c5715142e7a5b2c144566ac3094a"
            "58727611e011137d440e8d549a2e329b",
        ),
        "text": bytes.fromhex(
            "10b582b00c4669460822fff7feff00281"
            "cbfdde90012c4e9001202b010bd"
        ),
        "unrelocated": (
            "bfaf01f7496cce042c84c35708421508"
            "fbf2fa5acd9d9fcb209753901e09af10"
        ),
        "offset": 126_432,
        "runtime": 0x007B_3104,
        "relocated_text": bytes.fromhex(
            "10b582b00c4669460822dcf456f900281"
            "cbfdde90012c4e9001202b010bd"
        ),
        "relocated": (
            "4e067bc2e9e3cb63335507bd64f3e733"
            "21c24294ec3313c72f57cd801a9b8968"
        ),
        "patch": (
            "22f3aabf" + "00bf" * 14,
            "918801fc87be3e7e55a1509e10d0ab05"
            "f969b4578038c147fd100e2feecfc9c0",
        ),
    },
}

HOST_HARNESS = r"""
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "components/shared/nanopb/runtime_nanopb_decode_fixed64.h"
#include "pb_decode.h"

struct open_cfw_test_input {
    const uint8_t *bytes;
    size_t size;
    size_t offset;
    uint32_t calls;
    uint32_t fail_call;
};

struct open_cfw_test_result {
    uint64_t destination;
    uint64_t bytes_left;
    uint64_t consumed;
    uint32_t status;
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

static bool open_cfw_test_production_callback(
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
        if (stream->errmsg == NULL) stream->errmsg = "end-of-stream";
        return false;
    }
    if (!stream->callback(stream, buffer, count)) {
        if (stream->errmsg == NULL) stream->errmsg = "io error";
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
    uint64_t destination,
    const char *error,
    const struct open_cfw_test_input *input,
    struct open_cfw_test_result *result
)
{
    result->destination = destination;
    result->bytes_left = bytes_left;
    result->consumed = input->offset;
    result->status = status ? 1U : 0U;
    result->calls = input->calls;
    result->error = open_cfw_test_error(error);
}

void open_cfw_test_run_production(
    const uint8_t *bytes,
    size_t size,
    size_t bytes_left,
    uint32_t fail_call,
    uint32_t existing_error,
    uint64_t initial_destination,
    struct open_cfw_test_result *result
)
{
    struct open_cfw_test_input input = {
        bytes, size, 0U, 0U, fail_call
    };
    struct open_cfw_nanopb_istream stream = {
        open_cfw_test_production_callback,
        &input,
        bytes_left,
        existing_error ? open_cfw_test_existing_error : NULL
    };
    uint64_t destination = initial_destination;
    bool status = open_cfw_nanopb_decode_fixed64(
        &stream, &destination
    );
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
    uint64_t initial_destination,
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
    uint64_t destination = initial_destination;
    bool status = pb_decode_fixed64(&stream, &destination);
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
        ("destination", ctypes.c_uint64),
        ("bytes_left", ctypes.c_uint64),
        ("consumed", ctypes.c_uint64),
        ("status", ctypes.c_uint32),
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


class NanopbDecodeFixed64ProductionTests(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.package = OFFICIAL.read_bytes()
        cls.application = cls.package[PACKAGE_PREAMBLE:]
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="openCFW-nanopb-fixed64-production-"
        )
        cls.output = Path(cls.temporary.name)
        harness = cls.output / "host.c"
        harness.write_text(HOST_HARNESS, encoding="ascii")
        library = cls.output / "libnanopb_fixed64_production.dylib"
        result = subprocess.run(
            [
                os.environ.get("CC", "clang"),
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
        for name in ("production", "upstream"):
            function = getattr(cls.library, f"open_cfw_test_run_{name}")
            function.argtypes = arguments
            function.restype = None

        specification = importlib.util.spec_from_file_location(
            "open_cfw_fixed64_apollo_overlay", OVERLAY_TOOL
        )
        assert specification is not None and specification.loader is not None
        cls.apollo_overlay = importlib.util.module_from_spec(specification)
        sys.modules[specification.name] = cls.apollo_overlay
        specification.loader.exec_module(cls.apollo_overlay)

        point_specification = importlib.util.spec_from_file_location(
            "open_cfw_fixed64_point_release", POINT_RELEASE_TOOL
        )
        assert (
            point_specification is not None
            and point_specification.loader is not None
        )
        cls.point_release = importlib.util.module_from_spec(point_specification)
        sys.modules[point_specification.name] = cls.point_release
        point_specification.loader.exec_module(cls.point_release)

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
        bytes_left: int,
        fail_call: int,
        existing_error: int,
        initial_destination: int,
    ) -> tuple[int, ...]:
        storage = (ctypes.c_uint8 * max(1, len(payload)))()
        if payload:
            storage[: len(payload)] = payload
        output = Result()
        getattr(self.library, f"open_cfw_test_run_{name}")(
            storage,
            len(payload),
            bytes_left,
            fail_call,
            existing_error,
            initial_destination,
            ctypes.byref(output),
        )
        return output.values()

    def compare_case(
        self,
        payload: bytes,
        bytes_left: int,
        fail_call: int,
        existing_error: int,
        initial_destination: int,
    ) -> tuple[int, ...]:
        production = self.run_case(
            "production",
            payload,
            bytes_left,
            fail_call,
            existing_error,
            initial_destination,
        )
        upstream = self.run_case(
            "upstream",
            payload,
            bytes_left,
            fail_call,
            existing_error,
            initial_destination,
        )
        self.assertEqual(production, upstream)
        if not production[0]:
            self.assertEqual(production[1], initial_destination)
        return production

    def test_authenticated_source_range_and_production_pins(self) -> None:
        for path, pin in (
            (SOURCE, SOURCE_PIN),
            (HEADER, HEADER_PIN),
            (UPSTREAM, UPSTREAM_PIN),
            (CONFIG, CONFIG_PIN),
        ):
            payload = path.read_bytes()
            self.assertEqual((len(payload), sha256(payload)), pin)

        definition = UPSTREAM.read_bytes()[slice(*UPSTREAM_DEFINITION)]
        self.assertEqual(
            (len(definition), sha256(definition)), UPSTREAM_DEFINITION_PIN
        )
        self.assertTrue(definition.startswith(b"bool pb_decode_fixed64("))
        self.assertTrue(definition.endswith(b"    return true;\n}\n"))
        self.assertIn(b"if (!pb_read(stream, u.bytes, 8))", definition)
        self.assertIn(b"*(uint64_t*)dest = u.fixed64", definition)

        releases = self.point_release.UPSTREAM_RELEASES
        for version, expected in RELEASE_DEFINITION_RECORDS.items():
            self.assertEqual(releases[version]["commit"], expected["commit"])
            self.assertEqual(
                releases[version]["files"]["pb_decode.c"],
                expected["source"],
            )
            self.assertEqual(
                expected["span"][1] - expected["span"][0],
                UPSTREAM_DEFINITION_PIN[0],
            )
        self.assertEqual(
            RELEASE_DEFINITION_RECORDS["0.4.7"]["source"],
            RELEASE_DEFINITION_RECORDS["0.4.8"]["source"],
        )

        provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        self.assertEqual(
            provenance["upstream"]["selected_commit"],
            RELEASE_DEFINITION_RECORDS["0.4.9"]["commit"],
        )
        self.assertEqual(provenance["upstream"]["selected_tag"], "nanopb-0.4.9")
        self.assertEqual(
            provenance["selection"]["g2_compatible_pristine_release_range"],
            ["0.4.7", "0.4.8", "0.4.9", "0.4.9.1"],
        )
        self.assertFalse(
            provenance["selection"]["exact_g2_point_release_proven"]
        )
        self.assertEqual(provenance["license"], "Zlib")
        self.assertEqual(
            provenance["selection"]["production_decode_fixed64_leaf"],
            {
                "upstream_function": "pb_decode_fixed64",
                "upstream_source": "pb_decode.c",
                "upstream_commit": (
                    "98bf4db69897b53434f3d0ba72e0a3ab1a902824"
                ),
                "upstream_definition_span": (
                    "pb_decode.c bytes [43854,44688)"
                ),
                "upstream_definition_size": UPSTREAM_DEFINITION_PIN[0],
                "upstream_definition_sha256": UPSTREAM_DEFINITION_PIN[1],
                "local_source": SOURCE_PATH,
                "local_source_size": SOURCE_PIN[0],
                "local_source_sha256": SOURCE_PIN[1],
                "local_header": HEADER_PATH,
                "local_header_size": HEADER_PIN[0],
                "local_header_sha256": HEADER_PIN[1],
                "stock_span": "[0x004901AC,0x004901CC)",
                "stock_size": END - START,
                "stock_sha256": STOCK_SHA256,
                "stock_read_seam": "0x0048F3BE",
                "configuration": "g2-config/pb_g2_options.h",
                "qualification": (
                    "Altered local source selected against authenticated "
                    "nanopb 0.4.9 as a compatibility baseline within the "
                    "authenticated 0.4.7-0.4.9 range; not proof of the "
                    "vendor nanopb revision or checkout. Its pb_read ABI entry "
                    "now redirects to the separately pinned "
                    "production_read_leaf, while that provider retains three "
                    "authenticated stock identity/data seams. The broader "
                    "pristine pb_common, pb_decode, and pb_encode translation "
                    "units remain unregistered."
                ),
            },
        )

        source_text = SOURCE.read_text(encoding="utf-8")
        header_text = HEADER.read_text(encoding="utf-8")
        self.assertIn("Altered production source adaptation", source_text)
        self.assertIn("open_cfw_nanopb_read(stream", source_text)
        self.assertIn("0.4.7, 0.4.8, and 0.4.9", source_text)
        self.assertIn("prove the vendor's historical", source_text)
        self.assertIn("sizeof(uint64_t) == 8U", header_text)

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

    def test_stock_boundary_caller_and_read_seam_are_exact(self) -> None:
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
        self.assertEqual(sha256(self.span(*READ_BODY)), READ_BODY_SHA256)

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
            wide_branch_target(OUTGOING, first, second, link=True), READ_ENTRY
        )

        outgoing_calls = []
        for address in range(START, END - 3, 2):
            first, second = struct.unpack(
                "<HH", self.span(address, address + 4)
            )
            target = wide_branch_target(address, first, second, link=True)
            if target is not None:
                outgoing_calls.append((address, target))
        self.assertEqual(outgoing_calls, [(OUTGOING, READ_ENTRY)])
        self.assertEqual(self.span(START - 2, START), bytes.fromhex("16bd"))
        self.assertEqual(self.span(END, END + 2), bytes.fromhex("80b5"))

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

    def test_abi_configuration_and_failure_before_store_contract(self) -> None:
        config_text = CONFIG.read_text(encoding="utf-8")
        self.assertIn("requires 64-bit scalar support", config_text)
        self.assertIn("retains callback stream support", config_text)
        self.assertIn("retains runtime error strings", config_text)

        source_text = SOURCE.read_text(encoding="utf-8")
        self.assertIn(
            "open_cfw_nanopb_read(stream, value.bytes, sizeof(value.bytes))",
            source_text,
        )
        self.assertLess(
            source_text.index("if (!open_cfw_nanopb_read"),
            source_text.index("*(uint64_t *)destination"),
        )
        self.assertIn("little-endian fast path", source_text)
        self.assertNotIn("malloc", source_text.lower())
        self.assertNotIn("memcpy", source_text)

    def test_deterministic_profile_object_and_reviewed_call_relocation(self) -> None:
        compiler = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        if not Path(compiler).is_file():
            self.skipTest("reviewed target compiler is unavailable")
        version = subprocess.run(
            [compiler, "--version"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=True,
        ).stdout.splitlines()[0]
        matches = [
            (name, pins)
            for name, pins in PROFILE_PINS.items()
            if (compiler, version) == (pins["compiler"], pins["version"])
        ]
        self.assertEqual(len(matches), 1, (compiler, version))
        profile, pins = matches[0]

        objects = []
        paths = []
        for index in range(2):
            output = self.output / f"{profile}-{index}.o"
            result = subprocess.run(
                [
                    compiler,
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
            paths.append(output)
        self.assertEqual(objects[0], objects[1])
        self.assertEqual(
            (len(objects[0]), sha256(objects[0])), pins["object"]
        )

        data, sections = self.apollo_overlay.parse_elf32(paths[0])
        symbols = self.apollo_overlay.parse_elf32_symbols(data, sections)
        function = next(
            symbol for symbol in symbols if symbol["name"] == FUNCTION
        )
        section = sections[function["section_index"]]
        text = data[section["offset"] : section["offset"] + section["size"]]
        self.assertEqual(section["name"], SECTION)
        self.assertEqual(section["alignment"], 4)
        self.assertEqual(text, pins["text"])
        self.assertEqual(sha256(text), pins["unrelocated"])

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
        self.assertEqual(relocations, [(10, 10, READ_SYMBOL)])
        undefined = sorted(
            symbol["name"] for symbol in symbols
            if symbol["name"] and symbol["section_index"] == 0
        )
        self.assertEqual(undefined, [READ_SYMBOL])
        allocated = {
            item["name"]: item["size"]
            for item in sections if item["size"] and item["flags"] & 2
        }
        self.assertEqual(
            allocated, {SECTION: len(pins["text"]), ".ARM.exidx" + SECTION: 8}
        )

        relocated = bytearray(text)
        self.assertEqual(
            pins["runtime"], OVERLAY_RUNTIME_BASE + pins["offset"]
        )
        site = pins["runtime"] + 10
        relocated[10:14] = self.apollo_overlay.encode_thumb_branch(
            site, READ_ENTRY, link=True
        )
        self.assertEqual(relocated, pins["relocated_text"])
        self.assertEqual(sha256(relocated), pins["relocated"])
        self.assertEqual(
            self.apollo_overlay.decode_thumb_branch(
                site, bytes(relocated[10:14]), link=True
            ),
            READ_ENTRY,
        )

    def test_broad_differential_and_failure_preserves_destination(self) -> None:
        initial = 0xA55A_F00D_DEAD_BEEF
        patterns = (
            bytes(8),
            bytes([0xFF] * 8),
            bytes(range(8)),
            bytes(reversed(range(8))),
            bytes.fromhex("0100000000000000"),
            bytes.fromhex("0000000000000080"),
            bytes.fromhex("efbeadde0df05aa5"),
            bytes.fromhex("0123456789abcdef"),
        )
        cases = [(value, 8, 0, 0, initial) for value in patterns]
        cases.extend((bytes(range(length)), length, 0, 0, initial) for length in range(8))
        cases.extend((bytes(range(8)), budget, 0, 0, initial) for budget in range(8))
        cases.extend(
            (
                (bytes(range(8)), 8, 1, 0, initial),
                (bytes(range(16)), 16, 1, 1, initial),
                (bytes(range(8)), 8, 0, 1, initial),
                (bytes(range(7)), 8, 0, 1, initial),
                (bytes(range(16)), 16, 0, 0, initial),
                (bytes(range(7)), 16, 0, 0, initial),
            )
        )
        self.assertEqual(len(cases), 30)

        generator = random.Random(0x4901AC ^ 0x0409)
        for _ in range(25_000):
            size = generator.randrange(17)
            cases.append(
                (
                    generator.randbytes(size),
                    generator.randrange(17),
                    generator.randrange(3),
                    generator.randrange(2),
                    generator.getrandbits(64),
                )
            )

        successes = 0
        failures = 0
        for arguments in cases:
            result = self.compare_case(*arguments)
            if result[0]:
                successes += 1
                self.assertEqual(
                    result[1], int.from_bytes(arguments[0][:8], "little")
                )
            else:
                failures += 1
        self.assertEqual(len(cases), 25_030)
        self.assertGreater(successes, 1_000)
        self.assertGreater(failures, 1_000)

    def test_production_registration_patch_and_audit_scope(self) -> None:
        config = json.loads(OVERLAY.read_text(encoding="utf-8"))
        self.assertEqual(
            (
                len(config["functions"]),
                len(config["patch_sites"]),
                len(config["relocated_leaves"]),
            ),
            (2443, 2331, 1874),
        )
        self.assertEqual(config["functions"].count(FUNCTION), 1)
        leaves = [
            leaf for leaf in config["relocated_leaves"]
            if leaf.get("function") == FUNCTION
        ]
        self.assertEqual(len(leaves), 1)
        leaf = leaves[0]
        self.assertTrue(leaf["strict_relocation_contract"])
        self.assertEqual(
            {
                key: leaf["source"][key]
                for key in ("path", "size", "sha256", "license")
            },
            {
                "path": SOURCE_PATH,
                "size": SOURCE_PIN[0],
                "sha256": SOURCE_PIN[1],
                "license": "Zlib",
            },
        )
        relocation = [{
            "offset": 10,
            "type": "R_ARM_THM_CALL",
            "symbol": READ_SYMBOL,
            "symbol_type": "STT_NOTYPE",
            "target_address": READ_ENTRY,
        }]
        self.assertEqual(leaf["relocations"], relocation)
        for profile, pins in PROFILE_PINS.items():
            selected = (
                leaf if profile == "apple-clang"
                else leaf["toolchain_profiles"][profile]
            )
            self.assertEqual(
                selected["expected"],
                {
                    "size": len(pins["text"]),
                    "sha256": pins["relocated"],
                    "alignment": 4,
                    "offset": pins["offset"],
                    "unrelocated_sha256": pins["unrelocated"],
                },
            )
            self.assertEqual(selected["relocations"], relocation)

        patches = [
            patch for patch in config["patch_sites"]
            if patch.get("target_function") == FUNCTION
        ]
        self.assertEqual(
            patches,
            [{
                "name": "replace_nanopb_decode_fixed64",
                "runtime_address": START,
                "expected_size": END - START,
                "expected_sha256": STOCK_SHA256,
                "branch": "b_w",
                "target_function": FUNCTION,
            }],
        )

        boot = BOOT_OVERLAY.read_text(encoding="utf-8")
        self.assertNotIn(FUNCTION, boot)
        self.assertNotIn(SOURCE_PATH, boot)
        manifest = MANIFEST.read_text(encoding="utf-8")
        self.assertIn("nanopb_decode_fixed64_source_replacement", manifest)
        self.assertIn("apollo_nanopb_decode_fixed64_source_leaf", manifest)

        audit = AUDIT.read_text(encoding="utf-8")
        for needle in (
            "production source leaf",
            "0x004901AC",
            "0x004901CC",
            "0x0048F8C6",
            "0x0048F3BE",
            UPSTREAM_DEFINITION_PIN[1],
            STOCK_SHA256,
            PROFILE_PINS["apple-clang"]["unrelocated"],
            PROFILE_PINS["apple-clang"]["relocated"],
            PROFILE_PINS["linux-clang"]["unrelocated"],
            PROFILE_PINS["linux-clang"]["relocated"],
            "destination",
            "source-owned `pb_read`",
            "No authenticated bootloader homolog",
            "No firmware was signed or flashed",
        ):
            self.assertIn(needle, audit)


if __name__ == "__main__":
    unittest.main()
