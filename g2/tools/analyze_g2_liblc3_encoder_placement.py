#!/usr/bin/env python3
"""Audit the fail-closed Apollo liblc3 encoder placement/routing proposal.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


G2 = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(G2 / "tools"))

from apollo_overlay import BuildError, decode_thumb_bl, encode_thumb_bl  # noqa: E402


PROPOSAL = (
    G2 / "components/apollo_main/liblc3_encoder/placement_routing_proposal.json"
)
CORE_CONFIG = G2 / "components/apollo_main/core_overlay/overlay.json"
CORE_ARTIFACT = (
    G2 / "components/apollo_main/core_overlay/build/ota_s200_firmware_ota.bin"
)
FLASH_PLAN = G2 / "build/flash-plan.json"
OPEN_CFW_TOOL = G2 / "tools/open_cfw.py"
ADMISSION = G2 / "components/shared/liblc3/encoder_source_admission.json"
PROVIDER_HEADER = G2 / "components/shared/liblc3/runtime_liblc3_encoder_provider.h"


class PlacementError(RuntimeError):
    """Raised when placement evidence or blocked-state arithmetic drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PlacementError(message)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise PlacementError(f"cannot read {path}: {error}") from error
    require(isinstance(value, dict), f"{path}: expected JSON object")
    return value


def resolve(relative: str) -> Path:
    path = (G2 / relative).resolve()
    try:
        path.relative_to(G2.resolve())
    except ValueError as error:
        raise PlacementError(f"path escapes G2 root: {relative}") from error
    return path


def align_up(value: int, alignment: int) -> int:
    require(alignment > 0 and alignment & (alignment - 1) == 0,
            "section alignment is not a positive power of two")
    return (value + alignment - 1) & -alignment


def image_slice(image: bytes, run_base: int, preamble: int,
                start: int, end: int) -> bytes:
    begin = start - run_base + preamble
    finish = end - run_base + preamble
    require(0 <= begin <= finish <= len(image),
            f"runtime interval 0x{start:08X}..0x{end:08X} escapes image")
    return image[begin:finish]


def _component_receipt(proposal: dict[str, Any]) -> dict[str, Any]:
    evidence = proposal["evidence"]["encoder_component"]
    path = resolve(evidence["path"])
    require(path.is_file() and sha256(path) == evidence["sha256"],
            "encoder component receipt hash drift")
    component = read_json(path)
    require(component["mode"] == evidence["mode"] and
            component["placement"] is None and
            component["stock_patch_sites"] == [] and
            not component["service_audio_routed"],
            "build-only encoder gained placement or routing")
    active = component["profiles"][evidence["profile"]]["expected"]
    require(active["linked_object"] == evidence["linked_object"],
            "encoder linked-object receipt drift")
    for name, record in evidence["sections"].items():
        observed = active["artifacts"][name]
        require(observed["size"] == record["size"] and
                observed["sha256"] == record["sha256"],
                f"encoder {name} receipt drift")
    relocations = active["relocations"]
    external = sum(relocations["external_by_symbol"].values())
    require(relocations["total"] == evidence["relocations"]["total"] and
            external == evidence["relocations"]["external"] and
            relocations["total"] - external ==
            evidence["relocations"]["internal"] and
            relocations["records_sha256"] ==
            evidence["relocations"]["records_sha256"],
            "encoder relocation accounting drift")
    require(active["retained_imports"] == evidence["retained_imports"] and
            set(active["retained_imports"]) ==
            set(relocations["external_by_symbol"]),
            "encoder runtime-import closure drift")
    return component


