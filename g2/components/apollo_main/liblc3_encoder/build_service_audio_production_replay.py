#!/usr/bin/env python3
"""Build the LC3-owned target runtime and exact production-order replay.

No stock/component image is written.  The builder places a zero-import scalar
runtime in authenticated stock-slot NOP tails, binds the retained source-owned
sqrtf leaf, and applies every LC3 relocation at the suffix-pack addresses.

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
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
G2 = ROOT.parents[2]
MANIFEST = ROOT / "service_audio_production_replay.json"
SUFFIX_TOOL = G2 / "tools/analyze_g2_liblc3_service_audio_suffix_pack.py"
ROUTE_BUILDER = ROOT / "build_service_audio_route_experiment.py"


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
                  suffix_report: dict[str, Any], bindings: dict[str, int],
                  core_report: dict[str, Any], output: Path) -> dict[str, Any]:
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
    if profile == "apple-clang":
        layout_rows = suffix_report["lc3_placement"]["sections"]
    else:
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


def build(*, manifest_path: Path = MANIFEST, output_dir: Path,
          profile: str, record: bool = False) -> dict[str, Any]:
    manifest = read_json(manifest_path)
    require((manifest.get("schema_version"), manifest.get("mode")) ==
            (1, "production-order-replay-proven-image-routing-blocked"),
            "production replay schema drift")
    require(manifest["routing"] == {
        "production_placement": False, "service_audio_routed": False,
        "firmware_image_emitted": False, "hardware_operations": False},
        "production replay gained image authority")
    require(set(SCRIPT_SOURCE_NAMES).issubset(manifest.get("sources", {})),
            "production replay script pins are incomplete")
    for name in SCRIPT_SOURCE_NAMES:
        authenticate(manifest["sources"][name])
    output_dir.mkdir(parents=True, exist_ok=True)
    obj, items = _compile_runtime(manifest, profile, output_dir)
    suffix_report, core_report, packed, placements = _runtime_placement(
        manifest, items)
    bindings, runtime = _link_runtime(
        manifest, profile, obj, packed, placements, output_dir)
    final = _finalize_lc3(
        manifest, profile, suffix_report, bindings, core_report, output_dir)
    report = {
        "schema_version": 1, "profile": profile,
        "status": "production-order-replay-proven-image-routing-blocked",
        "target_runtime": runtime, "lc3_finalization": final,
        "adapter_state": suffix_report["adapter_state"],
        "routing": manifest["routing"],
        "remaining_software_blockers": [
            "Integrate the proven runtime tails, 84 suffix redirects, LC3 XIP sections, four RAM slots, and two service_audio veneers into one atomic package builder and refresh final CRC/integrity receipts."
        ],
    }
    expected = manifest["profiles"][profile].get("expected_report_sha256")
    if not record:
        require(canonical_sha256(report) == expected,
                f"{profile}: production replay receipt drift")
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
