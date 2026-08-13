#!/usr/bin/env python3
"""Fail-closed object/provider audit for G2 product/s200/app/config/rtos.c."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import struct
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x0043_7FE0
IMAGE_SIZE = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
FUNCTION_MAP = ROOT / "tools/manifests/g2-product-rtos-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-product-rtos-closure.tsv"
PROVIDER_MAP = ROOT / "tools/manifests/g2-product-rtos-provider-map.tsv"
SOURCE_MAP = ROOT / "tools/manifests/ambiqsuite-apollo510-rtos-provider-source.tsv"
INPUT_PINS = {
    FUNCTION_MAP: "148ef17fb8e47f5978c28889574b463103974e397117c9257ce645c5cf3b472d",
    CLOSURE: "e35a12e8e29662b3bc8efab7bb603cebbe0be64bb36d33ae21b29cc3d52fa013",
    PROVIDER_MAP: "5e4bc1ef78b636a3940062fcfda435cef3a8afe1977c143c5be9b2da61d6d560",
    SOURCE_MAP: "b139ffa4b34e8a96d0a93ecf5589c5805965be8abc238523a491c979c6f51666",
}

RETAINED_PATH = r"D:\01_workspace\s200_ap510b_iar_git\product\s200\app\config\rtos.c"
PATH_RUN = 0x0070_522C
PATH_POINTER_CELLS = [0x0046_D884]
PHYSICAL = (0x0046_D67C, 0x0046_D8A0)
PHYSICAL_BYTES = 548
PHYSICAL_SHA256 = "49cb456135815b5738f5b0a9f96aca18a7a8e30a35846df4a3cbb6e0c714aa86"
BODY_BYTES = 512
BODY_SHA256 = "ce8de3e8b2dddc2c8b4d2c569faa6f376cfbe944f2ffb92769e770b45955fd33"
POOL_REGIONS = 2
POOL_BYTES = 36
POOL_SHA256 = "30c31ea87943083be2ccacf0e5d1b6faead2e94072b58f0cc9311dd290e8ddeb"

PRECEDING = (0x0046_D584, 0x0046_D67C)
PRECEDING_SHA256 = "75334fc89a669a482b0eda7438d073427d70c00d48927da5cd4faa902415221f"
FOLLOWING = (0x0046_D8A0, 0x0046_D8E0)
FOLLOWING_SHA256 = "65cf363fa6a5f8bddba5dcd1307e8d898f5034a848a975b9871d71de772849f9"

ENTRY_COUNT = 19
EXTERNAL_ENTRY_COUNT = 13
ENTRY_SHA256 = "ea92ee9564973b2b26ad4642c02d338da629da6e3ff6ba68e7a91cf51710cde0"
BODY_CALL_COUNT = 24
INTERNAL_BODY_CALL_COUNT = 6
BODY_CALL_SHA256 = "3e403b8949130590d3fa4ecbed22d33f6a733c29cc53c61172dd474e4ba886ca"
STORED_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
EXTERNAL_TARGET_COUNTS = {
    0x0043_C0E4: 1,
    0x0043_CE9E: 1,
    0x0043_D0CE: 3,
    0x0043_D574: 1,
    0x0044_91AA: 2,
    0x0044_AB42: 2,
    0x0047_33EE: 2,
    0x0047_3940: 3,
    0x004B_29F8: 3,
}

SYSCTRL_SLEEP = (0x0044_AB42, 0x0044_B068)
SYSCTRL_SLEEP_SHA256 = "012c052f6ab7e829129ed966a94cfb1541605b2d05185115c1dfd06cbb9d2898"
SYSCTRL_WFI_SITES = [0x0044_ADF8, 0x0044_AF9A]
WDT_RESTART = (0x0052_A3DA, 0x0052_A3EE)
WDT_RESTART_SHA256 = "2ad33f20d1f8029f21d9fb6de08c813372a05bdff9c6d5526b5ba328a15a4fb3"
WDT_FEED_WRAPPER = (0x004B_29F8, 0x004B_2A02)
WDT_FEED_WRAPPER_SHA256 = "3980a9bebbdd4b3d483459d625ca2de470df5332eaed88c51cf8bd09f290d398"
BUILD_TIME_RUN = 0x0076_8290
BUILD_TIME = "2025-04-28T13:29:15Z"

STRINGS = {
    PATH_RUN: RETAINED_PATH,
    0x0076_4810: "Task vote system initialized",
    0x0078_8630: "task_vote_init",
    0x0078_E46C: "rtos",
    0x0075_8F4C: "[rtos]Task vote system initialized",
    0x0075_8F70: "MallocFailed: cannot malloc memory\n",
    0x0077_B1C4: "task %s stack overflow\n",
    BUILD_TIME_RUN: BUILD_TIME,
}


class AuditError(RuntimeError):
    """Raised when authenticated evidence or the object closure changes."""


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _slice(blob: bytes, start: int, end: int) -> bytes:
    first, last = start - BASE, end - BASE
    if first < 0 or last > len(blob) or first > last:
        raise AuditError(f"invalid image interval [0x{start:08x},0x{end:08x})")
    return blob[first:last]


def _pair_digest(pairs: list[tuple[int, int]]) -> str:
    return _sha256(b"".join(struct.pack("<II", *pair) for pair in pairs))


def _c_string(blob: bytes, address: int) -> str:
    offset = address - BASE
    end = blob.find(b"\0", offset)
    if offset < 0 or end < 0:
        raise AuditError(f"unterminated string at 0x{address:08x}")
    return blob[offset:end].decode("ascii")


def _validate_provider_pins() -> None:
    cmsis = json.loads((ROOT / "third_party/cmsis-freertos/PROVENANCE.json").read_text())
    if cmsis["upstreams"]["cmsis_freertos"]["selected_commit"] != "d213f261b5be6bb29a7cce8b84071706b72f4d53":
        raise AuditError("CMSIS-FreeRTOS provider commit changed")
    ambiq = json.loads((ROOT / "third_party/ambiqsuite-apollo510/PROVENANCE.json").read_text())
    if ambiq["upstream"]["selected_commit"] != "5efc0228528a8adce5eae0d226fac85d2551eb3b":
        raise AuditError("Apollo510 HAL replay commit changed")
    easy = json.loads((ROOT / "third_party/easylogger/PROVENANCE.json").read_text())
    if easy["upstream"]["selected_commit"] != "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":
        raise AuditError("EasyLogger provider commit changed")
    iar = (ROOT / "docs/research/iar-dlib-runtime-census.md").read_text()
    for marker in ("9.20 is therefore a practical lower bound", "9.60.2"):
        if marker not in iar:
            raise AuditError("IAR family-level provenance assessment changed")


def analyze(image: Path = IMAGE) -> dict[str, object]:
    blob = image.read_bytes()
    if len(blob) != IMAGE_SIZE or _sha256(blob) != IMAGE_SHA256:
        raise AuditError("official Apollo image changed")
    for path, expected in INPUT_PINS.items():
        if _sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned input changed: {path.name}")
    _validate_provider_pins()

    with FUNCTION_MAP.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    with PROVIDER_MAP.open(newline="", encoding="utf-8") as handle:
        provider_rows = list(csv.DictReader(handle, delimiter="\t"))
    with SOURCE_MAP.open(newline="", encoding="utf-8") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 13 or len(provider_rows) != 6 or len(source_rows) != 4:
        raise AuditError("function/provider/source inventory changed")
    edges = sum(int(re.match(r"(\d+)", row["edges"]).group(1)) for row in provider_rows)
    if edges != sum(EXTERNAL_TARGET_COUNTS.values()):
        raise AuditError("provider edge accounting changed")
    if [row["discriminator"] for row in source_rows[:2]] != [
        "am_hal_sysctrl_sleep contains one WFI",
        "am_hal_sysctrl_sleep contains two WFI instructions",
    ]:
        raise AuditError("Ambiq system-sleep source discriminator changed")
    if source_rows[1]["public_commit"] != "5efc0228528a8adce5eae0d226fac85d2551eb3b":
        raise AuditError("selected Ambiq 5.1.0 source row changed")

    starts: set[int] = set()
    interiors: set[int] = set()
    intervals: list[tuple[int, int]] = []
    bodies: list[bytes] = []
    gaps: list[bytes] = []
    anchored = 0
    previous_end = PHYSICAL[0]
    for row in rows:
        start, end = int(row["stock_start"], 0), int(row["stock_end_exclusive"], 0)
        if start in starts or start < previous_end or start >= end:
            raise AuditError(f"invalid or overlapping function at 0x{start:08x}")
        if previous_end < start:
            gaps.append(_slice(blob, previous_end, start))
        body = _slice(blob, start, end)
        if len(body) != int(row["stock_bytes"]) or _sha256(body) != row["stock_sha256"]:
            raise AuditError(f"function body changed: {row['function']}")
        starts.add(start)
        interiors.update(range(start + 2, end, 2))
        intervals.append((start, end))
        bodies.append(body)
        anchored += row["source_path_anchor"] == "yes"
        previous_end = end
    if previous_end < PHYSICAL[1]:
        gaps.append(_slice(blob, previous_end, PHYSICAL[1]))
    if anchored != 1 or intervals[0][0] != PHYSICAL[0] or previous_end != PHYSICAL[1]:
        raise AuditError("path anchor or object interval changed")
    if sum(map(len, bodies)) != BODY_BYTES or _sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body inventory changed")
    if len(gaps) != POOL_REGIONS or sum(map(len, gaps)) != POOL_BYTES or _sha256(b"".join(gaps)) != POOL_SHA256:
        raise AuditError("literal-pool inventory changed")
    if len(_slice(blob, *PHYSICAL)) != PHYSICAL_BYTES or _sha256(_slice(blob, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical product-RTOS object changed")
    for bounds, expected, label in (
        (PRECEDING, PRECEDING_SHA256, "preceding font-manager tail"),
        (FOLLOWING, FOLLOWING_SHA256, "following utility object"),
        (SYSCTRL_SLEEP, SYSCTRL_SLEEP_SHA256, "Ambiq system-sleep provider"),
        (WDT_RESTART, WDT_RESTART_SHA256, "Ambiq watchdog-restart provider"),
        (WDT_FEED_WRAPPER, WDT_FEED_WRAPPER_SHA256, "G2 watchdog-feed wrapper"),
    ):
        if _sha256(_slice(blob, *bounds)) != expected:
            raise AuditError(f"{label} changed")
    wfi = bytes.fromhex("30bf")
    sleep = _slice(blob, *SYSCTRL_SLEEP)
    wfi_sites = [SYSCTRL_SLEEP[0] + offset for offset in range(len(sleep) - 1) if sleep[offset:offset + 2] == wfi]
    if wfi_sites != SYSCTRL_WFI_SITES:
        raise AuditError(f"Ambiq 5.1 sleep discriminator changed: {wfi_sites!r}")
    if _slice(blob, WDT_RESTART[0], WDT_RESTART[1]) != bytes.fromhex("c0b2002804d1b22004490860002000e001207047"):
        raise AuditError("watchdog selector/key behavior changed")
    for address, expected in STRINGS.items():
        if _c_string(blob, address) != expected:
            raise AuditError(f"retained string changed at 0x{address:08x}")
    word = struct.pack("<I", PATH_RUN)
    hits, cursor = [], blob.find(word)
    while cursor >= 0:
        hits.append(BASE + cursor)
        cursor = blob.find(word, cursor + 1)
    if hits != PATH_POINTER_CELLS:
        raise AuditError(f"source-path pointer topology changed: {hits!r}")

    sys.path.insert(0, str(ROOT / "tools"))
    import recover_apollo_embedded_source_paths as decoder

    entries: list[tuple[int, int]] = []
    strict: list[tuple[int, int]] = []
    unknown: list[tuple[int, int]] = []
    for offset in range(0, len(blob) - 3, 2):
        site = BASE + offset
        target = decoder._thumb_bl_target(blob, site)
        if target in starts:
            entries.append((site, target))
        elif target in interiors:
            strict.append((site, target))
        elif target is not None and PHYSICAL[0] <= target < PHYSICAL[1]:
            unknown.append((site, target))
    if len(entries) != ENTRY_COUNT or _pair_digest(entries) != ENTRY_SHA256:
        raise AuditError("direct entry topology changed")
    external_entries = sum(not (PHYSICAL[0] <= site < PHYSICAL[1]) for site, _ in entries)
    if external_entries != EXTERNAL_ENTRY_COUNT or strict or unknown:
        raise AuditError("entry closure changed")

    calls: list[tuple[int, int]] = []
    image_end = BASE + len(blob)
    for start, end in intervals:
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(blob, site)
            if target is not None and BASE <= target < image_end:
                calls.append((site, target))
    if len(calls) != BODY_CALL_COUNT or _pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("body callee topology changed")
    if sum(target in starts for _, target in calls) != INTERNAL_BODY_CALL_COUNT:
        raise AuditError("internal body-call census changed")
    external_counts = Counter(target for _, target in calls if target not in starts)
    if dict(external_counts) != EXTERNAL_TARGET_COUNTS:
        raise AuditError(f"provider target accounting changed: {external_counts!r}")

    encoded_starts = starts | {entry | 1 for entry in starts}
    stored: list[tuple[int, int]] = []
    for offset in range(len(blob) - 3):
        if struct.unpack_from("<I", blob, offset)[0] in encoded_starts:
            stored.append((BASE + offset, struct.unpack_from("<I", blob, offset)[0]))
    if stored or _pair_digest(stored) != STORED_SHA256:
        raise AuditError("stored callback topology changed")

    overlay_text = (ROOT / "components/apollo_main/core_overlay/overlay.json").read_text().lower()
    routed = any(f"0x{start:08x}" in overlay_text for start in starts)
    if routed:
        raise AuditError("product RTOS object unexpectedly became production-routed")

    return {
        "schema_version": 1,
        "analysis_mode": "read-only; fail-closed linked-object and provider-version audit",
        "image": {"size": len(blob), "sha256": _sha256(blob), "build_time": BUILD_TIME},
        "identity": {
            "retained_path": RETAINED_PATH,
            "ownership": "g2_task_vote_policy_and_freertos_application_hooks",
            "historical_source_available": "Ambiq hook ancestry only",
            "private_producing_commit_observable": False,
            "embedded_third_party_definitions": [],
        },
        "surface": {
            "linked_functions": len(rows), "path_anchored_functions": anchored,
            "additional_recovered_functions": len(rows) - anchored,
            "body_bytes": sum(map(len, bodies)), "literal_pool_regions": len(gaps),
            "literal_pool_bytes": sum(map(len, gaps)), "physical_bytes": PHYSICAL_BYTES,
            "direct_bl_entry_sites": len(entries), "external_direct_bl_entry_sites": external_entries,
            "direct_body_calls": len(calls), "internal_direct_body_calls": INTERNAL_BODY_CALL_COUNT,
            "external_direct_body_calls": len(calls) - INTERNAL_BODY_CALL_COUNT,
            "stored_entry_pointers": len(stored), "strict_interior_raw_bl_decodes": len(strict),
            "unrecovered_direct_object_targets": len(unknown),
        },
        "behavior": {
            "vote_slots": 32, "vote_state_bytes": 0x108,
            "deep_sleep_requires_zero_active_votes": True,
            "watchdog_feed_hooks": ["pre-sleep", "post-sleep", "idle"],
            "malloc_failed_hook": "log then infinite loop",
            "stack_overflow_hook": "log task name then repeated BKPT",
            "freertos_config": {"configUSE_IDLE_HOOK": 1, "configUSE_TICK_HOOK": 0,
                "configUSE_MALLOC_FAILED_HOOK": 1, "configCHECK_FOR_STACK_OVERFLOW": ">1 (normally 2)"},
        },
        "provider_boundary": {
            "provider_rows": len(provider_rows), "direct_external_targets": len(external_counts),
            "direct_external_calls": sum(external_counts.values()),
            "cmsis_freertos": {"version": "v10.5.1", "commit": "d213f261b5be6bb29a7cce8b84071706b72f4d53",
                "function": "osThreadGetId", "calls": 2, "production_source_owned": True},
            "ambiq_hal": {"family": "Apollo510", "selected_source_equivalent_version": "5.1.0",
                "selected_public_commit": "5efc0228528a8adce5eae0d226fac85d2551eb3b",
                "sdk_revision": "release_sdk5p1p0-366b80e084", "stock_sleep_wfi_count": 2,
                "sdk_5_0_sleep_wfi_count": 1, "sdk_5_1_sleep_wfi_count": 2,
                "exact_private_pre_release_commit": None, "build_predates_public_import": True},
            "easylogger": {"version": "2.2.99 source-equivalent core", "calls": 5},
            "iar_dlib": {"floor": "EWARM 9.20+", "leading_candidate": "9.60.2",
                "exact_release": None, "calls": 1, "new_version_discriminator": False},
            "assessment": "all upstream relationships terminate at admitted source/provider seams; no opaque third-party definition is embedded",
        },
        "boundary": {"physical_start": f"0x{PHYSICAL[0]:08x}", "physical_end_exclusive": f"0x{PHYSICAL[1]:08x}",
            "path_pointer_cells": [f"0x{x:08x}" for x in PATH_POINTER_CELLS],
            "preceded_by": "LVGL font-manager terminal body and pool", "followed_by": "independent list utility object"},
        "production": {"candidate": None, "production_routed": routed, "ownership_bytes": 0},
        "limitations": [
            "the G2 task-vote policy and private producing commit remain unavailable",
            "the stock build predates the public 5.1.0 import, so the public commit is a source-equivalent replay rather than the generating checkout",
            "the watchdog-restart leaf is source-identical in 5.0.0 and 5.1.0 and is not independently version-discriminating",
            "production admission requires clean-room policy/hooks, atomic tickless integration, and Apollo510 power validation",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
    print("G2 product-RTOS audit: PASS")
