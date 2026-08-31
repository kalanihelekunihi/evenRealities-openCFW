#!/usr/bin/env python3
"""Fail-closed G2 util_error_check/Goodix app_error source audit."""
from __future__ import annotations

import argparse
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
IMAGE_BYTES = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"

FUNCTION_MAP = ROOT / "tools/manifests/g2-util-error-check-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-util-error-check-closure.tsv"
PROVIDER_MAP = ROOT / "tools/manifests/g2-util-error-check-provider-map.tsv"
SOURCE_MAP = ROOT / "tools/manifests/goodix-gr551x-app-error-source.tsv"
GOODIX_SOURCE = ROOT / "third_party/goodix-gr551x-app-error/upstream/app_error.c"
GOODIX_PROVENANCE = ROOT / "third_party/goodix-gr551x-app-error/PROVENANCE.json"
CANDIDATE = ROOT / "components/apollo_main/core_overlay/util_error_check.c"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
INPUT_PINS = {
    FUNCTION_MAP: "07708501087eec4e2df11cf0d1323c405b5ba47bbc18c76dce7356cdcaa53e1f",
    CLOSURE: "5fe9933e32e37a26c3f29421a0a70e042c17cda8fbf9cb455e72de235c90e480",
    PROVIDER_MAP: "5bcb1b7df57371ffc155baa6ccfaf83f5966d058f444713c49405d68477bc585",
    SOURCE_MAP: "34c2363f93d97184e96b588fa2de2114c423114d7b6b95efca5b91210ce52829",
    GOODIX_SOURCE: "2f64e42b0528db162846e91179d4f5be46811b10fae16cfb80c827df7016f40d",
    GOODIX_PROVENANCE: "41e3f67fd61d0aa9c79dca841ca946701d8f048b0a576a3a8efa62c04abd6f7f",
    CANDIDATE: "1c3bc2b8f21bf3a24d1fe9bee568bd46c6902a508b12a4ff66968d570d94cb48",
}

RETAINED_PATH = r"D:\01_workspace\s200_ap510b_iar_git\utils\assert\util_error_check.c"
PATH_RUN = 0x0070_86C4
PATH_POINTER_CELLS = [0x0050_9C10]
FUNCTION = (0x0050_9B48, 0x0050_9BFA)
BODY_SHA256 = "3c12f284fbaedb30146e40bad627cebfa6cf2a505d9e5b7fff74b13df2d9e971"
PHYSICAL = (0x0050_9B48, 0x0050_9C1C)
PHYSICAL_SHA256 = "6fde560091bae10b4785b22bc3bd8d73e1fd98d22fded2ef31c4e7c0ede23317"
LITERAL = (0x0050_9BFA, 0x0050_9C1C)
LITERAL_SHA256 = "5b823b839a0db910be2f521671dba362b30fb23cd43b1c7334cc40ba58bdecf5"
PRECEDING = (0x0050_9AEA, 0x0050_9B48)
PRECEDING_SHA256 = "e85c0f0f85a07d3a1383e95e1847c0448ed6fb592d327c639e358c58bfcb20b1"
FOLLOWING = (0x0050_9C1C, 0x0050_9C96)
FOLLOWING_SHA256 = "00ac1cca4c47e64610a796ba85cc674ee457836fef3f1ee214cbcde174178000"

TABLE = (0x006C_8E60, 0x006C_8FB8)
TABLE_ROWS = 43
TABLE_SHA256 = "c7b7e16e29e0f58dad6a2c290de75e8fbe2df65545267784ad37198f82bf35e1"
TABLE_CODES = list(range(0x00, 0x1D)) + [0x80, 0x1D] + list(range(0x1F, 0x2B))

