#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Comprehensive software-readiness ledger for the shipped G2 touch prefix."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
MANIFEST_DIR = TOOLS / "manifests"

ANALYZERS = {
    "identity": TOOLS / "analyze_g2_touch_identity.py",
    "prefix": TOOLS / "analyze_g2_touch_prefix_function_map.py",
    "helpers": TOOLS / "analyze_g2_touch_prefix_helper_evidence.py",
    "policy": TOOLS / "analyze_g2_touch_policy_helpers_source.py",
    "i2c_source": TOOLS / "analyze_g2_touch_i2c_source.py",
    "sensing_source": TOOLS / "analyze_g2_touch_sensing_source.py",
}

EXPECTED = {
    "function_count": 63,
    "function_status_counts": {
        "external_eula_clean_room_required": 20,
        "project_fail_closed_contract": 8,
        "project_source_candidate": 10,
        "still_unclassified": 3,
        "unsupported_intentional_noop": 1,
        "upstream_apache_provider": 14,
        "upstream_runtime_provider": 7,
    },
    "mapped_code_physical_bytes": 6316,
    "code_unmapped_or_data_bytes": 24048,
    "mapped_code_status_bytes": {
        "external_eula_clean_room_required": 1948,
        "project_fail_closed_contract": 1560,
        "project_source_candidate": 816,
        "still_unclassified": 142,
        "unsupported_intentional_noop": 8,
        "upstream_apache_provider": 1068,
        "upstream_runtime_provider": 774,
    },
    "whole_blob_bucket_bytes": {
        "generated_transport_fill": 512,
        "project_source_candidate": 816,
        "still_unclassified": 24190,
        "typed_external_or_unsupported": 8946,
    },
    "function_ledger_digest": "2eaa614f6a0a1d0270e29764db3f8f4565ac7bd890dc6485c4e54f34fdbc99c7",
    "byte_ledger_digest": "6daf63278f00904cbd791da8bee30edd5e515ff1b631461581b270f887d9b230",
}

EVIDENCE_STATUS = {
    0x02F4: ("external_eula_clean_room_required",
             "runtime_touch_sensing.c provider wrapper",
             "MIT OR GPL-3.0-only wrapper; LicenseRef-Infineon-EULA provider excluded",
             "implement/choose a CapSense sensor provider without copying EULA source"),
    0x0378: ("project_fail_closed_contract",
             "runtime_touch_i2c_protocol.c transport boundary",
             "MIT OR GPL-3.0-only wrapper",
             "supply SCB/resident-HAL initialization provider"),
    0x0400: ("project_source_candidate", "runtime_touch_i2c_protocol.c",
             "MIT OR GPL-3.0-only", "retain source candidate; supply IRQ/HAL integration externally"),
    0x0824: ("project_source_candidate", "runtime_touch_i2c_protocol.c",
             "MIT OR GPL-3.0-only", "retain source candidate and validate before production routing"),
    0x0BE0: ("unsupported_intentional_noop", "compiled-out logger",
             "not applicable", "omit or retain an explicit no-op logger"),
    0x3624: ("project_fail_closed_contract",
             "runtime_touch_i2c_protocol.c callback boundary",
             "MIT OR GPL-3.0-only wrapper", "supply the resident callback-registry integration"),
    0x36C4: ("project_source_candidate", "runtime_touch_sensing.c",
             "MIT OR GPL-3.0-only", "retain source candidate; supply MSCLP operations through ports"),
    0x37C0: ("project_fail_closed_contract",
             "runtime_touch_i2c_protocol.c event callback",
             "MIT OR GPL-3.0-only wrapper", "supply event-table/provider implementation"),
    0x4B14: ("upstream_apache_provider", "CMSIS-Core / Infineon CAT2 PDL",
             "Apache-2.0", "use upstream NVIC_SystemReset implementation with notices"),
    0x4B30: ("project_fail_closed_contract",
             "runtime_touch_i2c_protocol.c enter_dfu_and_reset port",
             "MIT OR GPL-3.0-only wrapper", "supply resident boot/DFU provider; unavailable in prefix"),
    0x67D8: ("project_source_candidate", "runtime_touch_i2c_protocol.c",
             "MIT OR GPL-3.0-only", "retain FIFO descriptor source candidate"),
    0x67F0: ("project_source_candidate", "runtime_touch_i2c_protocol.c",
             "MIT OR GPL-3.0-only", "retain FIFO descriptor source candidate"),
    0x6806: ("project_source_candidate", "runtime_touch_i2c_protocol.c",
             "MIT OR GPL-3.0-only", "retain FIFO position source candidate"),
    0x703C: ("upstream_apache_provider", "Infineon CAT2 PDL power API",
             "Apache-2.0", "use upstream power-mode provider with notices"),
    0x7074: ("upstream_apache_provider", "Cy_SysPm_CpuEnterSleepNoCallbacks",
             "Apache-2.0", "use upstream CAT2 PDL function with notices"),
    0x7088: ("upstream_apache_provider", "Cy_SysPm_CpuEnterDeepSleepNoCallbacks",
             "Apache-2.0", "use upstream CAT2 PDL function with notices"),
}

