#!/usr/bin/env python3
"""Fail-closed audit of the Apollo-main LC3 capacity-rebalancing proposal.

This tool never patches an image.  It authenticates the current Apple core
receipt, derives candidate source-owned stock slots, models a stable-order
append repack, and rejects the proposal as production-feasible while any moved
leaf lacks a strict relocation contract.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path
from typing import Any


G2 = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(G2 / "tools"))

from apollo_overlay import (  # noqa: E402
    BuildError,
    decode_thumb_branch,
    encode_thumb_branch,
)


DEFAULT_PROPOSAL = (
    G2
    / "components/apollo_main/liblc3_encoder/capacity_rebalancing_proposal.json"
)


class CapacityError(RuntimeError):
    """Raised when authenticated capacity evidence or arithmetic drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CapacityError(message)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return sha256_bytes(payload)


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise CapacityError(f"cannot read {path}: {error}") from error
    require(isinstance(value, dict), f"{path}: expected JSON object")
    return value


def resolve(relative: str) -> Path:
    path = (G2 / relative).resolve()
    try:
        path.relative_to(G2.resolve())
    except ValueError as error:
        raise CapacityError(f"path escapes G2 root: {relative}") from error
    return path


def align_up(value: int, alignment: int) -> int:
    require(
        alignment > 0 and alignment & (alignment - 1) == 0,
        f"invalid alignment {alignment}",
    )
    return (value + alignment - 1) & -alignment


def overlaps(start: int, end: int, other_start: int, other_end: int) -> bool:
    return start < other_end and other_start < end


def image_slice(
    image: bytes, run_base: int, preamble: int, start: int, end: int
) -> bytes:
    begin = start - run_base + preamble
    finish = end - run_base + preamble
    require(
        0 <= begin <= finish <= len(image),
        f"runtime interval 0x{start:08X}..0x{end:08X} escapes image",
    )
    return image[begin:finish]


def authenticate(record: dict[str, Any]) -> tuple[Path, bytes]:
    path = resolve(record["path"])
    try:
        payload = path.read_bytes()
    except OSError as error:
        raise CapacityError(f"cannot read {path}: {error}") from error
    require(len(payload) == record["size"], f"size drift: {path}")
    require(sha256_bytes(payload) == record["sha256"], f"hash drift: {path}")
    return path, payload


def _pin_core(
    proposal: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], bytes, bytes]:
    evidence = proposal["evidence"]
    config_path, _ = authenticate(evidence["core_config"])
    report_path, _ = authenticate(evidence["core_report"])
    _overlay_path, overlay = authenticate(evidence["overlay_artifact"])
    _component_path, component = authenticate(evidence["component_artifact"])
    config = read_json(config_path)
    report = read_json(report_path)

    address = proposal["address_model"]
    require(config["run_base"] == address["run_base"], "run-base drift")
    require(
        config["preamble_bytes"] == address["preamble_bytes"],
        "preamble drift",
    )
    live = report["overlay"]
    require(
        live["overlay_runtime_address"] == address["overlay_runtime_start"]
        and live["size"] == address["current_overlay_size"]
        and live["overlay_end_exclusive"]
        == address["current_core_end_exclusive"],
        "core overlay address receipt drift",
    )
    require(
        live["sha256"] == evidence["overlay_artifact"]["sha256"]
        and report["component"]["sha256"]
        == evidence["component_artifact"]["sha256"],
        "core report artifact receipt drift",
    )
    payload_offset = live["overlay_payload_offset"]
    require(
        component[payload_offset:] == overlay,
        "component append payload differs from overlay artifact",
    )
    require(
        address["run_base"]
        + len(component)
        - address["preamble_bytes"]
        == address["current_core_end_exclusive"],
        "component runtime-end arithmetic drift",
    )
    require(
        address["protected_update_start"]
        - address["current_core_end_exclusive"]
        == address["current_append_headroom"],
        "append-headroom arithmetic drift",
    )
    return config, report, overlay, component


