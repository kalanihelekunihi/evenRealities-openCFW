#!/usr/bin/env python3
"""Build and verify the routed LC3 service-audio production component.

``route_component`` consumes a same-build pre-CFF Apollo component and core
report, applies the authenticated suffix/runtime/LC3 plan, regenerates the
nested component CRC, and emits a guarded component for the following CFF
scatter stage.  The standalone entry point recompiles and relinks both LC3
closures at their admitted addresses, verifies an independently observed routed
component, and emits that pre-CFF image.  Neither entry point flashes or signs
hardware.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
G2 = ROOT.parents[2]
MANIFEST = ROOT / "service_audio_production_replay.json"
SUFFIX_TOOL = G2 / "tools/analyze_g2_liblc3_service_audio_suffix_pack.py"
ROUTE_BUILDER = ROOT / "build_service_audio_route_experiment.py"
AT_FS_SUFFIX_NAMES = {
    "open_cfw_at_fs_remove",
    "open_cfw_at_fs_list_recursive",
    "open_cfw_at_fs_list",
    "open_cfw_at_fs_mkdir",
}
AT_FS_COMMAND_POINTERS = {
    "open_cfw_at_fs_remove": 0x006C92B8,
    "open_cfw_at_fs_list": 0x006C92C8,
    "open_cfw_at_fs_mkdir": 0x006C92D8,
}


class ReplayError(RuntimeError):
    """Raised when runtime ownership or final relocation replay drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReplayError(message)


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ReplayError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


S = _load(SUFFIX_TOOL, "open_cfw_liblc3_production_suffix")
R = _load(ROUTE_BUILDER, "open_cfw_liblc3_production_route")
A = __import__("apollo_overlay")
X = R.X
EB = R.B


PUBLIC_RUNTIME = (
    "__aeabi_memclr", "__aeabi_memclr4", "fabsf", "floorf", "fmaxf",
    "fminf", "memcpy", "memmove", "memset", "truncf",
)
ALL_RUNTIME_SECTIONS = (*PUBLIC_RUNTIME, "open_cfw_liblc3_clear")
SCRIPT_SOURCE_NAMES = (
    "replay_builder", "suffix_analyzer", "route_builder", "xip_finalizer",
)
ROOTS = (
    "open_cfw_liblc3_service_audio_stock_encode",
    "open_cfw_liblc3_service_audio_stock_setup",
)
RUN_BASE = 0x00438000
PREAMBLE_BYTES = 32
PROTECTED_UPDATE_START = 0x007FE000
# The admitted cJSON parse-side and compact-log file-port source routes extend
# the core tail. Repack the resulting exact suffix so the LC3 table still
# starts at its authenticated fixed address. The compact-log closure adds
# exactly 1,106 aligned bytes to the previously admitted 11,698-byte suffix.
LC3_TABLE_START = 0x007EA620
LC3_IMAGE_END = 0x007FDFA0


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
        raise ReplayError(f"path escapes G2 root: {relative}") from error
    return path


def run(command: list[str]) -> str:
    completed = subprocess.run(command, cwd=G2, check=False,
                               capture_output=True, text=True,
                               env={"PATH": os.environ.get("PATH", ""),
                                    "LC_ALL": "C", "LANG": "C"})
    if completed.returncode:
        raise ReplayError(
            f"command failed ({completed.returncode}): {' '.join(command)}\n" +
            (completed.stderr.strip() or completed.stdout.strip()))
    return completed.stdout


def authenticate(record: dict[str, Any]) -> Path:
    path = resolve(record["path"])
    payload = path.read_bytes()
    require(len(payload) == record["size"] and
            sha256_bytes(payload) == record["sha256"],
            f"source pin drift: {path}")
    return path


def section_bytes(payload: bytes, section: dict[str, Any]) -> bytes:
    start = int(section["offset"])
    return payload[start:start + int(section["size"])]


def _compile_runtime(manifest: dict[str, Any], profile: str,
                     output: Path) -> tuple[Path, list[dict[str, Any]]]:
    source = authenticate(manifest["sources"]["runtime"])
    authenticate(manifest["sources"]["runtime_header"])
    tools = manifest["profiles"][profile]["tools"]
    flags = manifest["target_profile"]
    obj = output / "liblc3-target-runtime.o"
    run([tools["clang"], "--target=arm-none-eabi", *flags,
         "-c", str(source), "-o", str(obj)])
    payload, sections = A.parse_elf32(obj)
    symbols = A.parse_elf32_symbols(payload, sections)
    items = []
    for name in ALL_RUNTIME_SECTIONS:
        matches = [symbol for symbol in symbols if symbol["name"] == name]
        require(len(matches) == 1 and int(matches[0]["type"]) == 2,
                f"target runtime symbol drift: {name}")
        index = int(matches[0]["section_index"])
        section = next(row for row in sections if int(row["index"]) == index)
        require(section["name"] == f".text.{name}" and
                int(section["size"]) == int(matches[0]["size"]),
                f"target runtime section geometry drift: {name}")
        items.append({"function": name, "size": int(section["size"]),
                      "alignment": int(section["alignment"])})
    undefined = sorted(symbol["name"] for symbol in symbols
                       if int(symbol["section_index"]) == 0 and symbol["name"])
    require(not undefined, f"target runtime gained imports: {undefined}")
    return obj, items