LITERAL_WORDS = {
    0x0050_9BFC: TABLE[0],
    0x0050_9C00: 0x0077_D78C,
    0x0050_9C04: 0x0077_46E8,
    0x0050_9C08: 0x0078_9EF0,
    0x0050_9C0C: 0x0077_D774,
    0x0050_9C10: PATH_RUN,
    0x0050_9C14: 0x0078_EDC4,
    0x0050_9C18: 0x0077_D7A4,
}
STRINGS = {
    PATH_RUN: RETAINED_PATH,
    0x0077_D78C: "Error code 0x%04X: %s",
    0x0077_46E8: "(%s) is not established.",
    0x0078_9EF0: "%s, %s %d, %s",
    0x0077_D774: "APP_errorFaultHandler",
    0x0078_EDC4: "assert",
    0x0077_D7A4: "[assert]%s, %s %d, %s",
}

ENTRY_COUNT = 103
ENTRY_SHA256 = "628c5a69b443388f026d8447181a7a94bd48b865645e5b4fce624160c4d77825"
CALL_COUNT = 8
CALL_SHA256 = "e00793cfc3da68b76c7952d0d408bd161682c7a66205d2712ffacc0943089d04"
STORED_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
EXTERNAL_TARGET_COUNTS = {
    0x0043_C0E4: 1,
    0x004B_4728: 2,
    0x0043_D0CE: 3,
    0x0043_D574: 1,
    0x0043_CE9E: 1,
}

GOODIX_SELECTED_COMMIT = "854c43e0b96a24051ffce4c06ff629255aa56c59"
GOODIX_SELECTED_BLOB = "d5027735dd01b0948a7315d9c595356fcb91f59b"
GOODIX_FIRST_INCOMPATIBLE_BLOB = "639f5cf10c5c293c899c76af83a9404b847d1090"