def _pin_specialization(proposal: dict[str, Any]) -> dict[str, Any]:
    record = proposal["evidence"]["specialization"]
    path, _ = authenticate(record)
    specialization = read_json(path)
    variant = specialization["variants"][record["variant"]]
    require(variant["evidence_admitted"], "selected specialization is rejected")
    require(
        all(
            specialization["routing"].get(key) is False
            for key in (
                "placement_assigned",
                "service_audio_routed",
                "firmware_image_emitted",
                "hardware_operations",
            )
        ),
        "specialization unexpectedly gained placement or routing",
    )
    return variant["expected"]


def _protected_receipts(
    proposal: dict[str, Any], report: dict[str, Any]
) -> list[dict[str, Any]]:
    protected = proposal["protected_intervals"]
    require(
        protected[-1] == {
            "owner": "main_update_record",
            "start": 0x007FE000,
            "end_exclusive": 0x007FE010,
            "capacity": 16,
            "used": 16,
        },
        "protected update record drift",
    )
    providers = report["overlay"]["post_link_providers"]
    ltpf = providers["liblc3_ltpf"]["placement"]
    pt = providers["pt_protocol"]["placement"]
    observed = [
        {
            "owner": "liblc3_ltpf_text",
            "start": ltpf["text"]["runtime_address"],
            "end_exclusive": ltpf["text"]["runtime_address"]
            + ltpf["text"]["capacity"],
            "capacity": ltpf["text"]["capacity"],
            "used": ltpf["text"]["size"],
        },
        {
            "owner": "liblc3_ltpf_rodata",
            "start": ltpf["rodata"]["runtime_address"],
            "end_exclusive": ltpf["rodata"]["runtime_address"]
            + ltpf["rodata"]["capacity"],
            "capacity": ltpf["rodata"]["capacity"],
            "used": ltpf["rodata"]["size"],
        },
        {
            "owner": "pt_protocol",
            "start": pt["runtime_start"],
            "end_exclusive": pt["runtime_end_exclusive"],
            "capacity": pt["capacity"],
            "used": pt["loadable_size"],
        },
    ]
    require(observed == protected[:3], "PT/LTPF reservation receipt drift")
    return protected


