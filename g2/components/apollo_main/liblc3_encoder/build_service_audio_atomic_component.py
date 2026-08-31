#!/usr/bin/env python3
"""Atomically apply the joint CFF/LC3 service-audio component layout.

The input is one authenticated Apple-profile Apollo-main component after the
FreeType CFF scatter provider.  The output remains a component payload (not an
EVENOTA package): this stage packs the strict source-owned suffix, adds the
LC3-owned scalar runtime, scatter-links three whole LC3 functions around the
CFF tail, applies both service-audio veneers, and repairs the nested component
size/CRC header.  It never flashes hardware.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import struct
import sys
import tempfile
import zlib
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
G2 = ROOT.parents[2]
MANIFEST = ROOT / "service_audio_atomic_component.json"
PRODUCTION_BUILDER = ROOT / "build_service_audio_production_replay.py"
OPEN_CFW = G2 / "tools/open_cfw.py"

RUN_BASE = 0x00438000
PREAMBLE = 32
UPDATE_START = 0x007FE000
TABLE_START = 0x007EA620
RODATA_START = 0x007EA7C0
TEXT_START = 0x007F9400
CFF_TAIL_START = 0x007FCEC0
CFF_END = 0x007FDED4
SCATTER_NAMES = (
    ".text.lc3_sns_analyze",
    ".text.lc3_tns_analyze",
    ".text.fft",
)
TABLE_INPUTS = (
    ".data.lc3_band_lim",
    ".data.lc3_fft_twiddles_bf2",
    ".data.lc3_fft_twiddles_bf3",
    ".data.lc3_mdct_rot",
    ".data.lc3_mdct_win",
)
ROOTS = (
    "open_cfw_liblc3_service_audio_stock_encode",
    "open_cfw_liblc3_service_audio_stock_setup",
)


class AtomicComponentError(RuntimeError):
    """Raised when any address, source, relocation, or mutation drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AtomicComponentError(message)


