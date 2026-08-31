#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

"""Build a deterministic, relocatable CFF placement/link census.

The output is a linkable Cortex-M55 object and an exact accounting report.  It
does not assign runtime addresses, bind imports, patch the stock module table,
or emit a firmware image.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


G2 = Path(__file__).resolve().parents[3]
COMPONENT = Path(__file__).resolve().parent
FREETYPE = G2 / "third_party/freetype"
CFF_SOURCE = FREETYPE / "src/cff/cff.c"
POLICY_SOURCE = COMPONENT / "runtime_freetype_cff.c"
IMPORT_SOURCE = COMPONENT / "runtime_freetype_cff_import_providers.c"
LINKER_SCRIPT = COMPONENT / "placement_census.ld"
FINAL_LINKER_SCRIPT = COMPONENT / "placement_final.ld"
TARGET_COMPAT = G2 / "research/candidates/freetype/target_compat"
G2_CONFIG = G2 / "research/candidates/freetype/g2_config"

LLVM_ROOT = Path("/opt/homebrew/opt/llvm@22/bin")
TOOLS = {
    "lld": Path("/opt/homebrew/bin/ld.lld"),
    "nm": LLVM_ROOT / "llvm-nm",
    "objcopy": LLVM_ROOT / "llvm-objcopy",
    "readobj": LLVM_ROOT / "llvm-readobj",
    "size": LLVM_ROOT / "llvm-size",
}
PROFILES = {
    "apple-clang": Path("/usr/bin/clang"),
    "linux-clang": LLVM_ROOT / "clang",
}
TARGET_FLAGS = (
    "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
    "-mfloat-abi=hard", "-std=c11", "-O2", "-fshort-enums",
    "-ffreestanding", "-fno-builtin", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fno-addrsig",
    "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
    "-Werror", "-DFT2_BUILD_LIBRARY",
    "-DOPEN_CFW_FREETYPE_JMP_BUF_BYTES=128",
    "-DOPEN_CFW_FREETYPE_JMP_BUF_ALIGNMENT=8",
)
LOADABLE_SECTIONS = (
    ".placement_prefix", ".text", ".arm_exidx", ".rodata", ".data", ".bss"
)
REQUIRED_EXPORTS = (
    "cff_driver_class",
    "open_cfw_freetype_cff_get_darkening_parameters",
    "open_cfw_freetype_cff_get_hinting_engine",
    "open_cfw_freetype_cff_get_no_stem_darkening",
    "open_cfw_freetype_cff_set_darkening_parameters",
    "open_cfw_freetype_cff_set_hinting_engine",
    "open_cfw_freetype_cff_set_no_stem_darkening",
)
SOURCE_OWNED_IMPORTS = (
    "FT_Property_Get", "FT_Property_Set", "FT_Stream_Pos",
    "memcmp", "memcpy", "memset", "strcmp", "strlen", "strncmp", "strstr",
)
RETAINED_BINDINGS = {
    "FT_CMap_New": 0x00526E5A,
    "FT_DivFix": 0x00524754,
    "FT_Get_Module": 0x005273B8,
    "FT_Get_Module_Interface": 0x005273F2,
    "FT_Matrix_Multiply_Scaled": 0x00524820,
    "FT_MulDiv": 0x00524606,
    "FT_Outline_Get_CBox": 0x00527ACE,
    "FT_Outline_Transform": 0x00527BA0,
    "FT_Outline_Translate": 0x00527B2E,
    "FT_Request_Metrics": 0x00526B04,
    "FT_RoundFix": 0x005244EE,
    "FT_Select_Metrics": 0x00526A9C,
    "FT_Stream_EnterFrame": 0x005289D0,
    "FT_Stream_ExitFrame": 0x00528A66,
    "FT_Stream_ExtractFrame": 0x00528992,
    "FT_Stream_GetUShort": 0x00528AA0,
    "FT_Stream_Read": 0x00528928,
    "FT_Stream_ReadChar": 0x00528AFA,
    "FT_Stream_ReadFields": 0x00528C14,
    "FT_Stream_ReadULong": 0x00528BA8,
    "FT_Stream_ReadUShort": 0x00528B4A,
    "FT_Stream_ReleaseFrame": 0x005289B0,
    "FT_Stream_Seek": 0x005288E0,
    "FT_Stream_Skip": 0x00528914,
    "FT_Vector_Transform_Scaled": 0x005248AE,
    "ft_mem_alloc": 0x00529148,
    "ft_mem_free": 0x00529256,
    "ft_mem_realloc": 0x0052919C,
    "ft_mem_strcpyn": 0x005292BC,
    "ft_mem_strdup": 0x00529296,
    "ft_module_get_service": 0x00527406,
    "ft_service_list_lookup": 0x00524F44,
    "ft_synthesize_vertical_metrics": 0x00526A02,
    "ps_property_get": 0x00527FF2,
    "ps_property_set": 0x00527F0A,
}
FINAL_INTERVAL = (0x007ECA44, 0x007FE000)


class CensusError(RuntimeError):
    """Raised when the deterministic CFF build contract is violated."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CensusError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command: list[str]) -> str:
    try:
        return subprocess.run(
            command, check=True, capture_output=True, text=True
        ).stdout
    except subprocess.CalledProcessError as error:
        raise CensusError(
            f"command failed ({' '.join(command)}): {error.stderr.strip()}"
        ) from error


