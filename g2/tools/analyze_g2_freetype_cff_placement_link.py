#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

"""Audit the deterministic CFF link, capacity, and routing boundary.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import struct
import sys
from pathlib import Path
from typing import Any


G2 = Path(__file__).resolve().parents[1]
BUILDER = G2 / "components/shared/freetype_cff/build_placement_census.py"
BASE_MAP = G2 / "tools/manifests/g2-freetype-base-function-map.json"
ROUTE_ANALYZER = G2 / "tools/analyze_g2_freetype_cff_production_route.py"
ROUTE_MANIFEST = G2 / "tools/manifests/g2-freetype-cff-production-route.json"
CORE_CONFIG = G2 / "components/apollo_main/freetype_cff_scatter/overlay.json"
CORE_ARTIFACT = (
    G2 / "components/apollo_main/core_overlay/build/ota_s200_firmware_ota.bin"
)
ARCHIVED_CORE_ARTIFACT = (
    G2 / "build/canonical-lc3-final-apple-f/pt-component.bin"
)
OPEN_CFW = G2 / "tools/open_cfw.py"
FLASH_PLAN = G2 / "build/flash-plan.json"
FLASH_PACKAGE = (
    G2 / "build/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
)
MANIFEST = G2 / "tools/manifests/g2-freetype-cff-placement-link.json"

BASE_MAP_PIN = "487186bdfb32dfb7140dc7f18151708690b78cb666afd64a1e2a59f4f3a7dbc4"
ROUTE_ANALYZER_PIN = "1297834732108956ce0ca33e5289cf878715073b195882a87cab75c05c8828b6"
ROUTE_MANIFEST_PIN = "af95005c4343ee04cc0396c967802da7300ef8596f6bd9e263f89df045fe9e1f"
OPEN_CFW_PIN = "acdaaaae4260ba58bf27b4a901c7fb455b16296b45eff9488b3d9a495c8165d3"
FLASH_PLAN_PIN = (
    4_490_259,
    "963c0cc5459a9d2ddbf522ab0b47cb03683f850334c910c9c68c92070d0a3c01",
)
FLASH_PACKAGE_PIN = (
    4_739_498,
    "115c5ad73e32e308287034d1b1120f8ed576ec3c3c9294cafce1bfc561b727f9",
)
CORE_RECEIPT = {
    "run_base": 0x00438000,
    "preamble_bytes": 32,
    "component_size": 3_885_668,
    "component_sha256": "898d5efb1430dc0c3e0b8b7e26823a653952114ffeab0d3ae6e89d8925301ef5",
    "runtime_end_exclusive": 0x007ECA44,
}
CURRENT_CONFIG_BASE_RECEIPT = {
    "component_size": 3_956_672,
    "component_sha256": "a87158c7cae52a5a5a01e9f5cffa2f4a346ecaf6f48da134e67a7adea1acbd37",
    "runtime_end_exclusive": 0x007FDFA0,
}
PROTECTED_UPDATE_START = 0x007FE000
MODULE_TABLE = 0x0073EEF8
MODULE_SLOT = MODULE_TABLE + 2 * 4
STOCK_CFF_CLASS = 0x006DCB74

UNRESOLVED_BINDINGS = (
    "FT_Property_Get", "FT_Property_Set", "FT_Stream_Pos",
    "memcmp", "memcpy", "memset", "strcmp", "strlen", "strncmp", "strstr",
)


class PlacementError(RuntimeError):
    """Raised when CFF build, capacity, or route evidence drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PlacementError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None,
            f"cannot load dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _base_bindings(imports: set[str]) -> dict[str, str]:
    require(sha256(BASE_MAP) == BASE_MAP_PIN, "complete base-map pin drift")
    base = json.loads(BASE_MAP.read_text(encoding="utf-8"))
    rows = {row["symbol"]: row["start"] for row in base["functions"]}
    expected = imports - set(UNRESOLVED_BINDINGS)
    require(expected <= set(rows), "admitted CFF import disappeared from base map")
    bindings = {name: rows[name] for name in sorted(expected)}
    require(len(bindings) == 35, "authenticated import binding count drift")
    return bindings


