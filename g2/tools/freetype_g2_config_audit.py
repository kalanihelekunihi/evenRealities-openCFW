#!/usr/bin/env python3
"""Fail-closed, production-excluded G2 FreeType configuration audit.

This tool does not build or link FreeType.  It authenticates a small set of
configuration and integration facts directly against the official 2.2.6.10
Apollo image and emits a deterministic JSON report.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = (
    ROOT / "blobs" / "official" / "g2-2.2.6.10" / "ota_s200_firmware_ota.bin"
)
IMAGE_SIZE = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
MAPPING_BIAS = 0x00437FE0

SPAN_DIGESTS = {
    "default_module_table": (0x0073EEF8, 0x0073EF24, "1b7abc38c0b16cf1e5bcff6f2a4de87fd30d38cade102b276a42ccfe1041e2b1"),
    "tt_driver_class": (0x006DED34, 0x006DED94, "08612018ea9cb61fdaea5bbceb785d6d58f2f3c6eb55da1ca7d2ab92a3d134b6"),
    "tt_driver_init": (0x005F903C, 0x005F9048, "e9fa34c7e36a2d040315b03e434364a291c604ba644338fdcd2e3de12e37ecab"),
    "tt_property_set": (0x005EF0B0, 0x005EF0DE, "80331dce3cdff8477c6e80b5b31961f624f3e02c2515ef56d54dced3cdb599ff"),
    "tt_services": (0x00725060, 0x00725094, "dc49c81d5e183a747345d19fa7250883dafa3731e0e97a641f80afbedb5611ce"),
    "tt_gx_multi_masters": (0x007505A4, 0x007505CC, "8fc75309272a73a81a964b9e9c318d1606c1fc50cdcf193cda702854e8f876f6"),
    "tt_metrics_variations": (0x00767290, 0x007672B0, "91e58321ff4e9baa1a29dbcb113448eee03a3a3e7f5f13218db24972e06b0a03"),
    "ft_new_done_memory": (0x005676A0, 0x005676D2, "a1f8024e854df5dad7f79e8011acbb0e3056a19e6405902ed239304bc3a79c62"),
    "ft_memory_callbacks": (0x005676D4, 0x005676F6, "65f0808b9b6fbe2c85362912eda6f54b071632d289fe5f2dc5f88fa56c76ef20"),
    "xip_font_callback": (0x0046D238, 0x0046D29A, "5bb362b4b20a7fc85330bc57949be3927bdfec36ccec6e132362fb45a87d540a"),
    "xip_font_registration": (0x0046D29A, 0x0046D444, "08edaffae63c2d68bc8b9228e168c4190b1595f374ea53fe433af7738e85d475"),
    "font_manager_init": (0x0046D464, 0x0046D57C, "68e24de98ffe50dcc7c19b7d5ccaad70f72cd739e5fe674c79bb26a2c9cd3a9f"),
    "create_single_font": (0x0046CFA6, 0x0046D158, "b8ac81466debc40c8ea1fbd7ba593fa74ea452621a5036e84427323e118ba29a"),
    "ft_done_face": (0x00526814, 0x0052687E, "af8536a424c1e59043f426aea76b5a08cf38510924340cdf83c8761301c0d4b5"),
    "lv_face_cache_destroy": (0x004B2308, 0x004B2314, "4d53f8a42333cde3bb9032d39a957e34df67f71fcee207c33b88066da1660668"),
    "ft_open_face_failure_done": (0x00526594, 0x005265A2, "2db16886974b1ec1e44afdd59a4218d2501120bf615a632fa999f9a97f3281f6"),
    "ft_open_face_no_output_done": (0x005267C0, 0x005267D6, "0e1da4da7a9075516488ee4136d71531be01739c49461a6c0fb96a3841538039"),
    "face_internal_incremental": (0x005259BE, 0x00525ADA, "2a3eb27815750f4682cb524681e64a096917f8a61426256f8b049fa2e75afd48"),
    "smooth_lcd_emulation": (0x005E22E0, 0x005E2636, "e64dfdce6ebad7fab3f98a88de615bb4de47c0380abf896246011242e0381604"),
    "cff_driver_init": (0x005B004A, 0x005B00C4, "45a70c377d9169a6d25830e3ea2285e10ee4801318e1c2889d1534a6b93cd2ba"),
    "autofit_module_init": (0x005AB996, 0x005AB9D4, "dc98b716ffdb7213cf0290cbb947048cf0d225e2d3f83f266aa0ec61abf92a41"),
}

DEFAULT_MODULES = [
    ("autofitter", 0x00752520, 0x00000004, 56),
    ("truetype", 0x006DED34, 0x00000501, 68),
    ("cff", 0x006DCB74, 0x00000D01, 72),
    ("psaux", 0x00758A18, 0x00000000, 12),
    ("psnames", 0x00758A60, 0x00000000, 12),
    ("pshinter", 0x00758A3C, 0x00000000, 168),
    ("sfnt", 0x0075A3F8, 0x00000000, 12),
    ("smooth", 0x00718D9C, 0x00000002, 64),
    ("smooth-lcd", 0x00718DD8, 0x00000002, 64),
    ("smooth-lcdv", 0x00718E14, 0x00000002, 64),
]


def fail(message: str) -> None:
    raise SystemExit(f"G2 FreeType configuration audit failed: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


class Image:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.data = path.read_bytes()

    def offset(self, address: int) -> int:
        offset = address - MAPPING_BIAS
        require(0 <= offset < len(self.data), f"address outside image: 0x{address:08X}")
        return offset

    def bytes(self, start: int, end: int) -> bytes:
        require(start <= end, "invalid span")
        begin = self.offset(start)
        finish = end - MAPPING_BIAS
        require(finish <= len(self.data), f"span outside image: 0x{start:08X}..0x{end:08X}")
        return self.data[begin:finish]

    def u32(self, address: int) -> int:
        return struct.unpack_from("<I", self.data, self.offset(address))[0]

    def words(self, address: int, count: int) -> list[int]:
        return list(struct.unpack_from(f"<{count}I", self.data, self.offset(address)))

    def cstring(self, address: int, maximum: int = 512) -> str:
        offset = self.offset(address)
        end = self.data.find(b"\0", offset, offset + maximum)
        require(end >= 0, f"unterminated string at 0x{address:08X}")
        try:
            return self.data[offset:end].decode("ascii")
        except UnicodeDecodeError:
            fail(f"non-ASCII string at 0x{address:08X}")

    def thumb_bl_target(self, address: int) -> int:
        first, second = struct.unpack_from("<HH", self.data, self.offset(address))
        require(first & 0xF800 == 0xF000, f"not a Thumb BL first half at 0x{address:08X}")
        require(second & 0xD000 == 0xD000, f"not a Thumb BL second half at 0x{address:08X}")
        sign = (first >> 10) & 1
        j1 = (second >> 13) & 1
        j2 = (second >> 11) & 1
        i1 = (~(j1 ^ sign)) & 1
        i2 = (~(j2 ^ sign)) & 1
        immediate = (
            (sign << 24)
            | (i1 << 23)
            | (i2 << 22)
            | ((first & 0x3FF) << 12)
            | ((second & 0x7FF) << 1)
        )
        if immediate & (1 << 24):
            immediate -= 1 << 25
        return (address + 4 + immediate) & 0xFFFFFFFF

    def direct_thumb_branches_to(self, target: int) -> list[dict[str, Any]]:
        """Find every aligned immediate BL/B.W encoding targeting *target*.

        This deliberately scans data as well as code.  Requiring the complete
        result set therefore fails closed if either a real caller or an
        encoding-shaped data word appears or disappears in the official image.
        """

        references: list[dict[str, Any]] = []
        for offset in range(0, len(self.data) - 3, 2):
            first, second = struct.unpack_from("<HH", self.data, offset)
            if first & 0xF800 != 0xF000 or second & 0xD000 not in (0x9000, 0xD000):
                continue
            sign = (first >> 10) & 1
            j1 = (second >> 13) & 1
            j2 = (second >> 11) & 1
            i1 = (~(j1 ^ sign)) & 1
            i2 = (~(j2 ^ sign)) & 1
            immediate = (
                (sign << 24)
                | (i1 << 23)
                | (i2 << 22)
                | ((first & 0x3FF) << 12)
                | ((second & 0x7FF) << 1)
            )
            if immediate & (1 << 24):
                immediate -= 1 << 25
            address = MAPPING_BIAS + offset
            if (address + 4 + immediate) & 0xFFFFFFFF == target:
                references.append(
                    {
                        "address": f"0x{address:08X}",
                        "kind": "BL" if second & 0x1000 else "B.W",
                    }
                )
        return references

    def stored_u32_addresses(self, value: int) -> list[str]:
        needle = struct.pack("<I", value)
        addresses: list[str] = []
        offset = 0
        while True:
            offset = self.data.find(needle, offset)
            if offset < 0:
                return addresses
            addresses.append(f"0x{MAPPING_BIAS + offset:08X}")
            offset += 1


def authenticate(image: Image) -> dict[str, Any]:
    require(len(image.data) == IMAGE_SIZE, "official image size changed")
    require(hashlib.sha256(image.data).hexdigest() == IMAGE_SHA256, "official image SHA-256 changed")

    span_report: dict[str, dict[str, Any]] = {}
    for name, (start, end, expected) in SPAN_DIGESTS.items():
        digest = hashlib.sha256(image.bytes(start, end)).hexdigest()
        require(digest == expected, f"{name} span changed")
        span_report[name] = {
            "start": f"0x{start:08X}",
            "end": f"0x{end:08X}",
            "size": end - start,
            "sha256": digest,
        }

    default_module_pointers = image.words(0x0073EEF8, len(DEFAULT_MODULES) + 1)
    require(
        default_module_pointers == [item[1] for item in DEFAULT_MODULES] + [0],
        "default FreeType module table changed",
    )
    module_report: list[dict[str, Any]] = []
    for name, class_address, flags, object_size in DEFAULT_MODULES:
        class_header = image.words(class_address, 3)
        require(class_header[0] == flags, f"{name} module flags changed")
        require(class_header[1] == object_size, f"{name} module object size changed")
        require(image.cstring(class_header[2]) == name, f"{name} module name changed")
        module_report.append(
            {
                "name": name,
                "class": f"0x{class_address:08X}",
                "flags": f"0x{flags:08X}",
                "object_size": object_size,
            }
        )

    tt_class = image.words(0x006DED34, 24)
    require(tt_class[0] == 0x501, "TrueType class flags changed")
    require(tt_class[1] == 0x44, "TT_DriverRec size changed")
    require(image.cstring(tt_class[2]) == "truetype", "TrueType module name changed")
    require(tt_class[6] == 0x005F903D, "TrueType module initializer changed")
    require(tt_class[23] == 0x005EF1BD, "embedded-bitmap size selector missing")

    # Exact upstream-shaped initializer at 0x005F903C:
    # movs r1,#35; str r1,[r0,#0x40]; movs r1,#40;
    # str r1,[r0,#0x40]; movs r0,#0; bx lr.
    require(
        image.bytes(0x005F903C, 0x005F9048).hex()
        == "232101642821016400207047",
        "TrueType interpreter initializer no longer proves v40",
    )
    property_code = image.bytes(0x005EF0B0, 0x005EF0DE)
    require(property_code.startswith(bytes.fromhex("70b50400080015000026")), "property setter prologue changed")
    require(bytes.fromhex("2868232801d0282801d1") in property_code, "supported interpreter versions changed")
    require(image.cstring(0x00784BF0) == "FT_Stream_Open", "stream-support evidence changed")
    require(image.cstring(0x0078CDAC) == "warping", "autofit warper property changed")

    tt_service_words = image.words(0x00725060, 13)
    expected_service_names = [
        "font-format",
        "multi-masters",
        "metrics-variations",
        "truetype-engine",
        "tt-glyf",
        "properties",
    ]
    actual_service_names = [image.cstring(tt_service_words[index]) for index in range(0, 12, 2)]
    require(actual_service_names == expected_service_names, "TrueType service order changed")
    require(tt_service_words[12] == 0, "TrueType service table lost its terminator")
    require(image.cstring(tt_service_words[1]) == "TrueType", "font-format service value changed")
    require(tt_service_words[3] == 0x007505A4, "multi-masters service record moved")
    require(tt_service_words[5] == 0x00767290, "metrics-variations service record moved")

    multi_masters = image.words(0x007505A4, 10)
    metrics_variations = image.words(0x00767290, 8)
    require(multi_masters[:2] == [0, 0], "legacy MM slots changed")
    require(all(multi_masters[2:]), "GX variation service has a missing callable")
    require(
        [value != 0 for value in metrics_variations]
        == [True, False, False, True, False, False, False, True],
        "metrics-variation callable shape changed",
    )

    require(image.thumb_bl_target(0x00524320) == 0x005676A0, "FT_Init_FreeType memory call changed")
    require(image.thumb_bl_target(0x00524332) == 0x005274B2, "FT_New_Library call changed")
    require(image.thumb_bl_target(0x0052433E) == 0x005676C6, "FT_Init_FreeType error cleanup changed")
    require(image.thumb_bl_target(0x00524346) == 0x005242FC, "default-module call changed")
    require(image.u32(0x0056771C) == 0x20000354, "FreeType heap descriptor changed")
    heap_calls = {
        "FT_New_Memory allocation": (0x005676A6, 0x00484180),
        "FT_Done_Memory free": (0x005676CC, 0x0048429E),
        "FT_Memory alloc": (0x005676D8, 0x00484180),
        "FT_Memory realloc": (0x005676E6, 0x00484234),
        "FT_Memory free": (0x005676F0, 0x0048429E),
    }
    for label, (call, target) in heap_calls.items():
        require(image.thumb_bl_target(call) == target, f"{label} target changed")
    am_ftsystem_path = image.cstring(0x006D82B4)
    require(am_ftsystem_path.endswith(r"lvgl_ttf\src\am_ftsystem.c"), "am_ftsystem source path changed")
    require(image.u32(0x00567730) == 0x006D82B4, "am_ftsystem path reference changed")

    # FT_Done_Face is source-shaped down to its ownership topology.  The
    # three callers are the LVGL/FTC face-cache destructor and the two
    # FT_Open_Face cleanup paths.  No stored function pointer exists.
    done_face_callers = image.direct_thumb_branches_to(0x00526814)
    require(
        done_face_callers
        == [
            {"address": "0x004B2310", "kind": "BL"},
            {"address": "0x0052659C", "kind": "BL"},
            {"address": "0x005267D0", "kind": "BL"},
        ],
        "FT_Done_Face direct-caller topology changed",
    )
    require(not image.stored_u32_addresses(0x00526814), "even FT_Done_Face pointer appeared")
    require(not image.stored_u32_addresses(0x00526815), "Thumb FT_Done_Face pointer appeared")
    done_face_internal_calls = {
        "FT_List_Find": (0x0052684E, 0x005292E6),
        "FT_List_Remove": (0x0052685E, 0x00529324),
        "free_list_node": (0x00526866, 0x00529256),
        "destroy_face": (0x00526872, 0x005258A8),
    }
    for label, (call, target) in done_face_internal_calls.items():
        require(image.thumb_bl_target(call) == target, f"FT_Done_Face {label} call changed")

    # The 0x696E6372 ('incr') parameter tag, 0x44-byte face-internal
    # allocation, and incremental pointer at internal+0x34 exactly select
    # FT_CONFIG_OPTION_INCREMENTAL in 2.9.1.  The emulated LCD renderer is
    # the mutually exclusive !FT_CONFIG_OPTION_SUBPIXEL_RENDERING body.
    require(image.u32(0x005262A8) == 0x696E6372, "incremental parameter tag changed")
    require(
        image.bytes(0x00525A0C, 0x00525A1E).hex()
        == "01aa4421029803f099fb0500019800280ad1",
        "face-internal allocation shape changed",
    )
    require(
        image.bytes(0x00525A36, 0x00525A50).hex()
        == "51f83200dff86cc8604506d101ebc2004068d7f880c0ccf83400",
        "incremental parameter-selection loop changed",
    )
    require(
        image.bytes(0x005E2416, 0x005E245C).hex()
        == "002c00f084800020d9f800000590d9f80400d9f8081000910321b0fbf1f4d9f80c002044c9f80c0006a9786bba6b904702900298002840f0c68000227ff01401039845f769fb",
        "LCD three-pass emulation changed",
    )

    # CFF_CONFIG_OPTION_OLD_ENGINE changes the initializer's first field
    # between FT_HINTING_FREETYPE (0) and FT_HINTING_ADOBE (1).  The class
    # points to this initializer and the body stores 1 at driver+0x1c.
    cff_class = image.words(0x006DCB74, 7)
    require(cff_class[6] == 0x005B004B, "CFF module initializer changed")
    require(
        image.bytes(0x005B004A, 0x005B0054).hex() == "01b481b001990120c861",
        "CFF default hinting engine changed",
    )

    # AF_STYLE_FALLBACK expands to AF_STYLE_HANI_DFLT only with CJK.  In
    # authenticated 2.9.1, HANI_DFLT is enum 79 without the four guarded
    # Indic styles and enum 83 with them.  The module initializer stores 83,
    # proving that both AF_CONFIG_OPTION_CJK and AF_CONFIG_OPTION_INDIC are on.
    require(
        image.bytes(0x005AB996, 0x005AB99E).hex() == "5321c1601e210161",
        "autofit fallback/default initializer changed",
    )

    # A conventional FT_Done_FreeType must reach the separately compiled
    # FT_Done_Memory body.  The only immediate branch is FT_Init_FreeType's
    # constructor-failure cleanup, and neither even nor Thumb pointers are
    # stored.  This does not justify inventing an entry address.
    done_memory_references = image.direct_thumb_branches_to(0x005676C6)
    require(
        done_memory_references == [{"address": "0x0052433E", "kind": "BL"}],
        "FT_Done_Memory reference topology changed",
    )
    require(not image.stored_u32_addresses(0x005676C6), "even FT_Done_Memory pointer appeared")
    require(not image.stored_u32_addresses(0x005676C7), "Thumb FT_Done_Memory pointer appeared")

    # XIP font headers are in external address spaces, not inside this image.
    require(image.u32(0x0046D614) == 0x80100000, "background XIP font base changed")
    require(image.u32(0x0046D640) == 0x80700000, "foreground XIP font base changed")
    require(image.u32(0x0046D62C) == 0x20002C00, "background font descriptor changed")
    require(image.u32(0x0046D644) == 0x20002C24, "foreground font descriptor changed")
    require(image.u32(0x0046D64C) == 0x20002C48, "background font configuration array changed")
    require(image.u32(0x0046D664) == 0x20002C78, "foreground font configuration array changed")
    require(bytes.fromhex("b0f15a3f") in image.bytes(0x0046D29A, 0x0046D444), "XIP header magic check changed")
    require(image.thumb_bl_target(0x0046D470) == 0x0046CAE0, "background font-chain registration changed")
    require(image.thumb_bl_target(0x0046D4CE) == 0x0046CAE0, "foreground font-chain registration changed")
    require(
        image.bytes(0x0046D014, 0x0046D026).hex()
        == "606800282fd0a37a22890121606844f03bfe",
        "FreeType font configuration layout changed",
    )
    require(image.thumb_bl_target(0x0046D022) == 0x004B1C9C, "FreeType font creation call changed")
    require(image.thumb_bl_target(0x0046D1E0) == 0x004B1EF6, "FreeType font deletion call changed")
    font_manager_path = image.cstring(0x006FB45C)
    require(font_manager_path.endswith(r"app\gui\common\lvgl_font_manager.c"), "font-manager source path changed")

    try:
        report_path = image.path.relative_to(ROOT).as_posix()
    except ValueError:
        report_path = image.path.as_posix()

    return {
        "schema_version": 1,
        "status": "production-excluded static recovery",
        "image": {
            "path": report_path,
            "size": len(image.data),
            "sha256": IMAGE_SHA256,
            "mapping_bias": f"0x{MAPPING_BIAS:08X}",
        },
        "configuration": {
            "built_in_modules": module_report,
            "true_type": {
                "bytecode_interpreter": True,
                "interpreter_default": 40,
                "supported_interpreter_versions": [35, 40],
                "TT_CONFIG_OPTION_SUBPIXEL_HINTING": 2,
                "infinality_v38": False,
                "minimal_v40": True,
                "TT_CONFIG_OPTION_GX_VAR_SUPPORT": True,
                "TT_CONFIG_OPTION_EMBEDDED_BITMAPS": True,
            },
            "base": {
                "FT_CONFIG_OPTION_PIC": False,
                "FT_CONFIG_OPTION_ENVIRONMENT_PROPERTIES": False,
                "FT_CONFIG_OPTION_INCREMENTAL": True,
                "FT_CONFIG_OPTION_SUBPIXEL_RENDERING": False,
                "stream_support": True,
            },
            "cff": {
                "CFF_CONFIG_OPTION_OLD_ENGINE": False,
                "default_hinting_engine": "Adobe",
            },
            "autofit": {
                "AF_CONFIG_OPTION_USE_WARPER": True,
                "AF_CONFIG_OPTION_CJK": True,
                "AF_CONFIG_OPTION_INDIC": True,
                "fallback_style": {
                    "name": "AF_STYLE_HANI_DFLT",
                    "enum": 83,
                    "qualification": "HANI_DFLT is 79 without the four guarded Indic styles and 83 with them in authenticated 2.9.1",
                },
                "evidence": "warping property is present at 0x0078CDAC under its 2.9.1 compile guard",
            },
            "gx_variations": {
                "multi_masters_record": "0x007505A4",
                "multi_masters_callable_slots": 8,
                "metrics_variations_record": "0x00767290",
                "metrics_variations_callable_slots": 3,
                "scope": "fvar/gvar/cvar/avar plus HVAR/VVAR/MVAR service paths selected by the 2.9.1 guard",
            },
        },
        "allocator": {
            "source_path": am_ftsystem_path,
            "FT_Memory_size": 16,
            "heap_descriptor": "0x20000354",
            "generic_allocate": "0x00484180",
            "generic_reallocate": "0x00484234",
            "generic_free": "0x0048429E",
            "callbacks": {
                "alloc": "0x005676D4",
                "realloc": "0x005676E0",
                "free": "0x005676EC",
            },
            "lifecycle": {
                "FT_Init_FreeType": "0x0052431C",
                "FT_New_Memory": "0x005676A0",
                "FT_Done_Memory": "0x005676C6",
                "FT_New_Library": "0x005274B2",
                "FT_Add_Default_Modules": "0x005242FC",
                "lv_freetype_font_create": "0x004B1C9C",
                "lv_freetype_font_delete": "0x004B1EF6",
                "FT_Done_Face": {
                    "entry": "0x00526814",
                    "end": "0x0052687E",
                    "direct_callers": done_face_callers,
                    "caller_roles": [
                        "LVGL/FTC face-cache destructor",
                        "FT_Open_Face failure cleanup",
                        "FT_Open_Face no-output cleanup",
                    ],
                },
                "FT_Done_FreeType": {
                    "entry": None,
                    "stock_entry_recoverable": False,
                    "done_memory_direct_references": done_memory_references,
                    "qualification": "the only direct FT_Done_Memory reference is FT_Init_FreeType failure cleanup and no stored pointer exists; no stock FT_Done_FreeType entry can be assigned without guessing",
                },
            },
        },
        "abi": {
            "compiler_family": "IAR Arm (source-tree evidence)",
            "instruction_set": "Thumb-2",
            "byte_order": "little-endian",
            "pointer_bits": 32,
            "calling_convention": "Arm EABI register calling convention",
            "qualification": "exact IAR version, optimization, FPU ABI, preprocessor command, and linker flags are not recoverable from the raw image",
        },
        "font_registration": {
            "manager_source_path": font_manager_path,
            "external_headers": [
                {
                    "role": "background",
                    "base": "0x80100000",
                    "descriptor": "0x20002C00",
                    "configuration_array": "0x20002C48",
                },
                {
                    "role": "foreground",
                    "base": "0x80700000",
                    "descriptor": "0x20002C24",
                    "configuration_array": "0x20002C78",
                },
            ],
            "header_magic": "0x5A5A5A5A",
            "header_name_offset": 4,
            "header_font_pointer_offset": 52,
            "header_size_fields": [56, 58],
            "font_chain_entries_per_role": 4,
            "configuration_record": {
                "size": 12,
                "type": {"offset": 0, "size": 1},
                "font_pointer_or_face_path": {"offset": 4, "size": 4},
                "pixel_size": {"offset": 8, "size": 2},
                "style": {"offset": 10, "size": 1},
                "type_semantics": {
                    "0": "native lv_font_t pointer",
                    "1": "FreeType face path passed to lv_freetype_font_create",
                    "2": "binary-font path disabled in this build",
                },
            },
            "qualification": "external XIP payloads and runtime-initialized configuration arrays are absent from the official main image, so font names, hashes, formats, and FreeType face paths remain unresolved",
        },
        "spans": span_report,
        "unresolved": [
            "complete FT_CONFIG_OPTION_* state outside the proven subset",
            "optional compression helpers",
            "an exact stock FT_Done_FreeType entry (no conventional retained topology was found)",
            "IAR version and exact compiler/linker flags",
            "external font payload identities and runtime configuration-array contents",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    report = authenticate(Image(args.image.resolve()))
    if args.compact:
        print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    else:
        print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