def _patches_by_target(report: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for patch in report["overlay"]["patched_sites"]:
        target = patch.get("target_function")
        if isinstance(target, str):
            result.setdefault(target, []).append(patch)
    return result


def _derive_candidates(
    proposal: dict[str, Any],
    config: dict[str, Any],
    report: dict[str, Any],
    component: bytes,
    protected: list[dict[str, Any]],
) -> tuple[
    list[tuple[int, str, dict[str, Any], dict[str, Any]]],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
]:
    config_leaves = {item["function"]: item for item in config["relocated_leaves"]}
    leaves = {
        item["extraction"]["function"]: item for item in report["relocated_leaves"]
    }
    patches = _patches_by_target(report)
    run_base = proposal["address_model"]["run_base"]
    preamble = proposal["address_model"]["preamble_bytes"]
    reservations = protected[:-1]
    candidates: list[tuple[int, str, dict[str, Any], dict[str, Any]]] = []

    for name, leaf in leaves.items():
        config_leaf = config_leaves.get(name)
        require(config_leaf is not None, f"report leaf absent from config: {name}")
        target_patches = patches.get(name, [])
        if not config_leaf.get("strict_relocation_contract"):
            continue
        if len(target_patches) != 1:
            continue
        patch = target_patches[0]
        if patch.get("branch") != "b_w" or "expected_size" not in patch:
            continue
        placement = leaf["placement"]
        require(
            patch["target_address"] == placement["runtime_address"],
            f"patch no longer targets its reported closure: {name}",
        )
        if placement["size"] > patch["expected_size"]:
            continue
        if patch["runtime_address"] % placement["alignment"]:
            continue
        patch_end = patch["runtime_address"] + patch["expected_size"]
        if any(
            overlaps(
                patch["runtime_address"],
                patch_end,
                interval["start"],
                interval["end_exclusive"],
            )
            for interval in reservations
        ):
            continue
        final = image_slice(
            component,
            run_base,
            preamble,
            patch["runtime_address"],
            patch_end,
        )
        require(
            final.hex() == patch["replacement_hex"],
            f"generated patch bytes drift for {name}",
        )
        try:
            decoded_target = decode_thumb_branch(
                patch["runtime_address"], final[:4], link=False
            )
        except BuildError as error:
            raise CapacityError(f"stock patch is not B.W for {name}") from error
        require(
            decoded_target == placement["runtime_address"],
            f"stock patch target decode drift for {name}",
        )
        require(
            final[4:] == b"\x00\xbf" * ((len(final) - 4) // 2),
            f"full-span patch for {name} is not B.W plus generated NOPs",
        )
        candidates.append((placement["size"], name, patch, leaf))

    candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
    require(
        len(candidates) == proposal["expected"]["eligible_slot_count"],
        "eligible candidate count drift",
    )
    return candidates, config_leaves, leaves


def _repack(
    report: dict[str, Any],
    selected: set[str],
    config_leaves: dict[str, dict[str, Any]],
) -> tuple[int, dict[str, int]]:
    overlay = report["overlay"]
    base = overlay["overlay_runtime_address"]
    ordered = overlay["link"]["relocated_functions"]
    cursor = ordered[0]["offset"]
    addresses: dict[str, int] = {}
    for leaf in ordered:
        if leaf["function"] in selected:
            continue
        cursor = align_up(base + cursor, leaf["alignment"]) - base
        cursor += int(
            config_leaves[leaf["function"]].get(
                "reserved_padding_before",
                0,
            )
        )
        addresses[leaf["function"]] = base + cursor
        cursor += leaf["size"]
    return cursor, addresses


def _selection_and_layout(
    proposal: dict[str, Any],
    candidates: list[tuple[int, str, dict[str, Any], dict[str, Any]]],
    report: dict[str, Any],
    config_leaves: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    expected = proposal["expected"]
    current_size = report["overlay"]["size"]
    shortfall = proposal["address_model"]["current_shortfall"]
    derived: list[str] = []
    for _size, name, _patch, _leaf in candidates:
        derived.append(name)
        trial_size, _ = _repack(report, set(derived), config_leaves)
        if current_size - trial_size >= shortfall:
            break
    selected = proposal["selected_functions"]
    require(selected == derived, "selected prefix is not the minimal candidate prefix")
    require(len(selected) == expected["selected_count"], "selected count drift")
    require(
        canonical_sha256(selected) == expected["selected_list_sha256"],
        "selected list digest drift",
    )
    predecessor_size, _ = _repack(
        report, set(selected[:-1]), config_leaves
    )
    new_size, repacked_addresses = _repack(
        report, set(selected), config_leaves
    )
    predecessor_savings = current_size - predecessor_size
    savings = current_size - new_size
    require(
        predecessor_savings == expected["predecessor_savings"]
        and predecessor_savings < shortfall,
        "minimal-prefix predecessor proof drift",
    )
    require(
        savings == expected["conditional_repack_savings"]
        and new_size == expected["conditional_overlay_size"],
        "conditional repack arithmetic drift",
    )

    by_name = {name: (patch, leaf) for _size, name, patch, leaf in candidates}
    records: list[dict[str, Any]] = []
    for name in selected:
        patch, leaf = by_name[name]
        source = leaf["source"]
        records.append(
            {
                "function": name,
                "stock_start": patch["runtime_address"],
                "slot_size": patch["expected_size"],
                "closure_size": leaf["placement"]["size"],
                "closure_alignment": leaf["placement"]["alignment"],
                "old_append_address": leaf["placement"]["runtime_address"],
                "source_path": source["path"],
                "source_sha256": source["sha256"],
                "source_size": source["size"],
                "unrelocated_sha256": leaf["extraction"]["unrelocated_sha256"],
            }
        )
    require(
        canonical_sha256(records) == expected["selected_records_sha256"],
        "selected slot/source receipt digest drift",
    )
    closure_bytes = sum(item["closure_size"] for item in records)
    slot_bytes = sum(item["slot_size"] for item in records)
    generated_nop_bytes = slot_bytes - 4 * len(records)
    old_padding_before = sum(
        by_name[name][1]["placement"]["padding_before"] for name in selected
    )
    require(
        closure_bytes == expected["selected_closure_bytes"]
        and slot_bytes == expected["selected_slot_bytes"]
        and slot_bytes - closure_bytes == expected["selected_slot_slack"]
        and generated_nop_bytes == expected["selected_generated_nop_bytes"]
        and old_padding_before == expected["selected_old_append_padding_before"],
        "selected capacity accounting drift",
    )

    link = report["overlay"]["link"]
    ordered = link["relocated_functions"]
    relocated_region_start = report["overlay"]["overlay_runtime_address"] + ordered[0]["offset"]
    relocated_region_bytes = report["overlay"]["size"] - ordered[0]["offset"]
    require(
        link["isolated_padding_size"] == expected["current_isolated_padding"]
        and link["relocated_padding_size"]
        == expected["current_relocated_alignment_padding"]
        and link["relocated_closure_padding_size"]
        == expected["current_relocated_closure_padding"]
        and relocated_region_start == expected["source_owned_relocated_region_start"]
        and relocated_region_bytes == expected["source_owned_relocated_region_bytes"],
        "source-owned append/padding receipt drift",
    )

    sources = sorted(
        {
            (item["source_path"], item["source_sha256"], item["source_size"])
            for item in records
        }
    )
    require(len(sources) == expected["selected_source_count"], "source count drift")
    require(
        canonical_sha256(sources) == expected["selected_sources_sha256"],
        "selected source-set digest drift",
    )
    for relative, digest, size in sources:
        path = resolve(relative)
        payload = path.read_bytes()
        require(
            len(payload) == size and sha256_bytes(payload) == digest,
            f"selected source drift: {relative}",
        )

    new_addresses = dict(repacked_addresses)
    new_addresses.update({item["function"]: item["stock_start"] for item in records})
    return {
        "selected": selected,
        "selected_records": records,
        "new_size": new_size,
        "new_addresses": new_addresses,
        "predecessor_savings": predecessor_savings,
        "savings": savings,
        "closure_bytes": closure_bytes,
        "slot_bytes": slot_bytes,
        "generated_nop_bytes": generated_nop_bytes,
        "old_padding_before": old_padding_before,
        "relocated_region_start": relocated_region_start,
        "relocated_region_bytes": relocated_region_bytes,
        "source_count": len(sources),
    }


def _owner_index(
    report: dict[str, Any],
) -> tuple[list[int], list[tuple[int, int, str]]]:
    intervals = sorted(
        (
            leaf["placement"]["runtime_address"],
            leaf["placement"]["runtime_address"] + leaf["placement"]["size"],
            leaf["extraction"]["function"],
        )
        for leaf in report["relocated_leaves"]
    )
    for left, right in zip(intervals, intervals[1:]):
        require(left[1] <= right[0], "relocated leaf intervals overlap")
    return [item[0] for item in intervals], intervals


def _find_owner(
    address: int, starts: list[int], intervals: list[tuple[int, int, str]]
) -> tuple[str, int] | None:
    index = bisect.bisect_right(starts, address) - 1
    if index >= 0:
        start, end, name = intervals[index]
        if start <= address < end:
            return name, start
    return None


def _relocation_audit(
    proposal: dict[str, Any],
    config_leaves: dict[str, dict[str, Any]],
    report: dict[str, Any],
    layout: dict[str, Any],
) -> dict[str, Any]:
    expected = proposal["expected"]
    selected = set(layout["selected"])
    starts, intervals = _owner_index(report)
    new_addresses = layout["new_addresses"]
    supported = {
        "R_ARM_REL32",
        "R_ARM_THM_CALL",
        "R_ARM_THM_JUMP24",
        "R_ARM_THM_MOVW_ABS_NC",
        "R_ARM_THM_MOVT_ABS",
        "R_ARM_THM_MOVW_PREL_NC",
        "R_ARM_THM_MOVT_PREL",
    }
    incoming = 0
    incoming_fixed = 0
    selected_outgoing = 0
    movable = 0
    movable_named = 0
    changed_sites = 0
    changed_targets = 0
    maximum_branch = 0
    all_types: Counter[str] = Counter()
    movable_types: Counter[str] = Counter()
    incoming_types: Counter[str] = Counter()
    outgoing_types: Counter[str] = Counter()

    for leaf in report["relocated_leaves"]:
        name = leaf["extraction"]["function"]
        old_base = leaf["placement"]["runtime_address"]
        new_base = new_addresses[name]
        relocations = leaf["extraction"]["relocations"]
        if name in selected:
            require(
                config_leaves[name].get("strict_relocation_contract") is True,
                f"selected leaf lacks strict contract: {name}",
            )
        for relocation in relocations:
            kind = relocation["type"]
            require(kind in supported, f"unsupported relocation type {kind}")
            all_types[kind] += 1
            if name in selected:
                selected_outgoing += 1
                outgoing_types[kind] += 1
            old_site = relocation["runtime_address"]
            new_site = new_base + old_site - old_base
            old_target = relocation["target_address"]
            target_owner = _find_owner(old_target, starts, intervals)
            new_target = old_target
            if target_owner is not None:
                target_name, target_base = target_owner
                movable += 1
                movable_types[kind] += 1
                if "target_function" in relocation:
                    movable_named += 1
                new_target = new_addresses[target_name] + old_target - target_base
                if target_name in selected:
                    incoming += 1
                    incoming_types[kind] += 1
                    if "target_function" not in relocation:
                        incoming_fixed += 1
            if new_site != old_site:
                changed_sites += 1
            if new_target != old_target:
                changed_targets += 1
            delta = new_target - (new_site + 4)
            if kind in {"R_ARM_THM_CALL", "R_ARM_THM_JUMP24"}:
                try:
                    encoded = encode_thumb_branch(
                        new_site,
                        new_target,
                        link=kind == "R_ARM_THM_CALL",
                    )
                    require(
                        decode_thumb_branch(
                            new_site,
                            encoded,
                            link=kind == "R_ARM_THM_CALL",
                        )
                        == new_target,
                        "Thumb branch round-trip mismatch",
                    )
                except BuildError as error:
                    raise CapacityError(
                        f"branch reach failure in {name} at 0x{new_site:08X}"
                    ) from error
                maximum_branch = max(maximum_branch, abs(delta))
            elif kind in {
                "R_ARM_REL32",
                "R_ARM_THM_MOVW_PREL_NC",
                "R_ARM_THM_MOVT_PREL",
            }:
                require(
                    -(1 << 31) <= new_target - new_site < (1 << 31),
                    f"PC-relative 32-bit reach failure in {name}",
                )

    all_count = sum(all_types.values())
    checks = {
        "incoming_selected_relocations": incoming,
        "incoming_selected_fixed_target_records": incoming_fixed,
        "selected_outgoing_relocations": selected_outgoing,
        "movable_target_relocations": movable,
        "movable_named_target_relocations": movable_named,
        "movable_fixed_target_relocations": movable - movable_named,
        "all_relocated_leaf_relocations": all_count,
        "changed_relocation_sites_under_full_repack": changed_sites,
        "changed_relocation_targets_under_full_repack": changed_targets,
        "maximum_thumb_branch_displacement": maximum_branch,
    }
    for key, value in checks.items():
        require(value == expected[key], f"{key} drift: {value}")
    return {
        **checks,
        "all_by_type": dict(sorted(all_types.items())),
        "movable_by_type": dict(sorted(movable_types.items())),
        "incoming_selected_by_type": dict(sorted(incoming_types.items())),
        "selected_outgoing_by_type": dict(sorted(outgoing_types.items())),
    }


def _ingress_audit(
    proposal: dict[str, Any],
    report: dict[str, Any],
    component: bytes,
    layout: dict[str, Any],
) -> dict[str, Any]:
    address = proposal["address_model"]
    selected = set(layout["selected"])
    selected_old = {
        item["old_append_address"]: item["function"]
        for item in layout["selected_records"]
    }
    expected_branches: set[tuple[int, int, bool]] = set()
    for patch in report["overlay"]["patched_sites"]:
        if patch.get("target_function") in selected:
            expected_branches.add(
                (patch["runtime_address"], patch["target_address"], False)
            )
    for leaf in report["relocated_leaves"]:
        for relocation in leaf["extraction"]["relocations"]:
            if (
                relocation["type"] in {"R_ARM_THM_CALL", "R_ARM_THM_JUMP24"}
                and relocation["target_address"] in selected_old
            ):
                expected_branches.add(
                    (
                        relocation["runtime_address"],
                        relocation["target_address"],
                        relocation["type"] == "R_ARM_THM_CALL",
                    )
                )

    observed: set[tuple[int, int, bool]] = set()
    preamble = address["preamble_bytes"]
    run_base = address["run_base"]
    for offset in range(preamble, len(component) - 3, 2):
        site = run_base + offset - preamble
        encoded = component[offset : offset + 4]
        try:
            target = decode_thumb_branch(site, encoded)
        except BuildError:
            continue
        if target not in selected_old:
            continue
        _first, second = struct.unpack("<HH", encoded)
        observed.add((site, target, bool(second & 0x4000)))
    require(observed == expected_branches, "selected executable ingress drift")

    raw_pointers: list[tuple[int, int]] = []
    for offset in range(preamble, len(component) - 3):
        value = struct.unpack_from("<I", component, offset)[0]
        if (value & ~1) in selected_old:
            raw_pointers.append((run_base + offset - preamble, value))
    require(
        len(observed)
        == proposal["expected"]["artifact_selected_branch_ingress"],
        "artifact branch-ingress count drift",
    )
    require(
        len(raw_pointers)
        == proposal["expected"]["artifact_selected_raw_pointer_ingress"],
        "artifact raw-pointer ingress drift",
    )
    return {
        "branch_count": len(observed),
        "branch_link_count": sum(item[2] for item in observed),
        "branch_jump_count": sum(not item[2] for item in observed),
        "raw_pointer_count": len(raw_pointers),
        "branch_records_sha256": canonical_sha256(sorted(observed)),
    }


def _strict_blockers(
    proposal: dict[str, Any],
    config_leaves: dict[str, dict[str, Any]],
    report: dict[str, Any],
    layout: dict[str, Any],
) -> dict[str, Any]:
    expected = proposal["expected"]
    selected = set(layout["selected"])
    moved = []
    for leaf in report["overlay"]["link"]["relocated_functions"]:
        name = leaf["function"]
        if name in selected:
            continue
        if layout["new_addresses"][name] != leaf["runtime_address"]:
            moved.append(name)
    strict = [name for name in moved if config_leaves[name].get("strict_relocation_contract")]
    non_strict = [name for name in moved if name not in strict]
    require(
        len(moved) == expected["full_repack_moved_leaves"]
        and len(strict) == expected["full_repack_moved_strict_leaves"]
        and len(non_strict) == expected["full_repack_moved_non_strict_leaves"],
        "full-repack strict-contract census drift",
    )

    cutoff = report["overlay"]["size"] - proposal["address_model"]["current_shortfall"]
    report_leaves = {
        leaf["extraction"]["function"]: leaf for leaf in report["relocated_leaves"]
    }
    blockers = [
        leaf["function"]
        for leaf in report["overlay"]["link"]["relocated_functions"]
        if leaf["offset"] + leaf["size"] > cutoff
        and not config_leaves[leaf["function"]].get("strict_relocation_contract")
    ]
    require(
        blockers == proposal["minimum_suffix_contract_blockers"],
        "minimum suffix contract blocker set drift",
    )
    blocker_bytes = sum(report_leaves[name]["placement"]["size"] for name in blockers)
    blocker_relocations = sum(
        len(report_leaves[name]["extraction"]["relocations"]) for name in blockers
    )
    require(
        len(blockers) == expected["minimum_suffix_contract_blocker_count"]
        and blocker_bytes == expected["minimum_suffix_contract_blocker_bytes"]
        and blocker_relocations
        == expected["minimum_suffix_contract_blocker_relocations"],
        "minimum suffix blocker accounting drift",
    )
    return {
        "production_full_repack_allowed": not non_strict,
        "full_repack_moved_leaves": len(moved),
        "full_repack_moved_strict_leaves": len(strict),
        "full_repack_moved_non_strict_leaves": len(non_strict),
        "minimum_suffix_cutoff": report["overlay"]["overlay_runtime_address"] + cutoff,
        "minimum_suffix_contract_blockers": blockers,
        "minimum_suffix_contract_blocker_bytes": blocker_bytes,
        "minimum_suffix_contract_blocker_relocations": blocker_relocations,
    }


def _provider_rebase(
    proposal: dict[str, Any], report: dict[str, Any], layout: dict[str, Any]
) -> dict[str, Any]:
    receipt = report["overlay"]["post_link_providers"]["pt_protocol"][
        "source_uart_route_receipt"
    ]
    require(
        receipt["function"] == "open_cfw_box_uart_handle"
        and receipt["strict_relocation_contract"],
        "PT source-UART receipt drift",
    )
    new_leaf = layout["new_addresses"][receipt["function"]]
    sites = []
    for relocation in receipt["relocations"]:
        site = new_leaf + relocation["offset"]
        try:
            encoded = encode_thumb_branch(
                site, relocation["target_address"], link=True
            )
            require(
                decode_thumb_branch(site, encoded, link=True)
                == relocation["target_address"],
                "PT rebased branch mismatch",
            )
        except BuildError as error:
            raise CapacityError("PT source-UART branch would be out of range") from error
        sites.append(site)
    require(
        new_leaf == proposal["expected"]["pt_source_uart_new_leaf_address"]
        and sites == proposal["expected"]["pt_source_uart_new_call_sites"],
        "PT source-UART rebase receipt drift",
    )
    old_leaf = next(
        leaf["placement"]["runtime_address"]
        for leaf in report["relocated_leaves"]
        if leaf["extraction"]["function"] == receipt["function"]
    )
    return {
        "provider_interval_unchanged": True,
        "old_leaf_address": old_leaf,
        "new_leaf_address": new_leaf,
        "old_call_sites": [
            old_leaf + item["offset"]
            for item in receipt["relocations"]
        ],
        "new_call_sites": sites,
        "receipt_refresh_required": True,
    }


def _encoder_layout(
    proposal: dict[str, Any], specialized: dict[str, Any], layout: dict[str, Any]
) -> dict[str, Any]:
    address = proposal["address_model"]
    expected = proposal["expected"]
    current = address["current_core_end_exclusive"]
    current_start = current
    for name, alignment in (
        ("text", 16), ("rodata", 16), ("table_rodata", 8)
    ):
        current = align_up(current, alignment)
        current += specialized["artifacts"][name]["size"]
    current_span = current - current_start
    current_shortfall = current - address["protected_update_start"]
    require(
        current_span == address["current_specialized_encoder_aligned_span"]
        and current_shortfall == address["current_shortfall"],
        "current specialized LC3 shortfall drift",
    )

    new_core_end = address["overlay_runtime_start"] + layout["new_size"]
    require(
        new_core_end == expected["conditional_core_end_exclusive"],
        "conditional core end drift",
    )
    cursor = new_core_end
    sections = []
    for name, alignment in (
        ("text", 16), ("rodata", 16), ("table_rodata", 8)
    ):
        start = align_up(cursor, alignment)
        end = start + specialized["artifacts"][name]["size"]
        sections.append(
            {
                "name": name,
                "start": start,
                "end_exclusive": end,
                "alignment": alignment,
                "padding_before": start - cursor,
                "size": end - start,
            }
        )
        cursor = end
    span = cursor - new_core_end
    margin = address["protected_update_start"] - cursor
    require(
        address["protected_update_start"] - new_core_end
        == expected["conditional_append_headroom"]
        and span == address["conditional_specialized_encoder_aligned_span"]
        and cursor == expected["conditional_encoder_end_exclusive"]
        and margin == expected["conditional_margin_before_update"],
        "conditional LC3 placement arithmetic drift",
    )
    return {
        "current_aligned_span": current_span,
        "current_shortfall": current_shortfall,
        "conditional_core_end_exclusive": new_core_end,
        "conditional_sections": sections,
        "conditional_aligned_span": span,
        "conditional_encoder_end_exclusive": cursor,
        "conditional_margin_before_update": margin,
        "placement_authorized": False,
    }


def analyze(proposal_path: Path = DEFAULT_PROPOSAL) -> dict[str, Any]:
    proposal = read_json(proposal_path)
    require(proposal["schema_version"] == 1, "unsupported proposal schema")
    config, report, _overlay, component = _pin_core(proposal)
    specialized = _pin_specialization(proposal)
    protected = _protected_receipts(proposal, report)
    candidates, config_leaves, _leaves = _derive_candidates(
        proposal, config, report, component, protected
    )
    layout = _selection_and_layout(
        proposal, candidates, report, config_leaves
    )
    relocations = _relocation_audit(
        proposal, config_leaves, report, layout
    )
    ingress = _ingress_audit(proposal, report, component, layout)
    blockers = _strict_blockers(proposal, config_leaves, report, layout)
    pt = _provider_rebase(proposal, report, layout)
    encoder = _encoder_layout(proposal, specialized, layout)

    require(
        proposal["outcome"] == {
            "authenticated_capacity_exists_conditionally": True,
            "production_rebalancing_feasible_now": False,
            "move_applied": False,
            "encoder_placement_assigned": False,
            "service_audio_routed": False,
            "firmware_image_emitted": False,
            "hardware_operations": False,
        },
        "proposal outcome drift",
    )
    require(
        not blockers["production_full_repack_allowed"],
        "blocked outcome is stale: every moved leaf is now strict",
    )
    return {
        "schema_version": 1,
        "name": proposal["name"],
        "status": "conditional-capacity-proven-production-rebalance-blocked",
        "canonical_core": {
            "component_size": len(component),
            "component_sha256": sha256_bytes(component),
            "overlay_size": report["overlay"]["size"],
            "overlay_sha256": report["overlay"]["sha256"],
            "runtime_end_exclusive": report["overlay"]["overlay_end_exclusive"],
        },
        "capacity": {
            "eligible_slot_count": len(candidates),
            "selected_count": len(layout["selected"]),
            "selected_closure_bytes": layout["closure_bytes"],
            "selected_slot_bytes": layout["slot_bytes"],
            "selected_slot_slack": layout["slot_bytes"] - layout["closure_bytes"],
            "selected_generated_nop_bytes": layout["generated_nop_bytes"],
            "selected_old_append_padding_before": layout["old_padding_before"],
            "current_link_padding": {
                "isolated": proposal["expected"]["current_isolated_padding"],
                "relocated_alignment": proposal["expected"]["current_relocated_alignment_padding"],
                "relocated_closure": proposal["expected"]["current_relocated_closure_padding"],
            },
            "source_owned_relocated_region": {
                "start": layout["relocated_region_start"],
                "end_exclusive": report["overlay"]["overlay_end_exclusive"],
                "bytes": layout["relocated_region_bytes"],
            },
            "predecessor_savings": layout["predecessor_savings"],
            "conditional_repack_savings": layout["savings"],
            "conditional_overlay_size": layout["new_size"],
        },
        "relocations": relocations,
        "ingress": ingress,
        "strict_contracts": blockers,
        "pt_source_uart": pt,
        "encoder": encoder,
        "protected_intervals": protected,
        "outcome": proposal["outcome"],
        "remaining_software_blockers": [
            "Add source-closure-at-stock-slot placement and stable relocation "
            "replay; all seven minimum-suffix contracts are now strict, but "
            "the current core builder only appends relocated leaves.",
            "Remap all owner-relative fixed targets and refresh the two PT "
            "source-UART relocation-site receipts after any repack.",
            "Integrate the specialized LC3 final relocations/import ABI, writable "
            "data policy, and service_audio adapter before assigning placement "
            "or emitting OTA bytes.",
        ],
        "evidence_boundary": {
            "image_bytes_modified": False,
            "production_move_authorized": False,
            "hardware_validation_performed": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_PROPOSAL)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    try:
        report = analyze(args.manifest)
    except (CapacityError, OSError, KeyError, TypeError, ValueError) as error:
        print(f"capacity audit failed: {error}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            report,
            indent=2 if args.pretty else None,
            sort_keys=True,
            separators=None if args.pretty else (",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
