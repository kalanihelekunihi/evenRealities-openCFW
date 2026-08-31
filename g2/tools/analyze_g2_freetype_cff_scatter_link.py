#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

"""Prove an exact relocated CFF -Oz scatter link without routing an image."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


G2 = Path(__file__).resolve().parents[1]
SIZE_ANALYZER = G2 / "tools/analyze_g2_freetype_cff_size_optimization.py"
SIZE_MANIFEST = G2 / "tools/manifests/g2-freetype-cff-size-optimization.json"
CAPACITY_ANALYZER = G2 / "tools/analyze_g2_freetype_cff_capacity_solver.py"
CAPACITY_MANIFEST = G2 / "tools/manifests/g2-freetype-cff-capacity-solver.json"
PACKAGE = G2 / "build/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
MANIFEST = G2 / "tools/manifests/g2-freetype-cff-scatter-link.json"

PINS = {
    SIZE_ANALYZER: (31_687, "ee67f467d6314cd9b5a541cd2c924d513b50ee88f3520f1864225f739e0b65be"),
    SIZE_MANIFEST: (228_810, "faa7820d757665cc3e440f660c9085039d83fa3f05b8acc21f01b0bb934c24c8"),
    CAPACITY_ANALYZER: (41_444, "69a462c2c0f1be1aab265767377ceedcd823e8cf05c9fd8d805987b769ea3e2b"),
    CAPACITY_MANIFEST: (358_346, "f6b3b602fdfc1301db6523633dde9f92b962e8d35ca385e80926a930b816a5d2"),
    PACKAGE: (4_739_498, "115c5ad73e32e308287034d1b1120f8ed576ec3c3c9294cafce1bfc561b727f9"),
}

STOCK = (0x005ABEF8, 0x005B0114)
TAIL = (0x007FCEBA, 0x007FE000)
TAIL_TEXT_START = 0x007FCEC0
MODULE_SLOT = 0x0073EF00
STOCK_CLASS = 0x006DCB74
EXPECTED_CLASS = 0x005AC014
TARGET_TAIL_INPUT_BYTES = 4_100
EXPECTED_OUTPUTS = (
    ".cff_stock_rodata", ".cff_stock_text",
    ".cff_tail_text", ".cff_tail_exidx",
)


class ScatterError(RuntimeError):
    """Raised when exact placement, relocation, or ownership evidence drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ScatterError(message)


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256(path: Path) -> str:
    return digest(path.read_bytes())


def canonical(value: Any) -> str:
    return digest(json.dumps(
        value, sort_keys=True, separators=(",", ":")
    ).encode())


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None,
            f"cannot load pinned dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _pin_inputs(overrides: dict[Path, Path] | None) -> dict[Path, bytes]:
    overrides = overrides or {}
    data = {}
    for expected_path, expected in PINS.items():
        actual = overrides.get(expected_path, expected_path)
        body = actual.read_bytes()
        require((len(body), digest(body)) == expected,
                f"input pin drift: {expected_path}")
        data[expected_path] = body
    return data


def _sections(path: Path, builder: Any) -> list[dict[str, Any]]:
    output = builder.run([
        str(builder.TOOLS["readobj"]), "--sections", str(path)
    ])
    result: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for line in output.splitlines():
        match = re.match(r"\s+Name: (\S+) \(\d+\)$", line)
        if match:
            if current is not None:
                result.append(current)
            current = {"name": match.group(1)}
            continue
        if current is None:
            continue
        match = re.match(r"\s+Type: (\S+)", line)
        if match:
            current["type"] = match.group(1)
            continue
        match = re.match(r"\s+Flags \[ \((0x[0-9A-F]+)\)", line)
        if match:
            current["flags"] = int(match.group(1), 16)
            continue
        match = re.match(r"\s+Address: (0x[0-9A-F]+)$", line)
        if match:
            current["address"] = int(match.group(1), 16)
            continue
        match = re.match(r"\s+Size: (\d+)$", line)
        if match:
            current["size"] = int(match.group(1))
            continue
        match = re.match(r"\s+AddressAlignment: (\d+)$", line)
        if match:
            current["alignment"] = int(match.group(1))
    if current is not None:
        result.append(current)
    return result


