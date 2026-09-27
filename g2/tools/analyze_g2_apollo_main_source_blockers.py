#!/usr/bin/env python3
"""Summarize Apollo-main source-completion blockers."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import analyze_g2_completion_readiness as readiness


OUT = ROOT / "tools/manifests/g2-apollo-main-source-blockers.json"
CORE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
BUILD_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _source_build_route() -> dict:
    manifest = _read_json(CORE_MANIFEST)
    build = _read_json(BUILD_REPORT)
    provider = manifest["component_overrides"]["apollo_main"]["provider"]
    component = build["component"]
    if provider["kind"] != "source_build":
        raise RuntimeError("Apollo-main provider is not source_build")
    if provider["sha256"] != component["sha256"]:
        raise RuntimeError("Apollo-main provider digest disagrees")
    if provider["size"] != component["size"]:
        raise RuntimeError("Apollo-main provider size disagrees")
    return {
        "manifest": "manifests/g2-2.2.6.10-core-source.json",
        "provider_path": provider["path"],
        "provider_kind": provider["kind"],
        "provider_size": provider["size"],
        "provider_sha256": provider["sha256"],
        "toolchain_profile": build["toolchain"]["profile"],
        "toolchain_executable": build["toolchain"]["executable"],
        "source_owned_bytes": component["source_owned_bytes"],
        "source_owned_in_place_bytes": component[
            "source_owned_in_place_bytes"],
        "opaque_base_bytes": component["opaque_base_bytes"],
        "generated_patch_site_bytes": component[
            "generated_patch_site_bytes"],
        "generated_wrapper_bytes": component["generated_wrapper_bytes"],
    }


def analyze() -> dict:
    component = readiness.analyze()["components"]["apollo_main"]
    details = component["details"]
    pt_fields = {
        key: details[key]
        for key in sorted(details)
        if key.startswith("pt_protocol_")
    }
    return {
        "schema_version": 1,
        "component": "apollo_main",
        "size": component["size"],
        "release_blocking_bytes": component["release_blocking_bytes"],
        "production_routed": component["production_routed"],
        "buckets": component["buckets"],
        "origin_buckets": details["origin_buckets"],
        "release_readiness_partition": details["release_readiness_partition"],
        "unanchored_frontier_partition": details["unanchored_frontier_partition"],
        "pt_protocol": pt_fields,
        "raw_public_unrouted_bytes": readiness._read(
            readiness.RAW_ENCODING_SUMMARY
        )["metrics"]["public_unrouted_raw_instruction_transcript_bytes"],
        "source_build_route": _source_build_route(),
    }


def main() -> int:
    report = analyze()
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "release_blocking_bytes": report["release_blocking_bytes"],
        "origin_buckets": report["origin_buckets"],
        "unanchored_frontier_partition": report["unanchored_frontier_partition"],
        "raw_public_unrouted_bytes": report["raw_public_unrouted_bytes"],
        "pt_protocol_board_source_complete": report["pt_protocol"][
            "pt_protocol_board_source_complete"],
        "pt_protocol_retained_provider_bindings_remaining": report["pt_protocol"][
            "pt_protocol_retained_provider_bindings_remaining"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
