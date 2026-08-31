#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

"""Build and bound semantics-preserving CFF size-optimization experiments.

This analyzer never writes a firmware image or route.  It compiles the exact
admitted FreeType 2.9.1 CFF translation unit, policy adapter, and import
providers with reviewed optimization variants, closes every final relocation,
and compares their loadable bytes with the independently pinned legal scatter
capacity.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


G2 = Path(__file__).resolve().parents[1]
COMPONENT = G2 / "components/shared/freetype_cff"
FREETYPE = G2 / "third_party/freetype"
BUILDER = COMPONENT / "build_placement_census.py"
POLICY = COMPONENT / "runtime_freetype_cff.c"
PROVIDERS = COMPONENT / "runtime_freetype_cff_import_providers.c"
CENSUS_LINKER = COMPONENT / "placement_census.ld"
FINAL_LINKER = COMPONENT / "placement_final.ld"
ADMISSION = COMPONENT / "source_admission.json"
PROVENANCE = FREETYPE / "PROVENANCE.json"
CFF_SOURCE = FREETYPE / "src/cff/cff.c"
G2_OPTIONS = (
    G2 / "research/candidates/freetype/g2_config/freetype/config/ftoption.h"
)
G2_MODULES = FREETYPE / "g2-config/freetype/config/ftmodule.h"
CFF_MAP = G2 / "tools/manifests/g2-freetype-cff-function-map.json"
CAPACITY = G2 / "tools/manifests/g2-freetype-cff-capacity-solver.json"
FLASH_PLAN = G2 / "build/flash-plan.json"
MANIFEST = G2 / "tools/manifests/g2-freetype-cff-size-optimization.json"

PINS = {
    BUILDER: (18_482, "26f492728632e8838d59a93a1758540e9d9b8b97b8fa26fc287f8694b8f37aaf"),
    POLICY: (4_998, "98548455212e6254599766fd4475d8e68eb1b2aa3acd28722d83cb30bd5bb70c"),
    PROVIDERS: (4_831, "6504404f0cf523184a966de2d8d7fa50a6b498aa3830457194585865e00b6538"),
    CENSUS_LINKER: (687, "aa41febbfd7b64dec7f0cb410e1622c335c8b8b1739b33e24884e80afeb56c33"),
    FINAL_LINKER: (819, "2fe73a924aca12b8bec81eedc05db13f0ca8dfc4ed45be5637a254ccf7adeff4"),
    ADMISSION: (2_000, "cc8dc43ea6f4b38d32e605225f589a557858938a94e33e5f7c3aa3f4f4ba48ef"),
    PROVENANCE: (102_377, "2be8717625bceddee3aa95663186c0629247304c951c4790bc26cd372e3794bf"),
    CFF_SOURCE: (1_470, "4fb8b6e43985bc8fe518110b0631feaccc571c0d26055168b0f4e536ef9b70c1"),
    G2_OPTIONS: (1_831, "9c68e573dfcab0a059343cfa9988648db55aea5a942be53947a15f24f6df4278"),
    G2_MODULES: (876, "522c1d358dce8a141b2f8afec7020f66bf800d3d829a1ad22f3418ebf3f05d74"),
    CFF_MAP: (70_973, "f16b49ec344534f7cea59ce0a41350fb44ac7c2991baf884ba6b9bc96a2b2641"),
    CAPACITY: (358_346, "f6b3b602fdfc1301db6523633dde9f92b962e8d35ca385e80926a930b816a5d2"),
    FLASH_PLAN: (4_490_259, "963c0cc5459a9d2ddbf522ab0b47cb03683f850334c910c9c68c92070d0a3c01"),
}

AEABI_MEMCPY = 0x00439BE4
AEABI_MEMCPY_LEAF = 0x007C29F8
LEGAL_CAPACITY = 21_706
LOADABLE = ("text", "arm_exidx", "rodata", "data")


@dataclass(frozen=True)
class Variant:
    name: str
    optimization: str
    gc_sections: bool = False
    lto: bool = False
    merge_constants: bool = False


VARIANTS = (
    Variant("baseline-o2", "-O2"),
    Variant("size-os", "-Os"),
    Variant("size-oz", "-Oz"),
    Variant("size-oz-gc", "-Oz", gc_sections=True),
    Variant("size-oz-lto-gc", "-Oz", gc_sections=True, lto=True),
    Variant(
        "size-oz-lto-gc-merge", "-Oz", gc_sections=True, lto=True,
        merge_constants=True,
    ),
)
SELECTED = "size-oz"


class OptimizationError(RuntimeError):
    """Raised when optimization inputs or closure evidence drift."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise OptimizationError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical(value: Any) -> str:
    return sha256_bytes(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    )