class AuditError(RuntimeError):
    """Raised when authenticated object or source evidence changes."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _slice(blob: bytes, start: int, end: int) -> bytes:
    first, last = start - BASE, end - BASE
    if first < 0 or first >= last or last > len(blob):
        raise AuditError(f"invalid image interval [0x{start:08x},0x{end:08x})")
    return blob[first:last]


def _cstring(blob: bytes, address: int) -> str:
    first = address - BASE
    last = blob.find(b"\0", first)
    if first < 0 or last < first:
        raise AuditError(f"invalid C string at 0x{address:08x}")
    return blob[first:last].decode("ascii")


def _pair_digest(pairs: list[tuple[int, int]]) -> str:
    return _sha256(b"".join(struct.pack("<II", *pair) for pair in pairs))


def _load_decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    import recover_apollo_embedded_source_paths as decoder
    return decoder


def _source_rows(source: str) -> list[tuple[str, str]]:
    return re.findall(r'\{\s*(SDK[A-Z0-9_]+),\s*"([^"]+)"\s*\},', source)


def analyze(image: Path = IMAGE) -> dict[str, object]:
    blob = image.read_bytes()
    if len(blob) != IMAGE_BYTES or _sha256(blob) != IMAGE_SHA256:
        raise AuditError("official G2 image changed")
    for path, expected in INPUT_PINS.items():
        if not path.is_file() or _sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned input changed: {path}")

    with FUNCTION_MAP.open(newline="", encoding="utf-8") as handle:
        functions = list(csv.DictReader(handle, delimiter="\t"))
    with PROVIDER_MAP.open(newline="", encoding="utf-8") as handle:
        providers = list(csv.DictReader(handle, delimiter="\t"))
    with SOURCE_MAP.open(newline="", encoding="utf-8") as handle:
        source_versions = list(csv.DictReader(handle, delimiter="\t"))
    if len(functions) != 1 or len(providers) != 3 or len(source_versions) != 5:
        raise AuditError("function/provider/source inventory changed")
    row = functions[0]
    if (
        row["function"] != "APP_errorFaultHandler"
        or int(row["stock_start"], 0) != FUNCTION[0]
        or int(row["stock_end_exclusive"], 0) != FUNCTION[1]
        or row["source_path_anchor"] != "yes"
    ):
        raise AuditError("function identity changed")
    if sum(int(re.match(r"(\d+)", provider["edges"]).group(1)) for provider in providers) != CALL_COUNT:
        raise AuditError("provider edge accounting changed")

    body = _slice(blob, *FUNCTION)
    literal = _slice(blob, *LITERAL)
    physical = _slice(blob, *PHYSICAL)
    if len(body) != 178 or _sha256(body) != BODY_SHA256 or _sha256(body) != row["stock_sha256"]:
        raise AuditError("handler body changed")
    if len(literal) != 34 or _sha256(literal) != LITERAL_SHA256:
        raise AuditError("handler literal pool changed")
    if len(physical) != 212 or _sha256(physical) != PHYSICAL_SHA256:
        raise AuditError("physical util_error_check object changed")
    if _sha256(_slice(blob, *PRECEDING)) != PRECEDING_SHA256:
        raise AuditError("preceding sensor-calibration tail changed")
    if _sha256(_slice(blob, *FOLLOWING)) != FOLLOWING_SHA256:
        raise AuditError("following utility function changed")
    if literal[:2] != bytes.fromhex("00bf"):
        raise AuditError("literal-pool alignment changed")
    for address, expected in LITERAL_WORDS.items():
        if struct.unpack_from("<I", blob, address - BASE)[0] != expected:
            raise AuditError(f"literal word changed at 0x{address:08x}")
    for address, expected in STRINGS.items():
        if _cstring(blob, address) != expected:
            raise AuditError(f"retained string changed at 0x{address:08x}")

    encoded_path = struct.pack("<I", PATH_RUN)
    cells: list[int] = []
    offset = blob.find(encoded_path)
    while offset >= 0:
        cells.append(BASE + offset)
        offset = blob.find(encoded_path, offset + 1)
    if cells != PATH_POINTER_CELLS:
        raise AuditError(f"retained-path pointer topology changed: {cells!r}")

    source_text = GOODIX_SOURCE.read_text()
    if "#define APP_ERROR_INFO_LEN          512" not in source_text:
        raise AuditError("Goodix automatic-buffer discriminator changed")
    if "#define APP_ERROR_CODE_NB           43" not in source_text:
        raise AuditError("Goodix 43-row discriminator changed")
    if "char s_error_print_info[APP_ERROR_INFO_LEN];" not in source_text:
        raise AuditError("Goodix buffer storage class changed")
    source_rows = _source_rows(source_text)
    if len(source_rows) != TABLE_ROWS:
        raise AuditError("selected Goodix source table changed")

    table = _slice(blob, *TABLE)
    if len(table) != TABLE_ROWS * 8 or _sha256(table) != TABLE_SHA256:
        raise AuditError("stock Goodix-derived error table changed")
    stock_rows: list[tuple[int, str]] = []
    for index in range(TABLE_ROWS):
        code, pointer = struct.unpack_from("<II", table, index * 8)
        stock_rows.append((code, _cstring(blob, pointer)))
    if [code for code, _ in stock_rows] != TABLE_CODES:
        raise AuditError("stock Goodix error-code order changed")
    if [message for _, message in stock_rows] != [message for _, message in source_rows]:
        raise AuditError("stock error strings no longer match SDK 1.7.0 source")

    provenance = json.loads(GOODIX_PROVENANCE.read_text())
    upstream = provenance["upstream"]
    boundary = provenance["version_boundary"]
    if (
        upstream["selected_public_carrier_commit"] != GOODIX_SELECTED_COMMIT
        or upstream["selected_git_blob"] != GOODIX_SELECTED_BLOB
        or upstream["exact_generating_commit"] is not None
        or boundary["first_located_incompatible_blob"] != GOODIX_FIRST_INCOMPATIBLE_BLOB
    ):
        raise AuditError("Goodix source provenance changed")
    selected = next(item for item in source_versions if item["source_version"] == "1.7.0")
    incompatible = next(item for item in source_versions if item["source_version"] == "2.0.1")
    official_upper = next(item for item in source_versions if item["source_version"] == "2.0.2")
    if (
        selected["commit"] != GOODIX_SELECTED_COMMIT
        or selected["git_blob_sha1"] != GOODIX_SELECTED_BLOB
        or incompatible["git_blob_sha1"] != GOODIX_FIRST_INCOMPATIBLE_BLOB
        or official_upper["git_blob_sha1"] != GOODIX_FIRST_INCOMPATIBLE_BLOB
    ):
        raise AuditError("Goodix source interval changed")

    overlay = json.loads(OVERLAY.read_text())
    candidate_rel = str(CANDIDATE.relative_to(ROOT))
    leaves = [
        item for item in overlay["relocated_leaves"]
        if item.get("function") == "open_cfw_app_error_fault_handler"
    ]
    patches = [
        item for item in overlay["patch_sites"]
        if item.get("name") == "replace_goodix_derived_app_error_fault_handler"
    ]
    if len(leaves) != 1 or len(patches) != 1:
        raise AuditError("production util-error routing cardinality changed")
    leaf = leaves[0]
    patch = patches[0]
    relocation_targets = {
        (item["symbol"], item.get("target_address"))
        for item in leaf.get("relocations", [])
    }
    if (
        leaf.get("source", {}).get("path") != candidate_rel
        or leaf.get("source", {}).get("sha256") != INPUT_PINS[CANDIDATE]
        or leaf.get("profiles") != ["apple-clang"]
        or leaf.get("expected", {}).get("size") != 254
        or not isinstance(leaf.get("expected", {}).get("offset"), int)
        or leaf.get("expected", {}).get("offset") % 4 != 0
        or leaf.get("expected", {}).get("unrelocated_sha256")
            != "ba2e1b6c02afc40bf0bcc9e6ca5ccd27f99552b4d20c1ec5d7cda2af44967285"
        or len(leaf.get("relocations", [])) != 8
        or relocation_targets != {
            ("memset", 0x0043C0E4),
            ("open_cfw_util_error_format", 0x004B4728),
            ("open_cfw_util_error_filter", 0x0043D0CE),
            ("open_cfw_util_error_log", 0x0043D574),
            ("open_cfw_util_error_async_log", 0x0043CE9E),
        }
        or patch.get("runtime_address") != FUNCTION[0]
        or patch.get("expected_size") != len(body)
        or patch.get("expected_sha256") != BODY_SHA256
        or patch.get("branch") != "b_w"
        or patch.get("target_function") != leaf["function"]
        or patch.get("profiles") != ["apple-clang"]
    ):
        raise AuditError("production util-error routing changed")

    decoder = _load_decoder()
    start = FUNCTION[0]
    interiors = set(range(start + 2, FUNCTION[1], 2))
    entries: list[tuple[int, int]] = []
    strict: list[tuple[int, int]] = []
    unknown: list[tuple[int, int]] = []
    for offset in range(0, len(blob) - 3, 2):
        site = BASE + offset
        target = decoder._thumb_bl_target(blob, site)
        if target == start:
            entries.append((site, target))
        elif target in interiors:
            strict.append((site, target))
        elif target is not None and PHYSICAL[0] <= target < PHYSICAL[1]:
            unknown.append((site, target))
    if len(entries) != ENTRY_COUNT or _pair_digest(entries) != ENTRY_SHA256:
        raise AuditError("direct handler entry topology changed")
    if any(PHYSICAL[0] <= site < PHYSICAL[1] for site, _ in entries) or strict or unknown:
        raise AuditError("handler entry closure changed")

    calls: list[tuple[int, int]] = []
    for site in range(FUNCTION[0], FUNCTION[1] - 3, 2):
        target = decoder._thumb_bl_target(blob, site)
        if target is not None and BASE <= target < BASE + len(blob):
            calls.append((site, target))
    if len(calls) != CALL_COUNT or _pair_digest(calls) != CALL_SHA256:
        raise AuditError("handler provider-call topology changed")
    counts = Counter(target for _, target in calls)
    if dict(counts) != EXTERNAL_TARGET_COUNTS:
        raise AuditError(f"handler provider targets changed: {counts!r}")

    encoded_starts = {start, start | 1}
    stored: list[tuple[int, int]] = []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        if value in encoded_starts:
            stored.append((BASE + offset, value))
    if stored or _pair_digest(stored) != STORED_SHA256:
        raise AuditError("stored handler pointer topology changed")

    return {
        "schema_version": 1,
        "analysis_mode": "read-only; no signing, flashing, erase, or hardware operation",
        "surface": {
            "retained_path": RETAINED_PATH,
            "linked_functions": 1,
            "path_anchored_functions": 1,
            "body_bytes": len(body),
            "literal_pool_bytes": len(literal),
            "physical_bytes": len(physical),
            "external_direct_bl_entry_sites": len(entries),
            "direct_body_calls": len(calls),
            "stored_entry_pointers": len(stored),
            "strict_interior_raw_bl_decodes": len(strict),
            "unrecovered_direct_object_targets": len(unknown),
        },
        "goodix_source_lineage": {
            "origin": "Goodix GR551x SDK components/libraries/app_error/app_error.c",
            "exact_source_snapshot_version": "1.7.0",
            "selected_public_carrier_commit": GOODIX_SELECTED_COMMIT,
            "selected_git_blob": GOODIX_SELECTED_BLOB,
            "source_table_rows": len(source_rows),
            "stock_table_rows": len(stock_rows),
            "stock_table_bytes": len(table),
            "stock_table_sha256": TABLE_SHA256,
            "first_located_incompatible_version": "2.0.1",
            "first_located_incompatible_blob": GOODIX_FIRST_INCOMPATIBLE_BLOB,
            "official_2_0_2_confirms_incompatible_blob": True,
            "exact_generating_commit": None,
            "public_carrier_is_official_goodix_release_commit": False,
            "classification": "byte-exact source oracle for copied/adapted utility, not a linked Goodix BLE stack",
        },
        "local_delta": {
            "handler_name": "app_error_fault_handler -> APP_errorFaultHandler",
            "removed_behavior": "SDK 1.7.0's out-of-range fallback branch",
            "logging_backend": "Goodix app_log_output/app_log_flush -> G2 EasyLogger integration",
            "preserved_behavior": [
                "512-byte automatic formatter buffer",
                "43-row SDK error table and exact messages",
                "API-return and boolean-expression formatter branches",
            ],
        },
        "provider_boundary": {
            "provider_rows": len(providers),
            "direct_external_targets": len(counts),
            "direct_external_calls": sum(counts.values()),
            "providers": [provider["provider"] for provider in providers],
        },
        "identity": {
            "source_derived_third_party_functions": ["APP_errorFaultHandler"],
            "source_derived_third_party_data_regions": ["[0x006C8E60,0x006C8FB8)"],
            "goodix_ble_stack_linkage_proven": False,
        },
        "production": {
            "candidate": candidate_rel,
            "candidate_sha256": INPUT_PINS[CANDIDATE],
            "production_routed": True,
            "ownership_bytes": len(body),
            "retained_stock_noncode_bytes": len(literal) + len(table),
            "relocated_leaf_bytes": leaf["expected"]["size"],
            "toolchain_profiles": leaf["profiles"],
            "bounded_unknown_code_fallback": True,
            "bound_providers": {
                symbol: f"0x{target:08x}"
                for symbol, target in sorted(relocation_targets)
            },
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=IMAGE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = analyze(args.image)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        surface = report["surface"]
        lineage = report["goodix_source_lineage"]
        print(
            "G2 util_error_check closure: PASS "
            f"({surface['linked_functions']} function, {surface['body_bytes']} body bytes, "
            f"{lineage['stock_table_rows']} Goodix error rows)"
        )
        print(
            "Goodix source: GR551x SDK 1.7.0 exact file snapshot; "
            "original release/Even generating commit unavailable"
        )
        print("hardware/flash operations: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
