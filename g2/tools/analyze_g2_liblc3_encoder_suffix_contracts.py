#!/usr/bin/env python3
"""Authenticate the seven unavoidable Apollo-main LC3 suffix contracts.

The audit compiles each retained source leaf with the canonical Apple-Clang
profile, applies an exact strict relocation table at both the current and the
conditional stable-repack address, and then searches the unrelocated code for
executable addresses which the ELF relocation table does not describe.  It
does not patch, place, route, or emit firmware.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import struct
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


G2 = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(G2 / "tools"))

import analyze_g2_liblc3_encoder_capacity as capacity  # noqa: E402
from apollo_overlay import (  # noqa: E402
    BuildError,
    compile_in_place_leaf,
    decode_thumb_branch,
    extract_in_place_function_section,
    parse_elf32,
    parse_elf32_symbols,
    section_named,
    thumb_movwt_immediate,
)


DEFAULT_MANIFEST = (
    G2
    / "components/apollo_main/liblc3_encoder/suffix_strict_contracts.json"
)


class ContractError(RuntimeError):
    """Raised when strict-contract evidence or a reviewed pin drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


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
        raise ContractError(f"cannot read {path}: {error}") from error
    require(isinstance(value, dict), f"{path}: expected JSON object")
    return value


def resolve(relative: str) -> Path:
    path = (G2 / relative).resolve()
    try:
        path.relative_to(G2.resolve())
    except ValueError as error:
        raise ContractError(f"path escapes G2 root: {relative}") from error
    return path


def authenticate(record: dict[str, Any]) -> tuple[Path, bytes]:
    path = resolve(record["path"])
    try:
        payload = path.read_bytes()
    except OSError as error:
        raise ContractError(f"cannot read {path}: {error}") from error
    require(len(payload) == record["size"], f"size drift: {path}")
    require(sha256_bytes(payload) == record["sha256"], f"hash drift: {path}")
    return path, payload


