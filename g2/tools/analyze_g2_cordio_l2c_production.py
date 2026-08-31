#!/usr/bin/env python3
"""Shared production-admission checks for the G2 Cordio L2CAP units."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PACKAGE = ROOT / "build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
FLASH_PLAN = ROOT / "build/source/flash-plan.json"
HEADER = ROOT / "components/shared/cordio/runtime_cordio_l2c.h"

OVERLAY_SIZE = 360_632
OVERLAY_SHA256 = "8c80c3fa53a89c77d145533f59f63389dfa31f968642f783323ed81ac81be5ae"
COMPONENT_SIZE = 3_885_668
COMPONENT_SHA256 = "898d5efb1430dc0c3e0b8b7e26823a653952114ffeab0d3ae6e89d8925301ef5"
PACKAGE_SIZE = 4_678_740
PACKAGE_SHA256 = "d569793138c6bc2ee456536daee59dcef0bb6051034ed966f7144083790a777a"
FLASH_PLAN_SIZE = 4_595_610
FLASH_PLAN_SHA256 = "b217e924841c0fda423dfc7727d76d31499f8057aade7339e4bc3b338104c127"
HEADER_SHA256 = "3d070ea0bf7e79449425af83dbd14416a1ed606b8cb8044116be23523f21c3f3"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate(
    *, source: Path, source_sha256: str, functions: list[str],
    metrics: list[tuple[int, int, int]], patch_prefix: str,
    region_prefix: str, stock_functions: dict[str, tuple[int, int, str]],
    stock_bytes: int, source_functions: int, source_only: list[str],
    region_count: int, copy_indexes: set[int] | None = None,
    hardening: dict[str, object] | None = None,
) -> dict:
    copy_indexes = copy_indexes or set()
    if sha(source.read_bytes()) != source_sha256:
        raise RuntimeError(f"L2CAP production source changed: {source.name}")
    if sha(HEADER.read_bytes()) != HEADER_SHA256:
        raise RuntimeError("L2CAP production header changed")
    report = json.loads(REPORT.read_text())
    config = json.loads(CONFIG.read_text())
    manifest = json.loads(MANIFEST.read_text())
    leaves = [
        row for row in report["relocated_leaves"]
        if row.get("source", {}).get("path", "").endswith(source.name)
    ]
    leaves.sort(key=lambda row: row["pins"]["offset"])
    if len(leaves) != len(functions):
        raise RuntimeError(f"L2CAP production leaf count changed: {source.name}")
    for row, function, expected in zip(leaves, functions, metrics):
        observed = (
            row["pins"]["offset"], row["extraction"]["size"],
            row["extraction"]["relocation_count"],
        )
        if row["extraction"]["function"] != function or observed != expected:
            raise RuntimeError(f"L2CAP production leaf changed: {function}")
    sites = {
        row["name"]: row for row in config["patch_sites"]
        if row["name"].startswith(patch_prefix)
    }
    if len(sites) != len(functions):
        raise RuntimeError(f"L2CAP production route count changed: {source.name}")
    for index, (function, (start, end, expected_sha)) in enumerate(
        zip(functions, stock_functions.values()), 1
    ):
        site = sites.get(f"{patch_prefix}{index:02d}")
        if (
            site is None
            or site["target_function"] != function
            or site["runtime_address"] != start
            or site["expected_size"] != end - start
            or site["expected_sha256"] != expected_sha
            or site["branch"] != ("copy" if index in copy_indexes else "b_w")
        ):
            raise RuntimeError(f"L2CAP production route changed: {function}")
    compiled = sum(row[1] for row in metrics)
    alignment = leaves[0]["placement"]["padding_before"] + sum(
        row["placement"]["padding_before"] for row in leaves[1:]
    )
    relocations = sum(row[2] for row in metrics)
    build_overlay = report["overlay"]
    build_component = report["component"]
    override = manifest["component_overrides"]["apollo_main"]
    if (
        build_overlay["size"] != OVERLAY_SIZE
        or build_overlay["sha256"] != OVERLAY_SHA256
        or build_component["size"] != COMPONENT_SIZE
        or build_component["sha256"] != COMPONENT_SHA256
        or override["provider"].get("size") != COMPONENT_SIZE
        or override["provider"].get("sha256") != COMPONENT_SHA256
        or len([row for row in override["regions"]
                if row["name"].startswith(region_prefix)]) != region_count
    ):
        raise RuntimeError("L2CAP component/manifest ownership changed")
    if PACKAGE.stat().st_size != PACKAGE_SIZE or sha(PACKAGE.read_bytes()) != PACKAGE_SHA256:
        raise RuntimeError("L2CAP deterministic package changed")
    flash = json.loads(FLASH_PLAN.read_text())
    if (
        FLASH_PLAN.stat().st_size != FLASH_PLAN_SIZE
        or sha(FLASH_PLAN.read_bytes()) != FLASH_PLAN_SHA256
        or (len(flash["flash_regions"]), len(flash["unresolved_flash_regions"]),
            len(flash["container_only_regions"]), len(flash["protected_regions"]))
            != (6588, 0, 6, 6)
    ):
        raise RuntimeError("L2CAP flash plan changed")
    result = {
        "status": "routed",
        "linked_functions": len(functions),
        "source_functions": source_functions,
        "source_only_functions": source_only,
        "stock_bytes_replaced": stock_bytes,
        "source_owned_bytes_added": compiled,
        "compiled_text_bytes": compiled,
        "alignment_bytes": alignment,
        "strict_relocations": relocations,
        "guarded_redirects": len(functions) - len(copy_indexes),
        "exact_in_place_copies": len(copy_indexes),
        "hardware_validation": (
            "blocked by unavailable physical evidence; future qualification requires authorized responsive G2/EM9305 "
            "and ATT peer evidence"
        ),
    }
    result.update(hardening or {})
    return result
