#!/usr/bin/env python3
"""Focused provenance, topology, ABI, and behavior tests for production pb_read."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/shared/nanopb/runtime_nanopb_read.c"
HEADER = ROOT / "components/shared/nanopb/runtime_nanopb_read.h"
UPSTREAM = ROOT / "third_party/nanopb/pb_decode.c"
OFFICIAL = (
    ROOT
    / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
)
AUDIT = ROOT / "docs/research/nanopb-read-source-candidate-audit.md"
PROVENANCE = ROOT / "third_party/nanopb/PROVENANCE.json"
VERIFIER = ROOT / "third_party/nanopb/verify_snapshot.py"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
BOOT_OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"

LOAD_BASE = 0x00437FE0
PB_READ = (0x0048F3BE, 0x0048F454)
PB_READ_SHA256 = "69aecb900c749fd98bd2d05e2229e9a3d6829bd36f3e393f624e3579a9b4af7f"
BUF_READ = (0x0048F3A4, 0x0048F3BE)
BUF_READ_SHA256 = "9d6c6690294b82bbafba82ec0f63a6bb5b78e4146543db3a30fac92469ace723"
UPSTREAM_DEFINITION = (3745, 4559)
UPSTREAM_DEFINITION_SHA256 = (
    "3b69f6f4eb56a87c3f8a7f9ac30ac7573328c560047cbc5b2295daceef18fb1c"
)
APPLE_CLANG_VERSION = "Apple clang version 21.0.0 (clang-2100.3.27.1)"
APPLE_OBJECT_SHA256 = (
    "fafc2e4ec4081c523f87f1eda3ff87d9cc207119ec4f4ca77910bb08ccae0f0d"
)
SOURCE_PIN = (2944, "e4f99df8121553d4cb6d6c2f94aa7ef1b1445efd200cee4d872dd75894d24089")
HEADER_PIN = (2032, "22203e33b8cd9e07b94d24477ffb8a6f096a9ea8393c5723071b5f12c3ec4296")
BOOT_PIN = (148599, "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5")
END_OF_STREAM = (0x00787C70, b"end-of-stream\0")
END_OF_STREAM_SHA256 = "e167d4f2ec31a2197c7bc32affd9865ac8609d7dae984d0916e01f044fcc67b4"
IO_ERROR = (0x0078B690, b"io error\0")
IO_ERROR_SHA256 = "3faaf40b4ee3e3b23823ed9851dc77bf6fc2d7c7c330240eeaed08bd9d084ec1"
INTERNAL_CALLERS = (0x0048F3EA, 0x0048F3FC)
EXTERNAL_CALLERS = (
    0x0048F632, 0x0048F666, 0x0048F6C0, 0x0048F6D0, 0x0048F71A,
    0x0048F754, 0x0048F764, 0x0048F7DC, 0x00490198, 0x004901B4,
    0x004903E4, 0x00490478, 0x004905A2,
)
OVERLAY_RUNTIME_BASE = 0x00794324
PROFILE_PINS = {
    "apple-clang": {
        "offset": 124640,
        "runtime": 0x007B2A04,
        "patch_prefix": "23f321bb",
        "patch_sha256": "c2c44419ee24c41c8d0e8bc7f04689bb7f1c18b1f7ec3d7304e04c37579938a1",
    },
    "linux-clang": {
        "offset": 126464,
        "runtime": 0x007B3124,
        "patch_prefix": "23f3b1be",
        "patch_sha256": "4dc433588344c12d1a0abfab8c5f1673c24f6702d8f285f67fb0fd8b8e6e3eab",
    },
}
TEXT_PIN = (158, "06def086733fd9801b712161943b0da64e3b2bdf82e6f5962ee9207c738c00b1")
RELOCATED_SHA256 = "8b3de44a2cf7ca2e07715c913db0fa454ef65cbc453366190b12736e455aa7a8"
RELOCATIONS = (
    (28, 47, "open_cfw_nanopb_end_of_stream_error", 0x00787C70),
    (32, 48, "open_cfw_nanopb_end_of_stream_error", 0x00787C70),
    (66, 47, "open_cfw_nanopb_stock_buffer_read_identity", 0x0048F3A5),
    (70, 48, "open_cfw_nanopb_stock_buffer_read_identity", 0x0048F3A5),
    (134, 47, "open_cfw_nanopb_io_error", 0x0078B690),
    (138, 48, "open_cfw_nanopb_io_error", 0x0078B690),
)
TARGET_FLAGS = (
    "--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-fno-ident",
)
OVERLAY_TOOL = ROOT / "tools/apollo_overlay.py"


HOST_HARNESS = r'''
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "components/shared/nanopb/runtime_nanopb_read.h"

#define CHECK(value) do { if (!(value)) { return __LINE__; } } while (0)

const char open_cfw_nanopb_end_of_stream_error[] = "end-of-stream";
const char open_cfw_nanopb_io_error[] = "io error";

static size_t buffer_calls;
static uint8_t *buffer_last_destination;

bool open_cfw_nanopb_stock_buffer_read_identity(
    struct open_cfw_nanopb_istream *stream,
    uint8_t *buffer,
    size_t count
)
{
    const uint8_t *source = (const uint8_t *)stream->state;
    buffer_calls++;
    buffer_last_destination = buffer;
    stream->state = (void *)(source + count);
    if (buffer != NULL) {
        memcpy(buffer, source, count);
    }
    return true;
}

struct custom_context {
    const uint8_t *source;
    size_t offset;
    size_t calls;
    size_t counts[8];
    size_t fail_at;
    bool shrink_after_success;
};

static bool custom_read(
    struct open_cfw_nanopb_istream *stream,
    uint8_t *buffer,
    size_t count
)
{
    struct custom_context *context = (struct custom_context *)stream->state;
    size_t call_index = context->calls++;
    context->counts[call_index] = count;
    if (context->fail_at != 0U && context->calls == context->fail_at) {
        return false;
    }
    if (buffer == NULL) {
        return false;
    }
    memcpy(buffer, context->source + context->offset, count);
    context->offset += count;
    if (context->shrink_after_success) {
        stream->bytes_left = count - 1U;
    }
    return true;
}

static int test_zero_count(void)
{
    struct open_cfw_nanopb_istream stream = {
        NULL, (void *)(uintptr_t)0x1234U, 9U, "prior"
    };
    CHECK(open_cfw_nanopb_read(&stream, NULL, 0U));
    CHECK(stream.state == (void *)(uintptr_t)0x1234U);
    CHECK(stream.bytes_left == 9U);
    CHECK(strcmp(stream.errmsg, "prior") == 0);
    return 0;
}

static int test_normal_custom_read(void)
{
    static const uint8_t source[] = {1U, 2U, 3U, 4U, 5U, 6U};
    uint8_t destination[4] = {0U};
    struct custom_context context = {source, 0U, 0U, {0U}, 0U, false};
    struct open_cfw_nanopb_istream stream = {
        custom_read, &context, sizeof(source), NULL
    };
    CHECK(open_cfw_nanopb_read(&stream, destination, 4U));
    CHECK(memcmp(destination, source, 4U) == 0);
    CHECK(context.calls == 1U && context.counts[0] == 4U);
    CHECK(context.offset == 4U && stream.bytes_left == 2U);
    CHECK(stream.errmsg == NULL);
    return 0;
}

static int test_buffer_callback_null_fast_path(void)
{
    uint8_t source[20] = {0U};
    struct open_cfw_nanopb_istream stream = {
        open_cfw_nanopb_stock_buffer_read_identity,
        source,
        sizeof(source),
        NULL
    };
    buffer_calls = 0U;
    buffer_last_destination = (uint8_t *)(uintptr_t)1U;
    CHECK(open_cfw_nanopb_read(&stream, NULL, sizeof(source)));
    CHECK(buffer_calls == 1U);
    CHECK(buffer_last_destination == NULL);
    CHECK(stream.state == source + sizeof(source));
    CHECK(stream.bytes_left == 0U);
    return 0;
}

static int test_custom_null_skip_chunks(void)
{
    uint8_t source[35] = {0U};
    struct custom_context context = {source, 0U, 0U, {0U}, 0U, false};
    struct open_cfw_nanopb_istream stream = {
        custom_read, &context, sizeof(source), NULL
    };
    CHECK(open_cfw_nanopb_read(&stream, NULL, sizeof(source)));
    CHECK(context.calls == 3U);
    CHECK(context.counts[0] == 16U);
    CHECK(context.counts[1] == 16U);
    CHECK(context.counts[2] == 3U);
    CHECK(context.offset == sizeof(source));
    CHECK(stream.bytes_left == 0U);
    return 0;
}

static int test_initial_bound_failure(void)
{
    uint8_t source[3] = {0U};
    struct custom_context context = {source, 0U, 0U, {0U}, 0U, false};
    struct open_cfw_nanopb_istream stream = {
        custom_read, &context, 3U, NULL
    };
    CHECK(!open_cfw_nanopb_read(&stream, source, 4U));
    CHECK(context.calls == 0U && stream.bytes_left == 3U);
    CHECK(strcmp(stream.errmsg, "end-of-stream") == 0);
    stream.errmsg = "prior";
    CHECK(!open_cfw_nanopb_read(&stream, source, 4U));
    CHECK(strcmp(stream.errmsg, "prior") == 0);
    return 0;
}

static int test_callback_failure(void)
{
    uint8_t source[20] = {0U};
    struct custom_context context = {source, 0U, 0U, {0U}, 1U, false};
    struct open_cfw_nanopb_istream stream = {
        custom_read, &context, sizeof(source), NULL
    };
    CHECK(!open_cfw_nanopb_read(&stream, source, 4U));
    CHECK(context.calls == 1U && stream.bytes_left == sizeof(source));
    CHECK(strcmp(stream.errmsg, "io error") == 0);
    return 0;
}

static int test_recursive_failure_accounting(void)
{
    uint8_t source[20] = {0U};
    struct custom_context context = {source, 0U, 0U, {0U}, 2U, false};
    struct open_cfw_nanopb_istream stream = {
        custom_read, &context, sizeof(source), NULL
    };
    CHECK(!open_cfw_nanopb_read(&stream, NULL, sizeof(source)));
    CHECK(context.calls == 2U);
    CHECK(context.counts[0] == 16U && context.counts[1] == 4U);
    CHECK(context.offset == 16U && stream.bytes_left == 4U);
    CHECK(strcmp(stream.errmsg, "io error") == 0);
    return 0;
}

static int test_post_callback_saturating_accounting(void)
{
    uint8_t source[4] = {0U};
    struct custom_context context = {source, 0U, 0U, {0U}, 0U, true};
    struct open_cfw_nanopb_istream stream = {
        custom_read, &context, sizeof(source), NULL
    };
    CHECK(open_cfw_nanopb_read(&stream, source, sizeof(source)));
    CHECK(stream.bytes_left == 0U);
    return 0;
}

int main(void)
{
    int result;
    result = test_zero_count(); if (result != 0) return result;
    result = test_normal_custom_read(); if (result != 0) return result;
    result = test_buffer_callback_null_fast_path(); if (result != 0) return result;
    result = test_custom_null_skip_chunks(); if (result != 0) return result;
    result = test_initial_bound_failure(); if (result != 0) return result;
    result = test_callback_failure(); if (result != 0) return result;
    result = test_recursive_failure_accounting(); if (result != 0) return result;
    result = test_post_callback_saturating_accounting(); if (result != 0) return result;
    return 0;
}
'''


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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


class NanopbReadProductionTests(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory(prefix="openCFW-pb-read-")
        cls.output = Path(cls.temporary.name)
        cls.clang = shutil.which("clang")
        if cls.clang is None:
            xcrun = shutil.which("xcrun")
            if xcrun is not None:
                cls.clang = subprocess.check_output(
                    [xcrun, "--find", "clang"], text=True
                ).strip()
        if not cls.clang:
            raise unittest.SkipTest("clang is unavailable")
        cls.image = OFFICIAL.read_bytes()
        cls.application = cls.image[32:]
        spec = importlib.util.spec_from_file_location("open_cfw_pb_read_overlay", OVERLAY_TOOL)
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot load Apollo overlay helper")
        cls.apollo_overlay = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.apollo_overlay
        spec.loader.exec_module(cls.apollo_overlay)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_authenticated_upstream_definition(self) -> None:
        source = UPSTREAM.read_bytes()
        start, end = UPSTREAM_DEFINITION
        definition = source[start:end]
        self.assertEqual(len(definition), 814)
        self.assertEqual(sha256(definition), UPSTREAM_DEFINITION_SHA256)
        self.assertTrue(definition.startswith(b"bool checkreturn pb_read("))
        self.assertTrue(definition.endswith(b"return true;\n}"))

    def test_official_provider_and_private_buffer_callback_pins(self) -> None:
        image = OFFICIAL.read_bytes()
        for (start, end), expected in (
            (PB_READ, PB_READ_SHA256),
            (BUF_READ, BUF_READ_SHA256),
        ):
            body = image[start - LOAD_BASE : end - LOAD_BASE]
            self.assertEqual(len(body), end - start)
            self.assertEqual(sha256(body), expected)

        provider = image[PB_READ[0] - LOAD_BASE : PB_READ[1] - LOAD_BASE]
        self.assertIn(bytes.fromhex("dff8a0289042"), provider)
        self.assertIn(bytes.fromhex("2b689847"), provider)
        self.assertIn(bytes.fromhex("a868a04202d20020a860"), provider)

        for (address, value), expected in (
            (END_OF_STREAM, END_OF_STREAM_SHA256),
            (IO_ERROR, IO_ERROR_SHA256),
        ):
            observed = image[address - LOAD_BASE:address - LOAD_BASE + len(value)]
            self.assertEqual(observed, value)
            self.assertEqual(sha256(observed), expected)

    def test_thirteen_external_callers_and_no_interior_ingress(self) -> None:
        calls = []
        incoming_bw = []
        incoming_conditional = []
        for offset in range(0, len(self.image) - 3, 2):
            address = LOAD_BASE + offset
            first, second = struct.unpack_from("<HH", self.image, offset)
            target = wide_branch_target(address, first, second, link=True)
            if target is not None and PB_READ[0] <= target < PB_READ[1]:
                calls.append((address, target))
            if not PB_READ[0] <= address < PB_READ[1]:
                target = wide_branch_target(address, first, second, link=False)
                if target is not None and PB_READ[0] <= target < PB_READ[1]:
                    incoming_bw.append((address, target))
                target = wide_conditional_target(address, first, second)
                if target is not None and PB_READ[0] <= target < PB_READ[1]:
                    incoming_conditional.append((address, target))
        self.assertEqual(
            calls,
            [(address, PB_READ[0]) for address in (*INTERNAL_CALLERS, *EXTERNAL_CALLERS)],
        )
        self.assertEqual(incoming_bw, [])
        self.assertEqual(incoming_conditional, [])

        incoming_narrow = []
        for offset in range(0, len(self.image) - 1, 2):
            address = LOAD_BASE + offset
            if PB_READ[0] <= address < PB_READ[1]:
                continue
            halfword = struct.unpack_from("<H", self.image, offset)[0]
            for target in narrow_targets(address, halfword):
                if PB_READ[0] <= target < PB_READ[1]:
                    incoming_narrow.append((address, target))
        # The sole raw narrow-decoder hit is the low halfword of the aligned
        # literal-pool word 0x0075B9E8, not executable ingress.
        self.assertEqual(incoming_narrow, [(0x0048F39C, 0x0048F3DA)])
        self.assertEqual(
            struct.unpack_from(
                "<I", self.image, 0x0048F39C - LOAD_BASE
            )[0],
            0x0075B9E8,
        )

        stored = []
        for offset in range(len(self.image) - 3):
            value = struct.unpack_from("<I", self.image, offset)[0]
            if PB_READ[0] <= (value & ~1) < PB_READ[1]:
                stored.append((LOAD_BASE + offset, value))
        self.assertEqual(stored, [])

    def test_no_authenticated_bootloader_homolog(self) -> None:
        boot = BOOT_OFFICIAL.read_bytes()
        self.assertEqual((len(boot), sha256(boot)), BOOT_PIN)
        self.assertNotIn(
            self.image[PB_READ[0] - LOAD_BASE:PB_READ[1] - LOAD_BASE],
            boot,
        )
        self.assertNotIn(
            self.image[BUF_READ[0] - LOAD_BASE:BUF_READ[1] - LOAD_BASE],
            boot,
        )
        self.assertNotIn(END_OF_STREAM[1], boot)
        self.assertNotIn(IO_ERROR[1], boot)

    def test_host_behavior_matches_recovered_contract(self) -> None:
        harness = self.output / "pb_read_host.c"
        harness.write_text(HOST_HARNESS)
        executable = self.output / "pb_read_host"
        subprocess.run(
            [
                self.clang,
                "-std=c11",
                "-Wall",
                "-Wextra",
                "-Werror",
                "-I",
                str(ROOT),
                str(SOURCE),
                str(harness),
                "-o",
                str(executable),
            ],
            check=True,
            cwd=ROOT,
        )
        subprocess.run([str(executable)], check=True, cwd=ROOT)

    def test_production_object_and_six_absolute_relocations(self) -> None:
        output = self.output / "runtime_nanopb_read.o"
        subprocess.run(
            [
                self.clang,
                *TARGET_FLAGS,
                "-I",
                str(SOURCE.parent),
                "-c",
                str(SOURCE),
                "-o",
                str(output),
            ],
            check=True,
            cwd=ROOT,
        )
        self.assertGreater(output.stat().st_size, 0)
        version = subprocess.check_output(
            [self.clang, "--version"], text=True
        ).splitlines()[0]
        if version == APPLE_CLANG_VERSION:
            self.assertEqual(output.stat().st_size, 1192)
            self.assertEqual(sha256(output.read_bytes()), APPLE_OBJECT_SHA256)

        data, sections = self.apollo_overlay.parse_elf32(output)
        symbols = self.apollo_overlay.parse_elf32_symbols(data, sections)
        text_section = next(
            section for section in sections
            if section["name"] == ".text.open_cfw_nanopb_read"
        )
        text = data[
            text_section["offset"]:text_section["offset"] + text_section["size"]
        ]
        self.assertEqual((len(text), sha256(text)), TEXT_PIN)
        self.assertEqual(text_section["alignment"], 4)
        relocation_section = next(
            section for section in sections
            if section["name"] == ".rel.text.open_cfw_nanopb_read"
        )
        observed = []
        for offset in range(
            relocation_section["offset"],
            relocation_section["offset"] + relocation_section["size"],
            8,
        ):
            relocation_offset, information = struct.unpack_from("<II", data, offset)
            observed.append(
                (
                    relocation_offset,
                    information & 0xFF,
                    symbols[information >> 8]["name"],
                )
            )
        self.assertEqual(observed, [item[:3] for item in RELOCATIONS])
        undefined = sorted(
            symbol["name"] for symbol in symbols
            if symbol["name"] and symbol["section_index"] == 0
        )
        self.assertEqual(
            undefined,
            sorted({item[2] for item in RELOCATIONS}),
        )

        overlay = json.loads(OVERLAY.read_text())
        leaf = next(
            item for item in overlay["relocated_leaves"]
            if item.get("function") == "open_cfw_nanopb_read"
        )
        relocated, report = self.apollo_overlay.extract_in_place_function_section(
            output,
            "open_cfw_nanopb_read",
            runtime_address=PROFILE_PINS["apple-clang"]["runtime"],
            relocation_configs=leaf["relocations"],
            strict_relocation_contract=True,
        )
        self.assertEqual((len(relocated), sha256(relocated)), (158, RELOCATED_SHA256))
        self.assertEqual(report["relocation_count"], 6)

    def test_profile_placements_entry_patches_and_retained_seams(self) -> None:
        overlay = json.loads(OVERLAY.read_text())
        leaves = [
            item for item in overlay["relocated_leaves"]
            if item.get("function") == "open_cfw_nanopb_read"
        ]
        self.assertEqual(len(leaves), 1)
        leaf = leaves[0]
        self.assertTrue(leaf["strict_relocation_contract"])
        self.assertEqual(
            [
                (
                    item["offset"],
                    item["type"],
                    item["symbol"],
                    item["target_address"],
                )
                for item in leaf["relocations"]
            ],
            [
                (
                    offset,
                    "R_ARM_THM_MOVW_ABS_NC" if kind == 47 else "R_ARM_THM_MOVT_ABS",
                    symbol,
                    address,
                )
                for offset, kind, symbol, address in RELOCATIONS
            ],
        )
        for profile, pins in PROFILE_PINS.items():
            selected = leaf if profile == "apple-clang" else leaf["toolchain_profiles"][profile]
            self.assertEqual(
                selected["expected"],
                {
                    "size": 158,
                    "sha256": RELOCATED_SHA256,
                    "alignment": 4,
                    "offset": pins["offset"],
                    "unrelocated_sha256": TEXT_PIN[1],
                },
            )
            self.assertEqual(pins["runtime"], OVERLAY_RUNTIME_BASE + pins["offset"])
            patch = (
                self.apollo_overlay.encode_thumb_b_w(PB_READ[0], pins["runtime"])
                + b"\x00\xbf" * 73
            )
            self.assertEqual(len(patch), PB_READ[1] - PB_READ[0])
            self.assertEqual(patch[:4].hex(), pins["patch_prefix"])
            self.assertEqual(sha256(patch), pins["patch_sha256"])
            self.assertEqual(
                self.apollo_overlay.decode_thumb_branch(
                    PB_READ[0], patch[:4], link=False
                ),
                pins["runtime"],
            )

        patches = [
            item for item in overlay["patch_sites"]
            if item.get("target_function") == "open_cfw_nanopb_read"
        ]
        self.assertEqual(
            patches,
            [{
                "name": "replace_nanopb_read",
                "runtime_address": PB_READ[0],
                "expected_size": PB_READ[1] - PB_READ[0],
                "expected_sha256": PB_READ_SHA256,
                "branch": "b_w",
                "target_function": "open_cfw_nanopb_read",
            }],
        )

        record = json.loads(PROVENANCE.read_text())["selection"]["production_read_leaf"]
        self.assertEqual(record["local_source_size"], SOURCE_PIN[0])
        self.assertEqual(record["local_source_sha256"], SOURCE_PIN[1])
        self.assertEqual(record["local_header_size"], HEADER_PIN[0])
        self.assertEqual(record["local_header_sha256"], HEADER_PIN[1])
        self.assertEqual(record["stock_topology"]["external_direct_caller_count"], 13)
        self.assertEqual(record["stock_topology"]["interior_ingress_count"], 0)
        self.assertEqual(record["stock_topology"]["stored_pointer_ingress_count"], 0)
        self.assertFalse(record["bootloader_homolog"]["found"])
        self.assertEqual(len(record["relocations"]), 6)
        self.assertEqual(
            [item["target_address"] for item in record["retained_stock_seams"]],
            ["0x00787C70", "0x0048F3A5", "0x0078B690"],
        )

    def test_production_provenance_verifier_and_audit_scope(self) -> None:
        source = SOURCE.read_text()
        header = HEADER.read_text()
        audit = AUDIT.read_text()
        self.assertEqual((SOURCE.stat().st_size, sha256(SOURCE.read_bytes())), SOURCE_PIN)
        self.assertEqual((HEADER.stat().st_size, sha256(HEADER.read_bytes())), HEADER_PIN)
        self.assertNotIn("production-excluded", source)
        self.assertNotIn("production-excluded", header.lower())
        self.assertIn("open_cfw_nanopb_stock_buffer_read_identity", source)
        self.assertIn("0x0048F3A5", header)
        self.assertIn(UPSTREAM_DEFINITION_SHA256, audit)
        self.assertIn(PB_READ_SHA256, audit)
        self.assertIn(BUF_READ_SHA256, audit)
        self.assertIn("production source leaf", audit)
        self.assertIn("13 external direct callers", audit)
        self.assertIn("No authenticated bootloader homolog", audit)
        completed = subprocess.run(
            [sys.executable, str(VERIFIER)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout)
        self.assertEqual(
            completed.stdout,
            "nanopb 0.4.9 compatibility snapshot verification passed\n",
        )


if __name__ == "__main__":
    unittest.main()
