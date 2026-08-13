#!/usr/bin/env python3
"""Fail-closed stock/provider/source audit for G2 driver/rtc/drv_rtc.c."""
from __future__ import annotations

import csv
import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_ux_system as common
import recover_apollo_embedded_source_paths as thumb


AuditError = common.AuditError
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FUNCTION_MAP = ROOT / "tools/manifests/g2-drv-rtc-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-drv-rtc-closure.tsv"
PROVIDER_MAP = ROOT / "tools/manifests/g2-drv-rtc-provider-map.tsv"
SOURCE_MAP = ROOT / "tools/manifests/g2-drv-rtc-upstream-source.tsv"
REPLACEMENT = ROOT / "components/apollo_main/core_overlay/rtc_time_set.c"
INPUT_PINS = {
    FUNCTION_MAP: "b8caf3c8104a3064cc5ba126cf3141461431c5e0cd7a34606d8207996f256112",
    CLOSURE: "1bb186df217352994365a6cf6f4e0443d28051dba14c2bd39b8fb20d3aaad715",
    PROVIDER_MAP: "01be36e5f6b2f1256ad96281ea4a11c0825174d5adf41262b8c74de439b5f1c2",
    SOURCE_MAP: "1ca6bdb0c0429249cff39b5854cd29170da0f65a36db433a77bf51e3832f5934",
    REPLACEMENT: "52bd836b8b62cc2a293b445098de6850f419890046a2cd78686fd8a6f503258f",
}
RETAINED_PATH = r"D:\01_workspace\s200_ap510b_iar_git\driver\rtc\drv_rtc.c"
PATH_RUN = 0x0071_49A4
PATH_POINTER_CELLS = [0x0047_EF04]
FUNCTION = (0x0047_EE78, 0x0047_EEFA)
PHYSICAL = (0x0047_EE78, 0x0047_EF10)
PHYSICAL_SHA256 = "8da2c6106e20f3520a5b29ede1ffed207e3a95d3d0858813dc617183164f44f3"
BODY_SHA256 = "302009d8a0203801946379cd10edf6d4b4c985e76a9d9929012475b21700cc6a"
INSTRUCTION_COUNT = 56
INSTRUCTION_DIGEST = "e04f41989f27a51108fb61407930509a661636ba84182c42b3baf1949590d5ad"
POOL = (0x0047_EEFA, 0x0047_EF10)
POOL_SHA256 = "c279d27d840347bfcc3ebbd7b0c8327ae5e41ba5bd17d624f358425afa11613c"
PRECEDING_FUNCTION = (0x0047_EE60, 0x0047_EE78)
PRECEDING_SHA256 = "28494bf5da7ade208ce1bd8cec16c210af457cf63e36e967e9b4deb4fefe250c"
FOLLOWING_FUNCTION = (0x0047_EF10, 0x0047_EF18)
FOLLOWING_SHA256 = "1f74abfb1d2a857e62ce46c88abfcc69920e599fe924b1d92caa509efc95fe29"
CALLER = (0x0044_A1FE, 0x0044_A2B2)
CALLER_SHA256 = "9d0c644ee343de478084c430e5e21de2b50b7bea3d1561416a09e6aa70178ba1"
CALLS = [
    (0x0047_EE98, 0x004D_3CF8),
    (0x0047_EEB0, 0x004D_3ADC),
    (0x0047_EEB8, 0x0043_D0CE),
    (0x0047_EED0, 0x0043_D574),
    (0x0047_EED4, 0x0043_D0CE),
    (0x0047_EEDC, 0x0043_D0CE),
    (0x0047_EEEC, 0x0043_CE9E),
]
CALL_DIGEST = "3356645fd7d1efa7c3936bb63dd4be99700fd6e1deae9021c511a1ed6f03d226"
ENTRIES = [(0x0044_A20C, 0x0047_EE78)]
ENTRY_DIGEST = "cc67ec76985ab60d58ad7c90f2df37cf48fca34e67ff1ff0d642bb5ba2612937"
AMBIQ_BODIES = {
    (0x004D_3A38, 0x004D_3A58): "7c2dfeeb03158879103d61a84c6b1b18993b2339f32c2fedb604b931c618a6f2",
    (0x004D_3A58, 0x004D_3ACC): "94538a711db558bd81aa0223557747601c53b1778d7f622575aa80826166dee0",
    (0x004D_3ADC, 0x004D_3B9A): "bbd328dee3c9593b26e8bdbf6baf5aa2b3f0f49cea4c8ab71f4c05bf18147e99",
    (0x004D_3CF8, 0x004D_3DC4): "f6046590f6b197308e912a8a4f1bbd45f46ef9573acd47a369829a8bd806eb0c",
}
STRINGS = {
    PATH_RUN: RETAINED_PATH,
    0x0077_F180: "Invalid Input Value",
    0x0078_5D30: "DRV_RtcSetTime",
    0x0078_D4A4: "drv.rtc",
    0x0075_FA90: "[drv.rtc]Invalid Input Value",
}
SELECTED_COMMIT = "5efc0228528a8adce5eae0d226fac85d2551eb3b"


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def analyze(image: Path = IMAGE) -> dict[str, object]:
    blob = image.read_bytes()
    if len(blob) != common.IMAGE_SIZE or _sha256(blob) != common.IMAGE_SHA256:
        raise AuditError("official Apollo image changed")
    for path, expected in INPUT_PINS.items():
        if _sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned input changed: {path.name}")

    ambiq = json.loads((ROOT / "third_party/ambiqsuite-apollo510/PROVENANCE.json").read_text())
    easy = json.loads((ROOT / "third_party/easylogger/PROVENANCE.json").read_text())
    if (
        ambiq["upstream"]["selected_commit"] != SELECTED_COMMIT
        or ambiq["upstream"]["sdk_revision"] != "AmbiqSuite SDK 5.1.0 / release_sdk5p1p0-366b80e084"
        or easy["upstream"]["selected_commit"] != "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24"
    ):
        raise AuditError("provider source selection changed")

    with FUNCTION_MAP.open(newline="", encoding="utf-8") as handle:
        functions = list(csv.DictReader(handle, delimiter="\t"))
    with PROVIDER_MAP.open(newline="", encoding="utf-8") as handle:
        providers = list(csv.DictReader(handle, delimiter="\t"))
    with SOURCE_MAP.open(newline="", encoding="utf-8") as handle:
        sources = list(csv.DictReader(handle, delimiter="\t"))
    if len(functions) != 1 or len(providers) != 3 or len(sources) != 4:
        raise AuditError("function, provider, or source inventory changed")
    if sum(int(row["edges"].split()[0]) for row in providers) != 7:
        raise AuditError("provider edge inventory changed")
    selected = [row for row in sources if row["sdk_version"] == "5.1.0"]
    if (
        len(selected) != 2
        or {row["public_commit"] for row in selected} != {SELECTED_COMMIT}
        or {row["git_blob_sha1"] for row in selected}
        != {"e7b85936b657af138e3311b346630191fd2d30a4", "11c25ce3e5afd208005eb8484b314b6b84776fa4"}
    ):
        raise AuditError("selected Ambiq source identity changed")

    body = common._slice(blob, *FUNCTION)
    physical = common._slice(blob, *PHYSICAL)
    pool = common._slice(blob, *POOL)
    if len(body) != 130 or _sha256(body) != BODY_SHA256:
        raise AuditError("DRV_RtcSetTime body changed")
    if len(physical) != 152 or _sha256(physical) != PHYSICAL_SHA256:
        raise AuditError("physical drv_rtc object changed")
    if len(pool) != 22 or _sha256(pool) != POOL_SHA256:
        raise AuditError("RTC diagnostic pool changed")
    for bounds, expected, label in (
        (PRECEDING_FUNCTION, PRECEDING_SHA256, "preceding RTC initializer"),
        (FOLLOWING_FUNCTION, FOLLOWING_SHA256, "following RTC getter"),
        (CALLER, CALLER_SHA256, "sole caller"),
    ):
        if _sha256(common._slice(blob, *bounds)) != expected:
            raise AuditError(f"{label} changed")

    recovered, calls = common._recover_function(blob, *FUNCTION)
    pairs = sorted((address, instruction.size) for address, instruction in recovered.items())
    code = b"".join(
        common._slice(blob, address, address + instruction.size)
        for address, instruction in sorted(recovered.items())
    )
    if (
        len(recovered) != INSTRUCTION_COUNT
        or common._instruction_digest(pairs) != INSTRUCTION_DIGEST
        or code != body
        or common._uncovered(FUNCTION, recovered)
        or calls != CALLS
        or common._pair_digest(calls) != CALL_DIGEST
    ):
        raise AuditError("instruction or call closure changed")

    for bounds, expected in AMBIQ_BODIES.items():
        if _sha256(common._slice(blob, *bounds)) != expected:
            raise AuditError(f"Ambiq provider body changed at 0x{bounds[0]:08x}")
    for address, expected in STRINGS.items():
        if common._c_string(blob, address) != expected:
            raise AuditError(f"string changed at 0x{address:08x}")
    if struct.unpack_from("<IIIII", blob, 0x0047_EEFC - common.BASE) != (
        0x0077_F180, 0x0078_5D30, PATH_RUN, 0x0078_D4A4, 0x0075_FA90
    ):
        raise AuditError("diagnostic literal pool changed")
    path_word = struct.pack("<I", PATH_RUN)
    hits, cursor = [], blob.find(path_word)
    while cursor >= 0:
        hits.append(common.BASE + cursor)
        cursor = blob.find(path_word, cursor + 1)
    if hits != PATH_POINTER_CELLS:
        raise AuditError("retained path pointer topology changed")

    starts = {FUNCTION[0]}
    interiors = set(range(FUNCTION[0] + 2, FUNCTION[1], 2))
    entries, strict, unknown = [], [], []
    for offset in range(0, len(blob) - 3, 2):
        site = common.BASE + offset
        target = thumb._thumb_bl_target(blob, site)
        if target in starts:
            entries.append((site, target))
        elif target in interiors:
            strict.append((site, target))
        elif target is not None and PHYSICAL[0] <= target < PHYSICAL[1]:
            unknown.append((site, target))
    if entries != ENTRIES or common._pair_digest(entries) != ENTRY_DIGEST or strict or unknown:
        raise AuditError("entry topology changed")
    stored = []
    for offset in range(len(blob) - 3):
        if struct.unpack_from("<I", blob, offset)[0] in {FUNCTION[0], FUNCTION[0] | 1}:
            stored.append(common.BASE + offset)
    if stored:
        raise AuditError("unexpected stored RTC setter pointer")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    source = next((row for row in overlay["sources"] if row["path"].endswith("rtc_time_set.c")), None)
    patch = next((row for row in overlay["patch_sites"] if row["name"] == "replace_rtc_time_set"), None)
    if (
        source is None
        or source["sha256"] != INPUT_PINS[REPLACEMENT]
        or patch is None
        or patch["runtime_address"] != FUNCTION[0]
        or patch["expected_size"] != 130
        or patch["expected_sha256"] != BODY_SHA256
        or patch["target_function"] != "open_cfw_rtc_time_set"
    ):
        raise AuditError("production RTC replacement changed")
    replacement = REPLACEMENT.read_text(encoding="utf-8")
    for marker in (
        "open_cfw_rtc_time_set",
        "open_cfw_rtc_compute_weekday",
        "year % 400 != 0",
        "OPEN_CFW_RTC_TIME_COUNTER_LOW_ADDRESS",
        "OPEN_CFW_RTC_TIME_COUNTER_UP_ADDRESS",
    ):
        if marker not in replacement:
            raise AuditError(f"replacement marker missing: {marker}")

    target_counts = Counter(target for _, target in calls)
    return {
        "schema_version": 1,
        "analysis_mode": "read-only; fail-closed linked-object, upstream-source, and production-route audit",
        "image": {"size": len(blob), "sha256": _sha256(blob)},
        "identity": {
            "retained_path": RETAINED_PATH,
            "function": "DRV_RtcSetTime",
            "historical_source_available": False,
            "private_producing_commit_observable": False,
            "embedded_third_party_definitions": [],
        },
        "surface": {
            "linked_functions": 1,
            "ghidra_discovered_functions": 1,
            "additional_recovered_functions": 0,
            "path_anchored_functions": 1,
            "body_bytes": len(body),
            "reachable_instruction_bytes": len(code),
            "outer_pool_regions": 1,
            "outer_pool_bytes": len(pool),
            "physical_bytes": len(physical),
            "direct_bl_entry_sites": len(entries),
            "external_direct_bl_entry_sites": len(entries),
            "direct_body_calls": len(calls),
            "internal_direct_body_calls": 0,
            "external_direct_body_calls": len(calls),
            "indirect_body_calls": 0,
            "stored_entry_pointers": 0,
            "strict_interior_raw_bl_decodes": len(strict),
            "unrecovered_direct_object_targets": len(unknown),
        },
        "behavior": {
            "input_year_base": 2000,
            "ambiq_time_structure_bytes": 40,
            "success_return": 0,
            "failure_return": 1,
            "diagnostic_source_line": 221,
            "calendar_helper": "am_util_time_computeDayofWeek",
            "rtc_setter": "am_hal_rtc_time_set",
            "leap_predicate": "year % 4 == 0 && (year % 100 != 0 || year % 400 != 0)",
        },
        "provider_boundary": {
            "direct_external_calls": len(calls),
            "ambiq_calendar_utility_calls": target_counts[0x004D_3CF8],
            "ambiq_rtc_hal_calls": target_counts[0x004D_3ADC],
            "easylogger_calls": sum(target_counts[target] for target in (0x0043_CE9E, 0x0043_D0CE, 0x0043_D574)),
            "selected_public_commit": SELECTED_COMMIT,
            "selected_sdk_revision": "release_sdk5p1p0-366b80e084",
            "executable_logic_compatible_with_5_0_0": True,
            "new_version_discriminator": False,
        },
        "production": {
            "production_routed": True,
            "replacement_source": source["path"],
            "patch_name": patch["name"],
            "target_function": patch["target_function"],
        },
        "limitations": [
            "the stock image predates Ambiq's public 5.1.0 import, so the exact private generating commit is unavailable",
            "the RTC utility/HAL executable logic is also present in 5.0.0 and is not a local version discriminator",
            "production source is host-tested and linked, but final Apollo510 RTC behavior still requires hardware validation",
        ],
    }


def _text(report: dict[str, object]) -> str:
    surface = report["surface"]
    providers = report["provider_boundary"]
    production = report["production"]
    return "\n".join([
        "G2 drv_rtc closure",
        f"  image: {report['image']['sha256']}",
        f"  object: {surface['linked_functions']} function / {surface['body_bytes']} body bytes / {surface['physical_bytes']} physical bytes",
        f"  calls: {surface['direct_body_calls']} direct; Ambiq utility {providers['ambiq_calendar_utility_calls']}; Ambiq RTC HAL {providers['ambiq_rtc_hal_calls']}; EasyLogger {providers['easylogger_calls']}",
        f"  selected Ambiq replay: {providers['selected_sdk_revision']} at {providers['selected_public_commit']}",
        f"  production routed: {str(production['production_routed']).lower()} -> {production['target_function']}",
    ])


def main() -> int:
    report = analyze()
    if "--json" in sys.argv:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