def _core_receipt(proposal: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    evidence = proposal["evidence"]["core_overlay"]
    core = read_json(resolve(evidence["path"]))
    require(core["run_base"] == evidence["run_base"] and
            core["preamble_bytes"] == evidence["preamble_bytes"],
            "core address model drift")
    current = evidence["current_component"]
    require(core["expected"]["component_size"] == current["size"] and
            core["expected"]["component_sha256"] == current["sha256"] and
            core["expected"]["overlay_size"] ==
            evidence["current_overlay"]["size"] and
            core["expected"]["overlay_sha256"] ==
            evidence["current_overlay"]["sha256"],
            "current Apple core receipt drift")
    computed_end = core["run_base"] + current["size"] - core["preamble_bytes"]
    require(computed_end == current["runtime_end_exclusive"],
            "current core runtime end arithmetic drift")
    update = evidence["protected_update_record"]
    require(update == {"start": 0x007FE000, "end_exclusive": 0x007FE010},
            "protected update-record boundary drift")
    require(re.search(r"^MAIN_UPDATE_FLAG\s*=\s*0x007FE000\s*$",
                      OPEN_CFW_TOOL.read_text(encoding="utf-8"), re.MULTILINE)
            is not None, "package validator update boundary drift")
    headroom = evidence["append_headroom"]
    require(headroom == {
        "start": computed_end,
        "end_exclusive": update["start"],
        "bytes": update["start"] - computed_end,
    }, "core append-headroom receipt drift")

    providers = core["post_link_providers"]
    pt = providers["pt_protocol"]["placement"]
    pt_profile = providers["pt_protocol"]["profiles"][
        evidence["current_profile"]]
    pt_expected = evidence["pt_protocol_reserved"]
    require(pt_expected == {
        "start": pt["runtime_start"],
        "end_exclusive": pt["runtime_end_exclusive"],
        "capacity": pt["capacity"],
        "loadable_bytes": pt_profile["payload_size"],
        "reserved_padding_bytes": pt["capacity"] - pt_profile["payload_size"],
    } and pt["capacity"] == (pt_profile["payload_size"] +
                             pt_expected["reserved_padding_bytes"]),
            "PT reserved-placement receipt drift")

    ltpf = evidence["liblc3_ltpf"]
    ltpf_live = providers["liblc3_ltpf"]
    ltpf_profile = ltpf_live["profiles"][evidence["current_profile"]]
    require(ltpf_live["config"] == ltpf["config"] and
            ltpf_profile["overlay"] == {
                "size": ltpf["payload_size"],
                "sha256": ltpf["payload_sha256"],
            }, "canonical LTPF payload receipt drift")
    for name in ("text", "rodata"):
        expected = ltpf["sections"][name]
        placed = ltpf_profile["placement"][name]
        require(placed["runtime_address"] == expected["start"] and
                placed["capacity"] == expected["capacity"] and
                expected["capacity"] - expected["used"] ==
                expected["unused_but_reserved"],
                f"canonical LTPF {name} placement drift")

    artifact_report: dict[str, Any] = {"present": CORE_ARTIFACT.is_file()}
    if CORE_ARTIFACT.is_file():
        raw = CORE_ARTIFACT.read_bytes()
        require(len(raw) == current["size"] and
                sha256_bytes(raw) == current["sha256"],
                "current core artifact differs from canonical receipt")
        patch = ltpf["patch_site"]
        encoded = image_slice(raw, core["run_base"], core["preamble_bytes"],
                              patch, patch + 4)
        try:
            target = decode_thumb_bl(patch, encoded)
        except BuildError as error:
            raise PlacementError("current LTPF patch is not a Thumb BL") from error
        require(target == ltpf["patched_target"],
                "current LTPF route target drift")
        artifact_report.update({
            "size": len(raw),
            "sha256": sha256_bytes(raw),
            "ltpf_patch_hex": encoded.hex(),
            "ltpf_patch_target": target,
        })
    return core, artifact_report


def _stock_calls(proposal: dict[str, Any]) -> dict[str, Any]:
    official = proposal["evidence"]["official_component"]
    path = resolve(official["path"])
    raw = path.read_bytes()
    require(len(raw) == official["size"] and
            sha256_bytes(raw) == official["sha256"],
            "official Apollo-main component drift")
    require(official["runtime_end_exclusive"] ==
            official["run_base"] + len(raw) - official["preamble_bytes"],
            "official component runtime end drift")
    service = proposal["evidence"]["service_audio"]
    body = image_slice(raw, official["run_base"], official["preamble_bytes"],
                       service["object_start"], service["object_end_exclusive"])
    require(len(body) == service["object_size"] and
            sha256_bytes(body) == service["object_sha256"],
            "service_audio object receipt drift")
    observed: list[dict[str, Any]] = []
    for site in service["call_sites"]:
        encoded = image_slice(raw, official["run_base"],
                              official["preamble_bytes"],
                              site["address"], site["address"] + 4)
        require(encoded.hex() == site["expected_hex"] and
                sha256_bytes(encoded) == site["expected_sha256"],
                f"service_audio callsite drift at 0x{site['address']:08X}")
        try:
            target = decode_thumb_bl(site["address"], encoded)
        except BuildError as error:
            raise PlacementError(
                f"service_audio callsite 0x{site['address']:08X} is not BL"
            ) from error
        require(target == site["stock_target"],
                f"service_audio target drift at 0x{site['address']:08X}")
        observed.append({
            "address": site["address"],
            "caller": site["caller"],
            "stock_symbol": site["stock_symbol"],
            "stock_target": target,
            "expected_hex": encoded.hex(),
        })

    ltpf = proposal["evidence"]["core_overlay"]["liblc3_ltpf"]
    stock_ltpf = image_slice(raw, official["run_base"],
                             official["preamble_bytes"],
                             ltpf["patch_site"], ltpf["patch_site"] + 4)
    require(stock_ltpf.hex() == "a7f6acfd" and
            decode_thumb_bl(ltpf["patch_site"], stock_ltpf) == 0x00438FB8,
            "official stock LTPF call evidence drift")
    return {
        "object_sha256": sha256_bytes(body),
        "direct_calls": observed,
        "direct_call_count": len(observed),
        "stock_ltpf_call": {
            "address": ltpf["patch_site"],
            "target": 0x00438FB8,
            "expected_hex": stock_ltpf.hex(),
        },
    }


def _layout_and_capacity(proposal: dict[str, Any],
                         component: dict[str, Any]) -> dict[str, Any]:
    evidence = proposal["evidence"]
    sections = evidence["encoder_component"]["sections"]
    headroom = evidence["core_overlay"]["append_headroom"]
    cursor = headroom["start"]
    observed: dict[str, tuple[int, int]] = {}
    for name in ("text", "rodata", "data"):
        cursor = align_up(cursor, sections[name]["alignment"])
        start = cursor
        cursor += sections[name]["size"]
        observed[name] = (start, cursor)
    candidate = proposal["candidate_layout"]
    require(candidate["text_start"] == observed["text"][0] and
            candidate["text_end_exclusive"] == observed["text"][1] and
            candidate["rodata_start"] == observed["rodata"][0] and
            candidate["rodata_end_exclusive"] == observed["rodata"][1] and
            candidate["data_start"] == observed["data"][0] and
            candidate["data_end_exclusive"] == observed["data"][1] and
            candidate["span_from_current_end"] == cursor - headroom["start"] and
            candidate["overflow_past_update_record"] ==
            cursor - headroom["end_exclusive"] and
            candidate["text_rodata_overflow_without_data"] ==
            observed["rodata"][1] - headroom["end_exclusive"],
            "candidate section layout arithmetic drift")
    require(cursor > headroom["end_exclusive"] and
            not candidate["placement_authorized"],
            "overflowing layout was incorrectly authorized")

    roots = component["profiles"][evidence["encoder_component"]["profile"]][
        "expected"]["roots"]
    displacements: list[int] = []
    for site in evidence["service_audio"]["call_sites"]:
        for root in roots.values():
            target = candidate["text_start"] + root["offset"]
            require(candidate["text_start"] <= target < candidate["text_end_exclusive"],
                    "provider root escaped candidate text")
            try:
                encoded = encode_thumb_bl(site["address"], target)
                decoded = decode_thumb_bl(site["address"], encoded)
            except BuildError as error:
                raise PlacementError("provider root escaped Thumb BL range") from error
            require(decoded == target, "hypothetical Thumb BL round trip drift")
            displacements.append(target - (site["address"] + 4))
    require(candidate["all_stock_sites_can_reach_candidate_text"] and
            candidate["branch_encoding"] == "Thumb-2 BL" and
            candidate["branch_range_bytes"] == 1 << 24,
            "branch-range proposal drift")

    proof = proposal["capacity_proof"]
    pt_slack = evidence["core_overlay"]["pt_protocol_reserved"][
        "reserved_padding_bytes"]
    ltpf_sections = evidence["core_overlay"]["liblc3_ltpf"]["sections"]
    ltpf_slack = sum(item["unused_but_reserved"]
                     for item in ltpf_sections.values())
    ltpf_total = sum(item["capacity"] for item in ltpf_sections.values())
    required = candidate["span_from_current_end"]
    require(proof == {
        "current_append_headroom": headroom["bytes"],
        "required_aligned_span": required,
        "append_only_shortfall": required - headroom["bytes"],
        "existing_provider_unused_but_reserved": {
            "pt_protocol": pt_slack,
            "liblc3_ltpf": ltpf_slack,
        },
        "optimistic_no_move_capacity_including_all_reserved_slack":
            headroom["bytes"] + pt_slack + ltpf_slack,
        "optimistic_no_move_shortfall":
            required - headroom["bytes"] - pt_slack - ltpf_slack,
        "liblc3_ltpf_total_capacity_reclaim_requires_removal": ltpf_total,
        "optimistic_capacity_including_pt_slack_and_removed_liblc3_ltpf":
            headroom["bytes"] + pt_slack + ltpf_total,
        "optimistic_shortfall_even_after_liblc3_ltpf_removal":
            required - headroom["bytes"] - pt_slack - ltpf_total,
        "unauthenticated_gap_capacity": 0,
    }, "capacity upper-bound proof drift")
    require(proof["optimistic_shortfall_even_after_liblc3_ltpf_removal"] > 0,
            "known-capacity impossibility proof no longer holds")
    return {
        "current_core_end": headroom["start"],
        "protected_update_record": headroom["end_exclusive"],
        "append_headroom": headroom["bytes"],
        "candidate_sections": {
            name: {"start": span[0], "end_exclusive": span[1],
                   "size": sections[name]["size"]}
            for name, span in observed.items()
        },
        "required_aligned_span": required,
        "append_only_shortfall": proof["append_only_shortfall"],
        "optimistic_known_capacity":
            proof["optimistic_capacity_including_pt_slack_and_removed_liblc3_ltpf"],
        "optimistic_known_capacity_shortfall":
            proof["optimistic_shortfall_even_after_liblc3_ltpf_removal"],
        "minimum_branch_displacement": min(displacements),
        "maximum_branch_displacement": max(displacements),
        "branch_range_sufficient": True,
    }


def _optional_flash_plan(core: dict[str, Any]) -> dict[str, Any]:
    if not FLASH_PLAN.is_file():
        return {"present": False, "placement_authority": False}
    plan = read_json(FLASH_PLAN)
    rows = sorted(
        (row for row in plan.get("flash_regions", [])
         if row.get("component") == "apollo_main" and
         row.get("target") == "apollo510b_internal_mram"),
        key=lambda row: row["target_address"],
    )
    require(rows and rows[0]["target_address"] == core["run_base"],
            "generated flash plan has no Apollo-main installed interval")
    require(all(left["end_exclusive"] == right["target_address"]
                for left, right in zip(rows, rows[1:])),
            "generated Apollo-main flash plan is not contiguous")
    end = rows[-1]["end_exclusive"]
    size = end - core["run_base"] + core["preamble_bytes"]
    protected = [row for row in plan.get("protected_regions", [])
                 if row.get("target") == "apollo510b_internal_mram" and
                 row.get("end_exclusive") == 0x007FE010]
    require(protected, "generated flash plan lost protected update record")
    return {
        "present": True,
        "sha256": sha256(FLASH_PLAN),
        "apollo_region_count": len(rows),
        "component_size": size,
        "runtime_end_exclusive": end,
        "headroom_to_update_record": 0x007FE000 - end,
        "consistent_with_current_core":
            size == core["expected"]["component_size"] and
            end == core["run_base"] + size - core["preamble_bytes"],
        "placement_authority": False,
    }


def run_audit() -> dict[str, Any]:
    proposal = read_json(PROPOSAL)
    require(proposal["schema_version"] == 1 and
            proposal["mode"] == "fail-closed-blocked-proposal",
            "placement proposal schema or mode drift")
    component = _component_receipt(proposal)
    core, core_artifact = _core_receipt(proposal)
    stock = _stock_calls(proposal)
    placement = _layout_and_capacity(proposal, component)
    flash_plan = _optional_flash_plan(core)

    admission = read_json(ADMISSION)
    require("src/ltpf.c" in admission["upstream_encoder_sources"] and
            admission["provider_entries"] ==
            proposal["evidence"]["service_audio"]["provider_entries"] and
            admission["build_component"]["placement_assigned"] is False and
            admission["build_component"]["service_audio_routed"] is False,
            "encoder admission placement/LTPF state drift")
    header = PROVIDER_HEADER.read_text(encoding="utf-8")
    require(all(entry in header for entry in admission["provider_entries"]),
            "bounded-provider header entry drift")
    service = proposal["evidence"]["service_audio"]
    require(service["direct_patch_mapping"] is None and
            "do not map one-for-one" in service["reason"],
            "service ABI blocker was incorrectly closed")
    require(not any("service_audio.c" in source.get("path", "").lower()
                    for source in core["sources"]),
            "service_audio source route appeared; proposal must be redone")

    relocation = proposal["relocation_contract"]
    require(relocation == {
        "final_section_addresses_assigned": False,
        "runtime_import_bindings": {},
        "all_567_relocations_must_be_applied_after_final_placement": True,
        "all_12_import_symbols_must_have_authenticated_abi_compatible_targets": True,
        "writable_data_runtime_policy_proven": False,
        "raw_section_bins_are_not_loadable": True,
    }, "relocation contract drift")
    ltpf = proposal["ltpf_reconciliation"]
    require(ltpf == {
        "full_encoder_contains_upstream_ltpf_analysis": True,
        "existing_overlay_patch_remains_inside_stock_lc3_encode": True,
        "existing_caves_must_remain_reserved_without_an_explicit_supersession_plan": True,
        "removing_existing_liblc3_ltpf_alone_cannot_close_capacity_shortfall": True,
        "supersession_authorized": False,
    }, "LTPF overlap reconciliation drift")
    outcome = proposal["outcome"]
    require(not outcome["production_routing_feasible_without_moving_other_components"] and
            outcome["software_blocked"] and
            not outcome["hardware_operations"] and
            len(outcome["blockers"]) == 6,
            "blocked routing outcome drift")
    return {
        "status": "liblc3-encoder-placement-routing-blocked",
        "official_stock": stock,
        "current_core_artifact": core_artifact,
        "generated_flash_plan": flash_plan,
        "placement": placement,
        "relocations": {
            "total": 567,
            "internal": 400,
            "external": 167,
            "retained_imports":
                proposal["evidence"]["encoder_component"]["retained_imports"],
            "runtime_import_bindings": {},
            "writable_data_policy_proven": False,
        },
        "routing": {
            "authenticated_stock_calls": stock["direct_call_count"],
            "thumb_bl_range_sufficient": True,
            "bounded_provider_direct_patch_mapping": None,
            "service_audio_source_routed": False,
            "existing_liblc3_ltpf_superseded": False,
            "production_feasible_without_moving_other_components": False,
        },
        "software_blockers": outcome["blockers"],
        "hardware_operations": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run_audit(), sort_keys=True,
                     indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