def _runtime_placement(manifest: dict[str, Any], items: list[dict[str, Any]]):
    suffix_manifest = authenticate(manifest["evidence"]["suffix_pack"])
    suffix_report = S.analyze(suffix_manifest)
    suffix_data = read_json(suffix_manifest)
    (proposal, _config, core_report, _overlay, component, _protected,
     candidates, config_leaves) = S._pin_core(suffix_data)
    suffix, _start, _span = S._suffix(
        core_report, config_leaves,
        suffix_data["address_model"]["apple_best_order_shortfall"])
    bins = S._host_bins(proposal, candidates, component)
    forbidden = S._host_forbidden_entries(proposal, component, bins)
    occupied = S.pack_suffix(suffix, bins, forbidden["forbidden"])
    cursors = {row["entry"]: row["cursor"] for row in occupied}
    available = [{**row, "cursor": cursors.get(row["entry"], row["start"]),
                  "items": []} for row in bins]
    packed = S.pack_suffix(items, available, forbidden["forbidden"])
    placements = {item["function"]: item["start"]
                  for row in packed for item in row["items"]}
    require(set(placements) == set(ALL_RUNTIME_SECTIONS),
            "target runtime placement is incomplete")
    return suffix_report, core_report, packed, placements


def _link_runtime(manifest: dict[str, Any], profile: str, obj: Path,
                  packed: list[dict[str, Any]], placements: dict[str, int],
                  output: Path) -> tuple[dict[str, int], dict[str, Any]]:
    tools = manifest["profiles"][profile]["tools"]
    script = output / "target-runtime.ld"
    lines = ["SECTIONS", "{"]
    for name, address in sorted(placements.items(), key=lambda row: row[1]):
        lines.append(
            f"  .open_cfw_liblc3_runtime.{name} 0x{address:08X} : "
            f"{{ *(.text.{name}) }}")
    lines.extend(("  /DISCARD/ : { *(.ARM.exidx*) *(.comment*) *(.note*) }", "}"))
    script.write_text("\n".join(lines) + "\n", encoding="utf-8")
    final = output / "target-runtime.elf"
    run([tools["lld"], "-m", "armelf", "--gc-sections", "--build-id=none",
         *(f"--undefined={name}" for name in PUBLIC_RUNTIME),
         "-T", str(script), "-o", str(final), str(obj)])
    payload, sections = A.parse_elf32(final)
    symbols = A.parse_elf32_symbols(payload, sections)
    require(not any(int(row["type"]) == 9 and int(row["size"])
                    for row in sections), "target runtime retained relocations")
    require(not any(int(symbol["section_index"]) == 0 and symbol["name"]
                    for symbol in symbols), "target runtime retained imports")
    bindings = {}
    artifacts = []
    for name in ALL_RUNTIME_SECTIONS:
        symbol = next(row for row in symbols if row["name"] == name)
        require(int(symbol["value"]) == placements[name] | 1,
                f"target runtime symbol placement drift: {name}")
        section = next(row for row in sections
                       if row["name"] == f".open_cfw_liblc3_runtime.{name}")
        data = section_bytes(payload, section)
        require(len(data) == int(symbol["size"]),
                f"target runtime final size drift: {name}")
        artifacts.append({"function": name, "address": placements[name],
                          "size": len(data), "sha256": sha256_bytes(data)})
        if name in PUBLIC_RUNTIME:
            bindings[name] = int(symbol["value"])
    return bindings, {
        "object": {"size": obj.stat().st_size,
                   "sha256": sha256_bytes(obj.read_bytes())},
        "final_elf": {"size": len(payload), "sha256": sha256_bytes(payload)},
        "sections": artifacts,
        "placement_sha256": canonical_sha256(packed),
        "total_text_bytes": sum(row["size"] for row in artifacts),
        "undefined_symbols": [], "output_relocations": 0,
    }


