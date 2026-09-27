#!/usr/bin/env python3
"""Summarize codec component source-completion blockers."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import analyze_g2_completion_readiness as readiness
import analyze_gx8002_source_readiness as gx8002_readiness


OUT = ROOT / "tools/manifests/g2-codec-source-blockers.json"
GX8002_BUILD_REPORT = ROOT / "build/gx8002-source-candidate/build-report.json"
SOURCE_ONLY_MANIFEST = ROOT / "manifests/g2-2.2.6.10-source-only.json"


def _typed_external_spans() -> list[dict]:
    gx8002_readiness.run_audit()
    with gx8002_readiness.MANIFEST.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    spans = []
    cursor = 0
    for row in rows:
        start = int(row["start"], 16)
        end = int(row["end_exclusive"], 16)
        size = int(row["size"])
        if start != cursor:
            raise RuntimeError("codec readiness manifest is no longer contiguous")
        cursor = end
        if row["readiness"] != "typed_unsupported_external_boundary":
            continue
        spans.append({
            "region": row["region"],
            "file_offset": start,
            "end_exclusive": end,
            "size": size,
            "sha256": row["sha256"],
            "byte_class": row["byte_class"],
            "source_provider": row["source_provider"],
            "source_license": row["source_license"],
            "payload_redistribution": row["payload_redistribution"],
            "production_route": row["production_route"],
            "evidence": row["evidence"],
        })
    return spans


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _source_only_macos_route() -> dict:
    manifest = _read_json(SOURCE_ONLY_MANIFEST)
    build = _read_json(GX8002_BUILD_REPORT)
    override = manifest["component_overrides"]["codec"]
    provider = override["provider"]
    if provider["kind"] != "source_build":
        raise RuntimeError("codec source-only provider is not source_build")
    if provider["sha256"] != build["firmware_sha256"]:
        raise RuntimeError("codec source-only provider digest disagrees")
    if provider["size"] != build["firmware_size"]:
        raise RuntimeError("codec source-only provider size disagrees")
    return {
        "manifest": "manifests/g2-2.2.6.10-source-only.json",
        "provider_path": provider["path"],
        "provider_kind": provider["kind"],
        "provider_size": provider["size"],
        "provider_sha256": provider["sha256"],
        "toolchain_profile": "apple-clang",
        "source_only": build["source_only"],
        "hardware_qualified": build["hardware_qualified"],
        "source_replacement_occurrences": build[
            "source_replacement_occurrences"],
        "byte_ownership": build["byte_ownership"],
    }


def analyze() -> dict:
    component = readiness.analyze()["components"]["codec"]
    detail = component["details"]["external_provider_detail"]
    spans = _typed_external_spans()
    bytes_by_class = {}
    for span in spans:
        bytes_by_class[span["byte_class"]] = (
            bytes_by_class.get(span["byte_class"], 0) + span["size"]
        )
    if bytes_by_class != detail["bytes_by_class"]:
        raise RuntimeError("codec typed span classes disagree with readiness totals")
    if sum(span["size"] for span in spans) != detail["bytes"]:
        raise RuntimeError("codec typed spans do not conserve external-provider bytes")
    return {
        "schema_version": 1,
        "component": "codec",
        "size": component["size"],
        "release_blocking_bytes": component["release_blocking_bytes"],
        "production_routed": component["production_routed"],
        "source_complete": component["source_complete"],
        "buckets": component["buckets"],
        "typed_external_spans": component["details"]["typed_external_spans"],
        "external_provider": {
            "bytes": detail["bytes"],
            "bytes_by_class": detail["bytes_by_class"],
            "open_source_available": detail["open_source_available"],
            "payload_redistribution_authority": detail[
                "payload_redistribution_authority"],
            "provider_contract": detail["provider_contract"],
        },
        "typed_external_span_map": {
            "span_count": len(spans),
            "bytes": sum(span["size"] for span in spans),
            "bytes_by_class": bytes_by_class,
            "spans": spans,
        },
        "source_only_macos_route": _source_only_macos_route(),
    }


def main() -> int:
    report = analyze()
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "release_blocking_bytes": report["release_blocking_bytes"],
        "production_routed": report["production_routed"],
        "typed_external_spans": report["typed_external_spans"],
        "bytes_by_class": report["external_provider"]["bytes_by_class"],
        "open_source_available": report["external_provider"][
            "open_source_available"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