def _compile(compiler: Path, source: Path, output: Path) -> None:
    includes = (
        TARGET_COMPAT, G2_CONFIG, FREETYPE / "g2-config",
        FREETYPE / "include", FREETYPE, COMPONENT,
    )
    run([
        str(compiler), *TARGET_FLAGS,
        *(argument for path in includes for argument in ("-I", str(path))),
        "-c", str(source), "-o", str(output),
    ])


def _sections(path: Path, output_dir: Path) -> dict[str, dict[str, Any]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    sizes: dict[str, int] = {}
    for line in run([str(TOOLS["size"]), "-A", str(path)]).splitlines():
        match = re.match(r"^(\S+)\s+(\d+)\s+\d+$", line)
        if match:
            sizes[match.group(1)] = int(match.group(2))

    alignments: dict[str, int] = {}
    addresses: dict[str, int] = {}
    section = ""
    for line in run([str(TOOLS["readobj"]), "--sections", str(path)]).splitlines():
        match = re.match(r"\s+Name: (\S+) \(\d+\)$", line)
        if match:
            section = match.group(1)
            continue
        match = re.match(r"\s+Address: (0x[0-9A-F]+)$", line)
        if match and section:
            addresses[section] = int(match.group(1), 16)
            continue
        match = re.match(r"\s+AddressAlignment: (\d+)$", line)
        if match and section:
            alignments[section] = int(match.group(1))

    result: dict[str, dict[str, Any]] = {}
    for name in LOADABLE_SECTIONS:
        size = sizes.get(name, 0)
        record: dict[str, Any] = {
            "size": size,
            "alignment": alignments.get(name, 1),
            "address": addresses.get(name, 0),
            "sha256": hashlib.sha256(b"").hexdigest(),
        }
        if size:
            extracted = output_dir / f"section-{name.removeprefix('.').replace('.', '-')}.bin"
            run([
                str(TOOLS["objcopy"]), "--dump-section",
                f"{name}={extracted}", str(path),
            ])
            require(extracted.stat().st_size == size,
                    f"{name}: extracted section size drift")
            record["sha256"] = sha256(extracted)
        result[name.removeprefix(".")] = record
    return result


def _symbols(path: Path) -> tuple[list[str], list[str]]:
    output = run([str(TOOLS["nm"]), "--format=posix", str(path)])
    defined: set[str] = set()
    undefined: set[str] = set()
    for line in output.splitlines():
        fields = line.split()
        if len(fields) < 2:
            continue
        name, kind = fields[0], fields[1]
        if kind.upper() == "U":
            undefined.add(name)
        elif kind.isupper() and kind.upper() not in {"N"}:
            defined.add(name)
    return sorted(defined), sorted(undefined)


def _symbol_addresses(path: Path, required: tuple[str, ...]) -> dict[str, int]:
    output = run([str(TOOLS["nm"]), "--format=posix", str(path)])
    addresses: dict[str, int] = {}
    for line in output.splitlines():
        fields = line.split()
        if len(fields) >= 3 and fields[0] in required and fields[1].upper() != "U":
            addresses[fields[0]] = int(fields[2], 16)
    require(set(addresses) == set(required), "final export address set drift")
    return dict(sorted(addresses.items()))


def _relocations(path: Path, undefined: set[str]) -> dict[str, Any]:
    output = run([
        str(TOOLS["readobj"]), "--relocations", "--expand-relocs", str(path)
    ])
    section = ""
    record: dict[str, Any] | None = None
    records: list[dict[str, Any]] = []
    for line in output.splitlines():
        match = re.match(r"\s+Section \(\d+\) (\S+) \{", line)
        if match:
            section = match.group(1)
            continue
        if line.strip() == "Relocation {":
            record = {"section": section}
            continue
        if record is None:
            continue
        match = re.match(r"\s+Offset: (0x[0-9A-F]+)$", line)
        if match:
            record["offset"] = int(match.group(1), 16)
            continue
        match = re.match(r"\s+Type: (\S+) \(\d+\)$", line)
        if match:
            record["type"] = match.group(1)
            continue
        match = re.match(r"\s+Symbol: (\S+) \(\d+\)$", line)
        if match:
            record["symbol"] = match.group(1)
            continue
        if line.strip() == "}" and {
            "section", "offset", "type", "symbol"
        } <= record.keys():
            records.append(record)
            record = None
    external = [row for row in records if row["symbol"] in undefined]
    payload = json.dumps(records, sort_keys=True, separators=(",", ":")).encode()
    return {
        "total": len(records),
        "internal": len(records) - len(external),
        "external": len(external),
        "by_type": dict(sorted(Counter(row["type"] for row in records).items())),
        "external_by_symbol": dict(sorted(Counter(
            row["symbol"] for row in external
        ).items())),
        "records_sha256": hashlib.sha256(payload).hexdigest(),
    }


def _aligned_span(sections: dict[str, dict[str, Any]]) -> int:
    cursor = 0
    for name in ("text", "arm_exidx", "rodata", "data"):
        record = sections[name]
        alignment = record["alignment"]
        require(alignment > 0 and alignment & (alignment - 1) == 0,
                f"{name}: invalid section alignment")
        cursor = (cursor + alignment - 1) & -alignment
        cursor += record["size"]
    return cursor


def build_once(profile: str, compiler: Path, directory: Path) -> dict[str, Any]:
    directory.mkdir(parents=True)
    cff = directory / "cff.o"
    policy = directory / "policy.o"
    providers = directory / "import-providers.o"
    linked = directory / "cff-placement-census.o"
    closed = directory / "cff-provider-closed.o"
    final_elf = directory / "cff-final.elf"
    final_binary = directory / "cff-final.bin"
    _compile(compiler, CFF_SOURCE, cff)
    _compile(compiler, POLICY_SOURCE, policy)
    _compile(compiler, IMPORT_SOURCE, providers)
    run([
        str(TOOLS["lld"]), "-m", "armelf", "-r", "-T", str(LINKER_SCRIPT),
        str(cff), str(policy), "-o", str(linked),
    ])
    defined, undefined = _symbols(linked)
    require(set(REQUIRED_EXPORTS) <= set(defined),
            f"{profile}: required CFF exports missing")
    sections = _sections(linked, directory)
    require(sections["data"]["size"] == 0 and sections["bss"]["size"] == 0,
            f"{profile}: writable static sections unexpectedly appeared")
    relocations = _relocations(linked, set(undefined))
    require(set(relocations["external_by_symbol"]) == set(undefined),
            f"{profile}: import without relocation or relocation without import")
    require(set(undefined) == set(RETAINED_BINDINGS) | set(SOURCE_OWNED_IMPORTS),
            f"{profile}: original import ownership partition drift")

    run([
        str(TOOLS["lld"]), "-m", "armelf", "-r", "-T", str(LINKER_SCRIPT),
        str(cff), str(policy), str(providers), "-o", str(closed),
    ])
    closed_defined, closed_undefined = _symbols(closed)
    require(set(REQUIRED_EXPORTS) <= set(closed_defined) and
            set(closed_undefined) == set(RETAINED_BINDINGS),
            f"{profile}: source-owned import closure drift")
    closed_relocations = _relocations(closed, set(closed_undefined))
    source_owned_relocations = sum(
        relocations["external_by_symbol"][name] for name in SOURCE_OWNED_IMPORTS
    )
    require(source_owned_relocations + closed_relocations["external"] ==
            relocations["external"],
            f"{profile}: 255-relocation ownership partition drift")

    run([
        str(TOOLS["lld"]), "-m", "armelf", "-T", str(FINAL_LINKER_SCRIPT),
        *(f"--defsym={name}=0x{address:08X}"
          for name, address in sorted(RETAINED_BINDINGS.items())),
        str(cff), str(policy), str(providers), "-o", str(final_elf),
    ])
    run([
        str(TOOLS["objcopy"]), "-O", "binary", str(final_elf),
        str(final_binary),
    ])
    final_defined, final_undefined = _symbols(final_elf)
    final_relocations = _relocations(final_elf, set(final_undefined))
    require(not final_undefined and final_relocations["total"] == 0,
            f"{profile}: final link retains imports or relocations")
    final_sections = _sections(final_elf, directory / "final-sections")
    final_addresses = _symbol_addresses(final_elf, REQUIRED_EXPORTS)
    interval_start, interval_end = FINAL_INTERVAL
    require(final_sections["placement_prefix"]["address"] == interval_start and
            final_sections["text"]["address"] == 0x007ECA50,
            f"{profile}: final placement start/alignment drift")
    final_end = max(
        record["address"] + record["size"]
        for record in final_sections.values() if record["size"]
    )
    require(final_end <= interval_end and
            len(final_binary.read_bytes()) == final_end - interval_start,
            f"{profile}: final payload interval accounting drift")
    require(interval_start <= final_addresses["cff_driver_class"] < final_end,
            f"{profile}: final CFF class escapes payload")
    return {
        "compiler_version": run([str(compiler), "--version"]).splitlines()[0],
        "target_flags": list(TARGET_FLAGS),
        "objects": {
            "cff": {"size": cff.stat().st_size, "sha256": sha256(cff)},
            "policy": {"size": policy.stat().st_size, "sha256": sha256(policy)},
            "import_providers": {
                "size": providers.stat().st_size, "sha256": sha256(providers),
            },
            "relocatable_link": {
                "size": linked.stat().st_size, "sha256": sha256(linked),
            },
            "provider_closed_link": {
                "size": closed.stat().st_size, "sha256": sha256(closed),
            },
            "final_elf": {
                "size": final_elf.stat().st_size, "sha256": sha256(final_elf),
            },
            "final_binary": {
                "size": final_binary.stat().st_size,
                "sha256": sha256(final_binary),
            },
        },
        "sections": sections,
        "flash_loadable_bytes": sum(
            sections[name]["size"]
            for name in ("text", "arm_exidx", "rodata", "data")
        ),
        "required_aligned_flash_span": _aligned_span(sections),
        "static_ram_bytes": sections["data"]["size"] + sections["bss"]["size"],
        "required_exports": list(REQUIRED_EXPORTS),
        "defined_global_symbols": defined,
        "imports": undefined,
        "relocations": relocations,
        "provider_closure": {
            "source_owned_symbols": list(SOURCE_OWNED_IMPORTS),
            "source_owned_original_relocations": source_owned_relocations,
            "retained_symbols": sorted(RETAINED_BINDINGS),
            "retained_original_relocations": closed_relocations["external"],
            "remaining_imports": closed_undefined,
            "relocations": closed_relocations,
        },
        "finalized": {
            "interval_start": interval_start,
            "interval_end_exclusive": interval_end,
            "payload_end_exclusive": final_end,
            "remaining_bytes": interval_end - final_end,
            "sections": final_sections,
            "export_addresses": final_addresses,
            "undefined_symbols": final_undefined,
            "relocations": final_relocations,
        },
    }


def _reproducible(profile: str, compiler: Path, directory: Path) -> dict[str, Any]:
    first_dir = directory / "first"
    second_dir = directory / "second"
    first = build_once(profile, compiler, first_dir)
    second = build_once(profile, compiler, second_dir)
    require(first == second, f"{profile}: deterministic report drift")
    for name in (
        "cff.o", "policy.o", "import-providers.o", "cff-placement-census.o",
        "cff-provider-closed.o", "cff-final.elf", "cff-final.bin",
    ):
        require((first_dir / name).read_bytes() == (second_dir / name).read_bytes(),
                f"{profile}: {name} is not byte-reproducible")
    return first


def build_profiles(output_dir: Path | None = None) -> dict[str, Any]:
    for name, tool in {**TOOLS, **PROFILES}.items():
        require(tool.is_file(), f"required reviewed tool unavailable: {name}: {tool}")
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        return {
            profile: _reproducible(profile, compiler, output_dir / profile)
            for profile, compiler in PROFILES.items()
        }
    with tempfile.TemporaryDirectory(prefix="opencfw-cff-placement-") as temporary:
        root = Path(temporary)
        return {
            profile: _reproducible(profile, compiler, root / profile)
            for profile, compiler in PROFILES.items()
        }


def report(output_dir: Path | None = None) -> dict[str, Any]:
    profiles = build_profiles(output_dir)
    return {
        "schema_version": 1,
        "status": "g2-freetype-cff-deterministic-final-link",
        "mode": "build-only final payload; no firmware image, patch application, or hardware",
        "inputs": {
            path.relative_to(G2).as_posix(): {
                "bytes": path.stat().st_size, "sha256": sha256(path),
            }
            for path in (
                CFF_SOURCE, POLICY_SOURCE, IMPORT_SOURCE, LINKER_SCRIPT,
                FINAL_LINKER_SCRIPT,
            )
        },
        "profiles": profiles,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    try:
        value = report(args.output_dir)
    except (CensusError, OSError, ValueError) as error:
        print(f"CFF placement census build failed: {error}")
        return 1
    print(json.dumps(value, sort_keys=True, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