VECTOR_ENTRIES = {0x465C, 0x465E, 0x4674}


class AuditError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None,
            f"cannot load {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _set_digest(addresses: set[int], payload: bytes) -> tuple[str, str]:
    ordered = sorted(addresses)
    address_digest = sha256(b"".join(struct.pack("<I", value) for value in ordered))
    content_digest = sha256(bytes(payload[value] for value in ordered))
    return address_digest, content_digest


def _ledger_digest(rows: list[dict], keys: tuple[str, ...]) -> str:
    stable = [{key: row[key] for key in keys} for row in rows]
    return sha256(json.dumps(stable, sort_keys=True,
                             separators=(",", ":")).encode())


def analyze(*, enforce_expected: bool = True) -> dict:
    identity = _load(ANALYZERS["identity"], "touch_readiness_identity")
    prefix_mod = _load(ANALYZERS["prefix"], "touch_readiness_prefix")
    helper_mod = _load(ANALYZERS["helpers"], "touch_readiness_helpers")
    policy_mod = _load(ANALYZERS["policy"], "touch_readiness_policy")
    i2c_mod = _load(ANALYZERS["i2c_source"], "touch_readiness_i2c_source")
    sensing_mod = _load(ANALYZERS["sensing_source"], "touch_readiness_sensing_source")

    prefix = prefix_mod.analyze()
    helpers = helper_mod.analyze()
    policy = policy_mod.analyze()
    i2c_source = i2c_mod.audit()
    sensing_source = sensing_mod.audit()
    require(i2c_source["status"].startswith("implemented-in-source"),
            "I2C source closure changed")
    require(sensing_source["status"].startswith("implemented-in-source"),
            "sensing source closure changed")
    require(policy["metrics"]["stock_boundaries"] == 8,
            "policy source closure changed")

    blob = prefix_mod.BLOB.read_bytes()
    payload = blob[prefix_mod.RECORD_OFFSET:
                   prefix_mod.RECORD_OFFSET + prefix_mod.RECORD_SIZE]
    identity_report = identity.audit(blob)
    require(all(item["result"] == "pass" for item in identity_report["checks"]),
            "touch identity audit changed")

    helper_by_entry = {row["entry"]: row for row in helpers["rows"]}
    policy_by_entry = {row["stock_entry"]: row for row in policy["boundaries"]}
    function_rows = []
    status_by_entry = {}
    for row in prefix["rows"]:
        entry = row["entry"]
        name = row["name"]
        if entry in helper_by_entry:
            helper = helper_by_entry[entry]
            name = helper["proposed_name"]
            boundary = helper["boundary"]
            if boundary == "open_cfw_clean_room":
                closure = policy_by_entry[entry]
                if closure["closure"] == "implemented":
                    status = "project_source_candidate"
                else:
                    status = "project_fail_closed_contract"
                artifact = "components/shared/touch/runtime_touch_policy_helpers.c"
                license_name = "MIT"
                action = closure["evidence_limit"]
            elif boundary == "infineon_cat2_pdl":
                status = "upstream_apache_provider"
                artifact = helpers["providers"][boundary]["source"]
                license_name = "Apache-2.0"
                action = helpers["providers"][boundary]["use"]
            elif boundary in ("infineon_capsense", "infineon_emeeprom"):
                status = "external_eula_clean_room_required"
                artifact = helpers["providers"][boundary]["source"]
                license_name = "LicenseRef-Infineon-EULA"
                action = helpers["providers"][boundary]["use"]
            elif boundary == "toolchain_runtime":
                status = "upstream_runtime_provider"
                artifact = "selected ARM EABI/C runtime"
                license_name = "LicenseRef-Upstream-Toolchain-Runtime"
                action = helpers["providers"][boundary]["use"]
            else:
                raise AuditError(f"unknown helper boundary: {boundary}")
            evidence = helper["evidence"]
        elif entry in EVIDENCE_STATUS:
            status, artifact, license_name, action = EVIDENCE_STATUS[entry]
            evidence = row["evidence"]
        elif entry in VECTOR_ENTRIES:
            status = "still_unclassified"
            artifact = "none"
            license_name = "unknown"
            action = "resolve vector-target semantics before standalone startup replacement"
            evidence = "authenticated vector target with shared suffix; semantic role unresolved"
        else:
            raise AuditError(f"function {entry:#x} has no readiness classification")
        status_by_entry[entry] = status
        function_rows.append({
            "entry": entry,
            "name": name,
            "status": status,
            "instruction_bytes": row["instruction_bytes"],
            "instruction_sha256": row["instruction_sha256"],
            "source_or_provider": artifact,
            "license": license_name,
            "action": action,
            "evidence": evidence,
        })

    require(len(function_rows) == len(prefix["rows"]) == 63,
            "function ledger is not exhaustive")
    function_counts = dict(sorted(Counter(
        row["status"] for row in function_rows
    ).items()))

    entries = set(status_by_entry)
    byte_statuses: dict[int, set[str]] = defaultdict(set)
    for row in prefix["rows"]:
        body = prefix_mod._walk(payload, row["entry"], entries)
        status = status_by_entry[row["entry"]]
        for address, insn in body["instructions"].items():
            for byte in range(address, address + insn.size):
                byte_statuses[byte].add(status)
    require(all(len(statuses) == 1 for statuses in byte_statuses.values()),
            "shared function bytes have conflicting readiness statuses")
    code_sets: dict[str, set[int]] = defaultdict(set)
    for address, statuses in byte_statuses.items():
        code_sets[next(iter(statuses))].add(address)
    mapped_status_bytes = dict(sorted(
        (status, len(addresses)) for status, addresses in code_sets.items()
    ))
    all_code = set(range(prefix_mod.CODE_START, prefix_mod.CODE_END))
    mapped_code = set(byte_statuses)
    unmapped_code = all_code - mapped_code
    require(not (all_code - mapped_code - unmapped_code),
            "code accounting left an unassigned byte")

    byte_rows = []

    def add_set(scope: str, addresses: set[int], category: str,
                bucket: str, note: str, coordinate: str = "payload") -> None:
        address_digest, content_digest = _set_digest(addresses, payload)
        byte_rows.append({
            "scope": scope, "coordinate": coordinate,
            "start": min(addresses) if addresses else None,
            "end": max(addresses) + 1 if addresses else None,
            "bytes": len(addresses), "category": category,
            "bucket": bucket, "address_set_sha256": address_digest,
            "content_sha256": content_digest, "note": note,
        })

    # FWPK wrapper is outside payload coordinates; hash it directly.
    wrapper = blob[:prefix_mod.RECORD_OFFSET]
    byte_rows.append({
        "scope": "fwpk_wrapper", "coordinate": "blob", "start": 0,
        "end": prefix_mod.RECORD_OFFSET, "bytes": len(wrapper),
        "category": "generated_transport", "bucket": "generated_transport_fill",
        "address_set_sha256": sha256(b"".join(
            struct.pack("<I", value) for value in range(len(wrapper))
        )), "content_sha256": sha256(wrapper),
        "note": "FWPK header and type-3 record descriptor",
    })
    for status, addresses in sorted(code_sets.items()):
        bucket = ("project_source_candidate" if status == "project_source_candidate"
                  else "still_unclassified" if status == "still_unclassified"
                  else "typed_external_or_unsupported")
        add_set(f"reachable_code:{status}", addresses, status, bucket,
                "non-contiguous reachable instruction bytes; shared tails deduplicated")
    add_set("code_unmapped_or_data", unmapped_code, "still_unclassified",
            "still_unclassified",
            "literal pools, rodata, unreachable code, and undiscovered entry bodies are not distinguished")

    region_policy = {
        "vectors": ("typed_startup_data", "typed_external_or_unsupported"),
        "strings": ("unsupported_diagnostic_strings", "typed_external_or_unsupported"),
        "const_tables_a": ("external_capsense_configuration", "typed_external_or_unsupported"),
        "const_tables_b": ("external_capsense_configuration", "typed_external_or_unsupported"),
        "config_block": ("external_capsense_configuration", "typed_external_or_unsupported"),
        "zero_gap_1": ("generated_fill", "generated_transport_fill"),
        "zero_gap_2": ("generated_fill", "generated_transport_fill"),
        "ff_pad": ("generated_fill", "generated_transport_fill"),
        "trailing_crc": ("generated_transport", "generated_transport_fill"),
    }
    for name, start, end, digest, _cls, _state, notes in identity.REGIONS:
        if name == "code":
            continue
        category, bucket = region_policy[name]
        addresses = set(range(start, end))
        address_digest, content_digest = _set_digest(addresses, payload)
        require(content_digest == digest,
                f"identity region digest changed in byte ledger: {name}")
        byte_rows.append({
            "scope": name, "coordinate": "payload", "start": start,
            "end": end, "bytes": end - start, "category": category,
            "bucket": bucket, "address_set_sha256": address_digest,
            "content_sha256": content_digest, "note": notes,
        })

    require(sum(row["bytes"] for row in byte_rows) == len(blob),
            "whole-blob byte ledger does not reconcile")
    bucket_counter = Counter()
    for row in byte_rows:
        bucket_counter[row["bucket"]] += row["bytes"]
    bucket_bytes = dict(sorted(bucket_counter.items()))

    metrics = {
        "function_count": len(function_rows),
        "function_status_counts": function_counts,
        "mapped_code_physical_bytes": len(mapped_code),
        "code_unmapped_or_data_bytes": len(unmapped_code),
        "mapped_code_status_bytes": mapped_status_bytes,
        "whole_blob_bytes": len(blob),
        "payload_bytes": len(payload),
        "whole_blob_bucket_bytes": bucket_bytes,
        "function_ledger_digest": _ledger_digest(function_rows, (
            "entry", "name", "status", "instruction_bytes",
            "instruction_sha256", "source_or_provider", "license", "action",
        )),
        "byte_ledger_digest": _ledger_digest(byte_rows, (
            "scope", "coordinate", "start", "end", "bytes", "category",
            "bucket", "address_set_sha256", "content_sha256",
        )),
    }
    if enforce_expected:
        for key, expected in EXPECTED.items():
            require(metrics[key] == expected,
                    f"readiness {key} changed: {metrics[key]!r} != {expected!r}")

    resident = list(prefix["resident_abi"])
    return {
        "schema_version": 1,
        "component": "G2 touch-controller shipped prefix",
        "analysis_mode": "offline composed evidence/source/provider/byte ledger; no hardware, MMIO, reset, DFU, signing, or flash operation",
        "identity": prefix["identity"],
        "metrics": metrics,
        "function_rows": function_rows,
        "byte_rows": byte_rows,
        "resident_external_abi": resident,
        "source_audits": {
            "i2c": {"status": i2c_source["status"],
                    "license": i2c_source["license"], "exports": len(i2c_source["exports"])},
            "sensing": {"status": sensing_source["status"],
                        "license": sensing_source["license"], "exports": len(sensing_source["exports"])},
            "policy_helpers": {"status": "isolated candidate",
                               "license": policy["license"],
                               "exports": len(policy["exports"])},
        },
        "provider_boundaries": helpers["providers"],
        "release_readiness": {
            "software_complete": False,
            "blocking_unclassified_code_or_data_bytes": len(unmapped_code),
            "blocking_unclassified_reachable_functions": function_counts["still_unclassified"],
            "resident_abi_available": False,
            "production_routed": False,
            "hardware_validated": False,
            "next_actions": [
                "separate code from pools/data and discover remaining entries in the 24,048-byte code-span remainder",
                "resolve the three shared-suffix vector target roles",
                "supply or clean-room replace CAPSENSE and Em_EEPROM providers without copying EULA source",
                "specify/replace resident tables and resident boot/DFU ABI",
                "select Apache-2.0 CAT2 PDL and licensed ARM runtime versions",
                "retain the audited MIT OR GPL-3.0-only project-source grant while preserving all provider licenses",
            ],
        },
        "accounting_note": "Function instruction sizes overlap at shared tails and are not physical byte totals; byte_rows is the exhaustive deduplicated blob accounting.",
    }


