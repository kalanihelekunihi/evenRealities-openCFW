#!/usr/bin/env python3
"""Fail-closed linked-object/provider audit for teleprompt_file_list.c."""
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
from apollo_artifact_consistency import validate_apollo_main_artifacts


AuditError = common.AuditError
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FUNCTION_MAP = ROOT / "tools/manifests/g2-teleprompt-file-list-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-teleprompt-file-list-closure.tsv"
PROVIDER_MAP = ROOT / "tools/manifests/g2-teleprompt-file-list-provider-map.tsv"
SOURCE = ROOT / "components/apollo_main/core_overlay/teleprompt_file_list.c"
HEADER = ROOT / "components/apollo_main/core_overlay/teleprompt_file_list.h"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
INPUT_PINS = {
    FUNCTION_MAP: "b616ae850073917011964f2433f274b68a78bf106d54cc9da7c7972ce8f26e26",
    CLOSURE: "bfcd5d0668b0a0211f6850265e0e1f7d870c6f4cd0006d3fb211c7489982aca5",
    PROVIDER_MAP: "31253bd1a72b3a284fea72ba71724576ac2df54958d7423c8e9e9c2dcbe62192",
}
RETAINED_PATH = r"D:\01_workspace\s200_ap510b_iar_git\app\gui\teleprompt\teleprompt_file_list.c"
PATH_RUN = 0x006F_0088
PATH_POINTER_CELLS = [0x0058_BD90]
FUNCTIONS = (
    (0x0058_BCE0, 0x0058_BD70),
    (0x0058_BD70, 0x0058_BD74),
    (0x0058_BD74, 0x0058_BD86),
)
PHYSICAL = (0x0058_BCE0, 0x0058_BDA8)
PHYSICAL_SHA256 = "63362adada77f0ee0f6584b8b04c083733194c241a06a286b5050acd8430f9ab"
BODY_BYTES = 166
BODY_SHA256 = "0fe2ba5586a4f1e7b72b23534f5d44f7e76c78b5d02e52d2c96343fcb3c0d6e1"
INSTRUCTION_COUNT = 67
INSTRUCTION_DIGEST = "757e016acf182bdf5645b90024ac0252a890392151282ed959a2ce02be9bb3d8"
POOL = (0x0058_BD86, 0x0058_BDA8)
POOL_SHA256 = "e70876af70a42d8e2a58fd55ce310ed2e9566c94069228293752635a90bc9bbe"
PRECEDING_TAIL = (0x0058_BCA0, 0x0058_BCE0)
PRECEDING_TAIL_SHA256 = "380184750aa46437371f10dcb723215afce3acbcd639c456b47f20b423e6b7d9"
FOLLOWING_HEAD = (0x0058_BDA8, 0x0058_BDB0)
FOLLOWING_HEAD_SHA256 = "d88b00f616f674a57bffc726f9b531cd02a8e5580728086acefda0c24eff2c80"
CALLS = [
    (0x0058_BCE8, 0x0043_D0CE),
    (0x0058_BD00, 0x0043_D574),
    (0x0058_BD04, 0x0043_D0CE),
    (0x0058_BD0C, 0x0043_D0CE),
    (0x0058_BD1C, 0x0043_CE9E),
    (0x0058_BD2C, 0x0043_9BE4),
    (0x0058_BD30, 0x0043_D0CE),
    (0x0058_BD4C, 0x0043_D574),
    (0x0058_BD50, 0x0043_D0CE),
    (0x0058_BD58, 0x0043_D0CE),
    (0x0058_BD6A, 0x0043_CE9E),
    (0x0058_BD80, 0x0043_C0E4),
]
CALL_DIGEST = "991beeb2e6397252af75a85acb34f8ea81d3e92b8464177ac82d90f2b2325e30"
ENTRIES = [
    (0x0055_5712, 0x0058_BD70),
    (0x0055_5D20, 0x0058_BD70),
    (0x0055_6016, 0x0058_BD70),
    (0x0055_60BC, 0x0058_BD74),
    (0x0058_A23A, 0x0058_BD74),
    (0x0058_CFEE, 0x0058_BCE0),
]
ENTRY_DIGEST = "5df4c69f7dfbf07b41058957584b24d26904005568f4ff77db48731dfc69a809"
GLOBAL = 0x2010_93D4
RECORD_BYTES = 0xF52
SOURCE_SIZE = 2551
SOURCE_SHA256 = "5887f4353ef6569e989ab6280f5e65a8f3f926c96944be94bf06decf4b7c0565"
HEADER_SIZE = 607
HEADER_SHA256 = "c13ece03341385a955da40158807504f8ea82988bfed26a4be5840c2c6a0d781"
PRODUCTION_FUNCTIONS = (
    "open_cfw_teleprompt_file_list_update",
    "open_cfw_teleprompt_file_list_get",
    "open_cfw_teleprompt_file_list_reset",
)
STRINGS = {
    PATH_RUN: RETAINED_PATH,
    0x0078_3DFC: "file_list is NULL",
    0x0077_2A40: "teleprompt_file_list_update",
    0x0078_9720: "teleprompt.file",
    0x0075_ABB4: "[teleprompt.file]file_list is NULL",
    0x0075_ABD8: "file_list updated: file_count=%d",
    0x0072_E560: "[teleprompt.file]file_list updated: file_count=%d",
}


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _validate_production() -> dict[str, object]:
    source = SOURCE.read_bytes()
    header = HEADER.read_bytes()
    if (len(source), _sha256(source)) != (SOURCE_SIZE, SOURCE_SHA256):
        raise AuditError("production teleprompt file-list source changed")
    if (len(header), _sha256(header)) != (HEADER_SIZE, HEADER_SHA256):
        raise AuditError("production teleprompt file-list header changed")

    config = json.loads(OVERLAY.read_text())
    leaves = {
        item.get("function"): item for item in config["relocated_leaves"]
        if item.get("function") in PRODUCTION_FUNCTIONS
    }
    if set(leaves) != set(PRODUCTION_FUNCTIONS):
        raise AuditError("production teleprompt file-list leaf inventory changed")
    if any(
        item.get("profiles") != ["apple-clang", "linux-clang"]
        or item.get("strict_relocation_contract") is not True
        or item.get("source", {}).get("path")
            != "components/apollo_main/core_overlay/teleprompt_file_list.c"
        or item["source"].get("size") != SOURCE_SIZE
        or item["source"].get("sha256") != SOURCE_SHA256
        or item.get("expected", {}).get("alignment") != 4
        or item.get("toolchain_profiles", {}).get("linux-clang", {})
            .get("expected", {}).get("alignment") != 4
        for item in leaves.values()
    ):
        raise AuditError("production teleprompt file-list leaf contract changed")

    header_records = [
        item for item in config["sources"]
        if item.get("path")
            == "components/apollo_main/core_overlay/teleprompt_file_list.h"
    ]
    if (
        len(header_records) != 1
        or header_records[0].get("license") != "MIT"
        or header_records[0].get("size") != HEADER_SIZE
        or header_records[0].get("sha256") != HEADER_SHA256
        or {item["source"].get("license") for item in leaves.values()} != {"MIT"}
    ):
        raise AuditError("production teleprompt file-list source admission changed")

    apple_bytes = sum(item["expected"]["size"] for item in leaves.values())
    linux_bytes = sum(
        item["toolchain_profiles"]["linux-clang"]["expected"]["size"]
        for item in leaves.values()
    )
    apple_relocations = sum(
        len(item.get("relocations", [])) for item in leaves.values()
    )
    linux_relocations = sum(
        len(item["toolchain_profiles"]["linux-clang"].get("relocations", []))
        for item in leaves.values()
    )
    if (
        apple_bytes, linux_bytes, apple_relocations, linux_relocations
    ) != (52, 52, 2, 2):
        raise AuditError("production teleprompt file-list compiled closure changed")

    patches = [
        item for item in config["patch_sites"]
        if item.get("name", "").startswith("replace_teleprompt_file_list_")
    ]
    if (
        len(patches) != len(FUNCTIONS)
        or {item.get("runtime_address") for item in patches}
            != {start for start, _end in FUNCTIONS}
        or any(
            item.get("profiles") != ["apple-clang", "linux-clang"]
            or item.get("branch") != "b_w"
            for item in patches
        )
    ):
        raise AuditError("production teleprompt file-list patch route changed")

    report = json.loads(REPORT.read_text())
    built = {
        item.get("extraction", {}).get("function"): item
        for item in report["relocated_leaves"]
        if item.get("extraction", {}).get("function") in PRODUCTION_FUNCTIONS
    }
    if set(built) != set(PRODUCTION_FUNCTIONS) or any(
        built[name]["extraction"].get("sha256")
            != leaves[name]["expected"]["sha256"]
        or built[name]["placement"].get("offset")
            != leaves[name]["expected"]["offset"]
        for name in PRODUCTION_FUNCTIONS
    ):
        raise AuditError("built teleprompt file-list route changed")

    validate_apollo_main_artifacts(ROOT, AuditError, "teleprompt file-list")
    return {
        "production_routed": True,
        "source_routed_functions": len(PRODUCTION_FUNCTIONS),
        "source_compiled_bytes": {
            "apple-clang": apple_bytes,
            "linux-clang": linux_bytes,
        },
        "strict_relocations": apple_relocations,
        "stock_body_bytes_displaced": BODY_BYTES,
        "retained_diagnostic_pool_bytes": POOL[1] - POOL[0],
        "software_gap": False,
        "hardware_validation": "blocked by unavailable physical evidence",
        "hardware_operations": [],
    }


