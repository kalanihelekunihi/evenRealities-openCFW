#!/usr/bin/env python3
"""Fail-closed LVGL lineage/configuration audit for G2 firmware 2.2.6.10.

The analyzer reads only the pinned official Apollo-main payload.  It does not
contain a transport, programmer, signer, device, erase, or write path.

The result deliberately distinguishes three claims:

* selected G2 routines are source-equivalent to official LVGL development
  history;
* the complete G2 LVGL tree is a vendor fork with Ambiq and Even layers; and
* the released v9.3.0 tag is a useful reference, but is provably too new to be
  the exact source snapshot used by this firmware.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = (
    ROOT / "blobs" / "official" / "g2-2.2.6.10" / "ota_s200_firmware_ota.bin"
)
IMAGE_SIZE = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
LOAD_BASE = 0x00437FE0


class AuditError(RuntimeError):
    """Raised when the official image or a recovered invariant drifts."""


PINNED_SPANS = {
    "lv_tick_cluster": (
        0x00473474,
        0x004734BC,
        "4cd2008019ed18c308f6d25fe15694db454e820ce94991e8deeed9b815966c01",
    ),
    "lv_global_init": (
        0x004734CC,
        0x00473548,
        "0354fab1a6d848856adb4017ad8343717f1c40bd59976b81526c7d4518b5c154",
    ),
    "lv_init": (
        0x00473548,
        0x00473626,
        "864a6ef89d19b8f7dfb79aa84d4f85cf0df9fd1043a9f9104ad30c00c402fe33",
    ),
    "ambiq_display_setup": (
        0x00473782,
        0x0047381E,
        "d0f3a63dee7ba606340319bff6f4f094954e1834d3a60aac01e20e8732f13779",
    ),
    "lv_display_create": (
        0x0044F7C0,
        0x0044FA1A,
        "1756df60b038522fdc9d2ac9681818f045db8a0dc2046fb4691a10a59d1472ad",
    ),
    "lv_async_call": (
        0x00484014,
        0x00484052,
        "4a3b8927b10dd11d3b872207c2138dd85494060f948727dc021025c3b57c174f",
    ),
    "lv_async_call_cancel": (
        0x00484052,
        0x004840AA,
        "67cd3979de3365531652c6de47f55bbab9541e753c5091a8423229635ce99900",
    ),
    "lv_async_timer_cb": (
        0x004840AC,
        0x004840C6,
        "39c550823fd1d0bb1b80f29119c66bd33d2751de30c9d4c2ccc987bd99e5c8d8",
    ),
}


# These short windows are semantics-bearing operands, not loose byte searches.
# Each lies inside a complete hash-pinned function above.
INSTRUCTION_PINS = {
    # mov.w r1,#0x1ec; ... mov.w r1,#0x31c; ... movs r1,#0xdc
    0x0047350C: bytes.fromhex("4ff4f671"),
    0x00473516: bytes.fromhex("4ff44771"),
    0x00473520: bytes.fromhex("dc21"),
    # layout_count=3; style_last=0x89; event_last=0x42
    0x00473534: bytes.fromhex("0320a0658920e06242202067"),
    # Ambiq display-port allocation/configuration: 0x1c-byte draw buffer view,
    # 0x14400 output bytes, format A4=13, height 288, width 576.
    0x00473786: bytes.fromhex("1c20"),
    0x00473792: bytes.fromhex("5ff4a231"),
    0x0047379E: bytes.fromhex("0d234ff490724ff41071"),
    # Native LVGL buffer create: format L8=6, height 288, width 576.
    0x004737E2: bytes.fromhex("06224ff490714ff41070"),
    # Official lv_display_create topology compiles antialiasing=false for
    # LV_COLOR_DEPTH <= 8, then assigns LV_COLOR_FORMAT_NATIVE=6.  In the
    # interval's lv_color.h only LV_COLOR_DEPTH=8 maps native to L8=6.
    0x0044F828: bytes.fromhex("a06b30f48030a063"),
    0x0044F834: bytes.fromhex("062084f83c00"),
    # lv_async_info_t allocation is two 32-bit pointers.
    0x0048401A: bytes.fromhex("0820"),
}


LV_INIT_CALLS = [
    0x0044D25C,  # warning logger, already-initialized path
    0x004734CC,  # lv_global_init
    0x0048AA60,
    0x004C6D04,
    0x0049ACB0,
    0x00464330,
    0x004C6D8C,
    0x004546DC,
    0x004503A4,
    0x0044D32C,
    0x004B1B98,  # lv_freetype_init(0x40)
    0x0048438C,  # generic draw initialization
    0x004C73D6,  # Ambiq draw/backend initialization
    0x0044B90C,
    0x00488F4C,
    0x004C794C,
    0x0044D25C,  # UTF-8 warning
    0x0044D25C,  # endian assertion/fatal path
    0x004C8F0A,
    0x004C8EFC,
    0x004C91A8,
]


LVGL_PATH_RE = re.compile(
    rb"D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9\.3\\"
    rb"[^\x00]{1,300}\.c(?=\x00)"
)

PATH_CLASS_COUNTS = {
    "official_lvgl_core_or_optional_module": 61,
    "official_lvgl_freetype_wrapper": 4,
    "ambiq_draw_backend_inside_lvgl_tree": 11,
    "ambiq_display_port_outside_lvgl_tree": 1,
    "ambiq_freetype_system_glue_outside_lvgl_tree": 1,
}

REQUIRED_RELATIVE_PATHS = {
    r"LVGL\src\lv_init.c",
    r"LVGL\src\misc\cache\lv_cache_lru_rb.c",
    r"LVGL\src\misc\lv_array.c",
    r"LVGL\src\misc\lv_iter.c",
    r"LVGL\src\misc\lv_rb.c",
    r"LVGL\src\osal\lv_freertos.c",
    r"LVGL\src\layouts\flex\lv_flex.c",
    r"LVGL\src\layouts\grid\lv_grid.c",
    r"LVGL\src\libs\bin_decoder\lv_bin_decoder.c",
    r"LVGL\src\libs\bmp\lv_bmp.c",
    r"LVGL\src\libs\fsdrv\lv_fs_littlefs.c",
    r"LVGL\src\libs\freetype\lv_freetype.c",
    r"LVGL\src\draw\ambiq\lv_draw_ambiq.c",
    r"LVGL\src\draw\ambiq\lv_draw_ambiq_vector_font.c",
    r"lvgl_ambiq_porting\lv_ambiq_display.c",
    r"lvgl_ambiq_demo\lvgl_ttf\src\am_ftsystem.c",
}

# Boundaries outside the third-party LVGL root.  These establish that the
# platform display manager, input stack, font manager and Even UI are not part
# of an upstream LVGL source import.
FIRST_PARTY_PATHS = {
    0x006ECB68: r"D:\01_workspace\s200_ap510b_iar_git\platform\display_mgr\displaydrv_manager.c",
    0x006F5E5C: r"D:\01_workspace\s200_ap510b_iar_git\platform\input\service_input_manager.c",
    0x006FB45C: r"D:\01_workspace\s200_ap510b_iar_git\app\gui\common\lvgl_font_manager.c",
    0x006FAD0C: r"D:\01_workspace\s200_ap510b_iar_git\app\gui\common\generic_animation.c",
}


UPSTREAM = {
    "repository": "https://github.com/lvgl/lvgl.git",
    "license": {
        "spdx": "MIT",
        "path": "LICENCE.txt",
        "git_blob_sha1": "690d2dfd7e97ca8e06535a496761c5e81aece439",
        "size": 1072,
        "sha256": "27a80bd36832ab42d35ad60c08b2b230a807a9bc0d58e94ec1531543dc49cbe8",
    },
    "release_reference": {
        "tag": "v9.3.0",
        "annotated_tag_object": "108e5aff3c90cc4d969331ed61aff2bbd365d430",
        "tag_cryptographically_signed": False,
        "commit": "c033a98afddd65aaafeebea625382a94020fe4a7",
        "tree": "66bc30b9a8ecd144ba8b9ebfc984ac3028f55767",
        "commit_date": "2025-06-03T13:57:17+02:00",
        "lv_version_h_blob": "8bbd5506ef8c8c298c3c761fb58d08633dfcb5a2",
        "version": "9.3.0",
        "version_info": "",
    },
    "source_equivalence_floor": {
        "commit": "60d976c466e8619326edfbd193fd2a046c10113f",
        "tree": "37e23ad4b228c68133e3f65a8577c5028a4ea0c8",
        "date": "2025-03-25T12:18:02+01:00",
        "subject": "feat(draw/sw): add support for vector fonts (#7560)",
        "first_decisive_state": "LV_STYLE_LAST_BUILT_IN_PROP == 137",
    },
    "source_equivalence_ceiling": {
        "commit": "344c7c318047b7348e1be8572a9fd4260c251cfa",
        "tree": "2c76db856ec570f3ee12565181e5cf52bdd33d78",
        "date": "2025-04-10T14:25:23+02:00",
        "subject": "fix(area): test and fix lv_area_diff edge case (#7907)",
        "last_decisive_state": "LV_EVENT_LAST == 66",
    },
    "first_excluded_commit": {
        "commit": "f35f0859eb477c79906cf531ed394306119097f8",
        "tree": "7707c88edc0ea3e89db733b02ed1c2078330239d",
        "date": "2025-04-10T20:29:54+08:00",
        "subject": "feat(disp): support subscription and unsubscription of vsync event (#7487)",
        "incompatible_change": "adds LV_EVENT_VSYNC_REQUEST; LV_EVENT_LAST changes from 66 to 67",
    },
    "later_cache_refactor": {
        "commit": "4b6dac865eea3c1d2ad253897fbaa9e0f758c5db",
        "tree": "feff0c00a751c1a282fae7d9979a132fcfe0ef1d",
        "date": "2025-04-24T12:24:54+08:00",
        "change": "deletes/renames src/misc/cache/lv_cache_lru_rb.c",
    },
    "stable_interval_blobs": {
        "LICENCE.txt": "690d2dfd7e97ca8e06535a496761c5e81aece439",
        "lv_version.h": "6aa02efb6f0dae5919a86fe78532a9f8cee7fa01",
        "src/core/lv_global.h": "4515c01c9b80779a7d61701e28b4fb3554a92ba9",
        "src/display/lv_display.c": "695d38b2652decc2362b283dd69ee08b8b4f7582",
        "src/display/lv_display_private.h": "d831ec4861e73f53da86432fb221804f71fa5c79",
        "src/draw/lv_draw_buf.h": "c36e0a612f7fb46f69f5a7a4ae97000dd76a3837",
        "src/misc/cache/lv_cache_lru_rb.c": "be651dda9c22343444662acd204ec8a5ca37d516",
        "src/misc/lv_async.c": "b2e718dd3a3aefe274b6b962714c4e010bbd7f91",
        "src/misc/lv_event.h": "ca52d18e454b745ea5302d32e5f49152de9e9643",
        "src/misc/lv_style.h": "2da6cd1f8c903aebc142b473f4b1f846deb2073f",
    },
    "endpoint_variant_blobs": {
        "src/misc/lv_color.h": {
            "floor": "c5ea01f82feb95f10e9c61788b42417477a1a51b",
            "ceiling": "1a160b4a56b8a7bc01b59a20b72ae35f5fff518c",
            "stable_semantic": (
                "both map LV_COLOR_DEPTH=8 to LV_COLOR_FORMAT_NATIVE="
                "LV_COLOR_FORMAT_L8 (ordinal 6)"
            ),
        },
    },
}


def _slice(data: bytes, start: int, end: int) -> bytes:
    first = start - LOAD_BASE
    last = end - LOAD_BASE
    if first < 0 or last < first or last > len(data):
        raise AuditError(f"run span 0x{start:08x}..0x{end:08x} is outside image")
    return data[first:last]


def _cstr(data: bytes, run: int, limit: int = 512) -> str:
    raw = _slice(data, run, min(run + limit, LOAD_BASE + len(data)))
    end = raw.find(b"\0")
    if end < 0:
        raise AuditError(f"unterminated string at 0x{run:08x}")
    try:
        return raw[:end].decode("ascii")
    except UnicodeDecodeError as exc:
        raise AuditError(f"non-ASCII string at 0x{run:08x}") from exc


def _thumb_branch_target(data: bytes, run: int) -> int:
    first, second = struct.unpack("<HH", _slice(data, run, run + 4))
    if first & 0xF800 != 0xF000 or second & 0xD000 not in (0x9000, 0xD000):
        raise AuditError(f"not an immediate Thumb branch at 0x{run:08x}")
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
    return (run + 4 + immediate) & 0xFFFFFFFF


def _direct_branches(data: bytes, start: int, end: int) -> list[dict[str, int | str]]:
    result: list[dict[str, int | str]] = []
    for run in range(start, end - 3, 2):
        first, second = struct.unpack("<HH", _slice(data, run, run + 4))
        if first & 0xF800 != 0xF000 or second & 0xD000 not in (0x9000, 0xD000):
            continue
        result.append(
            {
                "run": run,
                "kind": "BL" if second & 0x1000 else "B.W",
                "target": _thumb_branch_target(data, run),
            }
        )
    return result


def _classify_relative_path(relative: str) -> str:
    if relative.startswith("LVGL\\src\\draw\\ambiq\\"):
        return "ambiq_draw_backend_inside_lvgl_tree"
    if relative.startswith("LVGL\\src\\libs\\freetype\\"):
        return "official_lvgl_freetype_wrapper"
    if relative.startswith("LVGL\\src\\"):
        return "official_lvgl_core_or_optional_module"
    if relative == r"lvgl_ambiq_porting\lv_ambiq_display.c":
        return "ambiq_display_port_outside_lvgl_tree"
    if relative == r"lvgl_ambiq_demo\lvgl_ttf\src\am_ftsystem.c":
        return "ambiq_freetype_system_glue_outside_lvgl_tree"
    raise AuditError(f"unclassified LVGL-root path: {relative}")


def _path_inventory(data: bytes) -> dict[str, Any]:
    prefix = "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\"
    paths: list[dict[str, Any]] = []
    counts: dict[str, int] = {key: 0 for key in PATH_CLASS_COUNTS}
    seen: set[str] = set()
    for match in LVGL_PATH_RE.finditer(data):
        value = match.group().decode("ascii")
        if value in seen:
            raise AuditError(f"duplicate LVGL source path: {value}")
        seen.add(value)
        if not value.startswith(prefix):
            raise AuditError("LVGL path prefix parser drift")
        relative = value[len(prefix):]
        classification = _classify_relative_path(relative)
        counts[classification] += 1
        paths.append(
            {
                "file_offset": match.start(),
                "run": LOAD_BASE + match.start(),
                "relative": relative,
                "classification": classification,
            }
        )
    if len(paths) != 78:
        raise AuditError(f"expected 78 unique LVGL-root source paths, found {len(paths)}")
    if counts != PATH_CLASS_COUNTS:
        raise AuditError(f"LVGL path classification changed: {counts!r}")
    relative_paths = {item["relative"] for item in paths}
    missing = sorted(REQUIRED_RELATIVE_PATHS - relative_paths)
    if missing:
        raise AuditError(f"required LVGL paths missing: {missing!r}")
    return {"total_unique_paths": len(paths), "class_counts": counts, "paths": paths}


def audit(data: bytes) -> dict[str, Any]:
    if len(data) != IMAGE_SIZE:
        raise AuditError(f"official image size changed: {len(data)}")
    digest = hashlib.sha256(data).hexdigest()
    if digest != IMAGE_SHA256:
        raise AuditError(f"official image SHA-256 changed: {digest}")

    spans: dict[str, dict[str, Any]] = {}
    for name, (start, end, expected) in PINNED_SPANS.items():
        actual = hashlib.sha256(_slice(data, start, end)).hexdigest()
        if actual != expected:
            raise AuditError(f"{name} span changed")
        spans[name] = {
            "start": start,
            "end": end,
            "size": end - start,
            "sha256": actual,
        }

    for run, expected in INSTRUCTION_PINS.items():
        if _slice(data, run, run + len(expected)) != expected:
            raise AuditError(f"semantics-bearing instruction window changed at 0x{run:08x}")

    init_branches = _direct_branches(data, 0x00473548, 0x00473626)
    init_targets = [int(item["target"]) for item in init_branches]
    if init_targets != LV_INIT_CALLS:
        raise AuditError(f"lv_init call topology changed: {init_targets!r}")

    paths = _path_inventory(data)
    first_party: list[dict[str, Any]] = []
    for run, expected in FIRST_PARTY_PATHS.items():
        actual = _cstr(data, run)
        if actual != expected:
            raise AuditError(f"first-party boundary path changed at 0x{run:08x}")
        first_party.append({"run": run, "path": actual})

    return {
        "schema_version": 1,
        "component": "LVGL 9.3.0-dev-compatible vendor stack",
        "analysis_mode": "read-only; no hardware or flash operation",
        "image": {
            "path": str(DEFAULT_IMAGE.relative_to(ROOT)),
            "size": len(data),
            "sha256": digest,
            "run_address_rule": "run = file_offset + 0x00437FE0",
        },
        "version_recovery": {
            "exact_vendor_commit_or_tree": None,
            "exact_released_tag": None,
            "classification": "vendor fork of official LVGL 9.3.0-dev lineage",
            "narrowest_official_history_source_equivalence_interval": {
                "first": UPSTREAM["source_equivalence_floor"]["commit"],
                "last": UPSTREAM["source_equivalence_ceiling"]["commit"],
                "first_date": UPSTREAM["source_equivalence_floor"]["date"],
                "last_date": UPSTREAM["source_equivalence_ceiling"]["date"],
            },
            "lower_bound": (
                "G2 stores LV_STYLE_LAST_BUILT_IN_PROP=137; official history first "
                "reaches that value at 60d976c"
            ),
            "upper_bound": (
                "G2 stores LV_EVENT_LAST=66; f35f0859 adds VSYNC_REQUEST and changes "
                "the value to 67"
            ),
            "corroboration": [
                "FreeType initialization precedes draw initialization (post-a4d70c behavior)",
                "src/misc/cache/lv_cache_lru_rb.c is retained (pre-4b6dac layout)",
                "lv_version.h is the interval's 9.3.0-dev blob, not the release blob",
            ],
            "why_v9_3_0_tag_is_not_exact": [
                "release tag has LV_EVENT_LAST=67, while G2 stores 66",
                "release tag no longer contains src/misc/cache/lv_cache_lru_rb.c",
                "release lv_version.h has empty VERSION_INFO; interval blob says dev",
                "Ambiq backend and Even/platform files are outside official LVGL",
            ],
            "why_interval_cannot_select_one_commit": (
                "The mapped lv_global_init/lv_async behavior and stable ABI headers are "
                "identical across the interval; the interval's lv_init.c change is in a "
                "deinitialization branch not retained by these mapped G2 bodies."
            ),
        },
        "version_discriminators": {
            "LV_STYLE_LAST_BUILT_IN_PROP": 137,
            "LV_EVENT_LAST": 66,
            "LV_LAYOUT_LAST": 3,
            "freetype_cache_glyph_count": 64,
            "freetype_initialized_before_draw": True,
            "legacy_cache_lru_rb_path_present": True,
        },
        "effective_configuration": {
            "LV_COLOR_DEPTH": 8,
            "LV_COLOR_FORMAT_NATIVE": {"ordinal": 6, "name": "LV_COLOR_FORMAT_L8", "bpp": 8},
            "ambiq_output_color_format": {"ordinal": 13, "name": "LV_COLOR_FORMAT_A4", "bpp": 4},
            "LV_USE_OS": "LV_OS_FREERTOS",
            "LV_USE_FREETYPE": True,
            "LV_USE_FLEX": True,
            "LV_USE_GRID": True,
            "LV_USE_FS_LITTLEFS": True,
            "LV_USE_BMP": True,
            "built_in_bin_decoder": True,
            "LV_USE_LOG": True,
            "LV_LOG_LEVEL": "LV_LOG_LEVEL_WARN",
            "LV_USE_ASSERT_NULL": True,
            "LV_BIG_ENDIAN_SYSTEM": 0,
            "enum_abi": "short enums (-fshort-enums-compatible)",
            "display": {"width": 576, "height": 288, "output_allocation": 0x14400},
            "notes": [
                "The complete hash-pinned lv_display_create body clears antialiasing "
                "and stores native format ordinal 6; official interval source and both "
                "endpoint lv_color.h blobs make LV_COLOR_DEPTH=8 the unique mapping.",
                "The FreeRTOS source file is compiled inside its LV_OS_FREERTOS guard.",
                "Warning calls survive while lv_init INFO/TRACE calls do not.",
                "The exact FreeRTOS task-notify selection and many unused widget switches remain unresolved.",
            ],
        },
        "abi": {
            "sizeof_lv_global_t": 0x1EC,
            "sizeof_lv_display_t": 0x31C,
            "sizeof_lv_indev_t": 0xDC,
            "sizeof_lv_draw_buf_t": 0x1C,
            "pointer_size": 4,
            "enum_abi": "short enums",
            "lv_async_info_t": {"size": 8, "fields": ["callback@0", "user_data@4"]},
            "qualification": (
                "These are G2 vendor-configuration ABI pins. They must be asserted when "
                "compiling upstream source; they do not make an unconfigured tag drop-in safe."
            ),
        },
        "mapped_source_equivalent_core": {
            "lv_global_init": {
                "observed": [
                    "zero complete lv_global_t",
                    "initialize display and input linked lists using recovered sizes",
                    "set memory sentinel, style refresh, layout/style/event sentinels",
                    "seed random state with 0x1234ABCD",
                ],
                "official_comparator": "src/lv_init.c static lv_global_init",
            },
            "lv_init": {
                "observed": [
                    "already-initialized warning",
                    "global/memory/draw-buffer/OS/timer/fs/layout/animation/group initialization",
                    "FreeType before generic and Ambiq draw initialization",
                    "binary decoder and little-endian checks",
                ],
                "official_comparator": "src/lv_init.c with vendor Ambiq init inserted",
            },
            "lv_async_cluster": {
                "observed": [
                    "two-pointer info allocation",
                    "zero-period one-shot timer",
                    "delete-before-free cancellation and callback ordering",
                    "remove every exact callback/user-data match",
                ],
                "official_comparator": "src/misc/lv_async.c blob b2e718d",
            },
        },
        "pinned_spans": spans,
        "lv_init_direct_branches": init_branches,
        "path_inventory": paths,
        "boundary_classification": {
            "official_lvgl_reusable_baseline": (
                "core, misc/container, display, standard draw, widgets, flex/grid, and "
                "selected optional LVGL adapters within the proven development interval"
            ),
            "lvgl_freetype_wrappers": (
                "four official LVGL wrapper translation units; the FreeType 2.9.1 library "
                "and am_ftsystem.c are separate provenance/configuration boundaries"
            ),
            "ambiq_backend": (
                "eleven src/draw/ambiq files plus lv_ambiq_display.c; absent from official "
                "LVGL and not covered by its commit/tree identity"
            ),
            "even_and_platform": (
                "display manager, input manager, font manager, animation and app/UI paths "
                "are first-party integration, not upstream LVGL"
            ),
            "first_party_path_pins": first_party,
        },
        "upstream_provenance": UPSTREAM,
        "integration_policy": [
            "Import/pin an official commit chosen from the proven interval, not v9.3.0 by label alone.",
            "Compile with G2 ABI static assertions before linking any opaque caller.",
            "Keep Ambiq draw/display, FreeType, display manager, input and Even UI as separate ports.",
            "Treat later v9.3.0 changes as explicit migrations requiring ABI/behavior tests.",
        ],
    }


def _load(path: Path = DEFAULT_IMAGE) -> bytes:
    try:
        return path.read_bytes()
    except OSError as exc:
        raise AuditError(f"cannot read image {path}: {exc}") from exc


def _text(report: dict[str, Any]) -> str:
    version = report["version_recovery"]
    interval = version["narrowest_official_history_source_equivalence_interval"]
    counts = report["path_inventory"]["class_counts"]
    abi = report["abi"]
    return "\n".join(
        [
            "G2 LVGL version/configuration audit: PASS",
            "classification: vendor fork of LVGL 9.3.0-dev lineage",
            f"source-equivalence interval: {interval['first'][:8]}..{interval['last'][:8]}",
            "exact v9.3.0 release tag: excluded",
            (
                "discriminators: style-last=137, event-last=66, layout-last=3, "
                "FreeType-before-draw"
            ),
            (
                "ABI: lv_global=0x%X, lv_display=0x%X, lv_indev=0x%X, lv_draw_buf=0x%X"
                % (
                    abi["sizeof_lv_global_t"],
                    abi["sizeof_lv_display_t"],
                    abi["sizeof_lv_indev_t"],
                    abi["sizeof_lv_draw_buf_t"],
                )
            ),
            (
                "paths: 78 total (%d upstream core/optional, %d LVGL FreeType wrappers, "
                "%d Ambiq draw, 2 separate Ambiq glue)"
                % (
                    counts["official_lvgl_core_or_optional_module"],
                    counts["official_lvgl_freetype_wrapper"],
                    counts["ambiq_draw_backend_inside_lvgl_tree"],
                )
            ),
            "license: MIT (official LVGL LICENCE.txt pinned)",
            "hardware/flash operations: none",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        report = audit(_load(args.image))
    except AuditError as exc:
        parser.error(str(exc))
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
