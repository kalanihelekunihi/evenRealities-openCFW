#!/usr/bin/env python3
"""Integrate the routed PT provider into the canonical G2 source manifest."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import open_cfw  # noqa: E402


MANIFEST = ROOT / "manifests" / "g2-2.2.6.10-core-source.json"
BUILD_REPORT = (
    ROOT / "components" / "apollo_main" / "core_overlay" / "build" /
    "build-report.json"
)
MAIN_CONFIG = (
    ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"
)
RUN_BASE = 0x00437FE0
INTERVAL_START = 0x0056F178
INTERVAL_END = 0x00577C3C
PREFIX = "pt_protocol_in_place_"
CLOCK_PREFIX = "clkmgr_divider_"
CLOCK_FUNCTIONS = (
    "open_cfw_clkmgr_hfrc2_uq15_divider",
    "open_cfw_clkmgr_hfrc_integer_divider",
)


class IntegrationError(RuntimeError):
    pass


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _region(name: str, function: str, address: int, size: int,
            status: str) -> dict[str, object]:
    return {
        "address_status": status,
        "file_offset": address - RUN_BASE,
        "function": function,
        "name": PREFIX + name,
        "output": f"apollo510b/main-pt-{name}-0x{address:08x}.bin",
        "size": size,
        "target": "apollo510b_internal_mram",
        "target_address": address,
    }


def _pt_regions(provider: dict[str, object]) -> list[dict[str, object]]:
    placement = provider["placement"]
    sections = sorted(
        ((name, int(record["runtime_address"]), int(record["size"]))
         for name, record in placement["sections"].items()),
        key=lambda item: item[1],
    )
    result: list[dict[str, object]] = []
    cursor = INTERVAL_START
    for name, address, size in sections:
        if address < cursor or address + size > INTERVAL_END:
            raise IntegrationError("PT source section leaves its interval")
        if address > cursor:
            result.append(_region(
                f"generated_gap_{cursor:08x}",
                "Generated erased padding around fixed-address PT source",
                cursor, address - cursor, "generated_padding"))
        label = name.removeprefix(".").replace("_", "-")
        result.append(_region(
            f"source_{label}",
            f"Compiled MIT G2 PT provider section {name}",
            address, size, "source_compiled"))
        cursor = address + size
    if cursor < INTERVAL_END:
        result.append(_region(
            f"generated_gap_{cursor:08x}",
            "Generated erased padding after in-place PT source",
            cursor, INTERVAL_END - cursor, "generated_padding"))
    if sum(int(item["size"]) for item in result) != INTERVAL_END - INTERVAL_START:
        raise IntegrationError("PT manifest interval does not conserve bytes")
    return result


def _sync_clock_regions(main: dict[str, object],
                        report: dict[str, object]) -> None:
    leaves = {
        item["extraction"]["function"]: item
        for item in report.get("relocated_leaves", [])
        if item.get("extraction", {}).get("function") in CLOCK_FUNCTIONS
    }
    if tuple(leaves) != CLOCK_FUNCTIONS:
        raise IntegrationError("canonical clock-manager leaf evidence changed")
    regions = [
        item for item in main["regions"]
        if not item["name"].startswith(CLOCK_PREFIX)
    ]
    cursor = sum(int(item["size"]) for item in regions)
    first_offset = (
        int(leaves[CLOCK_FUNCTIONS[0]]["extraction"]["runtime_address"])
        - RUN_BASE
    )
    if cursor != first_offset:
        padding = first_offset - cursor
        if padding <= 0:
            raise IntegrationError("clock-manager alignment placement changed")
        regions.append({
            "address_status": "generated_alignment",
            "file_offset": cursor,
            "function": "Generated alignment before the clock-manager divider source leaves",
            "name": CLOCK_PREFIX + "overlay_alignment",
            "output": "apollo510b/main-source-clkmgr-divider-alignment.bin",
            "size": padding,
            "target": "apollo510b_internal_mram",
            "target_address": RUN_BASE + cursor,
        })
        cursor += padding
    for function in CLOCK_FUNCTIONS:
        placement = leaves[function]["placement"]
        file_offset = int(placement["runtime_address"]) - RUN_BASE
        if file_offset != cursor:
            raise IntegrationError("clock-manager leaf partition is not contiguous")
        label = function.removeprefix("open_cfw_clkmgr_")
        size = int(placement["size"])
        regions.append({
            "address_status": "source_compiled",
            "file_offset": cursor,
            "function": f"Compiled MIT Apollo510 clock-manager leaf ({function})",
            "name": CLOCK_PREFIX + label + "_source_text",
            "output": f"apollo510b/main-source-clkmgr-{label.replace('_', '-')}-0x{RUN_BASE + cursor:08x}.bin",
            "size": size,
            "target": "apollo510b_internal_mram",
            "target_address": RUN_BASE + cursor,
        })
        cursor += size
    if cursor != int(main["provider"]["size"]):
        raise IntegrationError("clock-manager regions do not close at provider EOF")
    main["regions"] = regions


def apply() -> dict[str, object]:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    report = json.loads(BUILD_REPORT.read_text(encoding="utf-8"))
    component = report["component"]
    provider = report["overlay"]["post_link_providers"].get("pt_protocol")
    if not isinstance(provider, dict):
        raise IntegrationError("canonical build lacks routed PT provider")
    if (int(provider["placement"]["runtime_start"]) != INTERVAL_START or
            int(provider["placement"]["runtime_end_exclusive"]) != INTERVAL_END or
            int(provider["placement"]["writable_bytes"]) != 0 or
            len(provider["source_provider_routes"]) != 40 or
            len(provider["ingress_sites"]) != 3):
        raise IntegrationError("canonical PT provider evidence changed")

    main = data["component_overrides"]["apollo_main"]
    main_provider = main["provider"]
    main_provider["size"] = int(component["size"])
    main_provider["sha256"] = component["sha256"]
    main_config = json.loads(MAIN_CONFIG.read_text(encoding="utf-8"))
    linux_expected = main_config["toolchain_profiles"]["linux-clang"]["expected"]
    main_provider.setdefault("profiles", {})["linux-clang"] = {
        "size": int(linux_expected["component_size"]),
        "sha256": linux_expected["component_sha256"],
    }
    regions = main["regions"]
    overlapping = []
    for index, region in enumerate(regions):
        start = int(region["file_offset"]) + RUN_BASE
        end = start + int(region["size"])
        if start < INTERVAL_END and end > INTERVAL_START:
            overlapping.append((index, start, end, region))
    if not overlapping:
        raise IntegrationError("source manifest lacks the PT interval")
    first, last = overlapping[0][0], overlapping[-1][0]
    if [item[0] for item in overlapping] != list(range(first, last + 1)):
        raise IntegrationError("PT manifest interval is not contiguous")
    covered_start = overlapping[0][1]
    covered_end = overlapping[-1][2]
    if covered_start > INTERVAL_START or covered_end < INTERVAL_END:
        raise IntegrationError("PT manifest interval is not fully covered")

    replacement: list[dict[str, object]] = []
    if covered_start < INTERVAL_START:
        original = dict(overlapping[0][3])
        original["size"] = INTERVAL_START - covered_start
        replacement.append(original)
    replacement.extend(_pt_regions(provider))
    if covered_end > INTERVAL_END:
        original = dict(overlapping[-1][3])
        original["file_offset"] = INTERVAL_END - RUN_BASE
        original["target_address"] = INTERVAL_END
        original["size"] = covered_end - INTERVAL_END
        original["name"] = "opaque_after_pt_protocol_before_service_codec_dfu"
        original["function"] = (
            "Official Apollo bytes retained after source-owned PT protocol "
            "and before the authenticated codec-DFU service")
        original["output"] = (
            f"apollo510b/main-official-after-pt-before-codec-dfu-"
            f"0x{INTERVAL_END:08x}.bin")
        replacement.append(original)
    main["regions"][first:last + 1] = replacement
    _sync_clock_regions(main, report)
    marker = "source-owned complete product-test protocol"
    if marker not in main["function"]:
        main["function"] += "; " + marker
    clock_marker = "source-routed Apollo510 HFRC divider calculators"
    if clock_marker not in main["function"]:
        main["function"] += "; " + clock_marker

    open_cfw.atomic_write(
        MANIFEST,
        (json.dumps(data, indent=2) + "\n").encode("utf-8"),
    )
    merged, _root, payloads = open_cfw.verify_manifest(MANIFEST)
    image, _entries = open_cfw.assemble_evenota(merged, payloads)
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    data["package"]["expected_size"] = len(image)
    data["package"]["expected_sha256"] = sha256(image)
    open_cfw.atomic_write(
        MANIFEST,
        (json.dumps(data, indent=2) + "\n").encode("utf-8"),
    )
    return {
        "component_size": int(component["size"]),
        "component_sha256": component["sha256"],
        "package_size": len(image),
        "package_sha256": sha256(image),
        "pt_regions": len(_pt_regions(provider)),
        "hardware_validation": "blocked by unavailable physical evidence",
    }


def verify() -> dict[str, object]:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    report = json.loads(BUILD_REPORT.read_text(encoding="utf-8"))
    main = data["component_overrides"]["apollo_main"]
    component = report["component"]
    if (main["provider"]["size"], main["provider"]["sha256"]) != (
            component["size"], component["sha256"]):
        raise IntegrationError("PT provider manifest pin changed")
    pt = [item for item in main["regions"] if item["name"].startswith(PREFIX)]
    if (not pt or int(pt[0]["target_address"]) != INTERVAL_START or
            int(pt[-1]["target_address"]) + int(pt[-1]["size"]) != INTERVAL_END or
            sum(int(item["size"]) for item in pt) != INTERVAL_END - INTERVAL_START):
        raise IntegrationError("PT manifest region partition changed")
    clock = [item for item in main["regions"]
             if item["name"].startswith(CLOCK_PREFIX)]
    if (len(clock) != 3 or
            sum(int(item["size"]) for item in clock) != 108 or
            int(clock[-1]["target_address"]) + int(clock[-1]["size"])
            != int(main["provider"]["size"]) + RUN_BASE):
        raise IntegrationError("clock-manager manifest region partition changed")
    merged, _root, payloads = open_cfw.verify_manifest(MANIFEST)
    image, _entries = open_cfw.assemble_evenota(merged, payloads)
    if (len(image), sha256(image)) != (
            data["package"]["expected_size"],
            data["package"]["expected_sha256"]):
        raise IntegrationError("PT package pin changed")
    return {
        "component_sha256": component["sha256"],
        "package_sha256": sha256(image),
        "pt_regions": len(pt),
        "hardware_validation": "blocked by unavailable physical evidence",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("apply", "verify"))
    arguments = parser.parse_args()
    result = apply() if arguments.mode == "apply" else verify()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (IntegrationError, open_cfw.OpenCFWError, OSError, KeyError,
            json.JSONDecodeError) as error:
        raise SystemExit(f"G2 PT provider integration failed: {error}")
