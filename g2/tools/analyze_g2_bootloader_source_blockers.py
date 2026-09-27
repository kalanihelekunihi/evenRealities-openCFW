#!/usr/bin/env python3
"""Summarize Apollo bootloader source-completion blockers."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import analyze_g2_completion_readiness as readiness


OUT = ROOT / "tools/manifests/g2-bootloader-source-blockers.json"
CORE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
BUILD_REPORT = ROOT / "components/bootloader/core_overlay/build/build-report.json"


def _family(name: str) -> str:
    value = name.removeprefix("opaque_before_").removeprefix("opaque_after_")
    if value.startswith("replace_bootloader_easylogger"):
        return "easylogger_replacement_frontier"
    if value.startswith("replace_easylogger"):
        return "easylogger_replacement_frontier"
    if value.startswith("replace_littlefs"):
        return "littlefs_replacement_frontier"
    if "spotmgr" in value:
        return "spotmgr_source_in_place_frontier"
    if "platform_services" in value:
        return "platform_services_source_in_place_frontier"
    if value.startswith("source_redirects"):
        return "post_redirect_tail"
    if value.startswith("replace_bootloader_redirect_init"):
        return "redirect_init_frontier"
    return "other_retained_official"


def _retained_official_frontier() -> dict:
    core = json.loads(CORE_MANIFEST.read_text(encoding="utf-8"))
    regions = core["component_overrides"]["apollo_bootloader"]["regions"]
    retained = []
    for row in regions:
        if row.get("address_status") != "official_blob":
            continue
        retained.append({
            "name": row["name"],
            "file_offset": int(row["file_offset"]),
            "end_exclusive": int(row["file_offset"]) + int(row["size"]),
            "size": int(row["size"]),
            "family": _family(row["name"]),
            "function": row["function"],
            "output": row["output"],
        })
    bytes_by_family = {}
    intervals_by_family = {}
    for row in retained:
        family = row["family"]
        bytes_by_family[family] = bytes_by_family.get(family, 0) + row["size"]
        intervals_by_family[family] = intervals_by_family.get(family, 0) + 1
    return {
        "interval_count": len(retained),
        "bytes": sum(row["size"] for row in retained),
        "bytes_by_family": dict(sorted(
            bytes_by_family.items(),
            key=lambda item: (-item[1], item[0]),
        )),
        "intervals_by_family": dict(sorted(intervals_by_family.items())),
        "largest_intervals": sorted(
            retained,
            key=lambda row: (-row["size"], row["file_offset"]),
        )[:16],
    }


def _source_build_route() -> dict:
    build = json.loads(BUILD_REPORT.read_text(encoding="utf-8"))
    provider = build["provider_contract"]["provider"]
    component = build["component"]
    if provider["kind"] != "source_build":
        raise RuntimeError("bootloader provider is not source_build")
    if provider["sha256"] != component["sha256"]:
        raise RuntimeError("bootloader provider digest disagrees")
    if provider["size"] != component["size"]:
        raise RuntimeError("bootloader provider size disagrees")
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
        "hardware_operations": build["safety"]["hardware_operations"],
    }


def analyze() -> dict:
    component = readiness.analyze()["components"]["apollo_bootloader"]
    details = component["details"]
    frontier = _retained_official_frontier()
    if frontier["bytes"] != details["retained_complement"]["retained_official_bytes"]:
        raise RuntimeError("bootloader retained frontier disagrees with complement")
    if frontier["interval_count"] != details["retained_complement"][
        "intervals_by_address_status"]["official_blob"]:
        raise RuntimeError("bootloader retained interval count disagrees")
    return {
        "schema_version": 1,
        "component": "apollo_bootloader",
        "size": component["size"],
        "release_blocking_bytes": component["release_blocking_bytes"],
        "production_routed": component["production_routed"],
        "source_complete": component["source_complete"],
        "buckets": component["buckets"],
        "source_owned_in_place_bytes": details["source_owned_in_place_bytes"],
        "retained_complement": details["retained_complement"],
        "clkmgr_divider_source_functions": details[
            "clkmgr_divider_source_functions"],
        "clkmgr_divider_source_stock_bytes": details[
            "clkmgr_divider_source_stock_bytes"],
        "clkmgr_divider_production_routed": details[
            "clkmgr_divider_production_routed"],
        "retained_official_frontier": frontier,
        "source_build_route": _source_build_route(),
    }


def main() -> int:
    report = analyze()
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "release_blocking_bytes": report["release_blocking_bytes"],
        "production_routed": report["production_routed"],
        "source_owned_in_place_bytes": report["source_owned_in_place_bytes"],
        "retained_official_bytes": report["retained_complement"][
            "retained_official_bytes"],
        "intervals_by_address_status": report["retained_complement"][
            "intervals_by_address_status"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