def _capacity(
    profiles: dict[str, Any], *, core_config_path: Path,
    core_artifact_path: Path | None,
) -> dict[str, Any]:
    config = json.loads(core_config_path.read_text(encoding="utf-8"))
    expected = config["profiles"]["apple-clang"]["base_component"]
    require(expected["size"] == CURRENT_CONFIG_BASE_RECEIPT["component_size"] and
            expected["sha256"] == CURRENT_CONFIG_BASE_RECEIPT["component_sha256"] and
            expected["runtime_end_exclusive"] ==
            CURRENT_CONFIG_BASE_RECEIPT["runtime_end_exclusive"],
            "live scatter base-component receipt drift")
    component = _pre_cff_component(config, core_artifact_path)
    require(len(component) == CORE_RECEIPT["component_size"] and
            hashlib.sha256(component).hexdigest() ==
            CORE_RECEIPT["component_sha256"],
            "canonical pre-CFF Apollo component artifact unavailable or changed")
    end = (CORE_RECEIPT["run_base"] + CORE_RECEIPT["component_size"] -
           CORE_RECEIPT["preamble_bytes"])
    require(end == CORE_RECEIPT["runtime_end_exclusive"],
            "Apollo append-start arithmetic drift")
    require(sha256(OPEN_CFW) == OPEN_CFW_PIN and re.search(
        r"^MAIN_UPDATE_FLAG\s*=\s*0x007FE000\s*$",
        OPEN_CFW.read_text(encoding="utf-8"), re.MULTILINE
    ) is not None, "protected update-record boundary drift")
    headroom = PROTECTED_UPDATE_START - end
    require(headroom > 0, "canonical Apollo append interval disappeared")
    fits: dict[str, Any] = {}
    for name, profile in sorted(profiles.items()):
        span = profile["objects"]["final_binary"]["size"]
        final = profile["finalized"]
        require(final["interval_start"] == end and
                final["interval_end_exclusive"] == PROTECTED_UPDATE_START and
                final["payload_end_exclusive"] == end + span,
                f"{name}: final payload placement arithmetic drift")
        fits[name] = {
            "final_payload_bytes": span,
            "payload_end_exclusive": final["payload_end_exclusive"],
            "fits": span <= headroom,
            "remaining_bytes": headroom - span,
            "static_ram_bytes": profile["static_ram_bytes"],
            "static_ram_interval_required": profile["static_ram_bytes"] != 0,
        }
        require(span <= headroom, f"{name}: CFF flash capacity shortfall")
        require(profile["static_ram_bytes"] == 0,
                f"{name}: authenticated writable placement is required")
    return {
        "authenticated_current_flash_interval": {
            "start": end,
            "end_exclusive": PROTECTED_UPDATE_START,
            "bytes": headroom,
            "authority": (
                "canonical core artifact end plus package-protected update record"
            ),
        },
        "profiles": fits,
        "static_ram": {
            "bytes": 0,
            "placement_required": False,
            "dynamic_heap_stack_qualified": False,
        },
    }


def _pre_cff_component(
    config: dict[str, Any], artifact_path: Path | None,
) -> bytes:
    if artifact_path is not None:
        return artifact_path.read_bytes()
    # This census preserves the historical contiguous-placement experiment.
    # Bind its exact admitted core artifact directly; the live scatter base
    # package advances as later production routes compose.
    return ARCHIVED_CORE_ARTIFACT.read_bytes()


def _flash_plan(profiles: dict[str, Any]) -> dict[str, Any]:
    require((FLASH_PLAN.stat().st_size, sha256(FLASH_PLAN)) == FLASH_PLAN_PIN,
            "generated flash-plan receipt drift")
    require((FLASH_PACKAGE.stat().st_size, sha256(FLASH_PACKAGE)) ==
            FLASH_PACKAGE_PIN,
            "generated flash-plan package receipt drift")
    plan = json.loads(FLASH_PLAN.read_text(encoding="utf-8"))
    require(plan["package_sha256"] == FLASH_PACKAGE_PIN[1],
            "flash-plan/package digest relation drift")
    update = [
        row for row in plan["protected_regions"]
        if row["target"] == "apollo510b_internal_mram" and
        row["name"] == "update_flag"
    ]
    require(update == [{
        "end_exclusive": 0x007FE010,
        "end_exclusive_hex": "0x007FE010",
        "name": "update_flag",
        "policy": "bootloader_owned_do_not_include_in_application_image",
        "start": PROTECTED_UPDATE_START,
        "start_hex": "0x007FE000",
        "target": "apollo510b_internal_mram",
    }], "flash-plan protected update record drift")
    apollo = [
        row for row in plan["flash_regions"]
        if row.get("component") == "apollo_main"
    ]
    require(len(apollo) == 6_120, "flash-plan Apollo region census drift")
    maximum_end = max(row["end_exclusive"] for row in apollo)
    overlap = [
        row for row in apollo
        if row["target_address"] < PROTECTED_UPDATE_START and
        row["end_exclusive"] > CORE_RECEIPT["runtime_end_exclusive"]
    ]
    require(len(overlap) == 477 and maximum_end == 0x007FCEBA,
            "flash-plan CFF-interval overlap census drift")
    available_after_plan = PROTECTED_UPDATE_START - maximum_end
    profiles_report = {}
    for name, profile in sorted(profiles.items()):
        required = profile["objects"]["final_binary"]["size"]
        profiles_report[name] = {
            "required_payload_bytes": required,
            "available_after_planned_apollo_end": available_after_plan,
            "shortfall": required - available_after_plan,
            "nonoverlapping_fit": required <= available_after_plan,
        }
        require(required > available_after_plan,
                f"{name}: flash-plan conflict unexpectedly closed")
    return {
        "self_consistent_package_receipt": True,
        "plan_apollo_regions": len(apollo),
        "candidate_interval_overlap_regions": len(overlap),
        "planned_apollo_end_exclusive": maximum_end,
        "candidate_interval_occupied_bytes": (
            maximum_end - CORE_RECEIPT["runtime_end_exclusive"]
        ),
        "bytes_before_update_record": available_after_plan,
        "canonical_core_artifact_bytes": CORE_RECEIPT["component_size"],
        "planned_apollo_component_bytes": max(
            row["component_file_offset"] + row["size"] for row in apollo
        ),
        "plan_matches_canonical_core_artifact": False,
        "profiles": profiles_report,
        "placement_authority": False,
        "blocker": (
            "the self-consistent generated plan describes a different, larger "
            "Apollo component and occupies the proposed append interval; a current "
            "canonical flash plan must be regenerated before placement"
        ),
    }