def _load(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    require(specification is not None and specification.loader is not None,
            f"cannot load {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


P = _load(PRODUCTION_BUILDER, "open_cfw_liblc3_atomic_production")
S = P.S
R = P.R
A = P.A
X = P.X
O = _load(OPEN_CFW, "open_cfw_liblc3_atomic_open_cfw")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(json.dumps(
        value, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"{path}: expected object")
    return value


def resolve(relative: str) -> Path:
    path = (G2 / relative).resolve()
    try:
        path.relative_to(G2.resolve())
    except ValueError as error:
        raise AtomicComponentError(f"path escapes G2 root: {relative}") from error
    return path


def authenticate(record: dict[str, Any]) -> tuple[Path, bytes]:
    path = resolve(record["path"])
    payload = path.read_bytes()
    require(len(payload) == record["size"] and
            sha256_bytes(payload) == record["sha256"],
            f"source pin drift: {path}")
    return path, payload


def image_offset(address: int) -> int:
    require(RUN_BASE <= address < UPDATE_START,
            f"address outside application: 0x{address:08X}")
    return PREAMBLE + address - RUN_BASE


def image_slice(component: bytes, start: int, end: int) -> bytes:
    first, last = image_offset(start), image_offset(end)
    require(0 <= first <= last <= len(component),
            f"component interval unavailable: 0x{start:08X}..0x{end:08X}")
    return component[first:last]


def image_write(component: bytearray, start: int, payload: bytes) -> None:
    first = image_offset(start)
    last = first + len(payload)
    require(0 <= first <= last <= len(component),
            f"component write escapes at 0x{start:08X}")
    component[first:last] = payload


def _intervals_disjoint(rows: list[tuple[int, int, str]]) -> None:
    ordered = sorted(rows)
    require(all(left[1] <= right[0]
                for left, right in zip(ordered, ordered[1:])),
            "joint output intervals overlap")


def _scatter_ingress(component: bytes, placements: dict[str, int],
                     text_inputs: dict[str, Any],
                     expected: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for name, start in sorted(placements.items()):
        end = start + int(text_inputs[name]["size"])
        branch_targets: set[int] = set()
        byte_targets: set[int] = set()
        aligned_targets: set[int] = set()
        for offset in range(PREAMBLE, len(component) - 3, 2):
            site = RUN_BASE + offset - PREAMBLE
            try:
                target = A.decode_thumb_branch(
                    site, component[offset:offset + 4])
            except R.BuildError:
                continue
            if start <= target < end:
                branch_targets.add(target)
        for offset in range(PREAMBLE, len(component) - 3):
            target = struct.unpack_from("<I", component, offset)[0] & ~1
            if start <= target < end:
                byte_targets.add(target)
                if (RUN_BASE + offset - PREAMBLE) % 4 == 0:
                    aligned_targets.add(target)
        require(start not in branch_targets | byte_targets,
                f"scatter entry has preexisting ingress: {name}")
        require(not branch_targets and not aligned_targets,
                f"scatter range has executable/aligned-pointer ingress: {name}")
        rows.append({
            "section": name, "start": start, "end_exclusive": end,
            "branch_target_count": len(branch_targets),
            "byte_window_pointer_target_count": len(byte_targets),
            "aligned_word_pointer_target_count": len(aligned_targets),
            "byte_window_only_classification":
                "unaligned-sliding-window-false-positive"
                if byte_targets else "none",
        })
    require(rows == expected, "scatter ingress receipt drift")
    return {"ranges": rows, "records_sha256": canonical_sha256(rows),
            "all_entries_unreferenced": True,
            "all_branch_target_counts_zero": True,
            "all_aligned_word_pointer_target_counts_zero": True}


def _cff_intervals(report: dict[str, Any]) -> list[tuple[int, int, str]]:
    provider = report["overlay"]["post_link_providers"]["freetype_cff"]
    sections = provider["placement"]["sections"]
    expected_names = {
        ".cff_stock_rodata", ".cff_stock_text", ".cff_tail_text",
        ".cff_tail_exidx",
    }
    require({row["name"] for row in sections} == expected_names,
            "CFF section ownership drift")
    rows = [(int(row["start"]), int(row["end_exclusive"]),
             f"freetype_cff:{row['name']}") for row in sections]
    patch = provider["module_class_patch"]
    pointer = int(patch["runtime_address"], 0)
    require(pointer == 0x0073EF00 and
            patch["applied_after_all_preflight_checks"] is True and
            patch["compare_before_write"] is True,
            "CFF module-class ownership drift")
    rows.append((pointer, pointer + 4, "freetype_cff:module_class_pointer"))
    require(provider["placement"]["runtime_end_exclusive"] ==
            f"0x{CFF_END:08X}", "CFF runtime extent drift")
    _intervals_disjoint(rows)
    return rows


def _core_context(manifest: dict[str, Any], component: bytes, profile: str):
    proposal_path, _ = authenticate(manifest["evidence"]["capacity_proposal"])
    proposal = read_json(proposal_path)
    evidence = proposal["evidence"]
    config_path, _ = authenticate(evidence["core_config"])
    core = manifest["profiles"][profile]["core"]
    report_path, _ = authenticate(core["report"])
    _overlay_path, overlay = authenticate(core["overlay"])
    config, report = read_json(config_path), read_json(report_path)
    address = proposal["address_model"]
    require((address["run_base"], address["preamble_bytes"],
             address["protected_update_start"]) ==
            (RUN_BASE, PREAMBLE, UPDATE_START), "core address model drift")
    live = report["overlay"]
    require(live["sha256"] == sha256_bytes(overlay) and
            live["overlay_end_exclusive"] == core["overlay_end_exclusive"],
            "core overlay receipt drift")
    offset = int(live["overlay_payload_offset"])
    require(component[offset:offset + len(overlay)] == overlay,
            "CFF input does not contain the authenticated core overlay")
    cff_intervals = _cff_intervals(report)
    if profile == "apple-clang":
        require(live["overlay_end_exclusive"] ==
                address["current_core_end_exclusive"],
                "Apple capacity proposal core-end drift")
        protected = S.C._protected_receipts(proposal, report)
        candidates, config_leaves, _ = S.C._derive_candidates(
            proposal, config, report, component, protected)
        suffix, suffix_start, suffix_span = S._suffix(
            report, config_leaves,
            manifest["joint_layout"]["minimum_suffix_span"])
        require((suffix_start, suffix_span, len(suffix)) ==
                (TABLE_START, 9252, 84), "strict suffix geometry drift")
        bins = S._host_bins(proposal, candidates, component)
        forbidden = S._host_forbidden_entries(proposal, component, bins)
        suffix_packed = S.pack_suffix(suffix, bins, forbidden["forbidden"])
        suffix_placements = {
            item["function"]: item["start"]
            for row in suffix_packed for item in row["items"]
        }
        require(len(suffix_placements) == 84,
                "strict suffix pack incomplete")
        ingress = S._ingress(proposal, report, component, suffix)
    else:
        # The Linux core is substantially smaller and has no authenticated
        # need for the Apple-only suffix reclaim. Preserve it byte-for-byte.
        protected, suffix, bins, suffix_packed = [], [], [], []
        suffix_placements = {}
        forbidden = {"forbidden": frozenset(), "branch_target_count": 0,
                     "byte_window_pointer_target_count": 0,
                     "aligned_word_pointer_target_count": 0}
        ingress = {"exact_entry_branch_count": 0,
                   "stock_entry_redirect_count": 0,
                   "suffix_internal_branch_count": 0,
                   "raw_pointer_count": 0,
                   "records_sha256": canonical_sha256([])}
    return (proposal, report, component, protected, suffix, bins, forbidden,
            suffix_packed, suffix_placements, ingress, cff_intervals)


def _rebase_suffix(proposal: dict[str, Any], report: dict[str, Any],
                   component: bytes, suffix: list[dict[str, Any]],
                   placements: dict[str, int], profile: str) -> tuple[
                       dict[str, bytes], list[dict[str, Any]]]:
    base = report["overlay"]["overlay_runtime_address"]
    intervals = sorted((base + row["offset"],
                        base + row["offset"] + row["size"], row["function"])
                       for row in suffix)
    leaves = {row["extraction"]["function"]: row
              for row in report["relocated_leaves"]}
    rebased, records = {}, []
    for row in suffix:
        name = row["function"]
        leaf = leaves[name]
        old = image_slice(component,
                          leaf["placement"]["runtime_address"],
                          leaf["placement"]["runtime_address"] + row["size"])
        require(sha256_bytes(old) == leaf["extraction"]["sha256"],
                f"strict suffix source drift: {name}")
        moved, replay = S._rebase_leaf(
            old, leaf, placements[name], placements, intervals)
        rebased[name] = moved
        records.extend({"function": name, **item} for item in replay)
    require(len(records) == (288 if profile == "apple-clang" else 0),
            "strict suffix relocation replay drift")
    return rebased, records


def _compile_unique(manifest: dict[str, Any], profile: str,
                    directory: Path) -> tuple[Path, dict[str, Any]]:
    production_path, _ = authenticate(manifest["evidence"]["production_replay"])
    production = read_json(production_path)
    capacity_path, _ = authenticate(production["evidence"]["capacity_experiment"])
    capacity = read_json(capacity_path)
    route_config_path = resolve(capacity["route_config"]["path"])
    require(sha256_bytes(route_config_path.read_bytes()) ==
            capacity["route_config"]["sha256"], "route config pin drift")
    route = read_json(route_config_path)
    admission_path = resolve(route["encoder_admission"]["path"])
    require(sha256_bytes(admission_path.read_bytes()) ==
            route["encoder_admission"]["sha256"], "encoder admission drift")
    admission = read_json(admission_path)
    tools = production["profiles"][profile]["tools"]
    clang, lld, objcopy = tools["clang"], tools["lld"], tools["objcopy"]
    builtin = R.B.compiler_builtin_include_dir(clang)
    flags = [*R.B.hermetic_compiler_arguments(builtin),
             *admission["target_profile"], "-DLC3_PLUS_HR=0", "-Oz"]
    prefix = [clang, *flags]
    for include in (
            "components/shared/liblc3/target_compat",
            "third_party/liblc3/include", "third_party/liblc3/src",
            "components/shared/liblc3"):
        prefix.extend(("-I", include))
    sources = R.B._source_records(admission)
    for name in ("adapter", "shim"):
        reference = route["sources"][name]
        sources.append({"name": name, "path": reference["path"],
                        "sha256": reference["sha256"], "license": "MIT"})
    sources.append(S.B._helper_record(capacity))
    objects, object_records = [], []
    for source in sources:
        source_path = resolve(source["path"])
        require(sha256_bytes(source_path.read_bytes()) == source["sha256"],
                f"source hash drift: {source['name']}")
        output = directory / f"{source['name']}.o"
        R.B._run([*prefix, "-c", source["path"], "-o", str(output)])
        cantunwind_rows = R.B._validate_cantunwind(output)
        objects.append(output)
        object_records.append({"name": output.name,
                               "size": output.stat().st_size,
                               "sha256": P.sha256_bytes(output.read_bytes()),
                               "canonical_cantunwind_rows": cantunwind_rows})
    unique = directory / "service-audio.unique.o"
    R.B._run([
        lld, "-m", "armelf", "-r", "--unique", "--gc-sections",
        "--build-id=none", f"--entry={ROOTS[0]}",
        *(f"--undefined={root}" for root in ROOTS),
        "-o", str(unique), *(str(path) for path in objects),
    ])
    readonly = directory / "service-audio.unique-readonly.o"
    R.B._run([
        objcopy,
        "--remove-section=.ARM.exidx*",
        "--remove-section=.rel.ARM.exidx*",
        *(value for section in TABLE_INPUTS for value in (
            "--set-section-flags",
            f"{section}=alloc,load,readonly,data,contents")),
        str(unique), str(readonly),
    ])
    payload, sections = A.parse_elf32(readonly)
    require(not any(section["name"].startswith(".ARM.exidx") or
                    section["name"].startswith(".rel.ARM.exidx")
                    for section in sections),
            "admitted cantunwind sections survived finalization")
    symbols = A.parse_elf32_symbols(payload, sections)
    undefined = sorted(symbol["name"] for symbol in symbols
                       if int(symbol["section_index"]) == 0 and symbol["name"])
    require(set(undefined) == set(P.PUBLIC_RUNTIME) | {"sqrtf"},
        "unique link runtime import drift")
    text = {section["name"]: {
                "size": int(section["size"]),
                "alignment": int(section["alignment"])}
            for section in sections
            if (section["name"] == ".text" or
                section["name"].startswith(".text.")) and
            int(section["size"])}
    require(set(SCATTER_NAMES) <= set(text), "scatter input section disappeared")
    raw_records = X.relocation_records(payload, sections, symbols)
    table_offsets = {f".data.{name}": offset
                     for name, (offset, _size) in X.TABLE_SYMBOLS.items()}
    normalized = []
    for row in raw_records:
        record = dict(row)
        if record["section"].startswith(".text."):
            record["section"] = ".text"
        elif record["section"].startswith(".rodata"):
            record["section"] = ".rodata"
        elif record["section"] in table_offsets:
            record["offset"] += table_offsets[record["section"]]
            record["section"] = X.TABLE_SECTION
        if record["symbol_section"].startswith(".text."):
            record["symbol_section"] = ".text"
        elif record["symbol_section"].startswith(".rodata"):
            record["symbol_section"] = ".rodata"
        elif record["symbol_section"] in table_offsets:
            record["symbol_section"] = X.TABLE_SECTION
        normalized.append(record)
    relocation_report = X.validate_relocation_closure(
        normalized, set(undefined), S.B.TABLE_REFERENCE_CONTRACT)
    expected_total = 485 if profile == "apple-clang" else 486
    require(relocation_report["total"] == expected_total,
            f"{profile}: unique relocation total drift")
    cantunwind_rows = sum(row["canonical_cantunwind_rows"]
                          for row in object_records)
    require(cantunwind_rows == manifest["profiles"][profile]
            ["expected_layout"]["canonical_cantunwind_rows"],
            f"{profile}: admitted cantunwind row count drift")
    return readonly, {
        "objects": object_records,
        "canonical_cantunwind_rows_discarded": cantunwind_rows,
        "retained_unwind_sections": 0,
        "unique_object": {"size": len(payload),
                          "sha256": sha256_bytes(payload)},
        "text_inputs": text,
        "imports": undefined,
        "relocations": relocation_report,
        "table_initializer_offsets": relocation_report["table_initializers"]
            ["offsets"],
        "tools": tools,
    }


def _runtime_and_scatter_placements(
        manifest: dict[str, Any], profile: str, directory: Path,
        bins: list[dict[str, Any]], forbidden: dict[str, Any],
        suffix_packed: list[dict[str, Any]], text_inputs: dict[str, Any],
        core_report: dict[str, Any]):
    production = read_json(authenticate(
        manifest["evidence"]["production_replay"])[0])
    runtime_object, runtime_items = P._compile_runtime(
        production, profile, directory)
    if profile == "apple-clang":
        cursors = {row["entry"]: row["cursor"] for row in suffix_packed}
        available = [
            {**row, "cursor": cursors.get(row["entry"], row["start"]),
             "items": []} for row in bins]
        runtime_packed = S.pack_suffix(
            runtime_items, available, forbidden["forbidden"])
        cursors.update({row["entry"]: row["cursor"]
                        for row in runtime_packed})
        scatter_items = [{"function": name, **text_inputs[name]}
                         for name in SCATTER_NAMES]
        available = [
            {**row, "cursor": cursors.get(row["entry"], row["start"]),
             "items": []} for row in bins]
        scatter_packed = S.pack_suffix(
            scatter_items, available, forbidden["forbidden"])
    else:
        cursor = int(core_report["overlay"]["overlay_end_exclusive"])
        items = []
        for item in runtime_items:
            start = S.align_up(cursor, item["alignment"])
            items.append({**item, "start": start,
                          "padding_before": start - cursor})
            cursor = start + item["size"]
        runtime_packed = [{
            "host_function": "linux_source_owned_append",
            "entry": int(core_report["overlay"]["overlay_end_exclusive"]),
            "start": int(core_report["overlay"]["overlay_end_exclusive"]),
            "end_exclusive": cursor,
            "cursor": cursor,
            "items": items,
        }]
        scatter_packed = []
    runtime_placements = {item["function"]: item["start"]
                          for row in runtime_packed for item in row["items"]}
    scatter_placements = {item["function"]: item["start"]
                          for row in scatter_packed for item in row["items"]}
    require(set(runtime_placements) == set(P.ALL_RUNTIME_SECTIONS) and
            set(scatter_placements) ==
            (set(SCATTER_NAMES) if profile == "apple-clang" else set()),
            "runtime/scatter placement incomplete")
    bindings, runtime_report = P._link_runtime(
        production, profile, runtime_object, runtime_packed,
        runtime_placements, directory)
    runtime_end = max(address + next(item["size"] for item in runtime_items
                                    if item["function"] == name)
                      for name, address in runtime_placements.items())
    if profile == "apple-clang":
        layout = {"table": TABLE_START, "rodata": RODATA_START,
                  "text": TEXT_START}
    else:
        table = S.align_up(runtime_end, X.TABLE_ALIGNMENT)
        rodata = S.align_up(table + X.TABLE_BYTES, 16)
        text = rodata + 60480
        layout = {"table": table, "rodata": rodata, "text": text}
    return (production, bindings, runtime_report, runtime_packed,
            scatter_packed, scatter_placements, layout)


def _joint_link(profile: str, unique: Path, compile_report: dict[str, Any],
                bindings: dict[str, int], scatter: dict[str, int],
                core_report: dict[str, Any], layout: dict[str, int],
                cff_intervals: list[tuple[int, int, str]],
                expected_layout: dict[str, int], directory: Path):
    sqrt_leaf = next(row for row in core_report["relocated_leaves"]
                     if row["extraction"]["function"] ==
                     "open_cfw_iar_sqrtf")
    require(sqrt_leaf["source"]["path"] ==
            "components/apollo_main/core_overlay/candidates/iar_runtime_math_errno.S",
            "sqrtf ownership drift")
    bindings = {**bindings, "sqrtf":
                int(sqrt_leaf["placement"]["runtime_address"]) | 1}
    require(set(bindings) == set(compile_report["imports"]),
            "joint link binding set drift")
    scatter_names = tuple(name for name in SCATTER_NAMES if name in scatter)
    require(set(scatter_names) == set(scatter),
            "joint scatter section set drift")
    script = directory / "service-audio-joint.ld"
    script.write_text(
        "SECTIONS\n{\n"
        f"  {X.TABLE_SECTION} 0x{layout['table']:08X} : ALIGN(8) {{ " +
        " ".join(f"*({name})" for name in TABLE_INPUTS) + " }\n"
        f"  .rodata 0x{layout['rodata']:08X} : ALIGN(16) "
        "{ *(SORT_BY_NAME(.rodata*)) }\n" +
        "".join(
            f"  .lc3_scatter_{index} 0x{scatter[name]:08X} : "
            f"{{ *({name}) }}\n"
            for index, name in enumerate(scatter_names)) +
        f"  .text 0x{layout['text']:08X} : ALIGN(16) "
        "{ *(SORT_BY_NAME(.text.*)) }\n"
        f"  ASSERT(ADDR(.text) + SIZEOF(.text) <= 0x{CFF_TAIL_START:08X}, "
        '"LC3 text overlaps CFF tail")\n'
        f"  ASSERT(SIZEOF({X.TABLE_SECTION}) == {X.TABLE_BYTES}, "
        '"LC3 table size")\n'
        "  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) "
        "*(.note*) *(.ARM.attributes*) }\n}\n",
        encoding="utf-8")
    final = directory / "service-audio-joint.elf"
    lld = compile_report["tools"]["lld"]
    P.run([
        lld, "-m", "armelf", "--gc-sections", "--build-id=none",
        *(f"--undefined={root}" for root in ROOTS),
        *(f"--defsym={name}=0x{address:08X}"
          for name, address in sorted(bindings.items())),
        "-T", str(script), "-o", str(final), str(unique),
    ])
    payload, sections = A.parse_elf32(final)
    symbols = A.parse_elf32_symbols(payload, sections)
    require(not any(int(row["type"]) == 9 and int(row["size"])
                    for row in sections), "joint ELF retained relocations")
    require(not any(int(symbol["section_index"]) == 0 and symbol["name"]
                    for symbol in symbols), "joint ELF retained imports")
    section_names = [X.TABLE_SECTION, ".rodata",
                     *(f".lc3_scatter_{index}"
                       for index in range(len(scatter_names))), ".text"]
    artifacts, intervals = {}, []
    for name in section_names:
        section = next(row for row in sections if row["name"] == name)
        body = P.section_bytes(payload, section)
        require(not int(section["flags"]) & 1,
                f"joint section unexpectedly writable: {name}")
        artifacts[name] = {"address": int(section["address"]),
                           "size": len(body), "sha256": sha256_bytes(body)}
        intervals.append((int(section["address"]),
                          int(section["address"]) + len(body), name))
    input_text = sum(row["size"] for name, row in
                     compile_report["text_inputs"].items()
                     if name not in scatter)
    require(artifacts[X.TABLE_SECTION]["address"] == layout["table"] and
            artifacts[X.TABLE_SECTION]["size"] == X.TABLE_BYTES and
            artifacts[".rodata"]["address"] == layout["rodata"] and
            artifacts[".rodata"]["size"] == 60480 and
            artifacts[".text"]["address"] == layout["text"] and
            artifacts[".text"]["size"] ==
            expected_layout["main_text_bytes"] and
            artifacts[".text"]["address"] + artifacts[".text"]["size"] <=
            CFF_TAIL_START,
            "joint section geometry drift: " + json.dumps({
                "layout": layout, "artifacts": artifacts,
                "expected_text": expected_layout["main_text_bytes"]},
                sort_keys=True))
    require(artifacts[".text"]["size"] >= input_text,
            "joint text is smaller than its admitted input sections")
    all_intervals = [*intervals, *cff_intervals]
    _intervals_disjoint(all_intervals)
    table_source = b"".join(P.section_bytes(
        A.parse_elf32(unique)[0], next(row for row in A.parse_elf32(unique)[1]
                                     if row["name"] == name))
                            for name in TABLE_INPUTS)
    final_table = P.section_bytes(payload, next(
        row for row in sections if row["name"] == X.TABLE_SECTION))
    # The unique-object closure already authenticates all 78 initializer
    # offsets; exact final bytes are additionally pinned in the report.
    require(len(table_source) == len(final_table) == X.TABLE_BYTES,
            "joint table template geometry drift")
    initializer_offsets = set(compile_report["table_initializer_offsets"])
    require(len(initializer_offsets) == 78, "table initializer offset drift")
    for offset in range(0, X.TABLE_BYTES, 4):
        before = struct.unpack_from("<I", table_source, offset)[0]
        after = struct.unpack_from("<I", final_table, offset)[0]
        if offset in initializer_offsets:
            require(layout["rodata"] <= after < layout["rodata"] + 60480 and
                    after % 2 == 0,
                    "final table initializer escaped read-only data")
        else:
            require(before == after == 0,
                    "unrelocated table word changed or gained a pointer")
    roots = {}
    for name in ROOTS:
        symbol = next(row for row in symbols if row["name"] == name)
        require(int(symbol["type"]) == 2 and int(symbol["binding"]) == 1,
                f"joint root symbol drift: {name}")
        roots[name] = {"address": int(symbol["value"]) & ~1,
                       "size": int(symbol["size"])}
    veneers = []
    for root, entry in ((ROOTS[0], 0x0057A940),
                        (ROOTS[1], 0x0057A926)):
        encoded = A.encode_thumb_b_w(entry, roots[root]["address"])
        require(A.decode_thumb_branch(entry, encoded, link=False) ==
                roots[root]["address"], "service veneer reach drift")
        veneers.append({"root": root, "entry": entry,
                        "target": roots[root]["address"],
                        "encoding_hex": encoded.hex()})
    return final, payload, sections, {
        "final_elf": {"size": len(payload), "sha256": sha256_bytes(payload)},
        "artifacts": artifacts, "intervals": intervals,
        "runtime_bindings": dict(sorted(bindings.items())),
        "input_relocations": compile_report["relocations"]["total"],
        "output_relocations": 0, "undefined_symbols": [],
        "all_input_relocations_applied": True,
        "table_initializers": 78, "table_code_references": 6,
        "input_text_bytes": input_text,
        "linker_padding_and_thunk_bytes":
            artifacts[".text"]["size"] - input_text,
        "roots": roots, "service_audio_veneers": veneers,
    }


def _section_body(elf_payload: bytes, elf_sections: list[dict[str, Any]],
                  name: str) -> bytes:
    return P.section_bytes(elf_payload, next(
        row for row in elf_sections if row["name"] == name))


def _apply_component(input_component: bytes, core_report: dict[str, Any],
                     suffix: list[dict[str, Any]], suffix_packed,
                     suffix_placements, rebased, runtime_packed,
                     runtime_elf: Path, scatter_packed, scatter_placements,
                     joint_elf: Path, joint_payload: bytes, joint_sections,
                     final_report: dict[str, Any], profile: str,
                     cff_intervals: list[tuple[int, int, str]],
                     layout: dict[str, int]):
    O.validate_apollo_main(input_component)
    require(RUN_BASE + len(input_component) - PREAMBLE == CFF_END,
            "input component is not the exact CFF component extent")
    cff_before = {(start, end, name): image_slice(input_component, start, end)
                  for start, end, name in cff_intervals}
    output = bytearray(input_component)
    mutation_intervals: list[tuple[int, int, str]] = []
    suffix_names = set(suffix_placements)
    patches = [row for row in core_report["overlay"]["patched_sites"]
               if row.get("target_function") in suffix_names]
    require(len(patches) == (84 if profile == "apple-clang" else 0),
            "strict suffix redirect count drift")
    for patch in patches:
        address = int(patch["runtime_address"])
        current = image_slice(input_component, address,
                              address + int(patch["expected_size"]))
        require(current.hex() == patch["replacement_hex"],
                f"strict suffix entry guard drift: {patch['name']}")
        replacement = A.encode_thumb_b_w(
            address, suffix_placements[patch["target_function"]])
        replacement += b"\x00\xBF" * ((len(current) - 4) // 2)
        image_write(output, address, replacement)
        mutation_intervals.append((address, address + len(replacement),
                                   f"suffix_redirect:{patch['name']}"))
    for row in suffix_packed:
        for item in row["items"]:
            body = rebased[item["function"]]
            image_write(output, item["start"], body)
            mutation_intervals.append((item["start"],
                                       item["start"] + len(body),
                                       f"suffix:{item['function']}"))
    runtime_payload, runtime_sections = A.parse_elf32(runtime_elf)
    for row in runtime_packed:
        for item in row["items"]:
            body = P.section_bytes(runtime_payload, next(
                section for section in runtime_sections
                if section["name"] ==
                f".open_cfw_liblc3_runtime.{item['function']}"))
            require(len(body) == item["size"], "runtime body size drift")
            image_write(output, item["start"], body)
            mutation_intervals.append((item["start"],
                                       item["start"] + len(body),
                                       f"runtime:{item['function']}"))
    joint_names = [X.TABLE_SECTION, ".rodata",
                   *(f".lc3_scatter_{index}"
                     for index in range(len(scatter_placements))), ".text"]
    for name in joint_names:
        section = next(row for row in joint_sections if row["name"] == name)
        body = P.section_bytes(joint_payload, section)
        address = int(section["address"])
        image_write(output, address, body)
        mutation_intervals.append((address, address + len(body), f"lc3:{name}"))
    # The table/rodata alignment gap belonged to the now-redirected strict
    # suffix. Retire those authenticated source bytes explicitly. The gap
    # before the CFF tail was already erased and must remain so.
    retired_start = layout["table"] + X.TABLE_BYTES
    retired_end = layout["rodata"]
    if profile == "apple-clang":
        require(retired_end <= TABLE_START + sum(row["size"] for row in suffix),
                "retired suffix padding escaped the authenticated suffix")
        image_write(output, retired_start,
                    b"\xFF" * (retired_end - retired_start))
        mutation_intervals.append((retired_start, retired_end,
                                   "retired_suffix_alignment"))
    for start, end in ((retired_start, retired_end),
                       (final_report["artifacts"][".text"]["address"] +
                        final_report["artifacts"][".text"]["size"],
                        CFF_TAIL_START)):
        require(image_slice(bytes(output), start, end) == b"\xFF" * (end - start),
                f"joint erased padding drift: 0x{start:08X}")
    entry_guard = {0x0057A926: bytes.fromhex("10b50400"),
                   0x0057A940: bytes.fromhex("2de9f84f")}
    for veneer in final_report["service_audio_veneers"]:
        entry = veneer["entry"]
        require(image_slice(input_component, entry, entry + 4) ==
                entry_guard[entry], "service_audio entry guard drift")
        body = bytes.fromhex(veneer["encoding_hex"])
        image_write(output, entry, body)
        mutation_intervals.append((entry, entry + 4,
                                   f"service_veneer:{veneer['root']}"))
    require(all(cff_before[key] == image_slice(bytes(output), key[0], key[1])
                for key in cff_before), "CFF provider bytes changed")
    _intervals_disjoint(mutation_intervals)
    struct.pack_into("<I", output, 0, 0x04000000 | len(output))
    struct.pack_into("<I", output, 4, 0)
    nested_crc = zlib.crc32(output[8:]) & 0xFFFFFFFF
    struct.pack_into("<I", output, 4, nested_crc)
    result = bytes(output)
    O.validate_apollo_main(result)
    # RAM contexts are runtime-owned state; no flash alias or initializer is
    # emitted. The shim's exact fixed slots are nevertheless part of admission.
    slots = [0x20106A7C, 0x201074C0, 0x20107F04, 0x20108948]
    require(all(right - left == 2628 for left, right in zip(slots, slots[1:]))
            and slots[-1] + 2628 == 0x2010938C,
            "four-context RAM geometry drift")
    return result, {
        "size": len(result), "sha256": sha256_bytes(result),
        "nested_crc32": f"0x{nested_crc:08X}",
        "runtime_end_exclusive": CFF_END,
        "mutation_interval_count": len(mutation_intervals),
        "mutation_intervals_sha256": canonical_sha256(mutation_intervals),
        "cff_intervals_preserved": True,
        "protected_update_overlap_bytes": 0,
        "adapter_state": {"contexts": slots, "slot_count": 4,
                          "slot_bytes": 2628, "total_bytes": 10512,
                          "end_exclusive": 0x2010938C,
                          "flash_initializer_bytes": 0},
    }


def build(*, manifest_path: Path = MANIFEST, input_component: Path,
          output_dir: Path, profile: str, record: bool = False):
    manifest = read_json(manifest_path)
    require((manifest.get("schema_version"), manifest.get("mode")) ==
            (1, "joint-cff-lc3-atomic-component"), "atomic schema drift")
    require(profile in ("apple-clang", "linux-clang"), "unknown profile")
    builder_path, _ = authenticate(manifest["builder"])
    require(builder_path == Path(__file__).resolve(),
            "atomic manifest names a different builder")
    input_payload = input_component.read_bytes()
    expected_input = manifest["profiles"][profile]["input_component"]
    require((len(input_payload), sha256_bytes(input_payload)) ==
            (expected_input["size"], expected_input["sha256"]),
            "input CFF component pin drift")
    (proposal, core_report, _component, protected, suffix, bins, forbidden,
     suffix_packed, suffix_placements, ingress, cff_intervals) = _core_context(
        manifest, input_payload, profile)
    rebased, suffix_records = _rebase_suffix(
        proposal, core_report, input_payload, suffix, suffix_placements,
        profile)
    with tempfile.TemporaryDirectory(prefix="open-cfw-lc3-atomic-") as raw:
        temporary = Path(raw)
        unique, compile_report = _compile_unique(manifest, profile, temporary)
        (production, bindings, runtime_report, runtime_packed,
         scatter_packed, scatter_placements,
         layout) = _runtime_and_scatter_placements(
            manifest, profile, temporary, bins, forbidden, suffix_packed,
            compile_report["text_inputs"], core_report)
        scatter_ingress = _scatter_ingress(
            input_payload, scatter_placements, compile_report["text_inputs"],
            manifest["profiles"][profile]["expected_scatter_ingress"])
        final, final_payload, final_sections, final_report = _joint_link(
            profile, unique, compile_report, bindings, scatter_placements,
            core_report, layout, cff_intervals,
            manifest["profiles"][profile]["expected_layout"], temporary)
        runtime_intervals = [
            (row["address"], row["address"] + row["size"],
             f"lc3_runtime:{row['function']}")
            for row in runtime_report["sections"]]
        production_intervals = [
            *cff_intervals, *runtime_intervals,
            *(tuple(row) for row in final_report["intervals"]),
        ]
        _intervals_disjoint(production_intervals)
        require(max(row[1] for row in production_intervals) <= UPDATE_START,
                "joint placement crosses protected update boundary")
        component, component_report = _apply_component(
            input_payload, core_report, suffix, suffix_packed,
            suffix_placements, rebased, runtime_packed,
            temporary / "target-runtime.elf", scatter_packed,
            scatter_placements, final, final_payload, final_sections,
            final_report, profile, cff_intervals, layout)
    report = {
        "schema_version": 1, "profile": profile,
        "status": "joint-cff-lc3-atomic-component-emitted-package-pending",
        "evidence": {
            "builder": manifest["builder"],
            "capacity_proposal": manifest["evidence"]["capacity_proposal"],
            "production_replay": manifest["evidence"]["production_replay"],
            "core": manifest["profiles"][profile]["core"],
        },
        "input_component": {"size": len(input_payload),
                            "sha256": sha256_bytes(input_payload)},
        "component": component_report,
        "strict_suffix": {
            "leaf_count": len(suffix),
            "relocation_count": len(suffix_records),
            "host_slots": suffix_packed,
            "placement_sha256": canonical_sha256(suffix_packed),
            "replay_sha256": canonical_sha256(suffix_records),
            "ingress": ingress,
        },
        "target_runtime": runtime_report,
        "lc3_compile": compile_report,
        "joint_finalization": final_report,
        "joint_layout": {
            "cff_intervals": [
                {"start": start, "end_exclusive": end, "owner": name}
                for start, end, name in cff_intervals],
            "runtime_slots": runtime_packed,
            "scatter_slots": scatter_packed,
            "scatter_ingress": scatter_ingress,
            "forbidden_host_entries": {
                "forbidden_entry_count": len(forbidden["forbidden"]),
                **{key: forbidden[key] for key in (
                    "branch_target_count", "byte_window_pointer_target_count",
                    "aligned_word_pointer_target_count")}},
            "zero_overlap_verified": True,
            "production_intervals_sha256":
                canonical_sha256(sorted(production_intervals)),
            "protected_update_start": UPDATE_START,
            "protected_update_overlap_bytes": 0,
        },
        "routing": {
            "component_mutations_applied_atomically": True,
            "service_audio_veneers_applied": True,
            "component_crc_repaired": True,
            "outer_evenota_package_emitted": False,
            "hardware_operations": False,
            "hardware_qualified": False,
        },
        "remaining_software_blockers": [
            "Replace Apollo-main entry 6 in the EVENOTA package atomically, update the entry CRC-32C/table size, and rerun whole-package validation."
        ],
    }
    expected = manifest["profiles"][profile].get("expected_report_sha256")
    if not record:
        require(canonical_sha256(report) == expected,
                f"{profile}: atomic component receipt drift")
    require(not output_dir.exists(), "atomic output directory already exists")
    staging = output_dir.parent / f".{output_dir.name}.staging-{os.getpid()}"
    require(not staging.exists(), "atomic staging path already exists")
    staging.mkdir(parents=True)
    try:
        (staging / "ota_s200_firmware_ota.bin").write_bytes(component)
        (staging / "build-report.json").write_text(
            json.dumps(report, sort_keys=True, indent=2) + "\n",
            encoding="utf-8")
        os.replace(staging, output_dir)
    finally:
        if staging.exists():
            for path in staging.iterdir():
                path.unlink()
            staging.rmdir()
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--input-component", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--profile", choices=("apple-clang", "linux-clang"),
                        default="apple-clang")
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    try:
        report = build(
            manifest_path=args.manifest.resolve(),
            input_component=args.input_component.resolve(),
            output_dir=args.output_dir.resolve(), profile=args.profile,
            record=args.record)
    except (AtomicComponentError, S.SuffixPackError, S.C.CapacityError,
            R.BuildError, X.SpecializedXipError, O.OpenCFWError,
            OSError, KeyError, TypeError, ValueError) as error:
        print(f"atomic LC3 component failed: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