def load_module(path: Path) -> Any:
    spec = importlib.util.spec_from_file_location("g2_cff_size_builder", path)
    require(spec is not None and spec.loader is not None,
            "cannot load pinned CFF builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _records(path: Path, builder: Any) -> list[dict[str, Any]]:
    output = builder.run([
        str(builder.TOOLS["readobj"]), "--relocations", "--expand-relocs",
        str(path),
    ])
    section = ""
    current: dict[str, Any] | None = None
    result: list[dict[str, Any]] = []
    for line in output.splitlines():
        match = re.match(r"\s+Section \(\d+\) (\S+) \{", line)
        if match:
            section = match.group(1)
            continue
        if line.strip() == "Relocation {":
            current = {"section": section}
            continue
        if current is None:
            continue
        match = re.match(r"\s+Offset: (0x[0-9A-F]+)$", line)
        if match:
            current["offset"] = int(match.group(1), 16)
            continue
        match = re.match(r"\s+Type: (\S+) \(\d+\)$", line)
        if match:
            current["type"] = match.group(1)
            continue
        match = re.match(r"\s+Symbol: (\S+) \(\d+\)$", line)
        if match:
            current["symbol"] = match.group(1)
            continue
        if line.strip() == "}" and {
            "section", "offset", "type", "symbol"
        } <= current.keys():
            result.append(current)
            current = None
    return result


def _all_text_symbols(path: Path, builder: Any) -> set[str]:
    result = set()
    for line in builder.run([
        str(builder.TOOLS["nm"]), "--format=posix", str(path)
    ]).splitlines():
        fields = line.split()
        if len(fields) >= 2 and fields[1].lower() == "t":
            result.add(fields[0])
    return result


def _decode_thumb_bw(body: bytes, address: int) -> int:
    require(len(body) >= 4, "retained __aeabi_memcpy redirect is truncated")
    first = int.from_bytes(body[0:2], "little")
    second = int.from_bytes(body[2:4], "little")
    require(first & 0xF800 == 0xF000 and second & 0xD000 == 0x9000,
            "retained __aeabi_memcpy redirect is not B.W")
    sign = (first >> 10) & 1
    i1 = 1 ^ ((second >> 13) & 1) ^ sign
    i2 = 1 ^ ((second >> 11) & 1) ^ sign
    immediate = (
        (sign << 24) | (i1 << 23) | (i2 << 22) |
        ((first & 0x3FF) << 12) | ((second & 0x7FF) << 1)
    )
    if immediate & (1 << 24):
        immediate -= 1 << 25
    return address + 4 + immediate


def _verify_inputs(overrides: dict[Path, Path] | None) -> dict[Path, bytes]:
    overrides = overrides or {}
    result = {}
    for expected_path, expected in PINS.items():
        actual = overrides.get(expected_path, expected_path)
        body = actual.read_bytes()
        require((len(body), sha256_bytes(body)) == expected,
                f"input pin drift: {expected_path}")
        result[expected_path] = body
    return result


def _verify_source_inventory(provenance: dict[str, Any]) -> dict[str, Any]:
    rows = [
        row for row in provenance["files"]
        if row["local_path"].startswith("src/cff/")
    ]
    require(len(rows) == 17 and sum(row["size"] for row in rows) == 269_028,
            "CFF source inventory drift")
    for row in rows:
        body = (FREETYPE / row["local_path"]).read_bytes()
        require((len(body), sha256_bytes(body)) ==
                (row["size"], row["sha256"]),
                f"CFF source record drift: {row['local_path']}")
    return {
        "files": len(rows),
        "bytes": sum(row["size"] for row in rows),
        "records_sha256": canonical([
            {key: row[key] for key in ("local_path", "size", "sha256")}
            for row in rows
        ]),
    }


def _verify_aeabi_provider(plan: dict[str, Any]) -> dict[str, Any]:
    rows = plan["flash_regions"]
    public = [
        row for row in rows
        if row.get("component") == "apollo_main" and
        row["target_address"] == AEABI_MEMCPY
    ]
    leaf = [
        row for row in rows
        if row.get("component") == "apollo_main" and
        row["target_address"] == AEABI_MEMCPY_LEAF
    ]
    require(len(public) == len(leaf) == 1,
            "retained __aeabi_memcpy provider rows drift")
    public_row, leaf_row = public[0], leaf[0]
    public_body = (G2 / "build" / public_row["artifact"]).read_bytes()
    leaf_body = (G2 / "build" / leaf_row["artifact"]).read_bytes()
    require(
        public_row["address_status"] == "generated_source_entry_replacement" and
        public_row["end_exclusive"] == 0x00439C04 and
        len(public_body) == 32 and sha256_bytes(public_body) ==
        "7a656bccb8aeacd1f153cf87f82adc5c786573d3d5f2f8ae8b69bcded1223cac" and
        _decode_thumb_bw(public_body, AEABI_MEMCPY) == AEABI_MEMCPY_LEAF,
        "retained __aeabi_memcpy public redirect drift",
    )
    require(
        leaf_row["address_status"] == "source_compiled" and
        leaf_row["end_exclusive"] == 0x007C2A90 and
        len(leaf_body) == 152 and sha256_bytes(leaf_body) ==
        "ee2582dc5c82d4bd438403a2682be0debc10c301ec0549942b7c56baa61d026f",
        "retained __aeabi_memcpy source leaf drift",
    )
    return {
        "symbol": "__aeabi_memcpy",
        "binding": f"0x{AEABI_MEMCPY:08X}",
        "public_redirect_bytes": len(public_body),
        "public_redirect_sha256": sha256_bytes(public_body),
        "source_leaf": f"0x{AEABI_MEMCPY_LEAF:08X}",
        "source_leaf_bytes": len(leaf_body),
        "source_leaf_sha256": sha256_bytes(leaf_body),
        "abi": "Arm void-EABI forward copy; r0 destination, r1 source, r2 count",
        "current_package_route_authenticated": True,
    }


def _flags(builder: Any, variant: Variant) -> tuple[str, ...]:
    flags = tuple(
        value for value in builder.TARGET_FLAGS
        if value not in {"-O2", "-Os", "-Oz", "-flto=full",
                         "-fmerge-all-constants"}
    ) + (variant.optimization,)
    if variant.lto:
        flags += ("-flto=full",)
    if variant.merge_constants:
        flags += ("-fmerge-all-constants",)
    return flags


def _inline_proof(
    builder: Any, compiler: Path, flags: tuple[str, ...], output: Path,
) -> set[str]:
    includes = (
        builder.TARGET_COMPAT, builder.G2_CONFIG,
        builder.FREETYPE / "g2-config", builder.FREETYPE / "include",
        builder.FREETYPE, builder.COMPONENT,
    )
    completed = subprocess.run([
        str(compiler), *flags, "-Rpass=inline",
        *(argument for path in includes for argument in ("-I", str(path))),
        "-c", str(CFF_SOURCE), "-o", str(output),
    ], check=False, capture_output=True, text=True)
    require(completed.returncode == 0,
            f"inline-proof compile failed: {completed.stderr.strip()}")
    names = {
        match.group(1)
        for match in re.finditer(
            r"remark: '([^']+)' inlined into", completed.stderr
        )
    }
    require(names, "clang inline proof disappeared")
    return names


def _build_once(
    builder: Any, variant: Variant, profile: str, compiler: Path,
    directory: Path, map_symbols: set[str], required_exports: tuple[str, ...],
) -> dict[str, Any]:
    directory.mkdir(parents=True)
    builder.TARGET_FLAGS = _flags(builder, variant)
    cff = directory / "cff.o"
    policy = directory / "policy.o"
    providers = directory / "providers.o"
    linked = directory / "provider-closed.o"
    final = directory / "final.elf"
    binary = directory / "final.bin"
    builder._compile(compiler, CFF_SOURCE, cff)
    builder._compile(compiler, POLICY, policy)
    builder._compile(compiler, PROVIDERS, providers)

    roots = [f"--undefined={name}" for name in required_exports]
    builder.run([
        str(builder.TOOLS["lld"]), "-m", "armelf", "-r", "-T",
        str(CENSUS_LINKER), *roots, str(cff), str(policy), str(providers),
        "-o", str(linked),
    ])
    defined, undefined = builder._symbols(linked)
    relocations = builder._relocations(linked, set(undefined))
    sections = builder._sections(linked, directory / "linked-sections")

    bindings = dict(builder.RETAINED_BINDINGS)
    if "__aeabi_memcpy" in undefined:
        bindings["__aeabi_memcpy"] = AEABI_MEMCPY
    require(set(undefined) == set(bindings),
            f"{variant.name}/{profile}: provider-closed import drift")
    command = [
        str(builder.TOOLS["lld"]), "-m", "armelf", "-T", str(FINAL_LINKER),
        *(("--gc-sections",) if variant.gc_sections else ()),
        *roots,
        *(f"--defsym={name}=0x{address:08X}"
          for name, address in sorted(bindings.items())),
        str(cff), str(policy), str(providers), "-o", str(final),
    ]
    builder.run(command)
    builder.run([
        str(builder.TOOLS["objcopy"]), "-O", "binary", str(final), str(binary)
    ])
    final_defined, final_undefined = builder._symbols(final)
    final_relocations = builder._relocations(final, set(final_undefined))
    final_sections = builder._sections(final, directory / "final-sections")
    require(not final_undefined and final_relocations["total"] == 0,
            f"{variant.name}/{profile}: final closure incomplete")
    require(set(required_exports) <= set(final_defined),
            f"{variant.name}/{profile}: required public root missing")
    require(final_sections["data"]["size"] == 0 and
            final_sections["bss"]["size"] == 0,
            f"{variant.name}/{profile}: static RAM appeared")

    cff_records = _records(cff, builder) if not variant.lto else []
    callback_records = [
        (row["section"], row["offset"], row["type"], row["symbol"])
        for row in cff_records
        if row["section"].startswith(".rel.rodata") and
        row["symbol"] in map_symbols
    ]
    cff_import_records = [
        row for row in cff_records if row["symbol"] == "__aeabi_memcpy"
    ]
    if variant.name == SELECTED:
        require(len(callback_records) == 58 and
                len({row[3] for row in callback_records}) == 55 and
                canonical(callback_records) ==
                "dd4e5d792b4ba5b5ca5e42c399b05b3a482b224d0166194ec65d9ef077199211",
                f"{profile}: selected CFF callback roots drift")
        require(cff_import_records == [{
            "section": ".rel.text.cff_ps_get_font_info", "offset": 26,
            "type": "R_ARM_THM_CALL", "symbol": "__aeabi_memcpy",
        }], f"{profile}: selected __aeabi_memcpy callsite drift")

    text_symbols = _all_text_symbols(final, builder)
    mapped_materialized = sorted(map_symbols & text_symbols)
    inlined_map_symbols: list[str] = []
    if variant.name == SELECTED:
        inlined = _inline_proof(
            builder, compiler, builder.TARGET_FLAGS,
            directory / "inline-proof.o",
        )
        inlined_map_symbols = sorted(map_symbols - set(mapped_materialized))
        require(
            set(inlined_map_symbols) <= inlined and
            set(mapped_materialized).isdisjoint(inlined_map_symbols) and
            set(mapped_materialized) | set(inlined_map_symbols) == map_symbols and
            len(mapped_materialized) == 81 and len(inlined_map_symbols) == 20,
            f"{profile}: complete map materialized/inlined coverage drift",
        )
    loadable = sum(final_sections[name]["size"] for name in LOADABLE)
    return {
        "compiler_version": builder.run([
            str(compiler), "--version"
        ]).splitlines()[0],
        "target_flags": list(builder.TARGET_FLAGS),
        "objects": {
            "cff": {"bytes": cff.stat().st_size, "sha256": sha256(cff)},
            "policy": {
                "bytes": policy.stat().st_size, "sha256": sha256(policy),
            },
            "providers": {
                "bytes": providers.stat().st_size, "sha256": sha256(providers),
            },
            "provider_closed": {
                "bytes": linked.stat().st_size, "sha256": sha256(linked),
            },
            "final_elf": {
                "bytes": final.stat().st_size, "sha256": sha256(final),
            },
            "final_binary": {
                "bytes": binary.stat().st_size, "sha256": sha256(binary),
            },
        },
        "provider_closed": {
            "sections": sections,
            "defined_global_symbols": defined,
            "imports": undefined,
            "import_count": len(undefined),
            "relocations": relocations,
        },
        "source_callback_roots": {
            "available_before_lto": not variant.lto,
            "relocations": len(callback_records),
            "distinct_targets": len({row[3] for row in callback_records}),
            "records_sha256": canonical(callback_records),
        },
        "compiler_runtime_import": {
            "symbol": "__aeabi_memcpy",
            "source_relocations": len(cff_import_records),
            "records": cff_import_records,
            "binding": (
                f"0x{AEABI_MEMCPY:08X}"
                if "__aeabi_memcpy" in bindings else None
            ),
        },
        "final": {
            "sections": final_sections,
            "loadable_bytes": loadable,
            "flat_binary_bytes": binary.stat().st_size,
            "static_ram_bytes": (
                final_sections["data"]["size"] +
                final_sections["bss"]["size"]
            ),
            "defined_global_symbols": final_defined,
            "required_exports": list(required_exports),
            "required_exports_present": True,
            "materialized_complete_map_symbols": len(mapped_materialized),
            "materialized_complete_map_symbol_names": mapped_materialized,
            "inlined_only_complete_map_symbols": len(inlined_map_symbols),
            "inlined_only_complete_map_symbol_names": inlined_map_symbols,
            "complete_map_source_behavior_covered": (
                len(mapped_materialized) + len(inlined_map_symbols)
            ),
            "undefined_symbols": final_undefined,
            "relocations": final_relocations,
            "legal_capacity_upper_bound": LEGAL_CAPACITY,
            "legal_capacity_loadable_margin": LEGAL_CAPACITY - loadable,
            "legal_capacity_flat_binary_margin": (
                LEGAL_CAPACITY - binary.stat().st_size
            ),
            "byte_capacity_fit": loadable <= LEGAL_CAPACITY,
        },
    }


def _build_reproducible(
    builder: Any, variant: Variant, profile: str, compiler: Path,
    directory: Path, map_symbols: set[str], required_exports: tuple[str, ...],
) -> dict[str, Any]:
    first = _build_once(
        builder, variant, profile, compiler, directory / "first",
        map_symbols, required_exports,
    )
    second = _build_once(
        builder, variant, profile, compiler, directory / "second",
        map_symbols, required_exports,
    )
    require(first == second,
            f"{variant.name}/{profile}: deterministic build drift")
    return first


def validate_selected_contract(report: dict[str, Any]) -> None:
    candidate = report["selected_candidate"]
    require(candidate["name"] == SELECTED and
            candidate["source_files_modified"] == 0 and
            candidate["lto_used"] is False and
            candidate["section_gc_used"] is False,
            "selected candidate policy drift")
    require(candidate["public_exports"] == [
        "cff_driver_class",
        "open_cfw_freetype_cff_get_darkening_parameters",
        "open_cfw_freetype_cff_get_hinting_engine",
        "open_cfw_freetype_cff_get_no_stem_darkening",
        "open_cfw_freetype_cff_set_darkening_parameters",
        "open_cfw_freetype_cff_set_hinting_engine",
        "open_cfw_freetype_cff_set_no_stem_darkening",
    ], "selected public root set drift")
    for name, profile in candidate["profiles"].items():
        require(profile["source_callback_roots"] == {
            "available_before_lto": True,
            "relocations": 58,
            "distinct_targets": 55,
            "records_sha256": (
                "dd4e5d792b4ba5b5ca5e42c399b05b3a482b224d0166194ec65d9ef077199211"
            ),
        }, f"{name}: callback-root contract drift")
        require(profile["compiler_runtime_import"]["binding"] ==
                "0x00439BE4" and
                profile["compiler_runtime_import"]["source_relocations"] == 1,
                f"{name}: compiler-runtime binding drift")
        final = profile["final"]
        require(final["byte_capacity_fit"] and
                final["undefined_symbols"] == [] and
                final["relocations"]["total"] == 0 and
                final["required_exports_present"] and
                final["static_ram_bytes"] == 0 and
                final["materialized_complete_map_symbols"] == 81 and
                final["inlined_only_complete_map_symbols"] == 20 and
                final["complete_map_source_behavior_covered"] == 101 and
                set(final["materialized_complete_map_symbol_names"]).isdisjoint(
                    final["inlined_only_complete_map_symbol_names"]
                ),
                f"{name}: selected final closure drift")
    routing = report["routing"]
    require(routing == {
        "byte_capacity_threshold_closed": True,
        "exact_scatter_placement_proven": False,
        "production_route_permitted": False,
        "module_class_pointer_patch_permitted": False,
        "firmware_image_emitted": False,
    }, "optimization experiment routing boundary drift")


def analyze(
    *, input_overrides: dict[Path, Path] | None = None,
    required_exports: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    data = _verify_inputs(input_overrides)
    builder = load_module(BUILDER)
    exports = tuple(required_exports or builder.REQUIRED_EXPORTS)
    require(exports == tuple(builder.REQUIRED_EXPORTS),
            "required public export root set drift")

    admission = json.loads(data[ADMISSION])
    provenance = json.loads(data[PROVENANCE])
    function_map = json.loads(data[CFF_MAP])
    capacity = json.loads(data[CAPACITY])
    plan = json.loads(data[FLASH_PLAN])
    require(
        admission["upstream"]["version"] == "2.9.1" and
        admission["complete_map"] == {
            "functions": 101, "callable_bytes": 16_718,
            "physical_bytes": 16_924, "physical_residue_bytes": 206,
            "unresolved_callable_bytes": 0,
            "mapping_sha256": (
                "16761c056d968c5c4847c918d5a4d04a1a5a7fb883f125e833054f3762b7266e"
            ),
        }, "complete CFF admission drift",
    )
    require(
        function_map["confidence"]["mapped_total"] == {
            "functions": 101, "bytes": 16_718,
        } and function_map["confidence"]["unresolved_code"]["bytes"] == 0,
        "complete CFF function map drift",
    )
    map_symbols = {row["symbol"] for row in function_map["functions"]}
    require(len(map_symbols) == 101, "complete CFF symbol set drift")
    source_inventory = _verify_source_inventory(provenance)

    require(
        capacity["scatter_placement"][
            "legal_application_capacity_upper_bound"
        ] == LEGAL_CAPACITY and
        capacity["routing"]["production_scatter_feasible"] is False and
        capacity["routing"]["module_class_pointer_patch_permitted"] is False,
        "legal scatter capacity evidence drift",
    )
    aeabi_provider = _verify_aeabi_provider(plan)

    built: dict[str, Any] = {}
    with tempfile.TemporaryDirectory(prefix="opencfw-cff-size-opt-") as raw:
        root = Path(raw)
        for variant in VARIANTS:
            profiles = {
                name: _build_reproducible(
                    builder, variant, name, compiler,
                    root / variant.name / name, map_symbols, exports,
                )
                for name, compiler in builder.PROFILES.items()
            }
            built[variant.name] = {
                "optimization": variant.optimization,
                "section_gc": variant.gc_sections,
                "lto": variant.lto,
                "merge_all_constants": variant.merge_constants,
                "profiles": profiles,
            }

    baseline = built["baseline-o2"]
    oz = built[SELECTED]
    oz_gc = built["size-oz-gc"]
    lto = built["size-oz-lto-gc"]
    lto_merge = built["size-oz-lto-gc-merge"]
    for name in builder.PROFILES:
        require(
            baseline["profiles"][name]["final"]["byte_capacity_fit"] is False,
            f"{name}: baseline capacity result drift",
        )
        require(
            built["size-os"]["profiles"][name]["final"][
                "byte_capacity_fit"
            ] is False,
            f"{name}: -Os capacity result drift",
        )
        require(
            oz["profiles"][name]["final"]["byte_capacity_fit"] is True,
            f"{name}: -Oz capacity result drift",
        )
        require(
            oz["profiles"][name]["objects"]["final_binary"] ==
            oz_gc["profiles"][name]["objects"]["final_binary"],
            f"{name}: section GC unexpectedly changes complete rooted closure",
        )
        require(
            lto["profiles"][name]["objects"]["final_binary"] ==
            lto_merge["profiles"][name]["objects"]["final_binary"],
            f"{name}: constant merging unexpectedly changes LTO result",
        )

    result: dict[str, Any] = {
        "schema_version": 1,
        "status": "g2-freetype-cff-byte-capacity-closed-scatter-link-unproven",
        "analysis_mode": (
            "software-only deterministic optimization experiment; no placement, "
            "patch, firmware image, or hardware operation"
        ),
        "inputs": {
            path.relative_to(G2).as_posix(): {
                "bytes": expected[0], "sha256": expected[1],
            }
            for path, expected in PINS.items()
        },
        "source_and_policy": {
            "upstream": "FreeType 2.9.1 / VER-2-9-1 / 86bc8a95056c97a810986434a3f268cbe67f2902",
            "complete_stock_map": {
                "functions": 101, "callable_bytes": 16_718,
                "physical_bytes": 16_924, "unresolved_callable_bytes": 0,
            },
            "source_inventory": source_inventory,
            "source_files_modified_for_optimization": 0,
            "preprocessor_definitions_added_for_optimization": [],
            "already_authenticated_configuration": {
                "environment_properties": False,
                "zlib": False,
                "incremental_loading": True,
                "old_cff_engine": False,
                "subpixel_rendering": False,
                "default_and_only_cff_hinting_engine": "Adobe",
                "cff_module_index": 2,
            },
            "additional_source_branch_eliminations_admitted": 0,
            "reason": (
                "the recovered G2 configuration already expresses every "
                "authenticated exclusion; no new feature or input restriction "
                "was introduced to obtain the size result"
            ),
        },
        "retained_compiler_runtime_provider": aeabi_provider,
        "legal_scatter_capacity_upper_bound": LEGAL_CAPACITY,
        "variants": built,
        "selected_candidate": {
            "name": SELECTED,
            "reason": (
                "smallest reviewed non-LTO whole-translation-unit result; "
                "retains the explicit callback relocation audit surface"
            ),
            "source_files_modified": 0,
            "section_gc_used": False,
            "lto_used": False,
            "constant_merging_used": False,
            "abi_or_feature_definitions_changed": False,
            "public_exports": list(exports),
            "complete_map_coverage": {
                "source_functions": 101,
                "materialized_named_functions": 81,
                "inlined_only_functions": 20,
                "address_taken_callback_relocations": 58,
                "distinct_callback_targets": 55,
                "public_roots": len(exports),
                "rooted_section_gc_binary_is_byte_identical": True,
                "proof": (
                    "clang inline remarks cover exactly the 20 nonmaterialized "
                    "map names; all 81 emitted map functions survive GC rooted "
                    "at cff_driver_class and the six adapter exports"
                ),
            },
            "profiles": oz["profiles"],
        },
        "optimization_conclusions": {
            "os_closes_byte_capacity": False,
            "oz_closes_byte_capacity": True,
            "section_gc_additional_bytes_saved_after_complete_roots": 0,
            "lto_closes_byte_capacity": True,
            "lto_selected": False,
            "lto_rejection_reason": (
                "LTO internalizes and folds the independently auditable source "
                "function/callback symbol surface; its smaller result is recorded "
                "but is unnecessary for byte capacity and is not selected"
            ),
            "constant_merging_additional_bytes_saved_after_lto": 0,
            "source_level_feature_elimination_used": False,
        },
        "semantic_bounds": {
            "same_complete_upstream_translation_unit": True,
            "same_recovered_g2_configuration": True,
            "same_policy_adapter_source": True,
            "same_allocator_and_error_paths_source": True,
            "same_module_class_and_callback_tables_source": True,
            "same_supported_cff_inputs": True,
            "compiler_optimization_preserves_defined_c_semantics": True,
            "compiler_byte_identity_claimed": False,
            "font_payload_authenticated": False,
            "target_execution_performed": False,
            "hardware_validation_performed": False,
        },
        "routing": {
            "byte_capacity_threshold_closed": True,
            "exact_scatter_placement_proven": False,
            "production_route_permitted": False,
            "module_class_pointer_patch_permitted": False,
            "firmware_image_emitted": False,
        },
    }
    result["experiment_sha256"] = canonical({
        "source_and_policy": result["source_and_policy"],
        "retained_compiler_runtime_provider": aeabi_provider,
        "variants": built,
        "selected_candidate": result["selected_candidate"],
        "optimization_conclusions": result["optimization_conclusions"],
        "routing": result["routing"],
    })
    validate_selected_contract(result)
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
                    "checked-in CFF size-optimization manifest drift")
    except (OptimizationError, OSError, KeyError, ValueError) as error:
        print(f"G2 FreeType CFF size optimization failed: {error}", file=sys.stderr)
        return 1
    print(rendered if args.pretty else json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