def analyze(
    *, core_config_path: Path = CORE_CONFIG,
    core_artifact_path: Path | None = None,
) -> dict[str, Any]:
    builder = load_module(BUILDER, "g2_cff_placement_builder")
    link = builder.report()
    profiles = link["profiles"]
    require(set(profiles) == {"apple-clang", "linux-clang"},
            "dual-profile CFF build set drift")
    imports = {tuple(profile["imports"]) for profile in profiles.values()}
    require(len(imports) == 1, "dual-profile CFF import surface diverged")
    import_set = set(next(iter(imports)))
    require(len(import_set) == 45, "CFF import count drift")
    bindings = _base_bindings(import_set)
    require({
        name: f"0x{address:08X}"
        for name, address in sorted(builder.RETAINED_BINDINGS.items())
    } == bindings, "component finalizer retained-binding table drift")
    source_owned = sorted(import_set - set(bindings))
    require(source_owned == sorted(UNRESOLVED_BINDINGS),
            "source-owned CFF production-binding surface drift")
    for name, profile in profiles.items():
        closure = profile["provider_closure"]
        final = profile["finalized"]
        require(closure["source_owned_symbols"] == list(UNRESOLVED_BINDINGS) and
                closure["source_owned_original_relocations"] == 43 and
                closure["retained_original_relocations"] == 212 and
                profile["relocations"]["external"] == 255 and
                not final["undefined_symbols"] and
                final["relocations"]["total"] == 0,
                f"{name}: complete import/relocation closure drift")

    require(sha256(ROUTE_ANALYZER) == ROUTE_ANALYZER_PIN and
            sha256(ROUTE_MANIFEST) == ROUTE_MANIFEST_PIN,
            "CFF route-census dependency pin drift")
    route = load_module(
        ROUTE_ANALYZER, "g2_cff_placement_route"
    ).analyze()
    require(route["route_state"]["stock_cff_module_registered"] is True and
            route["route_state"]["source_owned_lvgl_font_manager_consumer_routed"] is True and
            route["route_state"]["source_built_cff_driver_class_registered"] is True and
            route["route_state"]["canonical_package_manifest_route_enabled"] is True,
            "CFF registration/consumer boundary drift")
    capacity = _capacity(
        profiles, core_config_path=core_config_path,
        core_artifact_path=core_artifact_path,
    )
    flash_plan = _flash_plan(profiles)

    artifact = _pre_cff_component(
        json.loads(core_config_path.read_text(encoding="utf-8")),
        core_artifact_path,
    )
    slot_offset = (MODULE_SLOT - CORE_RECEIPT["run_base"] +
                   CORE_RECEIPT["preamble_bytes"])
    stock_pointer_bytes = artifact[slot_offset:slot_offset + 4]
    require(len(stock_pointer_bytes) == 4 and
            int.from_bytes(stock_pointer_bytes, "little") == STOCK_CFF_CLASS and
            stock_pointer_bytes.hex() == "74cb6d00",
            "stock CFF module-class pointer guard drift")
    replacements = {}
    for name, profile in sorted(profiles.items()):
        address = profile["finalized"]["export_addresses"]["cff_driver_class"]
        replacement = address.to_bytes(4, "little")
        replacements[name] = {
            "cff_driver_class_address": f"0x{address:08X}",
            "replacement_little_endian_hex": replacement.hex(),
            "replacement_sha256": hashlib.sha256(replacement).hexdigest(),
            "inside_final_payload": (
                profile["finalized"]["interval_start"] <= address <
                profile["finalized"]["payload_end_exclusive"]
            ),
        }
        require(replacements[name]["inside_final_payload"],
                f"{name}: module-class patch target escapes final payload")

    registration = {
        "stock_default_module_table": f"0x{MODULE_TABLE:08X}",
        "cff_slot_address": f"0x{MODULE_SLOT:08X}",
        "stock_cff_driver_class": f"0x{STOCK_CFF_CLASS:08X}",
        "required_replacement_symbol": "cff_driver_class",
        "required_pointer_patch_count": 1,
        "expected_stock_little_endian_hex": stock_pointer_bytes.hex(),
        "expected_stock_sha256": hashlib.sha256(stock_pointer_bytes).hexdigest(),
        "profile_replacements": replacements,
        "guard_policy": (
            "apply exactly one four-byte little-endian replacement only when the "
            "canonical component hash and stock pointer guard both match"
        ),
        "retained_lvgl_consumer_patch_count": 0,
        "consumer_contract": (
            "retain the authenticated LVGL FreeType create/delete path; replace only "
            "the default-module CFF class after all relocations and imports are bound"
        ),
    }
    blockers = [
        {
            "gate": "current canonical flash-plan ownership",
            "status": "blocked-self-consistent-plan-overlaps-candidate",
            "evidence": flash_plan["blocker"],
        },
        {
            "gate": "module-table patch application ownership",
            "status": "blocked-contract-authenticated-but-not-applied",
            "evidence": (
                "the finalizer emits a fully relocated payload and exact guarded patch "
                "bytes, but no canonical image writer owns this conflicting interval"
            ),
        },
        {
            "gate": "dynamic memory, stack, WCET, font payload, and hardware",
            "status": "blocked-unavailable-runtime-and-physical-evidence",
            "evidence": (
                "static data/BSS is zero, but font-dependent allocator use and live "
                "rendering evidence are unavailable"
            ),
        },
    ]
    result: dict[str, Any] = {
        "schema_version": 1,
        "status": "g2-freetype-cff-final-link-closed-routing-blocked-flash-plan",
        "analysis_mode": "software-only final link and read-only ownership census",
        "deterministic_link": link,
        "capacity": capacity,
        "flash_plan": flash_plan,
        "imports": {
            "total": len(import_set),
            "authenticated_retained_bindings": bindings,
            "authenticated_retained_count": len(bindings),
            "source_owned_bindings": source_owned,
            "source_owned_count": len(source_owned),
            "unresolved": [],
            "unresolved_count": 0,
        },
        "minimal_registration_consumer_contract": registration,
        "routing": {
            "flash_capacity_feasible": True,
            "static_ram_capacity_feasible": True,
            "all_imports_bound": True,
            "all_255_external_relocations_owned": True,
            "final_link_zero_relocations_and_undefined_symbols": True,
            "relocation_replay_implemented": True,
            "module_table_patch_contract_authenticated": True,
            "module_table_patch_implemented": False,
            "flash_plan_invariant_satisfied": False,
            "production_route_feasible_now": False,
            "firmware_image_emitted": False,
        },
        "blockers": blockers,
        "evidence_bounds": {
            "compiler_byte_identity_claimed": False,
            "production_placement_claimed": False,
            "production_routing_claimed": False,
            "dynamic_heap_stack_or_wcet_qualified": False,
            "font_payload_authenticated": False,
            "hardware_validation_performed": False,
        },
    }
    result["census_sha256"] = canonical({
        "profiles": profiles,
        "capacity": capacity,
        "flash_plan": flash_plan,
        "imports": result["imports"],
        "registration": registration,
        "blockers": blockers,
    })
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--write-manifest", action="store_true")
    parser.add_argument("--check-manifest", action="store_true")
    args = parser.parse_args()
    try:
        report = analyze()
        rendered = json.dumps(report, sort_keys=True, indent=2) + "\n"
        if args.write_manifest:
            MANIFEST.write_text(rendered, encoding="utf-8")
        if args.check_manifest:
            require(MANIFEST.is_file() and
                    json.loads(MANIFEST.read_text(encoding="utf-8")) == report,
                    "checked-in CFF placement/link manifest drift")
    except (PlacementError, OSError, KeyError, ValueError) as error:
        print(f"G2 FreeType CFF placement/link census failed: {error}", file=sys.stderr)
        return 1
    print(rendered if args.pretty else json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