def _finalize_lc3(manifest: dict[str, Any], profile: str,
                  suffix_report: dict[str, Any] | None,
                  bindings: dict[str, int],
                  core_report: dict[str, Any], output: Path,
                  layout_rows_override: list[dict[str, Any]] | None = None
                  ) -> dict[str, Any]:
    capacity_manifest = read_json(authenticate(manifest["evidence"][
        "capacity_experiment"]))
    tools = manifest["profiles"][profile]["tools"]
    helper = S.B._helper_record(capacity_manifest)
    relocatable = output / "service-route.relocatable.o"
    route = R.build(
        config_path=resolve(capacity_manifest["route_config"]["path"]),
        output_dir=output / "route", profile=profile,
        clang=tools["clang"], lld=tools["lld"], objcopy=tools["objcopy"],
        record=True, compiler_overrides=("-Oz",),
        additional_source_records=(helper,),
        table_reference_contract=S.B.TABLE_REFERENCE_CONTRACT,
        relocatable_output=relocatable)
    sqrt_leaf = next(row for row in core_report["relocated_leaves"]
                     if row["extraction"]["function"] == "open_cfw_iar_sqrtf")
    require(sqrt_leaf["source"]["path"] ==
            "components/apollo_main/core_overlay/candidates/iar_runtime_math_errno.S" and
            sqrt_leaf["extraction"]["relocation_count"] == 1,
            "source-owned sqrtf ownership drift")
    bindings = {**bindings, "sqrtf":
                int(sqrt_leaf["placement"]["runtime_address"]) | 1}
    require(sorted(bindings) == route["imports"],
            "production runtime binding set drift")
    external_consumers = route["relocations"]["external_by_symbol"]
    require(sorted(external_consumers) == sorted(bindings) and
            all(int(count) > 0 for count in external_consumers.values()),
            "production runtime relocation consumers drift")
    if layout_rows_override is not None:
        layout_rows = layout_rows_override
    elif profile == "apple-clang":
        require(suffix_report is not None, "Apple suffix report is missing")
        layout_rows = suffix_report["lc3_placement"]["sections"]
    else:
        require(suffix_report is not None, "suffix report is missing")
        cursor = suffix_report["capacity"]["new_core_end_exclusive"]
        layout_rows = []
        for name, alignment in (("table_rodata", 8), ("rodata", 16),
                                ("text", 16)):
            start = S.align_up(cursor, alignment)
            size = route["sections"][name]["size"]
            layout_rows.append({"name": name, "start": start,
                                "end_exclusive": start + size,
                                "size": size, "alignment": alignment,
                                "padding_before": start - cursor})
            cursor = start + size
    layout = {row["name"]: row for row in layout_rows}
    script = output / "lc3-production.ld"
    script.write_text(
        "SECTIONS\n{\n" +
        f"  {X.TABLE_SECTION} 0x{layout['table_rodata']['start']:08X} : "
        f"{{ *({X.TABLE_SECTION}) }}\n" +
        f"  .rodata 0x{layout['rodata']['start']:08X} : {{ *(.rodata) }}\n" +
        f"  .text 0x{layout['text']['start']:08X} : {{ *(.text) }}\n" +
        "  /DISCARD/ : { *(.ARM.exidx*) *(.comment*) *(.note*) }\n}\n",
        encoding="utf-8")
    final = output / "lc3-production.elf"
    run([tools["lld"], "-m", "armelf", "--gc-sections", "--build-id=none",
         *(f"--undefined={root}" for root in ROOTS),
         *(f"--defsym={name}=0x{address:08X}" for name, address in
           sorted(bindings.items())),
         "-T", str(script), "-o", str(final), str(relocatable)])
    payload, sections = A.parse_elf32(final)
    symbols = A.parse_elf32_symbols(payload, sections)
    require(not any(int(row["type"]) == 9 and int(row["size"])
                    for row in sections), "production LC3 ELF retained relocations")
    require(not any(int(symbol["section_index"]) == 0 and symbol["name"]
                    for symbol in symbols), "production LC3 ELF retained imports")
    artifacts = {}
    names = {"text": ".text", "rodata": ".rodata",
             "table_rodata": X.TABLE_SECTION}
    for name, section_name in names.items():
        section = next(row for row in sections if row["name"] == section_name)
        require(int(section["address"]) == layout[name]["start"] and
                int(section["size"]) == layout[name]["size"],
                f"production LC3 section geometry drift: {name}")
        data = section_bytes(payload, section)
        artifacts[name] = {"size": len(data), "sha256": sha256_bytes(data)}
    source_payload, source_sections = A.parse_elf32(relocatable)
    source_symbols = A.parse_elf32_symbols(source_payload, source_sections)
    records = X.relocation_records(
        source_payload, source_sections, source_symbols)
    table_records = [row for row in records if row["section"] == X.TABLE_SECTION]
    table_template = section_bytes(source_payload, next(
        row for row in source_sections if row["name"] == X.TABLE_SECTION))
    final_table = section_bytes(payload, next(
        row for row in sections if row["name"] == X.TABLE_SECTION))
    X._validate_final_table(
        template=table_template, final_table=final_table,
        table_relocations=table_records,
        rodata_start=layout["rodata"]["start"],
        rodata_size=layout["rodata"]["size"])
    roots = route["roots"]
    veneers = []
    for root, entry in manifest["service_audio_entries"].items():
        target = layout["text"]["start"] + roots[root]["offset"]
        encoded = A.encode_thumb_b_w(entry, target)
        require(A.decode_thumb_branch(entry, encoded, link=False) == target,
                f"production veneer reach drift: {root}")
        veneers.append({"root": root, "entry": entry, "target": target,
                        "encoding_hex": encoded.hex()})
    runtime_ownership = []
    for name, address in sorted(bindings.items()):
        if name == "sqrtf":
            runtime_ownership.append({
                "symbol": name,
                "binding": address,
                "runtime_address": address & ~1,
                "thumb": True,
                "symbol_type": "STT_FUNC",
                "provider_kind": "source-owned-core-leaf",
                "source": sqrt_leaf["source"],
                "provider_function": sqrt_leaf["extraction"]["function"],
                "provider_sha256": sqrt_leaf["extraction"]["sha256"],
                "provider_size": sqrt_leaf["extraction"]["size"],
                "provider_relocation_count":
                    sqrt_leaf["extraction"]["relocation_count"],
                "consumer_relocation_count": external_consumers[name],
            })
        else:
            runtime_ownership.append({
                "symbol": name,
                "binding": address,
                "runtime_address": address & ~1,
                "thumb": True,
                "symbol_type": "STT_FUNC",
                "provider_kind": "lc3-owned-target-runtime",
                "source": manifest["sources"]["runtime"],
                "provider_function": name,
                "consumer_relocation_count": external_consumers[name],
            })
    return {
        "layout": layout_rows,
        "runtime_bindings": dict(sorted(bindings.items())),
        "runtime_import_ownership": runtime_ownership,
        "input_relocations": route["relocations"]["total"],
        "output_relocations": 0,
        "input_relocation_contract": {
            key: route["relocations"][key] for key in (
                "by_type", "by_section", "external_by_symbol",
                "records_sha256")
        },
        "all_input_relocations_applied": True,
        "table_initializers": route["relocations"]["table_initializers"]["count"],
        "table_code_references": route["relocations"]["table_code_references"]["count"],
        "table_initializers_verified_word_for_word": True,
        "artifacts": artifacts,
        "final_elf": {"size": len(payload), "sha256": sha256_bytes(payload)},
        "service_audio_veneers": veneers,
    }


