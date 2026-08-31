#!/usr/bin/env python3
"""Authenticate the minimal Apollo-main LC3 suffix-to-stock-tail packing plan.

This analyzer never emits a firmware image.  It proves the exact core-capacity
move made possible by the admitted -Oz LC3 closure, replays every relocation
inside the moved suffix, and keeps final LC3 binding/routing/OTA authority
fail-closed.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import bisect
import struct
import sys
import tempfile
from pathlib import Path
from typing import Any


G2 = Path(__file__).resolve().parents[1]
MANIFEST = (
    G2 / "components/apollo_main/liblc3_encoder/"
    "service_audio_suffix_pack_proposal.json"
)
CAPACITY_TOOL = G2 / "tools/analyze_g2_liblc3_encoder_capacity.py"
CAPACITY_BUILDER = (
    G2 / "components/apollo_main/liblc3_encoder/"
    "build_service_audio_capacity_experiment.py"
)
sys.path.insert(0, str(G2 / "tools"))

from apollo_overlay import (  # noqa: E402
    BuildError,
    decode_thumb_branch,
    encode_thumb_branch,
    thumb_movwt_immediate,
    thumb_movwt_with_immediate,
)


class SuffixPackError(RuntimeError):
    """Raised when suffix placement evidence or arithmetic drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SuffixPackError(message)


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise SuffixPackError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


