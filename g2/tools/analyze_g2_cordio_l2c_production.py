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

OVERLAY_SIZE = 404_796
OVERLAY_SHA256 = "a55b20ca90792f195ef8de456a6cb7d90c831575b9aff147676a716844bfc73d"
COMPONENT_SIZE = 3_928_192
COMPONENT_SHA256 = "5979e515c76aa1601701a01e9c0aa1050a7cc0708d0b7470b94c3d6aac0c9a73"
PACKAGE_SIZE = 4_706_686
PACKAGE_SHA256 = "30afcda8c32cc34fb1a1c12df13aff2f97223e12d74425690e67a6e4d81bfddf"
FLASH_PLAN_SIZE = 4_071_097
FLASH_PLAN_SHA256 = "cf46c2b6e6ed099ce9ef240520be8d81847ae219d52479286a373c326d22da6d"
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
            != (5863, 2, 5, 6)
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
            "blocked by unavailable authorized responsive G2/EM9305 "
            "and ATT peer evidence"
        ),
    }
    result.update(hardening or {})
    return result