def _runtime_section_payloads(output: Path) -> dict[str, bytes]:
    payload, sections = A.parse_elf32(output / "target-runtime.elf")
    return {
        name: section_bytes(payload, next(
            row for row in sections
            if row["name"] == f".open_cfw_liblc3_runtime.{name}"))
        for name in ALL_RUNTIME_SECTIONS
    }


def _lc3_section_payloads(output: Path) -> dict[str, bytes]:
    payload, sections = A.parse_elf32(output / "lc3-production.elf")
    names = {"text": ".text", "rodata": ".rodata",
             "table_rodata": X.TABLE_SECTION}
    return {
        name: section_bytes(payload, next(
            row for row in sections if row["name"] == section_name))
        for name, section_name in names.items()
    }


def _runtime_write(image: bytearray, address: int, payload: bytes) -> None:
    first = PREAMBLE_BYTES + address - RUN_BASE
    last = first + len(payload)
    require(0 <= first <= last <= len(image),
            f"component write escapes at 0x{address:08X}")
    image[first:last] = payload


def _profile_host_bins(config: dict[str, Any], report: dict[str, Any],
                       component: bytes,
                       proposal: dict[str, Any], profile: str
                       ) -> list[dict[str, Any]]:
    """Authenticate the fixed generated-NOP host set for one profile."""
    config_leaves = {row["function"]: row
                     for row in config["relocated_leaves"]}
    report_leaves = {row["extraction"]["function"]: row
                     for row in report["relocated_leaves"]}
    patches: dict[str, list[dict[str, Any]]] = {}
    for patch in report["overlay"]["patched_sites"]:
        target = patch.get("target_function")
        if isinstance(target, str):
            patches.setdefault(target, []).append(patch)
    reservations = []
    providers = report["overlay"]["post_link_providers"]
    ltpf = providers["liblc3_ltpf"]["placement"]
    cave_sections = ltpf.get("sections", ltpf)
    if isinstance(cave_sections.get("text"), dict) and \
            isinstance(cave_sections.get("rodata"), dict):
        for section in ("text", "rodata"):
            row = cave_sections[section]
            reservations.append((int(row["runtime_address"]),
                                 int(row["runtime_address"]) +
                                 int(row["capacity"])))
    else:
        reservations.append((int(ltpf["runtime_address"]),
                             int(ltpf["runtime_address"]) +
                             int(providers["liblc3_ltpf"]["payload"]["size"])))
    pt = providers["pt_protocol"]["placement"]
    reservations.append((int(pt["runtime_start"]), int(pt["runtime_end_exclusive"])))

    names = (proposal["selected_functions"] if profile == "apple-clang" else
             sorted(report_leaves))
    bins = []
    for name in names:
        configured = config_leaves.get(name)
        leaf = report_leaves.get(name)
        target_patches = patches.get(name, [])
        eligible = (configured is not None and leaf is not None and
                    configured.get("strict_relocation_contract") is True and
                    len(target_patches) == 1)
        if not eligible and profile != "apple-clang":
            continue
        require(eligible, f"host function ownership drift: {name}")
        patch = target_patches[0]
        patch_eligible = (patch.get("branch") == "b_w" and
                          isinstance(patch.get("expected_size"), int))
        if not patch_eligible and profile != "apple-clang":
            continue
        require(patch_eligible, f"host function patch geometry drift: {name}")
        entry = int(patch["runtime_address"])
        end = entry + int(patch["expected_size"])
        overlaps_provider = any(entry < right and left < end
                                for left, right in reservations)
        if overlaps_provider and profile != "apple-clang":
            continue
        require(not overlaps_provider,
                f"host function overlaps a protected provider: {name}")
        first = PREAMBLE_BYTES + entry - RUN_BASE
        body = component[first:first + int(patch["expected_size"])]
        guarded = (body.hex() == patch["replacement_hex"] and
                   A.decode_thumb_branch(entry, body[:4], link=False) ==
                   int(leaf["placement"]["runtime_address"]) and
                   body[4:] == b"\x00\xBF" * ((len(body) - 4) // 2))
        if not guarded and profile != "apple-clang":
            continue
        require(guarded, f"host function component guard drift: {name}")
        bins.append({"host_function": name, "entry": entry,
                     "start": entry + 4, "end_exclusive": end,
                     "cursor": entry + 4, "items": []})
    bins.sort(key=lambda row: row["start"])
    return bins


def _suffix_plan(config: dict[str, Any], report: dict[str, Any],
                 component: bytes, proposal: dict[str, Any], profile: str,
                 bins: list[dict[str, Any]]) -> dict[str, Any]:
    """Build and replay the strict Apple suffix; Linux needs no truncation."""
    if profile != "apple-clang":
        return {"suffix": [], "span": 0, "start":
                RUN_BASE + len(component) - PREAMBLE_BYTES,
                "packed": [], "rebased": {}, "relocations": []}
    config_leaves = {row["function"]: row
                     for row in config["relocated_leaves"]}
    required_span = (
        int(report["overlay"]["overlay_end_exclusive"]) - LC3_TABLE_START
    )
    suffix, start, span = S._suffix(report, config_leaves, required_span)
    # The table boundary need not coincide with a function boundary.  Move the
    # complete minimal strict suffix that covers it; _apply_suffix truncates at
    # that suffix boundary and the image extension below leaves any resulting
    # prefix interval erased before writing LC3 at its fixed address.
    require(
        start <= LC3_TABLE_START
        and span == int(report["overlay"]["overlay_end_exclusive"]) - start
        and span >= required_span,
        "Apple suffix no longer covers the admitted LC3 start: "
        f"span={span}, required={required_span}, start=0x{start:08X}",
    )
    forbidden = S._host_forbidden_entries(proposal, component, bins)["forbidden"]
    packed = S.pack_suffix(suffix, bins, forbidden)
    placements = {item["function"]: item["start"]
                  for row in packed for item in row["items"]}
    base = int(report["overlay"]["overlay_runtime_address"])
    old_intervals = sorted((base + row["offset"],
                            base + row["offset"] + row["size"],
                            row["function"]) for row in suffix)
    report_leaves = {row["extraction"]["function"]: row
                     for row in report["relocated_leaves"]}
    rebased: dict[str, bytes] = {}
    relocations = []
    for row in suffix:
        name = row["function"]
        leaf = report_leaves[name]
        old = S.image_slice(component,
                            int(leaf["placement"]["runtime_address"]),
                            int(leaf["placement"]["runtime_address"]) + row["size"],
                            run_base=RUN_BASE, preamble=PREAMBLE_BYTES)
        require(sha256_bytes(old) == leaf["extraction"]["sha256"],
                f"suffix source bytes drift: {name}")
        moved, records = S._rebase_leaf(
            old, leaf, placements[name], placements, old_intervals)
        rebased[name] = moved
        relocations.extend({"function": name, **record} for record in records)
    return {"suffix": suffix, "span": span, "start": start,
            "packed": packed, "rebased": rebased,
            "relocations": relocations}


def _apply_suffix(component: bytes, report: dict[str, Any],
                  plan: dict[str, Any]) -> bytearray:
    image = bytearray(component)
    if not plan["suffix"]:
        return image
    placements = {item["function"]: item["start"]
                  for row in plan["packed"] for item in row["items"]}
    suffix_names = set(placements)
    patches = [row for row in report["overlay"]["patched_sites"]
               if row.get("target_function") in suffix_names]
    patch_names = {row["target_function"] for row in patches}
    pointer_routed = suffix_names - patch_names
    require(pointer_routed in (set(), AT_FS_SUFFIX_NAMES),
            "suffix non-branch ingress set drift")
    require(len(patches) + len(pointer_routed) == len(plan["suffix"]),
            "suffix stock-entry/pointer ingress count drift")
    for patch in patches:
        target = placements[patch["target_function"]]
        replacement = A.encode_thumb_b_w(int(patch["runtime_address"]), target)
        replacement += b"\x00\xBF" * ((int(patch["expected_size"]) - 4) // 2)
        _runtime_write(image, int(patch["runtime_address"]), replacement)
    command_rebases = []
    if pointer_routed:
        require(set(AT_FS_COMMAND_POINTERS) < pointer_routed,
                "eAT filesystem suffix ingress is incomplete")
        for function, pointer_address in AT_FS_COMMAND_POINTERS.items():
            target = placements[function] | 1
            _runtime_write(image, pointer_address, struct.pack("<I", target))
            command_rebases.append({
                "function": function,
                "pointer_address": pointer_address,
                "thumb_target": target,
            })
    plan["command_record_rebases"] = command_rebases
    for row in plan["packed"]:
        for item in row["items"]:
            _runtime_write(image, item["start"],
                           plan["rebased"][item["function"]])
    new_size = len(image) - int(plan["span"])
    require(RUN_BASE + new_size - PREAMBLE_BYTES == plan["start"],
            "suffix truncation endpoint drift")
    return image[:new_size]


def _layout_for_profile(route: dict[str, Any]) -> list[dict[str, Any]]:
    cursor = LC3_TABLE_START
    result = []
    for name, alignment in (("table_rodata", 8), ("rodata", 16),
                            ("text", 16)):
        start = S.align_up(cursor, alignment)
        size = int(route["sections"][name]["size"])
        result.append({"name": name, "start": start,
                       "end_exclusive": start + size, "size": size,
                       "alignment": alignment,
                       "padding_before": start - cursor})
        cursor = start + size
    require(cursor <= LC3_IMAGE_END,
            "profile LC3 closure exceeds the admitted common image end")
    return result


def route_component(*, manifest_path: Path = MANIFEST,
                    base_component: Path, core_config: dict[str, Any],
                    core_report: dict[str, Any], output_dir: Path,
                    profile: str) -> dict[str, Any]:
    """Atomically emit the production-routed pre-CFF Apollo component."""
    manifest = read_json(manifest_path)
    require(profile in manifest["profiles"], f"unknown profile: {profile}")
    component = base_component.read_bytes()
    require(RUN_BASE + len(component) - PREAMBLE_BYTES ==
            int(core_report["overlay"]["overlay_end_exclusive"]),
            "same-build pre-CFF component/report endpoint drift")
    require(component[:4] and (struct.unpack_from("<I", component, 0)[0] &
                               0x00FFFFFF) == len(component),
            "base component length header drift")
    proposal = read_json(resolve(read_json(authenticate(
        manifest["evidence"]["suffix_pack"]))["evidence"]
        ["capacity_rebalancing_proposal"]["path"]))

    output_dir.mkdir(parents=True, exist_ok=False)
    obj, items = _compile_runtime(manifest, profile, output_dir)
    bins = _profile_host_bins(core_config, core_report, component, proposal,
                              profile)
    suffix = _suffix_plan(core_config, core_report, component, proposal,
                          profile, bins)
    forbidden = S._host_forbidden_entries(proposal, component, bins)["forbidden"]
    suffix_cursors = {row["entry"]: row["cursor"] for row in suffix["packed"]}
    available = [{**row, "cursor": suffix_cursors.get(row["entry"], row["start"]),
                  "items": []} for row in bins]
    runtime_packed = S.pack_suffix(items, available, forbidden)
    runtime_placements = {item["function"]: item["start"]
                          for row in runtime_packed for item in row["items"]}
    require(set(runtime_placements) == set(ALL_RUNTIME_SECTIONS),
            "target runtime placement is incomplete")
    bindings, runtime = _link_runtime(
        manifest, profile, obj, runtime_packed, runtime_placements, output_dir)

    capacity_manifest = read_json(authenticate(
        manifest["evidence"]["capacity_experiment"]))
    tools = manifest["profiles"][profile]["tools"]
    route_probe = R.build(
        config_path=resolve(capacity_manifest["route_config"]["path"]),
        output_dir=output_dir / "layout-probe", profile=profile,
        clang=tools["clang"], lld=tools["lld"], objcopy=tools["objcopy"],
        record=True, compiler_overrides=("-Oz",),
        additional_source_records=(S.B._helper_record(capacity_manifest),),
        table_reference_contract=S.B.TABLE_REFERENCE_CONTRACT)
    layout = _layout_for_profile(route_probe)
    final = _finalize_lc3(manifest, profile, None, bindings, core_report,
                          output_dir, layout_rows_override=layout)

    image = _apply_suffix(component, core_report, suffix)
    if len(image) < PREAMBLE_BYTES + LC3_IMAGE_END - RUN_BASE:
        image.extend(b"\xFF" * (PREAMBLE_BYTES + LC3_IMAGE_END - RUN_BASE -
                                len(image)))
    for name, payload in _runtime_section_payloads(output_dir).items():
        _runtime_write(image, runtime_placements[name], payload)
    for name, payload in _lc3_section_payloads(output_dir).items():
        row = next(item for item in layout if item["name"] == name)
        _runtime_write(image, int(row["start"]), payload)
    entry_guards = []
    for veneer in final["service_audio_veneers"]:
        entry = int(veneer["entry"])
        offset = PREAMBLE_BYTES + entry - RUN_BASE
        before = bytes(image[offset:offset + 4])
        replacement = bytes.fromhex(veneer["encoding_hex"])
        require(len(before) == len(replacement) == 4,
                "service_audio veneer width drift")
        image[offset:offset + 4] = replacement
        entry_guards.append({"root": veneer["root"], "entry": entry,
                             "expected_hex": before.hex(),
                             "replacement_hex": replacement.hex(),
                             "target": veneer["target"]})
    struct.pack_into("<I", image, 0, 0x04000000 | len(image))
    struct.pack_into("<I", image, 4, 0)
    nested_crc = zlib.crc32(image[8:]) & 0xFFFFFFFF
    struct.pack_into("<I", image, 4, nested_crc)
    open_cfw = _load(G2 / "tools/open_cfw.py",
                     f"open_cfw_liblc3_route_{profile.replace('-', '_')}")
    open_cfw.validate_apollo_main(bytes(image))

    used = {row["entry"]: row["cursor"] for row in suffix["packed"]}
    used.update({row["entry"]: row["cursor"] for row in runtime_packed})
    residual_slots = [{**row, "start": used.get(row["entry"], row["start"]),
                       "cursor": used.get(row["entry"], row["start"]),
                       "forbidden_entries": sorted(
                           value for value in forbidden
                           if used.get(row["entry"], row["start"]) <= value <
                           row["end_exclusive"]),
                       "items": []}
                      for row in bins
                      if used.get(row["entry"], row["start"]) <
                      row["end_exclusive"]]
    routed = bytes(image)
    artifact = output_dir / "ota_s200_firmware_ota.bin"
    artifact.write_bytes(routed)
    report = {
        "schema_version": 2, "profile": profile,
        "status": "g2-liblc3-service-audio-component-routed",
        "component": {"size": len(routed), "sha256": sha256_bytes(routed),
                      "runtime_end_exclusive": LC3_IMAGE_END,
                      "nested_crc32": f"0x{nested_crc:08X}"},
        "suffix": {"count": len(suffix["suffix"]),
                   "span": suffix["span"], "start": suffix["start"],
                   "payload_bytes": sum(int(row["size"])
                                        for row in suffix["suffix"]),
                   "internal_padding_bytes": int(suffix["span"]) -
                       sum(int(row["size"]) for row in suffix["suffix"]),
                   "relocation_count": len(suffix["relocations"]),
                   "relocation_records_sha256":
                       canonical_sha256(suffix["relocations"]),
                   "command_record_rebases":
                       suffix.get("command_record_rebases", [])},
        "target_runtime": runtime,
        "lc3_finalization": final,
        "service_audio_entry_guards": entry_guards,
        "residual_host_slots": residual_slots,
        "routing": {"production_placement": True,
                    "service_audio_routed": True,
                    "firmware_image_emitted": True,
                    "hardware_operations": False},
        "hardware": {"validation": "blocked by unavailable physical evidence",
                     "qualification_complete": False},
    }
    (output_dir / "component-route-report.json").write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return report


def build(*, manifest_path: Path = MANIFEST, output_dir: Path,
          profile: str, record: bool = False) -> dict[str, Any]:
    manifest = read_json(manifest_path)
    require((manifest.get("schema_version"), manifest.get("mode")) ==
            (2, "production-routed-canonical-image-verified"),
            "production replay schema drift")
    require(manifest["routing"] == {
        "production_placement": True, "service_audio_routed": True,
        "firmware_image_emitted": True, "hardware_operations": False},
        "production replay routing authority drift")
    require(set(SCRIPT_SOURCE_NAMES).issubset(manifest.get("sources", {})),
            "production replay script pins are incomplete")
    for name in SCRIPT_SOURCE_NAMES:
        authenticate(manifest["sources"][name])
    canonical = manifest.get("canonical_profiles", {}).get(profile)
    require(isinstance(canonical, dict),
            f"{profile}: canonical routed evidence is missing")
    core_report_path = authenticate(canonical["core_report"])
    component_path = authenticate(canonical["component"])
    core_report = read_json(core_report_path)
    require(core_report.get("canonical_observation", {}).get("profile") == profile,
            f"{profile}: canonical observation profile drift")
    stage = core_report.get("canonical_stages", {}).get(
        "liblc3_service_audio")
    require(isinstance(stage, dict),
            f"{profile}: canonical LC3 service stage is missing")
    require(stage.get("routing") == manifest["routing"] and
            stage.get("hardware") == {
                "validation": "blocked by unavailable physical evidence",
                "qualification_complete": False,
            }, f"{profile}: canonical LC3 route boundary drift")
    component = component_path.read_bytes()
    require((len(component), sha256_bytes(component)) ==
            (stage["component"]["size"], stage["component"]["sha256"]),
            f"{profile}: routed component/stage receipt drift")
    require((struct.unpack_from("<I", component, 0)[0] & 0x00FFFFFF) ==
            len(component) and
            struct.unpack_from("<I", component, 4)[0] ==
            (zlib.crc32(component[8:]) & 0xFFFFFFFF),
            f"{profile}: routed component integrity drift")

    output_dir.mkdir(parents=True, exist_ok=False)
    obj, items = _compile_runtime(manifest, profile, output_dir)
    expected_runtime = stage["target_runtime"]
    placements = {row["function"]: int(row["address"])
                  for row in expected_runtime["sections"]}
    require({row["function"] for row in items} == set(placements),
            f"{profile}: canonical runtime function set drift")
    packed = [{"entry": address, "start": address,
               "end_exclusive": address + next(
                   row["size"] for row in items
                   if row["function"] == function),
               "cursor": address + next(
                   row["size"] for row in items
                   if row["function"] == function),
               "items": [{"function": function, "start": address,
                           "size": next(row["size"] for row in items
                                        if row["function"] == function)}]}
              for function, address in sorted(placements.items(),
                                               key=lambda row: row[1])]
    bindings, runtime = _link_runtime(
        manifest, profile, obj, packed, placements, output_dir)
    final = _finalize_lc3(
        manifest, profile, None, bindings, core_report, output_dir,
        layout_rows_override=stage["lc3_finalization"]["layout"])
    for key in ("object", "final_elf", "sections", "total_text_bytes",
                "undefined_symbols", "output_relocations"):
        require(runtime[key] == expected_runtime[key],
                f"{profile}: rebuilt target runtime {key} drift")
    runtime["placement_sha256"] = expected_runtime["placement_sha256"]
    require(final == stage["lc3_finalization"],
            f"{profile}: rebuilt LC3 finalization drift")
    for guard in stage["service_audio_entry_guards"]:
        offset = PREAMBLE_BYTES + int(guard["entry"]) - RUN_BASE
        replacement = bytes.fromhex(guard["replacement_hex"])
        require(component[offset:offset + len(replacement)] == replacement,
                f"{profile}: routed service entry guard drift")
    report = {
        "schema_version": 2, "profile": profile,
        "status": "production-routed-canonical-image-verified",
        "target_runtime": runtime, "lc3_finalization": final,
        "suffix": stage["suffix"],
        "service_audio_entry_guards": stage["service_audio_entry_guards"],
        "component": stage["component"],
        "routing": manifest["routing"],
        "hardware": stage["hardware"],
        "remaining_software_blockers": [],
    }
    expected = manifest["profiles"][profile].get("expected_report_sha256")
    if not record:
        require(canonical_sha256(report) == expected,
                f"{profile}: production replay receipt drift")
    (output_dir / "ota_s200_firmware_ota.bin").write_bytes(component)
    temporary = output_dir / ".build-report.json.tmp"
    temporary.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n",
                         encoding="utf-8")
    os.replace(temporary, output_dir / "build-report.json")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "build-production-replay")
    parser.add_argument("--profile", choices=("apple-clang", "linux-clang"),
                        default="apple-clang")
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    try:
        report = build(manifest_path=args.manifest.resolve(),
                       output_dir=args.output_dir.resolve(),
                       profile=args.profile, record=args.record)
    except (ReplayError, S.SuffixPackError, R.BuildError, OSError, KeyError,
            TypeError, ValueError) as error:
        print(f"production replay failed: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