def _text_inputs(objects: dict[str, Path], builder: Any) -> list[dict[str, Any]]:
    result = []
    for object_name, path in objects.items():
        for section in _sections(path, builder):
            if section.get("size", 0) and section["name"].startswith(".text."):
                result.append({"object": object_name, **section})
    require(len({row["name"] for row in result}) == len(result),
            "duplicate text section name prevents unambiguous scatter selection")
    return result


def _partition_text(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    tail: list[dict[str, Any]] = []
    used = 0
    for row in sorted(rows, key=lambda value: (-value["size"], value["name"])):
        aligned = (used + row["alignment"] - 1) & -row["alignment"]
        candidate = aligned + row["size"]
        if row["size"] <= 4_200 and candidate <= TARGET_TAIL_INPUT_BYTES:
            tail.append(row)
            used = candidate
    stock = [row for row in rows if row not in tail]
    require(used == TARGET_TAIL_INPUT_BYTES and stock and tail,
            "deterministic two-bin text partition drift")
    return stock, tail


def _linker_script(stock: list[dict[str, Any]], tail: list[dict[str, Any]]) -> str:
    def selectors(rows: list[dict[str, Any]]) -> str:
        return "\n".join(f"    *({row['name']})" for row in rows)

    return f"""/* SPDX-License-Identifier: MIT */
SECTIONS
{{
  .cff_stock_rodata 0x{STOCK[0]:08X} :
  {{
    *(.rodata)
    *(.rodata.*)
  }}
  .cff_stock_text ALIGN(16) :
  {{
{selectors(stock)}
  }}
  .cff_tail_text 0x{TAIL_TEXT_START:08X} :
  {{
{selectors(tail)}
  }}
  .cff_tail_exidx :
  {{
    *(.ARM.exidx*)
    *(.ARM.extab*)
  }}
  ASSERT(ADDR(.cff_stock_rodata) >= 0x{STOCK[0]:08X}, "stock start")
  ASSERT(ADDR(.cff_stock_text) + SIZEOF(.cff_stock_text) <= 0x{STOCK[1]:08X}, "stock overflow")
  ASSERT(ADDR(.cff_tail_text) >= 0x{TAIL[0]:08X}, "tail start")
  ASSERT(ADDR(.cff_tail_exidx) + SIZEOF(.cff_tail_exidx) <= 0x{TAIL[1]:08X}, "tail overflow")
  /DISCARD/ :
  {{
    *(.comment)
    *(.note.GNU-stack)
    *(.llvm_addrsig)
    *(.ARM.attributes)
  }}
}}
"""


def _nm_records(path: Path, builder: Any) -> list[dict[str, Any]]:
    result = []
    for line in builder.run([
        str(builder.TOOLS["nm"]), "--format=posix", str(path)
    ]).splitlines():
        fields = line.split()
        if len(fields) >= 3:
            result.append({
                "name": fields[0], "kind": fields[1],
                "address": int(fields[2], 16),
                "size": int(fields[3], 16) if len(fields) >= 4 else 0,
            })
    return result


def _build_once(
    size_module: Any, profile: str, compiler: Path, directory: Path,
    expected_map_symbols: set[str],
) -> dict[str, Any]:
    builder = size_module.load_module(size_module.BUILDER)
    selected = next(
        variant for variant in size_module.VARIANTS
        if variant.name == size_module.SELECTED
    )
    builder.TARGET_FLAGS = size_module._flags(builder, selected)
    directory.mkdir(parents=True)
    objects = {
        "cff.o": directory / "cff.o",
        "policy.o": directory / "policy.o",
        "providers.o": directory / "providers.o",
    }
    builder._compile(compiler, size_module.CFF_SOURCE, objects["cff.o"])
    builder._compile(compiler, size_module.POLICY, objects["policy.o"])
    builder._compile(compiler, size_module.PROVIDERS, objects["providers.o"])
    text = _text_inputs(objects, builder)
    stock, tail = _partition_text(text)
    script = _linker_script(stock, tail)
    script_path = directory / "scatter.ld"
    script_path.write_text(script, encoding="utf-8")
    final = directory / "cff-scatter.elf"
    bindings = {**builder.RETAINED_BINDINGS, "__aeabi_memcpy": 0x00439BE4}
    builder.run([
        str(builder.TOOLS["lld"]), "-m", "armelf", "-T", str(script_path),
        *(f"--undefined={name}" for name in builder.REQUIRED_EXPORTS),
        *(f"--defsym={name}=0x{address:08X}"
          for name, address in sorted(bindings.items())),
        *(str(path) for path in objects.values()), "-o", str(final),
    ])
    defined, undefined = builder._symbols(final)
    relocations = builder._relocations(final, set(undefined))
    require(not undefined and relocations["total"] == 0,
            f"{profile}: final scatter relocation closure drift")
    require(set(builder.REQUIRED_EXPORTS) <= set(defined),
            f"{profile}: final scatter public roots drift")

    alloc = [
        row for row in _sections(final, builder)
        if row.get("flags", 0) & 2 and row.get("size", 0)
    ]
    require([row["name"] for row in alloc] == list(EXPECTED_OUTPUTS),
            f"{profile}: unexpected allocated output section")
    section_records = []
    section_bodies: dict[str, bytes] = {}
    for row in alloc:
        output = directory / f"{row['name'][1:]}.bin"
        builder.run([
            str(builder.TOOLS["objcopy"]), "--dump-section",
            f"{row['name']}={output}", str(final),
        ])
        body = output.read_bytes()
        require(len(body) == row["size"],
                f"{profile}: extracted scatter section size drift")
        section_bodies[row["name"]] = body
        section_records.append({
            "name": row["name"],
            "start": f"0x{row['address']:08X}",
            "end_exclusive": f"0x{row['address'] + row['size']:08X}",
            "bytes": row["size"],
            "alignment": row["alignment"],
            "sha256": digest(body),
            "legal_interval": (
                "conditional-stock-cff-envelope"
                if STOCK[0] <= row["address"] < STOCK[1]
                else "directly-free-application-tail"
            ),
        })
    by_name = {row["name"]: row for row in section_records}
    stock_end = int(by_name[".cff_stock_text"]["end_exclusive"], 16)
    tail_end = int(by_name[".cff_tail_exidx"]["end_exclusive"], 16)
    require(
        int(by_name[".cff_stock_rodata"]["start"], 16) == STOCK[0] and
        stock_end <= STOCK[1] and
        int(by_name[".cff_tail_text"]["start"], 16) == TAIL_TEXT_START and
        tail_end <= TAIL[1],
        f"{profile}: final scatter section escaped legal intervals",
    )

    symbols = _nm_records(final, builder)
    symbol_addresses = {row["name"]: row["address"] for row in symbols}
    class_rows = [row for row in symbols if row["name"] == "cff_driver_class"]
    require(len(class_rows) == 1 and class_rows[0]["address"] == EXPECTED_CLASS,
            f"{profile}: relocated CFF class address drift")
    materialized = sorted(
        row["name"] for row in symbols
        if row["kind"].lower() == "t" and row["name"] in expected_map_symbols
    )
    require(len(set(materialized)) == 81,
            f"{profile}: materialized complete-map surface drift")
    callback_relocations = [
        row for row in size_module._records(objects["cff.o"], builder)
        if row["section"].startswith(".rel.rodata.") and
        row["symbol"] in expected_map_symbols
    ]
    callback_bindings = []
    stock_rodata = section_bodies[".cff_stock_rodata"]
    stock_rodata_start = int(
        by_name[".cff_stock_rodata"]["start"], 16
    )
    for row in callback_relocations:
        table = row["section"].removeprefix(".rel.rodata.")
        require(table in symbol_addresses and row["symbol"] in symbol_addresses,
                f"{profile}: callback table or target symbol disappeared")
        address = symbol_addresses[table] + row["offset"]
        offset = address - stock_rodata_start
        require(0 <= offset <= len(stock_rodata) - 4,
                f"{profile}: callback word escaped relocated rodata")
        word = int.from_bytes(stock_rodata[offset:offset + 4], "little")
        target = symbol_addresses[row["symbol"]]
        require(word & ~1 == target and word & 1 == 1,
                f"{profile}: relocated callback word target drift")
        callback_bindings.append({
            "table": table,
            "word_address": f"0x{address:08X}",
            "symbol": row["symbol"],
            "target": f"0x{target:08X}",
            "thumb_pointer": f"0x{word:08X}",
        })
    require(len(callback_bindings) == 58 and
            len({row["symbol"] for row in callback_bindings}) == 55,
            f"{profile}: final callback binding census drift")
    class_offset = EXPECTED_CLASS - stock_rodata_start
    class_size = class_rows[0]["size"]
    require(class_size == 96 and
            0 <= class_offset <= len(stock_rodata) - class_size,
            f"{profile}: relocated driver class extent drift")
    class_body = stock_rodata[class_offset:class_offset + class_size]
    veneers = sorted(
        (row for row in symbols
         if "Thunk" in row["name"] or "Ven" in row["name"]),
        key=lambda row: (row["address"], row["name"]),
    )
    widest = tail_end - min(bindings.values())
    require(widest < 16 * 1024 * 1024,
            f"{profile}: Thumb call/jump range drift")
    return {
        "compiler_version": builder.run([
            str(compiler), "--version"
        ]).splitlines()[0],
        "target_flags": list(builder.TARGET_FLAGS),
        "input_objects": {
            name: {"bytes": path.stat().st_size, "sha256": sha256(path)}
            for name, path in objects.items()
        },
        "partition": {
            "text_input_sections": len(text),
            "stock_text_input_sections": len(stock),
            "tail_text_input_sections": len(tail),
            "tail_text_input_bytes_with_alignment": TARGET_TAIL_INPUT_BYTES,
            "tail_section_names": [row["name"] for row in tail],
            "linker_script_bytes": len(script.encode()),
            "linker_script_sha256": digest(script.encode()),
        },
        "final_elf": {"bytes": final.stat().st_size, "sha256": sha256(final)},
        "sections": section_records,
        "loadable_bytes": sum(row["bytes"] for row in section_records),
        "stock_envelope_unused_bytes": STOCK[1] - stock_end,
        "tail_prefix_alignment_bytes": TAIL_TEXT_START - TAIL[0],
        "tail_suffix_unused_bytes": TAIL[1] - tail_end,
        "two_interval_unused_bytes": (
            (STOCK[1] - STOCK[0]) + (TAIL[1] - TAIL[0]) -
            sum(row["bytes"] for row in section_records)
        ),
        "cff_driver_class": f"0x{class_rows[0]['address']:08X}",
        "cff_driver_class_bytes": class_size,
        "cff_driver_class_sha256": digest(class_body),
        "final_callback_bindings": {
            "records": len(callback_bindings),
            "distinct_targets": len({
                row["symbol"] for row in callback_bindings
            }),
            "records_sha256": canonical(callback_bindings),
            "all_words_resolve_to_relocated_thumb_symbols": True,
        },
        "required_exports": list(builder.REQUIRED_EXPORTS),
        "materialized_complete_map_symbols": len(set(materialized)),
        "materialized_complete_map_symbol_names": sorted(set(materialized)),
        "undefined_symbols": undefined,
        "relocations": relocations,
        "binding_count": len(bindings),
        "bindings": {
            name: f"0x{address:08X}" for name, address in sorted(bindings.items())
        },
        "widest_binding_domain_bytes": widest,
        "thumb_call_jump_range_bytes_each_direction": 16 * 1024 * 1024,
        "range_compatible": True,
        "linker_generated_veneers": veneers,
    }


def _reproducible(
    size_module: Any, profile: str, compiler: Path, directory: Path,
    expected_map_symbols: set[str],
) -> dict[str, Any]:
    first = _build_once(
        size_module, profile, compiler, directory / "first",
        expected_map_symbols,
    )
    second = _build_once(
        size_module, profile, compiler, directory / "second",
        expected_map_symbols,
    )
    require(first == second, f"{profile}: scatter build is not reproducible")
    return first


def _payload_slice(capacity_module: Any, package: bytes, start: int, end: int) -> bytes:
    entry = capacity_module.EXPECTED_APOLLO_ENTRY
    payload_start = entry["package_offset"] + capacity_module.PACKAGE_COMPONENT_HEADER_BYTES
    first = payload_start + start - capacity_module.RUN_BASE + capacity_module.PREAMBLE_BYTES
    last = payload_start + end - capacity_module.RUN_BASE + capacity_module.PREAMBLE_BYTES
    require(0 <= first <= last <= len(package), "package slice unavailable")
    return package[first:last]


def validate_route_boundary(report: dict[str, Any]) -> None:
    require(report["routing"] == {
        "exact_dual_profile_scatter_link_proven": True,
        "all_mutations_single_apollo_application_entry": True,
        "cross_entry_ota_atomicity_required": False,
        "component_builder_integration_present": False,
        "production_route_permitted": False,
        "module_class_pointer_patch_applied": False,
        "firmware_image_emitted": False,
    }, "scatter route boundary drift")
    patch = report["module_class_patch_contract"]
    require(
        patch["address"] == "0x0073EF00" and
        patch["expected_stock_little_endian_hex"] == "74cb6d00" and
        patch["replacement_little_endian_hex"] == "14c05a00" and
        patch["applied"] is False,
        "module class pointer patch contract drift",
    )
    for name, profile in report["profiles"].items():
        require(profile["undefined_symbols"] == [] and
                profile["relocations"]["total"] == 0 and
                profile["range_compatible"] is True and
                profile["cff_driver_class"] == "0x005AC014" and
                profile["materialized_complete_map_symbols"] == 81,
                f"{name}: scatter closure drift")


def analyze(*, input_overrides: dict[Path, Path] | None = None) -> dict[str, Any]:
    data = _pin_inputs(input_overrides)
    size_module = load_module(SIZE_ANALYZER, "g2_cff_scatter_size_dependency")
    capacity_module = load_module(
        CAPACITY_ANALYZER, "g2_cff_scatter_capacity_dependency"
    )
    size_report = json.loads(data[SIZE_MANIFEST])
    capacity_report = capacity_module.analyze()
    require(capacity_report == json.loads(data[CAPACITY_MANIFEST]),
            "capacity analyzer/manifest drift")
    require(
        size_report["selected_candidate"]["name"] == "size-oz" and
        size_report["routing"]["byte_capacity_threshold_closed"] is True and
        size_report["routing"]["production_route_permitted"] is False,
        "selected -Oz size admission drift",
    )
    map_symbols = set(
        size_report["selected_candidate"]["profiles"]["apple-clang"]
        ["final"]["materialized_complete_map_symbol_names"]
    ) | set(
        size_report["selected_candidate"]["profiles"]["apple-clang"]
        ["final"]["inlined_only_complete_map_symbol_names"]
    )
    require(len(map_symbols) == 101, "selected complete-map set drift")

    builder = size_module.load_module(size_module.BUILDER)
    with tempfile.TemporaryDirectory(prefix="opencfw-cff-scatter-") as raw:
        root = Path(raw)
        profiles = {
            name: _reproducible(
                size_module, name, compiler, root / name, map_symbols
            )
            for name, compiler in builder.PROFILES.items()
        }

    package = data[PACKAGE]
    stock = _payload_slice(capacity_module, package, *STOCK)
    slot = _payload_slice(capacity_module, package, MODULE_SLOT, MODULE_SLOT + 4)
    require(
        digest(stock) ==
        "58b8b5e4c1b801d7ac4c6883dc8afeccd7cf370e3e9cccdf95f938e20b91358b" and
        slot == STOCK_CLASS.to_bytes(4, "little"),
        "stock CFF envelope or module slot package bytes drift",
    )
    plan = json.loads(size_module.FLASH_PLAN.read_text(encoding="utf-8"))
    stock_rows = [
        row for row in plan["flash_regions"]
        if row.get("component") == "apollo_main" and
        row["end_exclusive"] > STOCK[0] and row["target_address"] < STOCK[1]
    ]
    require(len(stock_rows) == 1 and
            stock_rows[0]["address_status"] == "official_blob" and
            stock_rows[0]["target_address"] <= STOCK[0] and
            stock_rows[0]["end_exclusive"] >= STOCK[1],
            "stock CFF flash-plan owner drift")
    require(
        capacity_report["whole_address_space"]["application_tail"] == {
            "start": "0x007FCEBA", "end_exclusive": "0x007FE000",
            "bytes": 4_422, "classification": "application-owned-free-tail",
        }, "application tail ownership drift",
    )

    expected_profile = {
        "apple-clang": (20_416, 622, 300, 930),
        "linux-clang": (20_356, 682, 300, 990),
    }
    for name, profile in profiles.items():
        require(
            (profile["loadable_bytes"], profile["stock_envelope_unused_bytes"],
             profile["tail_suffix_unused_bytes"],
             profile["two_interval_unused_bytes"]) == expected_profile[name],
            f"{name}: exact scatter capacity accounting drift",
        )

    result: dict[str, Any] = {
        "schema_version": 1,
        "status": "g2-freetype-cff-exact-scatter-link-closed-route-not-integrated",
        "analysis_mode": (
            "software-only deterministic final relocation replay; no package "
            "write, pointer patch application, signing, flashing, or hardware"
        ),
        "inputs": {
            path.relative_to(G2).as_posix(): {
                "bytes": expected[0], "sha256": expected[1],
            }
            for path, expected in PINS.items()
        },
        "ownership": {
            "conditional_stock_cff_envelope": {
                "start": "0x005ABEF8", "end_exclusive": "0x005B0114",
                "bytes": 16_924, "sha256": digest(stock),
                "current_plan_owner": "official_blob",
                "replacement_condition": (
                    "same-entry atomic module-class pointer replacement must "
                    "make the old CFF class and callbacks unreachable"
                ),
            },
            "direct_application_tail": {
                "start": "0x007FCEBA", "end_exclusive": "0x007FE000",
                "bytes": 4_422,
                "current_plan_collision_rows": 0,
            },
            "scattered_table_words_consumed": 0,
            "bootloader_partition_bytes_consumed": 0,
            "protected_update_record_bytes_consumed": 0,
            "byte_exact_plan_and_package_evidence": True,
        },
        "profiles": profiles,
        "module_class_patch_contract": {
            "address": "0x0073EF00",
            "expected_stock_class": "0x006DCB74",
            "expected_stock_little_endian_hex": slot.hex(),
            "replacement_class": "0x005AC014",
            "replacement_little_endian_hex": EXPECTED_CLASS.to_bytes(
                4, "little"
            ).hex(),
            "pointer_alignment": 4,
            "same_apollo_application_package_entry": True,
            "guarded_compare_before_write_required": True,
            "applied": False,
        },
        "ota_and_package": {
            "all_scatter_sections_and_pointer_patch_in_entry_id": 6,
            "cross_entry_mutations": 0,
            "cross_entry_ota_atomicity_required": False,
            "current_runtime_end_exclusive": "0x007FCEBA",
            "candidate_runtime_end_exclusive": "0x007FDED4",
            "component_growth_bytes": 4_122,
            "package_length_crc_and_flash_plan_regeneration_required": True,
            "candidate_component_or_package_emitted": False,
        },
        "routing": {
            "exact_dual_profile_scatter_link_proven": True,
            "all_mutations_single_apollo_application_entry": True,
            "cross_entry_ota_atomicity_required": False,
            "component_builder_integration_present": False,
            "production_route_permitted": False,
            "module_class_pointer_patch_applied": False,
            "firmware_image_emitted": False,
        },
        "evidence_bounds": {
            "compiler_byte_identity_claimed": False,
            "font_payload_authenticated": False,
            "stack_or_wcet_qualified": False,
            "hardware_validation_performed": False,
        },
    }
    result["scatter_sha256"] = canonical({
        "ownership": result["ownership"],
        "profiles": profiles,
        "module_class_patch_contract": result["module_class_patch_contract"],
        "ota_and_package": result["ota_and_package"],
        "routing": result["routing"],
    })
    validate_route_boundary(result)
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
                    "checked-in CFF scatter manifest drift")
    except (ScatterError, OSError, KeyError, ValueError) as error:
        print(f"G2 FreeType CFF scatter link failed: {error}", file=sys.stderr)
        return 1
    print(rendered if args.pretty else json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
