#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""MIT fail-closed consistency checks for mutable Apollo-main aggregates."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Type


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_apollo_main_artifacts(
    root: Path,
    error_type: Type[Exception] = RuntimeError,
    label: str = "Apollo-main",
) -> dict[str, Any]:
    """Validate current cross-artifact identities without freezing old totals.

    Module-local source/function/region pins belong in each analyzer. This
    helper owns only aggregate relationships that legitimately change after a
    reviewed source admission.
    """
    try:
        overlay = json.loads((root / "components/apollo_main/core_overlay/overlay.json").read_text())
        build = json.loads((root / "components/apollo_main/core_overlay/build/build-report.json").read_text())
        manifest = json.loads((root / "manifests/g2-2.2.6.10-core-source.json").read_text())
        package_path = (root / "build/source/package" /
                        manifest["package"]["output_name"])
        package = package_path.read_bytes()
        plan = json.loads((root / "build/source/flash-plan.json").read_text())
        expected = overlay["expected"]
        expected_build = (
            expected["overlay_size"], expected["overlay_sha256"],
            expected["component_size"], expected["component_sha256"],
        )
        actual_build = (
            build["overlay"]["size"], build["overlay"]["sha256"],
            build["component"]["size"], build["component"]["sha256"],
        )
        if actual_build != expected_build:
            raise error_type(f"{label} build diverges from overlay.json expected")
        provider = manifest["component_overrides"]["apollo_main"]["provider"]
        if (provider["size"], provider["sha256"]) != actual_build[2:]:
            raise error_type(f"{label} manifest provider diverges from build component")
        package_expected = manifest["package"]
        if (len(package), _sha256(package)) != (
                package_expected["expected_size"], package_expected["expected_sha256"]):
            raise error_type(f"{label} package file diverges from manifest")
        if plan.get("package_sha256") != package_expected["expected_sha256"]:
            raise error_type(f"{label} flash plan package hash diverges from manifest")
        if not plan.get("flash_regions"):
            raise error_type(f"{label} flash plan has no flash regions")
        if plan.get("unresolved_flash_regions") != []:
            raise error_type(f"{label} flash plan has unresolved regions")
        for collection in ("container_only_regions", "protected_regions"):
            if collection not in plan or not isinstance(plan[collection], list):
                raise error_type(f"{label} flash plan lacks {collection}")
        return {
            "overlay": build["overlay"],
            "component": build["component"],
            "package": {"size": len(package), "sha256": _sha256(package)},
            "flash_regions": len(plan["flash_regions"]),
            "unresolved_flash_regions": 0,
            "container_only_regions": len(plan["container_only_regions"]),
            "protected_regions": len(plan["protected_regions"]),
        }
    except error_type:
        raise
    except Exception as exc:
        raise error_type(f"{label} aggregate artifact structure invalid: {exc}") from exc


def validate_region_tiling(
    regions: Iterable[Mapping[str, Any]],
    start: int,
    end_exclusive: int,
    error_type: Type[Exception] = RuntimeError,
    label: str = "manifest interval",
    allowed_statuses: tuple[str, ...] = (
        "official_blob", "generated_source_entry_replacement",
    ),
) -> dict[str, int]:
    """Prove exact interval conservation without freezing ownership totals."""
    try:
        tiles = sorted(
            (item for item in regions
             if start <= item.get("target_address", -1) < end_exclusive),
            key=lambda item: item["target_address"],
        )
        cursor = start
        totals = {status: 0 for status in allowed_statuses}
        for item in tiles:
            address = item["target_address"]
            size = item["size"]
            status = item.get("address_status")
            if address != cursor or not isinstance(size, int) or size <= 0:
                raise error_type(f"{label} is gapped, overlapping, or zero-sized")
            if address + size > end_exclusive or status not in totals:
                raise error_type(f"{label} has an out-of-range or unsupported tile")
            totals[status] += size
            cursor += size
        if cursor != end_exclusive:
            raise error_type(f"{label} does not cover its complete interval")
        return totals
    except error_type:
        raise
    except Exception as exc:
        raise error_type(f"{label} tiling structure invalid: {exc}") from exc


def validate_composed_source_replacement(
    regions: Iterable[Mapping[str, Any]],
    start: int,
    end_exclusive: int,
    own_prefix: str,
    error_type: Type[Exception] = RuntimeError,
    label: str = "source replacement",
    composed_prefixes: tuple[str, ...] = (
        "liblc3_service_audio_", "freetype_cff_host_scatter_",
    ),
) -> dict[str, int]:
    """Prove a guarded redirect plus exact post-link host composition.

    Later source-owned packing stages may reuse the generated-NOP bytes after
    an earlier overlay's four-byte entry redirect.  The manifest therefore
    legitimately splits one stock function across multiple owners.  This
    check preserves the important invariants: complete non-overlapping
    coverage, the original redirect at the entry, and only authenticated
    source-data owners in the remaining interval.
    """
    try:
        tiles = sorted(
            (item for item in regions
             if isinstance(item.get("target_address"), int)
             and isinstance(item.get("size"), int)
             and item["target_address"] < end_exclusive
             and item["target_address"] + item["size"] > start),
            key=lambda item: item["target_address"],
        )
        cursor = start
        totals = {"entry": 0, "composed": 0}
        for item in tiles:
            address = max(start, item["target_address"])
            end = min(end_exclusive, item["target_address"] + item["size"])
            if address != cursor or end <= address:
                raise error_type(f"{label} is gapped or overlapping")
            name = str(item.get("name", ""))
            status = item.get("address_status")
            if name.startswith(own_prefix):
                if status != "generated_source_entry_replacement":
                    raise error_type(f"{label} entry ownership class changed")
                totals["entry"] += end - address
            elif any(name.startswith(prefix) for prefix in composed_prefixes):
                if status != "generated_source_data_replacement":
                    raise error_type(f"{label} composed ownership class changed")
                totals["composed"] += end - address
            else:
                raise error_type(f"{label} has an unsupported post-link owner")
            cursor = end
        if cursor != end_exclusive or not tiles:
            raise error_type(f"{label} does not cover its complete interval")
        first = tiles[0]
        if (
            first.get("target_address") != start
            or first.get("size", 0) < 4
            or not str(first.get("name", "")).startswith(own_prefix)
            or first.get("address_status")
            != "generated_source_entry_replacement"
        ):
            raise error_type(f"{label} entry redirect changed")
        return totals
    except error_type:
        raise
    except Exception as exc:
        raise error_type(f"{label} structure invalid: {exc}") from exc
