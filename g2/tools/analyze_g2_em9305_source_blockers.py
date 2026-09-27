#!/usr/bin/env python3
"""Summarize BLE EM9305 source-completion blockers."""

from __future__ import annotations

from collections import Counter
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import analyze_g2_completion_readiness as readiness
import analyze_em9305_source_readiness as em9305_readiness


OUT = ROOT / "tools/manifests/g2-em9305-source-blockers.json"
CORE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
BUILD_REPORT = ROOT / "components/em9305/source_overlay/build/build-report.json"


def _bucket_counter(rows: list[dict], key: str) -> dict:
    counts: Counter[str] = Counter()
    bytes_by_key: Counter[str] = Counter()
    for row in rows:
        value = row[key]
        counts[value] += 1
        bytes_by_key[value] += row["size"]
    return {
        value: {
            "spans": counts[value],
            "bytes": bytes_by_key[value],
        }
        for value in sorted(bytes_by_key, key=lambda item: (-bytes_by_key[item], item))
    }


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _source_build_route() -> dict:
    manifest = _read_json(CORE_MANIFEST)
    build = _read_json(BUILD_REPORT)
    provider = manifest["component_overrides"]["ble_em9305"]["provider"]
    if provider["kind"] != "source_build":
        raise RuntimeError("EM9305 core provider is not source_build")
    if provider["sha256"] != build["provider"]["sha256"]:
        raise RuntimeError("EM9305 provider digest disagrees")
    if provider["size"] != build["provider"]["size"]:
        raise RuntimeError("EM9305 provider size disagrees")
    if provider["opaque_base_bytes"] != build["accounting"][
            "typed_retained_or_external_bytes"]:
        raise RuntimeError("EM9305 retained/provider byte count disagrees")
    return {
        "manifest": "manifests/g2-2.2.6.10-core-source.json",
        "provider_path": provider["path"],
        "provider_kind": provider["kind"],
        "provider_size": provider["size"],
        "provider_sha256": provider["sha256"],
        "package_toolchain_profile": "apple-clang",
        "component_toolchain": build["compiler"],
        "production_routed": build["production_routed"],
        "hardware_validation": build["hardware_validation"],
        "hardware_operations": build["hardware_operations"],
        "status": build["status"],
        "accounting": build["accounting"],
        "undefined_symbols": build["undefined_symbols"],
    }


def _residual_frontier() -> dict:
    audit = em9305_readiness.run_audit()
    ledger = audit["residual"]["ledger"]
    unresolved = [
        row for row in ledger
        if row["readiness"] != "concrete_source_available"
    ]
    return {
        "residual_ledger_spans": len(ledger),
        "residual_ledger_bytes": sum(row["size"] for row in ledger),
        "readiness": _bucket_counter(ledger, "readiness"),
        "decision_origins": _bucket_counter(ledger, "decision_origin"),
        "decisions": _bucket_counter(ledger, "decision"),
        "largest_unresolved_spans": [
            {
                "start": row["start"],
                "end": row["end"],
                "size": row["size"],
                "readiness": row["readiness"],
                "decision_origin": row["decision_origin"],
                "decision": row["decision"],
                "sha256": row["sha256"],
            }
            for row in sorted(unresolved, key=lambda item: (-item["size"], item["start"]))[:12]
        ],
    }


def analyze() -> dict:
    component = readiness.analyze()["components"]["ble_em9305"]
    details = component["details"]
    frontier = _residual_frontier()
    readiness_bytes = {
        key: value["bytes"] for key, value in frontier["readiness"].items()
    }
    if readiness_bytes != details["residual_readiness_bytes"]:
        raise RuntimeError("EM9305 residual frontier disagrees with readiness bytes")
    return {
        "schema_version": 1,
        "component": "ble_em9305",
        "size": component["size"],
        "release_blocking_bytes": component["release_blocking_bytes"],
        "production_routed": component["production_routed"],
        "source_complete": component["source_complete"],
        "buckets": component["buckets"],
        "residual_scope_bytes": details["residual_scope_bytes"],
        "residual_readiness_bytes": details["residual_readiness_bytes"],
        "residual_unclassified_bytes": details["residual_unclassified_bytes"],
        "final_source_readiness_receipts": details[
            "final_source_readiness_receipts"],
        "completion_bucket_mapping": details["completion_bucket_mapping"],
        "residual_frontier": frontier,
        "source_build_route": _source_build_route(),
    }


def main() -> int:
    report = analyze()
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "release_blocking_bytes": report["release_blocking_bytes"],
        "production_routed": report["production_routed"],
        "residual_scope_bytes": report["residual_scope_bytes"],
        "residual_readiness_bytes": report["residual_readiness_bytes"],
        "ledger_sha256": report["final_source_readiness_receipts"]["ledger"][
            "sha256"],
        "summary_sha256": report["final_source_readiness_receipts"]["summary"][
            "sha256"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