def analyze(image: Path = IMAGE) -> dict[str, object]:
    blob = image.read_bytes()
    if len(blob) != common.IMAGE_SIZE or _sha256(blob) != common.IMAGE_SHA256:
        raise AuditError("official Apollo image changed")
    for path, expected in INPUT_PINS.items():
        if _sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned input changed: {path.name}")
    easy = json.loads((ROOT / "third_party/easylogger/PROVENANCE.json").read_text())
    if easy["upstream"]["selected_commit"] != "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":
        raise AuditError("EasyLogger source selection changed")

    with FUNCTION_MAP.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    with PROVIDER_MAP.open(newline="", encoding="utf-8") as handle:
        providers = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 3 or len(providers) != 2 or sum(int(row["edges"].split()[0]) for row in providers) != 12:
        raise AuditError("function or provider inventory changed")

    starts, interiors, bodies, all_instructions, calls = set(), set(), [], {}, []
    for row, expected_bounds in zip(rows, FUNCTIONS):
        start, end = int(row["stock_start"], 0), int(row["stock_end_exclusive"], 0)
        if (start, end) != expected_bounds:
            raise AuditError("function bounds changed")
        body = common._slice(blob, start, end)
        if len(body) != int(row["stock_bytes"]) or _sha256(body) != row["stock_sha256"]:
            raise AuditError(f"function changed: {row['function']}")
        recovered, function_calls = common._recover_function(blob, start, end)
        if common._uncovered((start, end), recovered):
            raise AuditError(f"function contains uncovered bytes: {row['function']}")
        starts.add(start)
        interiors.update(range(start + 2, end, 2))
        bodies.append(body)
        all_instructions.update(recovered)
        calls.extend(function_calls)
    code = b"".join(
        common._slice(blob, address, address + instruction.size)
        for address, instruction in sorted(all_instructions.items())
    )
    pairs = sorted((address, instruction.size) for address, instruction in all_instructions.items())
    if (
        sum(map(len, bodies)) != BODY_BYTES
        or _sha256(b"".join(bodies)) != BODY_SHA256
        or len(all_instructions) != INSTRUCTION_COUNT
        or common._instruction_digest(pairs) != INSTRUCTION_DIGEST
        or code != b"".join(bodies)
        or calls != CALLS
        or common._pair_digest(calls) != CALL_DIGEST
    ):
        raise AuditError("body, instruction, or call closure changed")
    if len(common._slice(blob, *PHYSICAL)) != 200 or _sha256(common._slice(blob, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical file-list object changed")
    if len(common._slice(blob, *POOL)) != 34 or _sha256(common._slice(blob, *POOL)) != POOL_SHA256:
        raise AuditError("file-list pool changed")
    for bounds, expected, label in (
        (PRECEDING_TAIL, PRECEDING_TAIL_SHA256, "preceding page-cache tail"),
        (FOLLOWING_HEAD, FOLLOWING_HEAD_SHA256, "following exit-prompt head"),
    ):
        if _sha256(common._slice(blob, *bounds)) != expected:
            raise AuditError(f"{label} changed")

    for address, expected in STRINGS.items():
        if common._c_string(blob, address) != expected:
            raise AuditError(f"string changed at 0x{address:08x}")
    if struct.unpack_from("<I", blob, 0x0058_BD9C - common.BASE)[0] != GLOBAL:
        raise AuditError("global file-list address changed")
    path_word = struct.pack("<I", PATH_RUN)
    hits, cursor = [], blob.find(path_word)
    while cursor >= 0:
        hits.append(common.BASE + cursor)
        cursor = blob.find(path_word, cursor + 1)
    if hits != PATH_POINTER_CELLS:
        raise AuditError("retained path pointer topology changed")

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
    encoded = starts | {start | 1 for start in starts}
    stored = []
    for offset in range(len(blob) - 3):
        if struct.unpack_from("<I", blob, offset)[0] in encoded:
            stored.append(common.BASE + offset)
    if stored:
        raise AuditError("unexpected stored file-list entry pointer")

    counts = Counter(target for _, target in calls)
    return {
        "schema_version": 1,
        "analysis_mode": "read-only; fail-closed linked-object and provider audit",
        "image": {"size": len(blob), "sha256": _sha256(blob)},
        "identity": {
            "retained_path": RETAINED_PATH,
            "ownership": "g2_local_teleprompt_file_list_storage",
            "historical_source_available": False,
            "private_producing_commit_observable": False,
            "embedded_third_party_definitions": [],
        },
        "surface": {
            "linked_functions": 3,
            "ghidra_discovered_functions": 1,
            "additional_recovered_functions": 2,
            "path_anchored_functions": 1,
            "body_bytes": BODY_BYTES,
            "reachable_instruction_bytes": len(code),
            "outer_pool_regions": 1,
            "outer_pool_bytes": len(common._slice(blob, *POOL)),
            "physical_bytes": len(common._slice(blob, *PHYSICAL)),
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
            "global_record_address": GLOBAL,
            "record_bytes": RECORD_BYTES,
            "file_count_bytes": 2,
            "payload_bytes_after_count": RECORD_BYTES - 2,
            "update_null_is_ignored": True,
            "get_returns_live_global": True,
            "reset_zeroes_complete_record": True,
        },
        "provider_boundary": {
            "direct_external_calls": len(calls),
            "easylogger_calls": sum(counts[target] for target in (0x0043_CE9E, 0x0043_D0CE, 0x0043_D574)),
            "iar_dlib_calls": counts[0x0043_9BE4] + counts[0x0043_C0E4],
            "nanopb_direct_calls": 0,
            "new_version_discriminator": False,
        },
        "production": _validate_production(),
        "limitations": [
            "the historical first-party source, schema declaration, and producing commit are unavailable",
            "this storage object does not itself decode nanopb; schema decoding remains in the caller/provider object",
            "end-to-end device qualification is blocked by unavailable physical evidence",
        ],
    }


def _text(report: dict[str, object]) -> str:
    surface, providers = report["surface"], report["provider_boundary"]
    return "\n".join([
        "G2 teleprompt file-list closure",
        f"  image: {report['image']['sha256']}",
        f"  object: {surface['linked_functions']} functions / {surface['body_bytes']} body bytes / {surface['physical_bytes']} physical bytes",
        f"  calls: {surface['direct_body_calls']} direct; EasyLogger {providers['easylogger_calls']}; IAR DLIB {providers['iar_dlib_calls']}",
        f"  production routed: {str(report['production']['production_routed']).lower()}",
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