def write_manifests(result: dict) -> list[Path]:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    functions = MANIFEST_DIR / "g2-touch-software-readiness-functions.tsv"
    with functions.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["entry", "name", "status", "instruction_bytes",
                         "instruction_sha256", "source_or_provider", "license",
                         "action", "evidence"])
        for row in result["function_rows"]:
            writer.writerow([
                f"0x{row['entry']:04X}", row["name"], row["status"],
                row["instruction_bytes"], row["instruction_sha256"],
                row["source_or_provider"], row["license"], row["action"],
                row["evidence"],
            ])

    bytes_path = MANIFEST_DIR / "g2-touch-software-readiness-bytes.tsv"
    with bytes_path.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["scope", "coordinate", "start", "end_exclusive",
                         "bytes", "category", "bucket", "address_set_sha256",
                         "content_sha256", "note"])
        for row in result["byte_rows"]:
            writer.writerow([
                row["scope"], row["coordinate"],
                "-" if row["start"] is None else f"0x{row['start']:04X}",
                "-" if row["end"] is None else f"0x{row['end']:04X}",
                row["bytes"], row["category"], row["bucket"],
                row["address_set_sha256"], row["content_sha256"], row["note"],
            ])

    abi = MANIFEST_DIR / "g2-touch-software-readiness-external-abi.tsv"
    with abi.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["reference_offset", "resident_address",
                         "availability", "role", "shipped_bytes"])
        for row in result["resident_external_abi"]:
            writer.writerow([
                "-" if row["reference_offset"] is None
                else f"0x{row['reference_offset']:04X}",
                "unavailable" if row["address"] is None
                else f"0x{row['address']:04X}",
                row["availability"], row["role"], 0,
            ])

    summary = MANIFEST_DIR / "g2-touch-software-readiness-summary.json"
    slim = {key: value for key, value in result.items()
            if key not in ("function_rows", "byte_rows")}
    slim["function_row_count"] = len(result["function_rows"])
    slim["byte_row_count"] = len(result["byte_rows"])
    summary.write_text(json.dumps(slim, indent=2, sort_keys=True) + "\n")
    return [functions, bytes_path, abi, summary]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-manifests", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = analyze()
    if args.write_manifests:
        for path in write_manifests(result):
            print(f"wrote {path.relative_to(ROOT)}")
    if args.json:
        print(json.dumps({key: value for key, value in result.items()
                          if key not in ("function_rows", "byte_rows")},
                         indent=2, sort_keys=True))
    else:
        metrics = result["metrics"]
        print(f"touch functions: {metrics['function_count']}")
        print(f"mapped code bytes: {metrics['mapped_code_physical_bytes']}")
        print(f"unclassified code/pool bytes: {metrics['code_unmapped_or_data_bytes']}")
        print(f"software complete: {result['release_readiness']['software_complete']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Touch software readiness audit failed: {exc}") from exc