def _clang_path(explicit: str | None) -> str:
    if explicit:
        return explicit
    configured = os.environ.get("OPENCFW_CLANG")
    if configured:
        return configured
    try:
        completed = subprocess.run(
            ["xcrun", "--find", "clang"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise ContractError(
            "canonical Apple clang is unavailable; set OPENCFW_CLANG"
        ) from error
    path = completed.stdout.strip()
    require(bool(path), "xcrun returned an empty clang path")
    return path


def _pin_inputs(
    manifest: dict[str, Any],
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    bytes,
    dict[str, Any],
    dict[str, Any],
]:
    evidence = manifest["evidence"]
    for key in ("core_config", "core_report", "component_artifact"):
        authenticate(evidence[key])
    capacity_path, _ = authenticate(evidence["capacity_proposal"])
    _ghidra_path, _ = authenticate(evidence["ghidra_functions"])
    source_payloads: dict[str, bytes] = {}
    for record in evidence["sources"]:
        path, payload = authenticate(record)
        source_payloads[str(path.relative_to(G2))] = payload

    proposal = capacity.read_json(capacity_path)
    config, report, _overlay, component = capacity._pin_core(proposal)
    protected = capacity._protected_receipts(proposal, report)
    candidates, config_leaves, _report_leaves = capacity._derive_candidates(
        proposal, config, report, component, protected
    )
    layout = capacity._selection_and_layout(
        proposal, candidates, report, config_leaves
    )

    names = [item["function"] for item in manifest["functions"]]
    require(
        proposal["minimum_suffix_contract_blockers"] == [],
        "repaired minimum suffix unexpectedly regained blockers",
    )
    require(
        manifest["address_model"]["current_component_end_exclusive"]
        == report["overlay"]["overlay_end_exclusive"],
        "component runtime end drift",
    )
    require(
        len(component) == evidence["component_artifact"]["size"],
        "component evidence size drift",
    )
    require(
        manifest["address_model"]["conditional_repack_savings"]
        == layout["savings"]
        and manifest["address_model"]["conditional_encoder_margin"]
        == proposal["expected"]["conditional_margin_before_update"],
        "capacity proposal arithmetic drift",
    )

    scan_c = source_payloads["components/shared/runtime/runtime_format_scan.c"]
    engine_c = source_payloads[
        "components/shared/runtime/runtime_iar_vsnprintf_engine.c"
    ]
    require(
        b'#include "runtime_format_scan.h"' in scan_c,
        "scan transitive-header inclusion drift",
    )
    require(
        b'#include "../../apollo_main/core_overlay/runtime_vsnprintf.c"'
        in engine_c,
        "formatter transitive-template inclusion drift",
    )
    require(
        b"OPEN_CFW_RUNTIME_VSNPRINTF_RECURSE_ADDRESS" not in engine_c
        and b"0x007F7060" not in engine_c,
        "formatter regained a placement-specific recursive address",
    )
    return config, report, component, layout, config_leaves


def _relocation_contracts(
    names: list[str],
    report_leaf: dict[str, Any],
    *,
    proposed: bool,
    layout: dict[str, Any],
    starts: list[int],
    intervals: list[tuple[int, int, str]],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for relocation in report_leaf["extraction"]["relocations"]:
        target = relocation["target_address"]
        if proposed:
            owner = capacity._find_owner(target, starts, intervals)
            if owner is not None:
                owner_name, owner_start = owner
                target = layout["new_addresses"][owner_name] + target - owner_start
        records.append(
            {
                "offset": relocation["offset"],
                "type": relocation["type"],
                "symbol": relocation["symbol"],
                "target_address": target,
                "symbol_type": relocation["symbol_type"],
            }
        )
    return records


def _section_bytes(object_path: Path, section_name: str) -> tuple[bytes, list[dict[str, Any]]]:
    data, sections = parse_elf32(object_path)
    section = section_named(sections, section_name)
    start = int(section["offset"])
    payload = data[start : start + int(section["size"])]
    return payload, parse_elf32_symbols(data, sections)


def _materializations(
    function: str,
    payload: bytes,
    relocations: list[dict[str, Any]],
    current_address: int,
    proposed_address: int,
    address_model: dict[str, Any],
) -> list[dict[str, Any]]:
    covered = {item["offset"] for item in relocations}
    observed: list[dict[str, Any]] = []
    for movw_offset in range(0, len(payload) - 3, 2):
        first, second = struct.unpack_from("<HH", payload, movw_offset)
        if first & 0xFBF0 != 0xF240:
            continue
        register = (second >> 8) & 0xF
        for movt_offset in range(
            movw_offset + 4, min(movw_offset + 34, len(payload) - 3), 2
        ):
            high_first, high_second = struct.unpack_from(
                "<HH", payload, movt_offset
            )
            if (
                high_first & 0xFBF0 != 0xF2C0
                or (high_second >> 8) & 0xF != register
            ):
                continue
            pointer = thumb_movwt_immediate(first, second) | (
                thumb_movwt_immediate(high_first, high_second) << 16
            )
            executable = pointer & ~1
            if not (
                address_model["run_base"]
                <= executable
                < address_model["protected_update_start"]
            ):
                continue
            call_offset = None
            call_hex = None
            for offset in range(movt_offset + 4, min(movt_offset + 14, len(payload) - 1), 2):
                instruction = struct.unpack_from("<H", payload, offset)[0]
                if instruction & 0xFF87 == 0x4780 and (
                    instruction >> 3
                ) & 0xF == register:
                    call_offset = offset
                    call_hex = payload[offset : offset + 2].hex()
                    break
            if call_offset is None:
                continue
            observed.append(
                {
                    "function": function,
                    "movw_offset": movw_offset,
                    "movt_offset": movt_offset,
                    "register": register,
                    "pointer": pointer,
                    "pointer_hex": f"0x{pointer:08X}",
                    "movw_hex": payload[movw_offset : movw_offset + 4].hex(),
                    "movt_hex": payload[movt_offset : movt_offset + 4].hex(),
                    "indirect_call_offset": call_offset,
                    "indirect_call_hex": call_hex,
                    "relocation_present": (
                        movw_offset in covered or movt_offset in covered
                    ),
                    "current_expected_pointer": current_address | 1,
                    "proposed_expected_pointer": proposed_address | 1,
                    "target_bytes_emitted": (
                        address_model["run_base"]
                        <= executable
                        < address_model["current_component_end_exclusive"]
                    ),
                }
            )
            break
    return observed


def _symbol_receipt(
    function: str,
    symbols: list[dict[str, Any]],
    relocations: list[dict[str, Any]],
) -> dict[str, Any]:
    selected = [item for item in symbols if item["name"] == function]
    require(len(selected) == 1, f"{function}: selected symbol census drift")
    symbol = selected[0]
    require(
        symbol["binding"] == 1
        and symbol["type"] == 2
        and symbol["visibility"] == 0
        and symbol["section_index"] != 0,
        f"{function}: selected symbol is not global/default STT_FUNC",
    )
    imports: dict[str, str] = {}
    for relocation in relocations:
        matches = [
            item for item in symbols if item["name"] == relocation["symbol"]
        ]
        require(
            len(matches) == 1,
            f"{function}: symbol-table multiplicity drift for {relocation['symbol']}",
        )
        imported = matches[0]
        expected_type = 2 if relocation["symbol_type"] == "STT_FUNC" else 0
        require(
            imported["binding"] == 1
            and imported["visibility"] == 0
            and imported["type"] == expected_type,
            f"{function}: strict symbol metadata drift for {relocation['symbol']}",
        )
        if expected_type == 0:
            require(
                imported["section_index"] == 0,
                f"{function}: runtime import unexpectedly became defined",
            )
        else:
            require(
                imported["section_index"] != 0,
                f"{function}: defined scan target unexpectedly became undefined",
            )
        imports[relocation["symbol"]] = relocation["symbol_type"]
    return {
        "selected": "GLOBAL/DEFAULT/STT_FUNC",
        "relocation_symbols": dict(sorted(imports.items())),
    }


def _compile_and_replay(
    manifest: dict[str, Any],
    config: dict[str, Any],
    report: dict[str, Any],
    component: bytes,
    layout: dict[str, Any],
    clang: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    names = [item["function"] for item in manifest["functions"]]
    manifest_by_name = {item["function"]: item for item in manifest["functions"]}
    config_by_name = {item["function"]: item for item in config["relocated_leaves"]}
    report_by_name = {
        item["extraction"]["function"]: item for item in report["relocated_leaves"]
    }
    starts, intervals = capacity._owner_index(report)
    all_current: list[dict[str, Any]] = []
    all_proposed: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []
    materializations: list[dict[str, Any]] = []
    defined_scan = frozenset(names[:6])
    run_base = manifest["address_model"]["run_base"]
    preamble = manifest["address_model"]["preamble_bytes"]

    with tempfile.TemporaryDirectory(prefix="open-cfw-lc3-suffix-") as temporary:
        temporary_path = Path(temporary)
        for name in names:
            expected = manifest_by_name[name]
            leaf_config = config_by_name[name]
            leaf_report = report_by_name[name]
            placement = leaf_report["placement"]
            require(
                leaf_config.get("strict_relocation_contract") is True,
                f"{name}: repaired strict promotion is absent",
            )
            require(
                placement["runtime_address"] == expected["current_address"]
                and layout["new_addresses"][name] == expected["proposed_address"]
                and placement["size"] == expected["size"]
                and placement["alignment"] == expected["alignment"]
                and placement["padding_before"] == expected["padding_before"],
                f"{name}: placement receipt drift",
            )
            require(
                expected["proposed_address"] - expected["current_address"]
                == manifest["address_model"]["stable_repack_delta"],
                f"{name}: stable-repack delta drift",
            )
            require(
                leaf_config["toolchain"]["reviewed_version_prefix"]
                == manifest["toolchain"]["reviewed_version_prefix"]
                and leaf_config["toolchain"]["target"]
                == manifest["toolchain"]["target"],
                f"{name}: canonical compiler profile drift",
            )

            current_relocations = _relocation_contracts(
                names,
                leaf_report,
                proposed=False,
                layout=layout,
                starts=starts,
                intervals=intervals,
            )
            proposed_relocations = _relocation_contracts(
                names,
                leaf_report,
                proposed=True,
                layout=layout,
                starts=starts,
                intervals=intervals,
            )
            require(
                len(current_relocations) == expected["relocation_count"]
                and canonical_sha256(current_relocations)
                == expected["current_relocations_sha256"]
                and canonical_sha256(proposed_relocations)
                == expected["proposed_relocations_sha256"],
                f"{name}: strict relocation table drift",
            )
            all_current.extend(
                {"function": name, **item} for item in current_relocations
            )
            all_proposed.extend(
                {"function": name, **item} for item in proposed_relocations
            )

            strict_config = copy.deepcopy(leaf_config)
            strict_config.update(
                {
                    "runtime_address": expected["current_address"],
                    "stock": copy.deepcopy(leaf_config["expected"]),
                    "strict_relocation_contract": True,
                    "relocations": current_relocations,
                }
            )
            object_path = temporary_path / f"{name}.o"
            allowed_defined = defined_scan - {name}
            prel = (
                frozenset({"open_cfw_runtime_noop_output"})
                if name == "open_cfw_runtime_iar_vsnprintf_engine"
                else frozenset()
            )
            current_payload, current_receipt = compile_in_place_leaf(
                root=G2,
                clang=clang,
                leaf_config=strict_config,
                object_path=object_path,
                toolchain_profile=manifest["toolchain"]["profile"],
                allowed_defined_relocation_targets=allowed_defined,
                thumb_prel_symbols=prel,
            )
            require(
                len(current_payload) == expected["size"]
                and sha256_bytes(current_payload) == expected["sha256"]
                and current_receipt["extraction"]["unrelocated_sha256"]
                == expected["unrelocated_sha256"],
                f"{name}: current strict replay drift",
            )
            artifact_start = expected["current_address"] - run_base + preamble
            require(
                component[artifact_start : artifact_start + len(current_payload)]
                == current_payload,
                f"{name}: canonical artifact bytes differ from strict replay",
            )

            proposed_payload, proposed_receipt = extract_in_place_function_section(
                object_path,
                name,
                runtime_address=expected["proposed_address"],
                relocation_configs=proposed_relocations,
                record=True,
                allowed_defined_relocation_targets=allowed_defined,
                thumb_prel_symbols=prel,
                strict_relocation_contract=True,
                allow_self_relocation=leaf_config.get(
                    "allow_self_relocation", False
                ),
                allow_discarded_alloc_sections=leaf_config.get(
                    "allow_discarded_alloc_sections", False
                ),
            )
            require(
                len(proposed_payload) == expected["size"]
                and sha256_bytes(proposed_payload) == expected["proposed_sha256"]
                and proposed_receipt["unrelocated_sha256"]
                == expected["unrelocated_sha256"],
                f"{name}: proposed strict replay drift",
            )

            unrelocated, symbols = _section_bytes(
                object_path, current_receipt["extraction"]["section"]
            )
            require(
                sha256_bytes(unrelocated) == expected["unrelocated_sha256"],
                f"{name}: object-section identity drift",
            )
            symbol_receipt = _symbol_receipt(name, symbols, current_relocations)
            hidden = _materializations(
                name,
                unrelocated,
                current_relocations,
                expected["current_address"],
                expected["proposed_address"],
                manifest["address_model"],
            )
            materializations.extend(hidden)
            feasible = not hidden
            require(
                feasible is expected["strict_contract_feasible"],
                f"{name}: strict feasibility classification drift",
            )
            results.append(
                {
                    "function": name,
                    "current_address": expected["current_address"],
                    "proposed_address": expected["proposed_address"],
                    "size": expected["size"],
                    "relocation_count": len(current_relocations),
                    "strict_elf_replay_current": True,
                    "strict_elf_replay_proposed": True,
                    "symbol_contract": symbol_receipt,
                    "unrelocated_executable_materialization_count": len(hidden),
                    "strict_contract_authenticated": feasible,
                    "promotion_applied": True,
                }
            )

    require(
        materializations == manifest["embedded_executable_materializations"],
        "unrelocated executable-address materialization drift",
    )
    expected = manifest["expected"]
    require(
        canonical_sha256(all_current) == expected["current_relocations_sha256"]
        and canonical_sha256(all_proposed)
        == expected["proposed_relocations_sha256"],
        "aggregate strict relocation digest drift",
    )
    return results, materializations, all_current


def _inside(address: int, interval: tuple[int, int, str]) -> bool:
    return interval[0] <= address < interval[1]


def _ingress_audit(
    manifest: dict[str, Any], report: dict[str, Any], component: bytes
) -> dict[str, Any]:
    names = {item["function"] for item in manifest["functions"]}
    intervals = sorted(
        (
            item["placement"]["runtime_address"],
            item["placement"]["runtime_address"] + item["placement"]["size"],
            item["extraction"]["function"],
        )
        for item in report["relocated_leaves"]
        if item["extraction"]["function"] in names
    )
    entries = {start: name for start, _end, name in intervals}
    expected_entries: set[tuple[int, int, bool]] = set()
    for patch in report["overlay"]["patched_sites"]:
        if patch.get("target_function") in names:
            expected_entries.add(
                (patch["runtime_address"], patch["target_address"], False)
            )
    for leaf in report["relocated_leaves"]:
        for relocation in leaf["extraction"]["relocations"]:
            if (
                relocation["target_address"] in entries
                and relocation["target_address"]
                != leaf["placement"]["runtime_address"]
                and relocation["type"] in {
                    "R_ARM_THM_CALL",
                    "R_ARM_THM_JUMP24",
                }
            ):
                expected_entries.add(
                    (
                        relocation["runtime_address"],
                        relocation["target_address"],
                        relocation["type"] == "R_ARM_THM_CALL",
                    )
                )

    run_base = manifest["address_model"]["run_base"]
    preamble = manifest["address_model"]["preamble_bytes"]
    observed_entries: set[tuple[int, int, bool]] = set()
    observed_interiors: list[dict[str, Any]] = []
    for offset in range(preamble, len(component) - 3, 2):
        site = run_base + offset - preamble
        encoded = component[offset : offset + 4]
        try:
            target = decode_thumb_branch(site, encoded)
        except BuildError:
            continue
        owners = [interval for interval in intervals if _inside(target, interval)]
        if not owners:
            continue
        owner = owners[0]
        if _inside(site, owner):
            continue
        _first, second = struct.unpack("<HH", encoded)
        if target == owner[0]:
            observed_entries.add((site, target, bool(second & 0x4000)))
        else:
            observed_interiors.append(
                {
                    "decode_site": site,
                    "target": target,
                    "target_function": owner[2],
                }
            )
    require(
        observed_entries == expected_entries,
        "exact suffix entry branch ingress drift",
    )

    false_expected = manifest["false_external_branch_decodes"]
    observed_interiors.sort(key=lambda item: item["decode_site"])
    require(
        observed_interiors
        == [
            {
                "decode_site": item["decode_site"],
                "target": item["target"],
                "target_function": item["target_function"],
            }
            for item in false_expected
        ],
        "external interior-decode census drift",
    )
    ghidra_path = resolve(manifest["evidence"]["ghidra_functions"]["path"])
    ghidra: dict[str, dict[str, Any]] = {}
    for line in ghidra_path.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        if record.get("entry") in {
            item["owner_entry"] for item in false_expected
        }:
            ghidra[record["entry"]] = record
    for expected in false_expected:
        record = ghidra.get(expected["owner_entry"])
        require(record is not None, "Ghidra false-decode owner missing")
        require(
            record["name"] == expected["owner_name"]
            and record["body_sha256"] == expected["owner_body_sha256"],
            "Ghidra false-decode owner drift",
        )
        file_offset = (
            expected["instruction_start"] - run_base + preamble
        )
        instruction = component[file_offset : file_offset + 4]
        require(
            instruction.hex() == expected["instruction_hex"],
            "false-decode aligned instruction bytes drift",
        )
        require(
            (expected["mnemonic"] == "udiv" and instruction.hex() == "b0fbf1f2")
            or (
                expected["mnemonic"] == "sdiv"
                and instruction.hex() in {"93fbf1f1", "92fbf1f1"}
            ),
            "false-decode opcode classification drift",
        )

    raw_pointers: list[tuple[int, int]] = []
    for offset in range(preamble, len(component) - 3):
        value = struct.unpack_from("<I", component, offset)[0]
        if value & ~1 in entries:
            raw_pointers.append((run_base + offset - preamble, value))
    expected = manifest["expected"]
    require(
        len(observed_entries) == expected["exact_entry_branch_ingress"]
        and len(observed_interiors)
        == expected["external_false_interior_decodes"]
        and len(raw_pointers) == expected["raw_entry_pointer_ingress"],
        "suffix ingress accounting drift",
    )
    entry_digest = canonical_sha256(sorted(observed_entries))
    require(
        entry_digest == expected["exact_entry_branches_sha256"],
        "exact suffix entry-branch digest drift",
    )
    return {
        "exact_entry_branch_count": len(observed_entries),
        "exact_entry_call_count": sum(item[2] for item in observed_entries),
        "exact_entry_jump_count": sum(not item[2] for item in observed_entries),
        "false_interior_decode_count": len(observed_interiors),
        "raw_entry_pointer_count": len(raw_pointers),
        "exact_entry_branches_sha256": entry_digest,
    }


def analyze(
    manifest_path: Path = DEFAULT_MANIFEST, *, clang: str | None = None
) -> dict[str, Any]:
    manifest = read_json(manifest_path)
    require(manifest["schema_version"] == 1, "unsupported manifest schema")
    config, report, component, layout, _config_leaves = _pin_inputs(manifest)
    compiler = _clang_path(clang)
    functions, materializations, relocations = _compile_and_replay(
        manifest, config, report, component, layout, compiler
    )
    ingress = _ingress_audit(manifest, report, component)

    expected = manifest["expected"]
    types = Counter(item["type"] for item in relocations)
    qualified = [item for item in functions if item["strict_contract_authenticated"]]
    blocked = [item for item in functions if not item["strict_contract_authenticated"]]
    require(
        len(functions) == expected["function_count"]
        and sum(item["size"] for item in functions) == expected["function_bytes"]
        and len(relocations) == expected["relocation_count"]
        and dict(sorted(types.items())) == expected["relocation_types"],
        "suffix function/relocation accounting drift",
    )
    require(
        len(qualified) == expected["strict_qualified_count"]
        and sum(item["size"] for item in qualified)
        == expected["strict_qualified_bytes"]
        and sum(item["relocation_count"] for item in qualified)
        == expected["strict_qualified_relocations"]
        and len(blocked) == expected["blocked_count"]
        and sum(item["size"] for item in blocked) == expected["blocked_bytes"]
        and sum(item["relocation_count"] for item in blocked)
        == expected["blocked_relocations"],
        "strict qualification accounting drift",
    )
    require(not blocked, "repaired suffix unexpectedly regained a blocker")
    require(
        manifest["outcome"]
        == {
            "all_seven_strict_contracts_authenticated": True,
            "production_rebalancing_feasible_now": False,
            "contract_changes_applied": True,
            "image_bytes_modified": True,
            "encoder_placement_assigned": False,
            "service_audio_routed": False,
            "firmware_image_emitted": False,
            "hardware_operations": False,
        },
        "manifest outcome drift",
    )
    require(
        not materializations,
        "formatter still contains an unrelocated executable materialization",
    )

    return {
        "schema_version": 1,
        "name": manifest["name"],
        "status": "all-seven-suffix-strict-contracts-authenticated",
        "toolchain": {
            "profile": manifest["toolchain"]["profile"],
            "executable": compiler,
            "reviewed_version_prefix": manifest["toolchain"][
                "reviewed_version_prefix"
            ],
            "target": manifest["toolchain"]["target"],
        },
        "functions": functions,
        "summary": {
            "function_count": len(functions),
            "function_bytes": sum(item["size"] for item in functions),
            "relocation_count": len(relocations),
            "relocation_types": dict(sorted(types.items())),
            "strict_authenticated_count": len(qualified),
            "strict_authenticated_bytes": sum(item["size"] for item in qualified),
            "blocked_count": len(blocked),
            "blocked_bytes": sum(item["size"] for item in blocked),
            "blocked_function": None,
        },
        "unrelocated_executable_materializations": materializations,
        "ingress": ingress,
        "capacity": {
            "conditional_repack_savings": layout["savings"],
            "conditional_encoder_margin": manifest["address_model"][
                "conditional_encoder_margin"
            ],
            "production_rebalancing_feasible_now": False,
        },
        "outcome": manifest["outcome"],
        "remaining_software_blockers": [
            "Implement the capacity proposal's source-closure-at-stock-slot "
            "placement and stable relocation replay; the current core builder "
            "still only appends relocated leaves.",
            "Remap owner-relative fixed targets and refresh the two PT "
            "source-UART relocation-site receipts after any repack.",
            "Integrate final LC3 relocations/import ABIs, writable data, and "
            "service_audio adaptation before placement or routing.",
        ],
        "evidence_boundary": {
            "image_bytes_modified": True,
            "production_move_authorized": False,
            "encoder_routing_claimed": False,
            "hardware_validation_performed": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--clang")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    try:
        report = analyze(args.manifest, clang=args.clang)
    except (
        BuildError,
        ContractError,
        OSError,
        KeyError,
        TypeError,
        ValueError,
        subprocess.SubprocessError,
    ) as error:
        print(f"suffix strict-contract audit failed: {error}", file=sys.stderr)
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