C = _load(CAPACITY_TOOL, "open_cfw_liblc3_suffix_capacity")
B = _load(CAPACITY_BUILDER, "open_cfw_liblc3_suffix_capacity_builder")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(json.dumps(
        value, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"{path}: expected JSON object")
    return value


def resolve(relative: str) -> Path:
    path = (G2 / relative).resolve()
    try:
        path.relative_to(G2.resolve())
    except ValueError as error:
        raise SuffixPackError(f"path escapes G2 root: {relative}") from error
    return path


def authenticate(record: dict[str, Any]) -> tuple[Path, bytes]:
    path = resolve(record["path"])
    payload = path.read_bytes()
    require(len(payload) == record["size"], f"size drift: {path}")
    require(sha256_bytes(payload) == record["sha256"], f"hash drift: {path}")
    return path, payload


def align_up(value: int, alignment: int) -> int:
    require(alignment > 0 and not alignment & (alignment - 1),
            f"invalid alignment {alignment}")
    return (value + alignment - 1) & -alignment


def image_slice(component: bytes, start: int, end: int,
                *, run_base: int, preamble: int) -> bytes:
    first = start - run_base + preamble
    last = end - run_base + preamble
    require(0 <= first <= last <= len(component),
            f"image interval escapes component: 0x{start:08X}..0x{end:08X}")
    return component[first:last]


def image_write(component: bytearray, start: int, payload: bytes,
                *, run_base: int, preamble: int) -> None:
    first = start - run_base + preamble
    last = first + len(payload)
    require(0 <= first <= last <= len(component),
            f"image write escapes component at 0x{start:08X}")
    component[first:last] = payload


def _capacity_receipt(manifest: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    capacity_manifest, payload = authenticate(manifest["evidence"][
        "capacity_experiment"])
    require(sha256_bytes(payload) == manifest["evidence"][
        "capacity_experiment"]["sha256"], "capacity manifest drift")
    capacity = read_json(capacity_manifest)
    route_reference = capacity["route_config"]
    route_path = resolve(route_reference["path"])
    require(sha256_bytes(route_path.read_bytes()) == route_reference["sha256"],
            "capacity route-config pin drift")
    route = read_json(route_path)
    stock = route["stock_evidence"]
    adapter = {
        "contexts": stock["contexts"],
        "slot_bytes": stock["slot_bytes"],
        "context_end_exclusive": stock["context_end_exclusive"],
    }
    require(adapter == manifest["adapter_state"],
            "four-slot adapter-state geometry drift")
    require(len(adapter["contexts"]) == 4 and all(
        right - left == adapter["slot_bytes"]
        for left, right in zip(adapter["contexts"], adapter["contexts"][1:])) and
        adapter["contexts"][-1] + adapter["slot_bytes"] ==
        adapter["context_end_exclusive"],
        "adapter-state slots overlap or are not exact")
    with tempfile.TemporaryDirectory(prefix="liblc3-suffix-capacity-") as temp:
        report = B.build(
            manifest_path=capacity_manifest,
            output_dir=Path(temp), profile="apple-clang", record=False)
    require(B.canonical_sha256(report) == manifest["expected"][
        "apple_capacity_report_sha256"], "Apple capacity receipt drift")
    oz = report["accepted"]["oz_gc"]
    require(oz["imports"] == manifest["required_runtime_imports"],
            "LC3 runtime import boundary drift")
    return oz, adapter


def _pin_core(manifest: dict[str, Any]):
    proposal_path, _ = authenticate(manifest["evidence"][
        "capacity_rebalancing_proposal"])
    proposal = C.read_json(proposal_path)
    config, report, overlay, component = C._pin_core(proposal)
    protected = C._protected_receipts(proposal, report)
    candidates, config_leaves, _ = C._derive_candidates(
        proposal, config, report, component, protected)
    return proposal, config, report, overlay, component, protected, candidates, config_leaves


def _suffix(report: dict[str, Any], config_leaves: dict[str, Any],
            required: int) -> tuple[list[dict[str, Any]], int, int]:
    base = report["overlay"]["overlay_runtime_address"]
    end = report["overlay"]["overlay_end_exclusive"]
    ordered = report["overlay"]["link"]["relocated_functions"]
    suffix: list[dict[str, Any]] = []
    for leaf in reversed(ordered):
        suffix.append(leaf)
        start = base + suffix[-1]["offset"]
        if end - start >= required:
            suffix.reverse()
            break
    else:
        raise SuffixPackError("relocated suffix cannot satisfy capacity")
    start = base + suffix[0]["offset"]
    require(all(config_leaves[row["function"]].get(
        "strict_relocation_contract") is True for row in suffix),
        "minimal suffix contains a non-strict leaf")
    return suffix, start, end - start


def _host_bins(proposal: dict[str, Any], candidates: list[Any],
               component: bytes) -> list[dict[str, Any]]:
    by_name = {name: (patch, leaf) for _size, name, patch, leaf in candidates}
    run_base = proposal["address_model"]["run_base"]
    preamble = proposal["address_model"]["preamble_bytes"]
    bins = []
    for name in proposal["selected_functions"]:
        patch, _leaf = by_name[name]
        start = patch["runtime_address"] + 4
        end = patch["runtime_address"] + patch["expected_size"]
        tail = image_slice(component, start, end,
                           run_base=run_base, preamble=preamble)
        require(tail == b"\x00\xBF" * (len(tail) // 2),
                f"host slot tail is not generated Thumb NOP padding: {name}")
        bins.append({
            "host_function": name,
            "entry": patch["runtime_address"],
            "start": start,
            "end_exclusive": end,
            "cursor": start,
            "items": [],
        })
    bins.sort(key=lambda row: row["start"])
    return bins


def pack_suffix(suffix: list[dict[str, Any]], bins: list[dict[str, Any]],
                forbidden_entries: frozenset[int] = frozenset()) -> list[dict[str, Any]]:
    """First-fit-decreasing packing with exact per-leaf alignment."""
    work = [{**row, "items": [], "cursor": row.get("cursor", row["start"])}
            for row in bins]
    items = sorted(suffix, key=lambda row: (row["size"], row["function"]),
                   reverse=True)
    for leaf in items:
        for slot in work:
            start = align_up(slot["cursor"], leaf["alignment"])
            while start in forbidden_entries:
                start += leaf["alignment"]
            if start + leaf["size"] <= slot["end_exclusive"]:
                slot["items"].append({
                    "function": leaf["function"],
                    "start": start,
                    "size": leaf["size"],
                    "alignment": leaf["alignment"],
                    "padding_before": start - slot["cursor"],
                })
                slot["cursor"] = start + leaf["size"]
                break
        else:
            raise SuffixPackError(
                f"suffix leaf does not fit authenticated host tails: {leaf['function']}")
    return [row for row in work if row["items"]]


def _host_forbidden_entries(proposal: dict[str, Any], component: bytes,
                            bins: list[dict[str, Any]]) -> dict[str, Any]:
    """Find existing exact branch/pointer materializations into host tails."""
    intervals = sorted((row["start"], row["end_exclusive"]) for row in bins)
    starts = [row[0] for row in intervals]

    def inside(value: int) -> bool:
        index = bisect.bisect_right(starts, value) - 1
        return index >= 0 and intervals[index][0] <= value < intervals[index][1]

    run_base = proposal["address_model"]["run_base"]
    preamble = proposal["address_model"]["preamble_bytes"]
    branches = set()
    for offset in range(preamble, len(component) - 3, 2):
        site = run_base + offset - preamble
        try:
            target = decode_thumb_branch(site, component[offset:offset + 4])
        except BuildError:
            continue
        if inside(target):
            branches.add(target)
    pointers = set()
    aligned_pointers = set()
    for offset in range(preamble, len(component) - 3):
        target = struct.unpack_from("<I", component, offset)[0] & ~1
        if inside(target):
            pointers.add(target)
            if (run_base + offset - preamble) % 4 == 0:
                aligned_pointers.add(target)
    return {
        "forbidden": frozenset(branches | pointers),
        "branch_target_count": len(branches),
        "byte_window_pointer_target_count": len(pointers),
        "aligned_word_pointer_target_count": len(aligned_pointers),
    }


def _owner(address: int, intervals: list[tuple[int, int, str]]) -> tuple[int, str] | None:
    for start, end, name in intervals:
        if start <= address < end:
            return start, name
    return None


def _rebase_leaf(payload: bytes, leaf: dict[str, Any], new_base: int,
                 new_addresses: dict[str, int],
                 intervals: list[tuple[int, int, str]]) -> tuple[bytes, list[dict[str, Any]]]:
    old_base = leaf["placement"]["runtime_address"]
    blob = bytearray(payload)
    relocations = leaf["extraction"]["relocations"]
    replay = []
    index = 0
    while index < len(relocations):
        relocation = relocations[index]
        kind = relocation["type"]
        offset = relocation["offset"]
        old_target = relocation["target_address"]
        target_owner = _owner(old_target, intervals)
        new_target = old_target if target_owner is None else (
            new_addresses[target_owner[1]] + old_target - target_owner[0])
        new_site = new_base + offset
        if kind in {"R_ARM_THM_CALL", "R_ARM_THM_JUMP24"}:
            encoded = encode_thumb_branch(
                new_site, new_target, link=kind == "R_ARM_THM_CALL")
            require(decode_thumb_branch(
                new_site, encoded, link=kind == "R_ARM_THM_CALL") == new_target,
                f"rebased branch round-trip failed: {leaf['extraction']['function']}")
            blob[offset:offset + 4] = encoded
            replay.append({"type": kind, "site": new_site, "target": new_target})
            index += 1
            continue
        require(kind == "R_ARM_THM_MOVW_PREL_NC",
                f"unsupported suffix relocation: {kind}")
        require(index + 1 < len(relocations), "unpaired suffix PREL MOVW")
        high = relocations[index + 1]
        require(high["type"] == "R_ARM_THM_MOVT_PREL" and
                high["symbol"] == relocation["symbol"] and
                high["target_address"] == old_target,
                "suffix PREL MOVW/MOVT pair drift")
        low_first, low_second = struct.unpack_from("<HH", blob, offset)
        high_first, high_second = struct.unpack_from("<HH", blob, high["offset"])
        require(thumb_movwt_immediate(low_first, low_second) ==
                (relocation["low_result"] & 0xFFFF) and
                thumb_movwt_immediate(high_first, high_second) ==
                (relocation["high_result"] >> 16),
                "suffix PREL encoded receipt drift")
        low_result = (((new_target + relocation["low_addend"]) | 1) -
                      new_site) & 0xFFFFFFFF
        high_site = new_base + high["offset"]
        high_result = (new_target + relocation["high_addend"] -
                       high_site) & 0xFFFFFFFF
        require(low_result >> 16 == high_result >> 16,
                "rebased suffix PREL pair crosses a 64-KiB half boundary")
        low_first, low_second = thumb_movwt_with_immediate(
            low_first, low_second, low_result)
        high_first, high_second = thumb_movwt_with_immediate(
            high_first, high_second, high_result >> 16)
        struct.pack_into("<HH", blob, offset, low_first, low_second)
        struct.pack_into("<HH", blob, high["offset"], high_first, high_second)
        replay.extend((
            {"type": kind, "site": new_site, "target": new_target},
            {"type": high["type"], "site": high_site, "target": new_target},
        ))
        index += 2
    return bytes(blob), replay


def _ingress(proposal: dict[str, Any], report: dict[str, Any],
             component: bytes, suffix: list[dict[str, Any]]) -> dict[str, Any]:
    run_base = proposal["address_model"]["run_base"]
    preamble = proposal["address_model"]["preamble_bytes"]
    base = report["overlay"]["overlay_runtime_address"]
    starts = {base + row["offset"] for row in suffix}
    observed = set()
    for offset in range(preamble, len(component) - 3, 2):
        site = run_base + offset - preamble
        try:
            target = decode_thumb_branch(site, component[offset:offset + 4])
        except BuildError:
            continue
        if target in starts:
            observed.add((site, target))
    expected = set()
    for patch in report["overlay"]["patched_sites"]:
        if patch.get("target_address") in starts:
            expected.add((patch["runtime_address"], patch["target_address"]))
    for leaf in report["relocated_leaves"]:
        for relocation in leaf["extraction"]["relocations"]:
            if relocation["type"] in {"R_ARM_THM_CALL", "R_ARM_THM_JUMP24"} and \
                    relocation["target_address"] in starts:
                expected.add((relocation["runtime_address"],
                              relocation["target_address"]))
    require(observed == expected, "suffix exact-entry executable ingress drift")
    raw = []
    for offset in range(preamble, len(component) - 3):
        value = struct.unpack_from("<I", component, offset)[0] & ~1
        if value in starts:
            raw.append((run_base + offset - preamble, value))
    require(not raw, "suffix has raw-pointer ingress")
    stock = sum(1 for patch in report["overlay"]["patched_sites"]
                if patch.get("target_address") in starts)
    return {
        "exact_entry_branch_count": len(observed),
        "stock_entry_redirect_count": stock,
        "suffix_internal_branch_count": len(observed) - stock,
        "raw_pointer_count": 0,
        "records_sha256": canonical_sha256(sorted(observed)),
    }


def analyze(manifest_path: Path = MANIFEST, *, record: bool = False) -> dict[str, Any]:
    manifest = read_json(manifest_path)
    require((manifest.get("schema_version"), manifest.get("mode")) ==
            (1, "exact-suffix-pack-capacity-proof-routing-blocked"),
            "suffix-pack schema drift")
    require(manifest["routing"] == {
        "production_placement": False, "service_audio_routed": False,
        "firmware_image_emitted": False, "hardware_operations": False},
        "suffix-pack proposal gained production authority")
    oz, adapter = _capacity_receipt(manifest)
    (proposal, config, report, _overlay, component, protected, candidates,
     config_leaves) = _pin_core(manifest)
    required = manifest["address_model"]["apple_best_order_shortfall"]
    suffix, suffix_start, suffix_span = _suffix(
        report, config_leaves, required)
    bins = _host_bins(proposal, candidates, component)
    forbidden = _host_forbidden_entries(proposal, component, bins)
    packed = pack_suffix(suffix, bins, forbidden["forbidden"])
    placements = {
        item["function"]: item["start"]
        for slot in packed for item in slot["items"]
    }
    require(len(placements) == len(suffix), "suffix placement lost a leaf")
    ingress = _ingress(proposal, report, component, suffix)

    base = report["overlay"]["overlay_runtime_address"]
    old_intervals = sorted((
        base + row["offset"], base + row["offset"] + row["size"], row["function"])
        for row in suffix)
    reports = {row["extraction"]["function"]: row
               for row in report["relocated_leaves"]}
    run_base = proposal["address_model"]["run_base"]
    preamble = proposal["address_model"]["preamble_bytes"]
    rebased: dict[str, bytes] = {}
    replay_records = []
    for row in suffix:
        name = row["function"]
        leaf = reports[name]
        old = image_slice(component, leaf["placement"]["runtime_address"],
                          leaf["placement"]["runtime_address"] + row["size"],
                          run_base=run_base, preamble=preamble)
        require(sha256_bytes(old) == leaf["extraction"]["sha256"],
                f"suffix source bytes drift: {name}")
        identity, _ = _rebase_leaf(
            old, leaf, leaf["placement"]["runtime_address"],
            {item[2]: item[0] for item in old_intervals}, old_intervals)
        require(identity == old, f"identity relocation replay drift: {name}")
        moved, records = _rebase_leaf(
            old, leaf, placements[name], placements, old_intervals)
        rebased[name] = moved
        replay_records.extend({"function": name, **record} for record in records)

    patched = bytearray(component)
    suffix_names = set(placements)
    suffix_patches = [row for row in report["overlay"]["patched_sites"]
                      if row.get("target_function") in suffix_names]
    require(len(suffix_patches) == len(suffix),
            "suffix does not have exactly one stock entry redirect per leaf")
    for patch in suffix_patches:
        target = placements[patch["target_function"]]
        replacement = encode_thumb_branch(
            patch["runtime_address"], target, link=False)
        replacement += b"\x00\xBF" * ((patch["expected_size"] - 4) // 2)
        image_write(patched, patch["runtime_address"], replacement,
                    run_base=run_base, preamble=preamble)
    for slot in packed:
        for item in slot["items"]:
            image_write(patched, item["start"], rebased[item["function"]],
                        run_base=run_base, preamble=preamble)

    new_component_size = len(component) - suffix_span
    new_component = bytes(patched[:new_component_size])
    new_core_end = report["overlay"]["overlay_end_exclusive"] - suffix_span
    require(run_base + len(new_component) - preamble == new_core_end,
            "truncated component runtime-end drift")
    sizes = {name: oz["sections"][name]["size"] for name in
             ("text", "rodata", "table_rodata")}
    cursor = new_core_end
    section_rows = []
    for name, alignment in (("table_rodata", 8), ("rodata", 16), ("text", 16)):
        start = align_up(cursor, alignment)
        end = start + sizes[name]
        section_rows.append({"name": name, "start": start,
                             "end_exclusive": end, "size": sizes[name],
                             "alignment": alignment,
                             "padding_before": start - cursor})
        cursor = end
    update_start = manifest["address_model"]["protected_update_start"]
    margin = update_start - cursor
    require(margin >= 0, "suffix pack still does not fit the LC3 closure")
    text = next(row for row in section_rows if row["name"] == "text")
    routes = []
    for name, entry in manifest["service_audio_entries"].items():
        target = text["start"] + oz["roots"][name]["offset"]
        encoded = encode_thumb_branch(entry, target, link=False)
        require(decode_thumb_branch(entry, encoded, link=False) == target,
                f"service_audio entry branch is out of range: {name}")
        routes.append({"root": name, "entry": entry, "target": target,
                       "encoding_hex": encoded.hex()})

    summary = {
        "suffix_count": len(suffix),
        "suffix_start": suffix_start,
        "suffix_span": suffix_span,
        "suffix_payload_bytes": sum(row["size"] for row in suffix),
        "suffix_internal_padding": suffix_span - sum(row["size"] for row in suffix),
        "used_host_count": len(packed),
        "used_host_span": sum(row["cursor"] - row["start"] for row in packed),
        "used_host_payload": sum(item["size"] for row in packed for item in row["items"]),
        "used_host_alignment_padding": sum(item["padding_before"] for row in packed for item in row["items"]),
        "all_host_tail_capacity": sum(row["end_exclusive"] - row["start"] for row in bins),
        "preexisting_host_tail_branch_targets": forbidden["branch_target_count"],
        "preexisting_host_tail_byte_window_pointer_targets": forbidden["byte_window_pointer_target_count"],
        "preexisting_host_tail_aligned_pointer_targets": forbidden["aligned_word_pointer_target_count"],
        "placement_records_sha256": canonical_sha256(packed),
        "relocation_count": len(replay_records),
        "relocation_records_sha256": canonical_sha256(replay_records),
        "rebased_payloads_sha256": canonical_sha256([
            (name, len(rebased[name]), sha256_bytes(rebased[name]))
            for name in sorted(rebased)]),
        "new_component_size": new_component_size,
        "new_component_sha256": sha256_bytes(new_component),
        "new_core_end_exclusive": new_core_end,
        "lc3_section_order": [row["name"] for row in section_rows],
        "lc3_end_exclusive": cursor,
        "margin_before_update_record": margin,
    }
    expected = manifest["expected"]
    for key, value in summary.items():
        if key in expected and not record:
            require(value == expected[key], f"expected {key} drift: {value}")
    require(ingress == expected["ingress"] if not record else True,
            "expected suffix ingress drift")
    require(len(oz["imports"]) == 11 and
            oz["relocations"]["total"] == 485 and
            oz["relocations"]["table_code_references"]["count"] == 6,
            "LC3 relocation/table policy drift")

    return {
        "schema_version": 1,
        "status": "exact-suffix-pack-capacity-proven-production-route-blocked",
        "capacity": summary,
        "host_slots": packed,
        "ingress": ingress,
        "suffix_relocation_replay": {
            "all_84_leaves_strict": True,
            "identity_replay_verified": True,
            "relocation_count": len(replay_records),
            "records_sha256": summary["relocation_records_sha256"],
            "rebased_payloads_sha256": summary["rebased_payloads_sha256"],
        },
        "lc3_placement": {
            "sections": section_rows,
            "margin_before_update_record": margin,
            "service_audio_entry_branches": routes,
            "runtime_import_count": len(oz["imports"]),
            "runtime_imports": oz["imports"],
            "input_relocations": oz["relocations"]["total"],
            "table_initializers": 78,
            "table_code_references": oz["relocations"]["table_code_references"]["count"],
            "final_lc3_relocation_replay": False,
            "placement_authorized": False,
        },
        "adapter_state": {
            **adapter,
            "slot_count": 4,
            "total_bytes": adapter["slot_bytes"] * 4,
            "alignment_and_nonoverlap_verified": True,
        },
        "protected_intervals": protected,
        "routing": manifest["routing"],
        "remaining_software_blockers": [
            "Authenticate stock addresses and ownership for all 11 retained runtime imports; the current finalizer deliberately uses synthetic bindings.",
            "Extend the LC3 finalizer to accept the proven table-rodata/rodata/text production order and replay all 485 relocations at these exact addresses.",
            "Integrate the 84 entry redirects, seven stock-tail payloads, suffix truncation, four exact adapter slots, and service_audio veneers into one atomic OTA builder with final package integrity receipts.",
        ],
        "evidence_boundary": {
            "core_bytes_synthesized_in_memory": True,
            "firmware_image_emitted": False,
            "production_routing_authorized": False,
            "hardware_validation_performed": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--record", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    try:
        report = analyze(args.manifest.resolve(), record=args.record)
    except (SuffixPackError, BuildError, OSError, KeyError, TypeError,
            ValueError) as error:
        print(f"suffix-pack audit failed: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True,
                     indent=2 if args.pretty else None,
                     separators=None if args.pretty else (",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
